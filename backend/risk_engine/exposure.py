"""ExposureRisk — hours a field's tiles spent past threshold, from FortyGuard's
`exceedance` heatmap layer. Per the quickstart repo's own documented finding,
duration matters more for crop stress than a single peak reading, so this
(and persistence.py) carry a majority of the total weight in risk_config.yaml.

Units note (from fortyguard/client.py docstring): exceedance tiles carry
`properties.value` interpreted via `stats_data.units` (typically "hour") --
a count of hours, not degree-hours.
"""

from __future__ import annotations

from .aggregator import RiskComponent

# Engineering default: 12+ exceedance hours in the analyzed window saturates the score.
HOURS_TO_SATURATE = 12.0


def compute(*, exceedance_hours: float, weight: float, source: str = "FortyGuard heatmap:exceedance") -> RiskComponent:
    score = max(0.0, min(100.0, (exceedance_hours / HOURS_TO_SATURATE) * 100.0))
    explanation = (
        f"The field spent {exceedance_hours:.1f} hours above the heat threshold in the analyzed window."
        if exceedance_hours > 0
        else "No recorded hours above the heat threshold in the analyzed window."
    )
    return RiskComponent(name="exposure", score_0_100=score, weight=weight, source=source, explanation=explanation)
