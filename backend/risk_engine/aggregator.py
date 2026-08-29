"""Transparent hybrid risk engine — combines documented components into a
0-100 risk_score with a full per-component breakdown for explainability.

No supervised ML here by design: no labeled crop-damage dataset exists (see
docs/methodology.md and Section 4/10 of the product spec). Each component
below is either (a) computed from real FortyGuard data, or (b) a static,
sourced value from a crop profile. Weights come from config/risk_config.yaml
and are documented there as engineering defaults, not fitted coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

RISK_LEVELS = (
    ("LOW", 0, 24),
    ("MODERATE", 25, 49),
    ("HIGH", 50, 74),
    ("CRITICAL", 75, 100),
)


def classify_risk_level(score: float) -> str:
    for name, lo, hi in RISK_LEVELS:
        if lo <= score <= hi:
            return name
    return "CRITICAL" if score > 100 else "LOW"


@dataclass
class RiskComponent:
    name: str
    score_0_100: float          # normalized 0-100 severity for this component
    weight: float                # from risk_config.yaml
    source: str                  # e.g. "FortyGuard heatmap:exceedance", "crop_profile:static"
    explanation: str             # one-sentence, user-facing reason

    @property
    def weighted_contribution(self) -> float:
        return self.score_0_100 * self.weight


@dataclass
class RiskResult:
    risk_score: float
    risk_level: str
    components: list[RiskComponent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
            "components": [
                {
                    "name": c.name,
                    "score_0_100": round(c.score_0_100, 1),
                    "weight": c.weight,
                    "weighted_contribution": round(c.weighted_contribution, 1),
                    "source": c.source,
                    "explanation": c.explanation,
                }
                for c in self.components
            ],
        }

    def primary_factors(self, top_n: int = 3) -> list[str]:
        """Names of the top-N components by weighted contribution, for the
        AI advisory layer's structured input (see backend/advisory/)."""
        ranked = sorted(self.components, key=lambda c: c.weighted_contribution, reverse=True)
        return [c.name for c in ranked[:top_n]]


def aggregate(components: list[RiskComponent]) -> RiskResult:
    total_weight = sum(c.weight for c in components) or 1.0
    raw_score = sum(c.weighted_contribution for c in components)
    # Normalize in case weights don't sum to exactly 1.0 (defensive; risk_config.yaml
    # is expected to sum to 1.0, but we don't want a config typo to silently distort scale).
    risk_score = max(0.0, min(100.0, raw_score / total_weight))
    return RiskResult(
        risk_score=risk_score,
        risk_level=classify_risk_level(risk_score),
        components=components,
    )
