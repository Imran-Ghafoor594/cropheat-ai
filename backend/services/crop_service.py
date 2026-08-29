"""Loads data/crop_profiles/*.json and exposes crop/growth-stage lookups.

No thresholds are invented here -- every reference_temperature_c and
heat_sensitivity rating traces to a citation embedded in the profile JSON.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

CROP_PROFILES_DIR = Path(__file__).resolve().parents[2] / "data" / "crop_profiles"

SUPPORTED_CROPS = ("wheat", "maize", "rice", "cotton")


class CropNotFoundError(Exception):
    pass


class GrowthStageNotFoundError(Exception):
    pass


@lru_cache(maxsize=None)
def _load_profile(crop: str) -> dict:
    path = CROP_PROFILES_DIR / f"{crop}.json"
    if not path.exists():
        raise CropNotFoundError(f"No crop profile for {crop!r}. Supported: {SUPPORTED_CROPS}")
    return json.loads(path.read_text())


def list_crops() -> list[str]:
    return list(SUPPORTED_CROPS)


def get_profile(crop: str) -> dict:
    return _load_profile(crop.lower())


def list_growth_stages(crop: str) -> list[str]:
    profile = get_profile(crop)
    return [s["stage"] for s in profile["growth_stages"]]


def get_growth_stage(crop: str, stage: str) -> dict:
    profile = get_profile(crop)
    for s in profile["growth_stages"]:
        if s["stage"] == stage:
            return s
    raise GrowthStageNotFoundError(
        f"No growth stage {stage!r} for crop {crop!r}. Available: {list_growth_stages(crop)}"
    )
