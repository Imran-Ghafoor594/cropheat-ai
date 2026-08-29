"""Pydantic models for CropHeat API requests/responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldLocation(BaseModel):
    latitude: float
    longitude: float
    label: str | None = None


class EnvironmentRequest(BaseModel):
    region_polygon_aoi: dict[str, Any] = Field(
        ..., description="GeoJSON-style polygon for the FortyGuard heatmap call, shared across all fields in the region."
    )
    fields: list[FieldLocation] = Field(..., min_length=1)
    date: str = Field(..., description="YYYY-MM-DD, must be within FortyGuard's supported range (2021-01-01 to today).")
    crop: str
    growth_stage: str
    demo_mode: bool = False


class RiskComponentOut(BaseModel):
    name: str
    score_0_100: float
    weight: float
    weighted_contribution: float
    source: str
    explanation: str


class FieldRiskResult(BaseModel):
    label: str | None
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    components: list[RiskComponentOut]
    primary_factors: list[str]
    data_source: str  # LIVE | CACHED | DEMO_DATA


class RiskResponse(BaseModel):
    crop: str
    growth_stage: str
    date: str
    region_data_source: str  # LIVE | CACHED | DEMO_DATA (heatmap-level)
    fields: list[FieldRiskResult]
    budget_snapshot: dict[str, Any] | None = None
    
    heatmap_exceedance: dict[str, Any] | None = None


class SimulationRequest(BaseModel):
    base_risk: RiskResponse
    temperature_delta_c: float = 0.0
    exceedance_hours_override: float | None = None
    persistence_hours_override: float | None = None
    crop: str | None = None
    growth_stage: str | None = None
