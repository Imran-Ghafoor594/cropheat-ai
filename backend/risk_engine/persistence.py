"""PersistenceRisk — longest CONTINUOUS run of hours past threshold, from
FortyGuard's `persistence` heatmap layer. Continuous heat exposure is
generally more physiologically damaging than the same total hours spread
across multiple short episodes with recovery windows in between (this is
the standard rationale in the heat-stress literature cited in the crop
profiles for exposure duration mattering; persistence isolates the
"no recovery window" case specifically).
"""

from __future__ import annotations

from .aggregator import RiskComponent

# Engineering default: 8+ continuous hours saturates the score.
HOURS_TO_SATURATE = 8.0


def compute(*, persistence_hours: float, weight: float, source: str = "FortyGuard heatmap:persistence") -> RiskComponent:
    score = max(0.0, min(100.0, (persistence_hours / HOURS_TO_SATURATE) * 100.0))
    explanation = (
        f"The longest continuous heat episode lasted {persistence_hours:.1f} hours with no recovery window."
        if persistence_hours > 0
        else "No continuous heat episode recorded in the analyzed window."
    )
    return RiskComponent(name="persistence", score_0_100=score, weight=weight, source=source, explanation=explanation)
