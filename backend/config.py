"""CropHeat backend configuration.

Coverage is validated dynamically, not hardcoded to California -- per
Section 3 of the product spec. `SUPPORTED_REGIONS` is a *starter* config the
team fills in with regions confirmed against the real API key (via a test
heatmap call in a known-good vs known-bad location), not an assumption.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

FORTYGUARD_API_KEY = os.getenv("FORTYGUARD_API_KEY")
FORTYGUARD_BASE_URL = os.getenv("FORTYGUARD_BASE_URL", "https://api.fortyguard.com")

# Credit budget guard floor: stop live calls once remaining credits fall to/below
# this fraction of the total hackathon allotment (2,000,000 credits, per the user).
CREDIT_BUDGET_FLOOR_FRACTION = float(os.getenv("CREDIT_BUDGET_FLOOR_FRACTION", "0.05"))

# FortyGuard's documented hard constraints (from the quickstart repo, not assumed):
COVERAGE_COUNTRY = "US"  # confirmed US-only in the quickstart repo README
MIN_SUPPORTED_DATE = "2021-01-01"
HEATMAP_GRANULARITY_OPTIONS = (60, 80, 100)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CROP_PROFILES_DIR = DATA_DIR / "crop_profiles"

# Starter region: San Jose, CA area, sized to fit FortyGuard's Basic-tier
# heatmap area cap (~10 sq mi). CONFIRMED working against a live key as of
# this build -- the earlier ~629 sq-mi Central Valley placeholder silently
# failed every real heatmap call (rejected for exceeding the area cap),
# which is why demo mode kept appearing even with a valid, funded key.
DEFAULT_REGION_AOI_PLACEHOLDER = {
    "type": "Polygon",
    "coordinates": [
        [
            [-121.9213, 37.3135],
            [-121.8848, 37.3135],
            [-121.8848, 37.3425],
            [-121.9213, 37.3425],
            [-121.9213, 37.3135],
        ]
    ],
    "_note": "~4 sq mi, confirmed under Basic tier's area cap. Centered on the frontend's SAMPLE_FIELDS (San Jose, CA).",
}