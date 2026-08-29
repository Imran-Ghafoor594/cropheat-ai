""" risk endpoint.

POST /api/risk -> per-field risk_score, risk_level, and full component
breakdown (temperature/exposure/persistence/humidity/crop_sensitivity/
growth_stage), using the transparent hybrid risk engine -- no black-box ML.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...fortyguard.client import FortyGuardClient
from ...fortyguard.exceptions import FortyGuardError
from ... import config
from ...models.schemas import EnvironmentRequest, RiskResponse
from ...services.crop_service import CropNotFoundError, GrowthStageNotFoundError
from ...services.fortyguard_service import FortyGuardService
from ...services.risk_service import RiskService
from ...utils.budget_guard import CreditBudgetGuard

router = APIRouter(prefix="/api", tags=["risk"])


def _build_risk_service() -> RiskService:
    if not config.FORTYGUARD_API_KEY:
        fg_service = FortyGuardService(client=None)
    else:
        client = FortyGuardClient(api_key=config.FORTYGUARD_API_KEY, base_url=config.FORTYGUARD_BASE_URL)
        guard = CreditBudgetGuard(client, floor_fraction=config.CREDIT_BUDGET_FLOOR_FRACTION)
        fg_service = FortyGuardService(client=client, budget_guard=guard)
    return RiskService(fg_service)


@router.post("/risk", response_model=RiskResponse)
def get_risk(req: EnvironmentRequest) -> RiskResponse:
    service = _build_risk_service()
    try:
        return service.compute_region_risk(
            region_polygon_aoi=req.region_polygon_aoi,
            fields=req.fields,
            date=req.date,
            crop=req.crop,
            growth_stage=req.growth_stage,
            demo_mode=req.demo_mode,
        )
    except (CropNotFoundError, GrowthStageNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FortyGuardError as exc:
        raise HTTPException(status_code=502, detail=f"FortyGuard error: {exc}") from exc
