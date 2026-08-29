"""FortyGuardService — the only place in CropHeat that talks to FortyGuard.

Credit-conservation rules enforced here:

1. ONE heatmap call per (region, date, analytic_type) serves every field in
   that region. Callers pass a region AOI (not a per-field polygon); fields
   are localized against the cached tile set via `field_mean_from_heatmap`
   (area-weighted mean over overlapping tiles), which costs zero credits.

2. env_params is only called for fields the caller has already identified as
   worth a closer look (e.g. top-N highest heatmap-derived risk) -- this
   service does not decide "who is top-N"; that's risk_service's job. This
   service just makes the call cheap to make correctly: it restricts
   `analysis` to the 3 Basic-tier parameters from risk_config.yaml, and lets
   the caller pass the diurnal-peak hour so we don't pull all 24 hours when
   only the peak matters (see quickstart repo's documented overnight-artifact
   trap for heat_index_celsius).

3. Every call is cache-first (FortyGuardCache) and budget-checked
   (CreditBudgetGuard) before it reaches the network.

4. DEMO MODE: if `demo_mode=True` is passed (or the budget guard trips),
   this service reads from `data/heatmaps/` and `data/env_params/` sample
   files bundled in the quickstart repo instead of calling the API, and
   tags the response with `"source": "DEMO_DATA"` so the UI can label it
   accurately 
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..fortyguard.client import FortyGuardClient
from ..fortyguard.exceptions import FortyGuardError
from ..utils.budget_guard import BudgetExceededError, CreditBudgetGuard
from ..utils.cache import FortyGuardCache, make_cache_key

logger = logging.getLogger("cropheat.fortyguard_service")

DEMO_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class FortyGuardService:
    def __init__(
        self,
        client: FortyGuardClient | None = None,
        cache: FortyGuardCache | None = None,
        budget_guard: CreditBudgetGuard | None = None,
    ) -> None:
        # client is optional so this service can be constructed in DEMO-only
        # contexts (e.g. tests, or a judge demo with no key at all).
        self._client = client
        self._cache = cache or FortyGuardCache()
        self._guard = budget_guard or (CreditBudgetGuard(client) if client else None)

    # --------------------------------------------------------------- mode

    def _should_use_demo(self, requested_demo_mode: bool) -> bool:
        if requested_demo_mode or self._client is None:
            return True
        if self._guard is None:
            return False
        try:

            if self._guard.snapshot is None:
                self._guard.refresh()
            self._guard.ensure_budget()
            return False
        except BudgetExceededError as exc:
            logger.warning("Falling back to DEMO MODE: %s", exc)
            return True

    # ------------------------------------------------------------ heatmap

    def get_region_heatmap(
        self,
        *,
        region_polygon_aoi: dict,
        date: str,
        analytic_type: str,
        threshold: float | None = None,
        direction: str | None = None,
        granularity: int = 100,
        demo_mode: bool = False,
    ) -> dict:
        """One shared heatmap for an entire region. Cached, budget-checked.

        Returns {"source": "LIVE" | "CACHED" | "DEMO_DATA", "data": <heatmap json>}
        """
        cache_key = make_cache_key(
            aoi_or_point=region_polygon_aoi,
            request_date=date,
            analytic_type=analytic_type,
            threshold=threshold,
            extra={"granularity": granularity, "direction": direction},
        )

        if self._should_use_demo(demo_mode):
            return self._demo_heatmap(analytic_type)

        cached = self._cache.get(cache_key)
        if cached is not None:
            # Same unwrap as below -- handles any cache entries written
            # before this fix that still have the old {"result": {...}} shape.
            if isinstance(cached, dict) and "result" in cached and "map_data" not in cached:
                cached = cached["result"]
            self._log_schema_diagnostic(analytic_type, cached)
            return {"source": "CACHED", "data": cached}

        assert self._client is not None and self._guard is not None
        try:
            with self._guard.track_call(f"heatmap:{analytic_type}"):
                result = self._client.create_heatmap(
                    polygon_aoi=region_polygon_aoi,
                    start_date=date,
                    filter_type=3,  # single day
                    granularity=granularity,
                    analytic_type=analytic_type,
                    threshold=threshold,
                    direction=direction,
                    verbose=False,
                )
        except FortyGuardError as exc:
            logger.error("FortyGuard heatmap call failed, falling back to DEMO MODE: %s", exc)
            return self._demo_heatmap(analytic_type)


        if isinstance(result, dict) and "result" in result and "map_data" not in result:
            result = result["result"]

        self._cache.set(cache_key, result, request_date=date, request_summary=f"heatmap:{analytic_type}")
        self._log_schema_diagnostic(analytic_type, result)
        return {"source": "LIVE", "data": result}

    def _log_schema_diagnostic(self, analytic_type: str, result: dict) -> None:
        """Temporary diagnostic: logs the SHAPE of a heatmap response (keys +
        counts only, never the full payload) so the real schema can be
        confirmed against a live key without spending extra credits -- fires
        on both fresh LIVE calls and CACHED hits, since cached data has the
        same real shape as when it was first fetched.
        """
        try:
            top_keys = list(result.keys()) if isinstance(result, dict) else type(result).__name__
            map_data = result.get("map_data") if isinstance(result, dict) else None
            features = (map_data or {}).get("features") if isinstance(map_data, dict) else None
            sample_feature = features[0] if isinstance(features, list) and features else None
            logger.warning(
                "SCHEMA DIAGNOSTIC [%s]: top-level keys=%s | map_data present=%s | "
                "features count=%s | sample feature=%s",
                analytic_type, top_keys, map_data is not None,
                len(features) if isinstance(features, list) else "N/A",
                sample_feature,
            )
        except Exception:  
            logger.warning("SCHEMA DIAGNOSTIC [%s]: failed to introspect response shape", analytic_type)

    # --------------------------------------------------------- env_params

    def get_field_env_params(
        self,
        *,
        latitude: float,
        longitude: float,
        temperature: float,
        date: str,
        peak_hour: str | None = None,
        selected_params: list[str] | None = None,
        demo_mode: bool = False,
    ) -> dict:
    
        point = {"lat": latitude, "lon": longitude}
        cache_key = make_cache_key(
            aoi_or_point=point,
            request_date=date,
            analytic_type="env_params",
            extra={"peak_hour": peak_hour, "params": selected_params},
        )

        if self._should_use_demo(demo_mode):
            return self._demo_env_params()

        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, dict) and "result" in cached and "locations" not in cached:
                cached = cached["result"]
            return {"source": "CACHED", "data": cached}

        assert self._client is not None and self._guard is not None
        filter_type = 1 if peak_hour else 3  # 1=single hour, 3=single day
        try:
            with self._guard.track_call("env_params"):
                result = self._client.environmental_parameters(
                    latitude=latitude,
                    longitude=longitude,
                    temperature=temperature,
                    start_date=date,
                    filter_type=filter_type,
                    start_time=peak_hour,
                    analysis=selected_params,
                    verbose=False,
                )
        except FortyGuardError as exc:
            logger.error("FortyGuard env_params call failed, falling back to DEMO MODE: %s", exc)
            return self._demo_env_params()

    
        if isinstance(result, dict) and "result" in result and "locations" not in result:
            result = result["result"]
        logger.warning(
            "SCHEMA DIAGNOSTIC [env_params]: top-level keys=%s | locations present=%s",
            list(result.keys()) if isinstance(result, dict) else type(result).__name__,
            isinstance(result, dict) and "locations" in result,
        )

        self._cache.set(cache_key, result, request_date=date, request_summary="env_params")
        return {"source": "LIVE", "data": result}

    # ----------------------------------------------------------- budget

    def refresh_budget(self) -> dict | None:
        if self._guard is None:
            return None
        snapshot = self._guard.refresh()
        return {
            "plan": snapshot.plan,
            "credits_total": snapshot.credits_total,
            "credits_remaining": snapshot.credits_remaining,
            "remaining_fraction": snapshot.remaining_fraction,
        }

    # ------------------------------------------------------------ demo data

    def _demo_heatmap(self, analytic_type: str) -> dict:
        candidates = sorted((DEMO_DATA_DIR / "heatmaps").glob(f"*_{analytic_type}.json"))
        if not candidates:
            raise FortyGuardError(f"No demo heatmap sample bundled for analytic_type={analytic_type!r}")
        data = json.loads(candidates[0].read_text())
        return {"source": "DEMO_DATA", "data": data}

    def _demo_env_params(self) -> dict:
        candidates = sorted((DEMO_DATA_DIR / "env_params").glob("*.json"))
        if not candidates:
            raise FortyGuardError("No demo env_params sample bundled")
        data = json.loads(candidates[0].read_text())
        return {"source": "DEMO_DATA", "data": data}