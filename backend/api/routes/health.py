""" GET /api/health/fortyguard — diagnostics endpoint.

Reports whether FortyGuard is actually configured and reachable, WITHOUT
ever exposing the API key. This is what the dashboard's LIVE/DEMO badge
should be based on, rather than silently guessing from a failed call.
"""

from __future__ import annotations

import time

from fastapi import APIRouter
from pydantic import BaseModel

from ... import config
from ...fortyguard.client import FortyGuardClient
from ...fortyguard.exceptions import FortyGuardError

router = APIRouter(prefix="/api/health", tags=["diagnostics"])


class FortyGuardHealth(BaseModel):
    api_configured: bool
    api_reachable: bool
    mode: str  # "LIVE" | "DEMO" | "UNCONFIGURED"
    test_location: str | None = None
    credits_remaining: float | None = None
    credits_total: float | None = None
    plan: str | None = None
    error: str | None = None
    checked_at: float


@router.get("/fortyguard", response_model=FortyGuardHealth)
def fortyguard_health() -> FortyGuardHealth:
    checked_at = time.time()

    if not config.FORTYGUARD_API_KEY:
        return FortyGuardHealth(
            api_configured=False, api_reachable=False, mode="UNCONFIGURED",
            checked_at=checked_at,
            error="FORTYGUARD_API_KEY not set in .env — running in DEMO mode.",
        )

    try:
        client = FortyGuardClient(api_key=config.FORTYGUARD_API_KEY, base_url=config.FORTYGUARD_BASE_URL)
        raw = client.fetch_api_key_usage()
        data = raw.get("data", raw) if isinstance(raw, dict) else {}

        def _first(*keys):
            for k in keys:
                if k in data:
                    return data[k]
            return None

        return FortyGuardHealth(
            api_configured=True, api_reachable=True, mode="LIVE",
            test_location="San Joaquin Valley, CA (unvalidated placeholder — see backend/config.py)",
            credits_remaining=_first("credits_remaining", "remaining_credits", "credits_left"),
            credits_total=_first("credits_total", "total_credits", "monthly_credits"),
            plan=_first("plan", "tier", "subscription_plan"),
            checked_at=checked_at,
        )
    except FortyGuardError as exc:
        return FortyGuardHealth(
            api_configured=True, api_reachable=False, mode="DEMO",
            error=f"FortyGuard configured but unreachable: {exc}. Falling back to DEMO mode.",
            checked_at=checked_at,
        )
    except Exception as exc:  # noqa: BLE001 -- diagnostics endpoint must never itself crash
        return FortyGuardHealth(
            api_configured=True, api_reachable=False, mode="DEMO",
            error=f"Unexpected error checking FortyGuard: {type(exc).__name__}: {exc}",
            checked_at=checked_at,
        )
