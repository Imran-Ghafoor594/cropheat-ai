
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...models.schemas import FieldRiskResult, RiskComponentOut, RiskResponse, SimulationRequest
from ...risk_engine.aggregator import classify_risk_level
from ...risk_engine.exposure import HOURS_TO_SATURATE as EXPOSURE_SATURATE
from ...risk_engine.persistence import HOURS_TO_SATURATE as PERSISTENCE_SATURATE
from ...risk_engine.temperature import DEGREES_TO_SATURATE

router = APIRouter(prefix="/api", tags=["simulation"])


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


@router.post("/simulate", response_model=RiskResponse)
def simulate(req: SimulationRequest) -> RiskResponse:
    if not req.base_risk.fields:
        raise HTTPException(status_code=400, detail="base_risk.fields must not be empty")

    new_fields: list[FieldRiskResult] = []
    for field in req.base_risk.fields:
        new_components: list[RiskComponentOut] = []
        for c in field.components:
            score = c.score_0_100
            if c.name == "temperature" and req.temperature_delta_c:
                score = _clamp(score + (req.temperature_delta_c / DEGREES_TO_SATURATE) * 100.0)
            elif c.name == "exposure" and req.exceedance_hours_override is not None:
                score = _clamp((req.exceedance_hours_override / EXPOSURE_SATURATE) * 100.0)
            elif c.name == "persistence" and req.persistence_hours_override is not None:
                score = _clamp((req.persistence_hours_override / PERSISTENCE_SATURATE) * 100.0)
            new_components.append(
                RiskComponentOut(
                    name=c.name,
                    score_0_100=score,
                    weight=c.weight,
                    weighted_contribution=score * c.weight,
                    source=c.source + " (simulated)" if score != c.score_0_100 else c.source,
                    explanation=c.explanation,
                )
            )

        total_weight = sum(c.weight for c in new_components) or 1.0
        new_score = _clamp(sum(c.weighted_contribution for c in new_components) / total_weight)
        ranked = sorted(new_components, key=lambda c: c.weighted_contribution, reverse=True)

        new_fields.append(
            FieldRiskResult(
                label=field.label, latitude=field.latitude, longitude=field.longitude,
                risk_score=new_score, risk_level=classify_risk_level(new_score),
                components=new_components,
                primary_factors=[c.name for c in ranked[:3]],
                data_source="DEMO_DATA" if field.data_source == "DEMO_DATA" else "SIMULATED",  # type: ignore[arg-type]
            )
        )

    return RiskResponse(
        crop=req.crop or req.base_risk.crop,
        growth_stage=req.growth_stage or req.base_risk.growth_stage,
        date=req.base_risk.date,
        region_data_source=req.base_risk.region_data_source,
        fields=new_fields,
        budget_snapshot=req.base_risk.budget_snapshot,
    )
