""" /api/advisory — generates plain-language explanation + action
recommendations from an already-computed field risk result. Never
recomputes or overrides risk_score/risk_level (see advisory_service.py)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ...services.advisory_service import AdvisoryService

router = APIRouter(prefix="/api", tags=["advisory"])


class AdvisoryRequest(BaseModel):
    crop: str
    growth_stage: str
    risk_score: float
    risk_level: str
    primary_factors: list[str]
    component_explanations: dict[str, str] = {}


class AdvisoryResponse(BaseModel):
    summary: str
    recommendations: list[str]
    source: str  # AI_GENERATED | RULE_BASED_FALLBACK


@router.post("/advisory", response_model=AdvisoryResponse)
def get_advisory(req: AdvisoryRequest) -> AdvisoryResponse:
    service = AdvisoryService()
    result = service.generate(
        crop=req.crop, growth_stage=req.growth_stage,
        risk_score=req.risk_score, risk_level=req.risk_level,
        primary_factors=req.primary_factors, component_explanations=req.component_explanations,
    )
    return AdvisoryResponse(**result)
