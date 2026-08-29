"""HumidityRisk / WetBulbRisk — combines FortyGuard env_params fields
(apparent_temperature_celsius, wet_bulb_temperature_celsius,
relative_humidity_percent) into one component.

IMPORTANT (documented in the quickstart repo, README section on env_params):
env_params anchors a single `temperature` value across all 24 returned hours
and only varies humidity, so `heat_index_celsius` artifactually peaks
overnight rather than at the true afternoon maximum. CropHeat therefore:
  (a) excludes heat_index_celsius from the default 3 Basic-tier params
      (see config/risk_config.yaml), and
  (b) only calls env_params at the actual diurnal peak hour (from the
      heatmap's time_of_measure layer or apparent_temperature's own peak),
      never averaging across all 24 hours.

Combines wet-bulb (heat stress under humid conditions is physiologically
worse because evaporative cooling is impaired) and apparent temperature into
one severity score.
"""

from __future__ import annotations

from .aggregator import RiskComponent

# Engineering defaults for saturation points.
WET_BULB_SATURATE_C = 30.0       # 30C wet-bulb is widely cited as a serious human/animal heat-stress mark;
                                    # used here as a crop-agnostic upper reference, not a crop-specific finding.
APPARENT_TEMP_SATURATE_DELTA_C = 8.0  # degrees apparent-temp exceeds air temp


def compute(
    *,
    apparent_temperature_c: float | None,
    wet_bulb_temperature_c: float | None,
    relative_humidity_pct: float | None,
    air_temperature_c: float,
    weight: float,
    source: str = "FortyGuard env_params",
) -> RiskComponent:
    sub_scores = []
    notes = []

    if wet_bulb_temperature_c is not None:
        wb_score = max(0.0, min(100.0, (wet_bulb_temperature_c / WET_BULB_SATURATE_C) * 100.0))
        sub_scores.append(wb_score)
        notes.append(f"wet-bulb {wet_bulb_temperature_c:.1f}C")

    if apparent_temperature_c is not None:
        delta = apparent_temperature_c - air_temperature_c
        at_score = max(0.0, min(100.0, (delta / APPARENT_TEMP_SATURATE_DELTA_C) * 100.0))
        sub_scores.append(at_score)
        notes.append(f"apparent temperature {apparent_temperature_c:.1f}C ({delta:+.1f}C vs air temp)")

    if relative_humidity_pct is not None:
        notes.append(f"{relative_humidity_pct:.0f}% relative humidity")

    if not sub_scores:
        return RiskComponent(
            name="humidity_wetbulb",
            score_0_100=0.0,
            weight=weight,
            source=source,
            explanation="No env_params data available for this field; humidity/wet-bulb contribution treated as zero.",
        )

    score = sum(sub_scores) / len(sub_scores)
    explanation = "Elevated humidity stress: " + ", ".join(notes) + "." if score > 30 else "Humidity/wet-bulb conditions within normal range: " + ", ".join(notes) + "."

    return RiskComponent(name="humidity_wetbulb", score_0_100=score, weight=weight, source=source, explanation=explanation)
