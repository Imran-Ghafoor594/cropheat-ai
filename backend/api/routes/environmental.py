""" minimal environment endpoint.

GET-semantics implemented as POST here because the request needs a polygon
AOI + field list in the body (not practical as query params). Retrieves real
FortyGuard heatmap data for a region -- this is the first endpoint that
should be exercised against the real API key to confirm coverage and
calibrate credit cost per call (see utils/budget_guard.py).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...fortyguard.client import FortyGuardClient
from ...fortyguard.exceptions import FortyGuardError
from ... import config
from ...services.fortyguard_service import FortyGuardService
from ...utils.budget_guard import CreditBudgetGuard
from ...models.schemas import EnvironmentRequest

router = APIRouter(prefix="/api", tags=["environment"])


def _build_service() -> FortyGuardService:
    if not config.FORTYGUARD_API_KEY:
        return FortyGuardService(client=None)  # demo-only mode
    client = FortyGuardClient(api_key=config.FORTYGUARD_API_KEY, base_url=config.FORTYGUARD_BASE_URL)
    guard = CreditBudgetGuard(client, floor_fraction=config.CREDIT_BUDGET_FLOOR_FRACTION)
    return FortyGuardService(client=client, budget_guard=guard)


@router.post("/environment")
def get_environment(req: EnvironmentRequest):
    """Fetch the region's tcm/exceedance/persistence heatmaps (one call each,
    shared across every field in `req.fields`) and return the raw layers plus
    data-source labeling (LIVE/CACHED/DEMO_DATA)."""
    service = _build_service()
    try:
        tcm = service.get_region_heatmap(
            region_polygon_aoi=req.region_polygon_aoi, date=req.date,
            analytic_type="tcm", demo_mode=req.demo_mode,
        )
        exceedance = service.get_region_heatmap(
            region_polygon_aoi=req.region_polygon_aoi, date=req.date,
            analytic_type="exceedance", threshold=30.0, direction="above",
            demo_mode=req.demo_mode,
        )
        persistence = service.get_region_heatmap(
            region_polygon_aoi=req.region_polygon_aoi, date=req.date,
            analytic_type="persistence", threshold=30.0, direction="above",
            demo_mode=req.demo_mode,
        )
    except FortyGuardError as exc:
        raise HTTPException(status_code=502, detail=f"FortyGuard error: {exc}") from exc

    return {
        "date": req.date,
        "tcm": tcm,
        "exceedance": exceedance,
        "persistence": persistence,
        "budget": service.refresh_budget(),
    }
