

from __future__ import annotations

import logging

from ..models.schemas import FieldLocation, FieldRiskResult, RiskComponentOut, RiskResponse
from ..risk_engine import crop_sensitivity, exposure, humidity, persistence, temperature
from ..risk_engine.aggregator import RiskComponent, aggregate
from ..utils.geometry import nearest_tile_value, peak_env_param_value
from . import crop_service
from .fortyguard_service import FortyGuardService

logger = logging.getLogger("cropheat.risk_service")

WEIGHTS = {
    "temperature": 0.15,
    "exposure": 0.15,
    "persistence": 0.20,
    "humidity_wetbulb": 0.15,
    "crop_sensitivity": 0.15,
    "growth_stage": 0.20,
}
ENV_PARAMS_SELECTED = ["apparent_temperature_celsius", "wet_bulb_temperature_celsius", "relative_humidity_percent"]
TOP_N_FOR_ENV_PARAMS = 3


class RiskService:
    def __init__(self, fortyguard_service: FortyGuardService):
        self._fg = fortyguard_service

    def compute_region_risk(
        self,
        *,
        region_polygon_aoi: dict,
        fields: list[FieldLocation],
        date: str,
        crop: str,
        growth_stage: str,
        demo_mode: bool = False,
    ) -> RiskResponse:
        stage_info = crop_service.get_growth_stage(crop, growth_stage)
        threshold_c = stage_info.get("reference_temperature_c")
        heat_sensitivity = stage_info.get("heat_sensitivity", "moderate")

        FALLBACK_HEATMAP_THRESHOLD_C = 35.0
        heatmap_threshold_c = threshold_c if threshold_c is not None else FALLBACK_HEATMAP_THRESHOLD_C


        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=3) as pool:
            exceedance_future = pool.submit(
                self._fg.get_region_heatmap,
                region_polygon_aoi=region_polygon_aoi, date=date,
                analytic_type="exceedance", threshold=heatmap_threshold_c,
                direction="above", demo_mode=demo_mode,
            )
            persistence_future = pool.submit(
                self._fg.get_region_heatmap,
                region_polygon_aoi=region_polygon_aoi, date=date,
                analytic_type="persistence", threshold=heatmap_threshold_c,
                direction="above", demo_mode=demo_mode,
            )
            tcm_future = pool.submit(
                self._fg.get_region_heatmap,
                region_polygon_aoi=region_polygon_aoi, date=date,
                analytic_type="tcm", demo_mode=demo_mode,
            )
            exceedance_resp = exceedance_future.result()
            persistence_resp = persistence_future.result()
            tcm_resp = tcm_future.result()

        region_data_source = exceedance_resp["source"]

        prelim: list[tuple[FieldLocation, list[RiskComponent], float]] = []
        for f in fields:
            exceedance_hours = nearest_tile_value(exceedance_resp["data"], f.latitude, f.longitude, "exceedance") or 0.0
            persistence_hours = nearest_tile_value(persistence_resp["data"], f.latitude, f.longitude, "persistence") or 0.0
            peak_temp_c = nearest_tile_value(tcm_resp["data"], f.latitude, f.longitude, "tcm")
            if peak_temp_c is None:
                peak_temp_c = threshold_c or 30.0

            components = [
                temperature.compute(
                    current_or_peak_temp_c=peak_temp_c, threshold_c=threshold_c,
                    weight=WEIGHTS["temperature"], source="FortyGuard heatmap:tcm",
                ),
                exposure.compute(exceedance_hours=exceedance_hours, weight=WEIGHTS["exposure"]),
                persistence.compute(persistence_hours=persistence_hours, weight=WEIGHTS["persistence"]),
                crop_sensitivity.compute_crop_sensitivity(heat_sensitivity=heat_sensitivity, crop=crop, weight=WEIGHTS["crop_sensitivity"]),
                crop_sensitivity.compute_growth_stage(heat_sensitivity=heat_sensitivity, stage=growth_stage, crop=crop, weight=WEIGHTS["growth_stage"]),
            ]
            prelim_result = aggregate(components)
            prelim.append((f, components, prelim_result.risk_score))

        prelim.sort(key=lambda t: t[2], reverse=True)
        top_n_labels = {id(t[0]) for t in prelim[:TOP_N_FOR_ENV_PARAMS]}

        field_results: list[FieldRiskResult] = []
        for f, components, _prelim_score in prelim:
            data_source = region_data_source
            if id(f) in top_n_labels:
                env_resp = self._fg.get_field_env_params(
                    latitude=f.latitude, longitude=f.longitude,
                    temperature=threshold_c or 30.0, date=date,
                    selected_params=ENV_PARAMS_SELECTED,
                    demo_mode=demo_mode,
                )
                env_data = env_resp["data"] if isinstance(env_resp.get("data"), dict) else {}
                data_source = env_resp["source"]
                humidity_component = humidity.compute(
                    apparent_temperature_c=peak_env_param_value(env_data, "apparent_temperature_celsius"),
                    wet_bulb_temperature_c=peak_env_param_value(env_data, "wet_bulb_temperature_celsius"),
                    relative_humidity_pct=peak_env_param_value(env_data, "relative_humidity_percent"),
                    air_temperature_c=threshold_c or 30.0,
                    weight=WEIGHTS["humidity_wetbulb"],
                )
            else:
                humidity_component = RiskComponent(
                    name="humidity_wetbulb", score_0_100=0.0, weight=WEIGHTS["humidity_wetbulb"],
                    source="not sampled (outside top-N by preliminary risk; credit-conservation policy)",
                    explanation="This field was not in the top-ranked fields for this region, so humidity/wet-bulb data was not fetched to conserve API credits.",
                )

            final = aggregate(components + [humidity_component])
            field_results.append(
                FieldRiskResult(
                    label=f.label, latitude=f.latitude, longitude=f.longitude,
                    risk_score=final.risk_score, risk_level=final.risk_level,
                    components=[RiskComponentOut(**c) for c in final.to_dict()["components"]],
                    primary_factors=final.primary_factors(),
                    data_source=data_source,
                )
            )

        budget_snapshot = self._fg.refresh_budget()
        return RiskResponse(
            crop=crop, growth_stage=growth_stage, date=date,
            region_data_source=region_data_source, fields=field_results,
            budget_snapshot=budget_snapshot,
            heatmap_exceedance=exceedance_resp["data"],
        )