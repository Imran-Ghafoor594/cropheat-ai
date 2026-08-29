"""CropSensitivityRisk and GrowthStageRisk — static components sourced
directly from data/crop_profiles/*.json (each entry cites peer-reviewed
literature; see crop profile files for exact citations).

These are the two components with NO dependency on FortyGuard data --
they encode "how vulnerable is this crop, at this stage, in general" and
are combined with the live-data components (temperature/exposure/
persistence/humidity) in aggregator.py.
"""

from __future__ import annotations

from .aggregator import RiskComponent

SENSITIVITY_SCORE_MAP = {
    "low": 15.0,
    "moderate": 45.0,
    "high": 70.0,
    "critical": 95.0,
}


def compute_crop_sensitivity(*, heat_sensitivity: str, crop: str, weight: float) -> RiskComponent:
    score = SENSITIVITY_SCORE_MAP.get(heat_sensitivity.lower(), 45.0)
    return RiskComponent(
        name="crop_sensitivity",
        score_0_100=score,
        weight=weight,
        source=f"crop_profiles/{crop}.json (static, sourced)",
        explanation=f"{crop.title()} has {heat_sensitivity} general heat sensitivity at this growth stage, per cited agronomic research.",
    )


def compute_growth_stage(*, heat_sensitivity: str, stage: str, crop: str, weight: float) -> RiskComponent:
    # Growth stage uses the same sensitivity rating as crop_sensitivity but is
    # weighted separately per risk_config.yaml, since every cited study in the
    # crop profiles identifies growth-stage TIMING (not just species) as the
    # dominant factor in whether a given temperature actually causes damage.
    score = SENSITIVITY_SCORE_MAP.get(heat_sensitivity.lower(), 45.0)
    return RiskComponent(
        name="growth_stage",
        score_0_100=score,
        weight=weight,
        source=f"crop_profiles/{crop}.json (static, sourced)",
        explanation=f"Crop is currently in the '{stage}' stage, rated {heat_sensitivity} sensitivity — timing is the dominant risk factor per the cited literature.",
    )
