"""TemperatureRisk — how far current/peak temperature is past the crop's
growth-stage reference threshold (from crop_profiles/*.json, itself sourced
from peer-reviewed literature -- see data/crop_profiles/README for citations).

Normalization: 0 at/under threshold, scaling to 100 at threshold+10C. The
+10C scale ceiling is a CropHeat engineering default (documented here, not
hidden), not a claim that +10C is a universal biological cutoff.
"""

from __future__ import annotations

from .aggregator import RiskComponent

DEGREES_TO_SATURATE = 10.0  


def compute(
    *,
    current_or_peak_temp_c: float,
    threshold_c: float | None,
    weight: float,
    source: str,
) -> RiskComponent:
    if threshold_c is None:
        # Crop stage has no documented reference temperature (e.g. wheat vegetative).
        return RiskComponent(
            name="temperature",
            score_0_100=0.0,
            weight=weight,
            source=source,
            explanation="No sourced heat-stress threshold for this growth stage; treated as low direct temperature risk.",
        )

    delta = current_or_peak_temp_c - threshold_c
    score = max(0.0, min(100.0, (delta / DEGREES_TO_SATURATE) * 100.0))

    if delta <= 0:
        explanation = f"Temperature ({current_or_peak_temp_c:.1f}C) is at or below the {threshold_c:.0f}C reference threshold for this stage."
    else:
        explanation = f"Temperature ({current_or_peak_temp_c:.1f}C) is {delta:.1f}C above the {threshold_c:.0f}C reference threshold for this growth stage."

    return RiskComponent(
        name="temperature",
        score_0_100=score,
        weight=weight,
        source=source,
        explanation=explanation,
    )
