"""Credit budget guard for FortyGuard API calls.

The hackathon key has a fixed, one-time allotment (2,000,000 credits for the
whole event -- confirmed by the user, not published by FortyGuard's docs).
Per-endpoint credit cost is NOT published anywhere in FortyGuard's docs or the
quickstart repo, so this guard does not hardcode a cost table. Instead it:

1. Reads real remaining balance via `fetch_api_key_usage()` before any batch
   operation.
2. Tracks a *calibration log* of (endpoint, credits_before, credits_after) so
   the actual per-call cost is learned empirically from the first few real
   calls in development, instead of guessed.
3. Hard-stops (raises BudgetExceededError) once remaining balance crosses a
   configurable floor, so the app can fall back to DEMO MODE cleanly rather
   than silently draining the key mid-demo.

This module has no opinion about *when* to call FortyGuard -- that decision
(top-N fields, one heatmap per region, etc.) lives in the service layer.
It only answers: "is there budget left, and how much did that last call cost?"
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

logger = logging.getLogger("cropheat.budget_guard")

DEFAULT_FLOOR_FRACTION = 0.05  # stop new live calls once <5% of the total budget remains
CALIBRATION_LOG_PATH = Path("data/credit_calibration_log.jsonl")


class BudgetExceededError(Exception):
    """Raised when the remaining credit balance is at/under the configured floor."""


@dataclass
class BudgetSnapshot:
    plan: str | None
    credits_total: float | None
    credits_used: float | None
    credits_remaining: float | None
    fetched_at: float = field(default_factory=time.time)

    @property
    def remaining_fraction(self) -> float | None:
        if self.credits_total in (None, 0) or self.credits_remaining is None:
            return None
        return self.credits_remaining / self.credits_total


class CreditBudgetGuard:
    
    def __init__(
        self,
        client,
        floor_fraction: float = DEFAULT_FLOOR_FRACTION,
        calibration_log_path: Path | str = CALIBRATION_LOG_PATH,
    ) -> None:
        self._client = client
        self._floor_fraction = floor_fraction
        self._calibration_log_path = Path(calibration_log_path)
        self._calibration_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._snapshot: BudgetSnapshot | None = None

    # ------------------------------------------------------------ balance

    def refresh(self) -> BudgetSnapshot:
      
        raw = self._client.fetch_api_key_usage()
        data = raw.get("data", raw) if isinstance(raw, dict) else {}

        plan_details = data.get("plan_details") or {}
        credit_summary = data.get("credit_summary") or {}

        def _first(*keys):
            for k in keys:
                if k in credit_summary:
                    return credit_summary[k]
                if k in data:
                    return data[k]
            return None

        snapshot = BudgetSnapshot(
            plan=plan_details.get("plan_type") or _first("plan", "tier", "subscription_plan"),
            credits_total=_first("total_available_credits", "credits_total", "total_credits", "monthly_credits"),
            credits_used=_first("cycle_credits_used", "total_credits_used", "credits_used", "used_credits"),
            credits_remaining=_first(
                "cycle_remaining_credits", "total_remaining_credits",
                "credits_remaining", "remaining_credits", "credits_left",
            ),
        )
        if snapshot.credits_remaining is None and snapshot.credits_total is not None and snapshot.credits_used is not None:
            snapshot.credits_remaining = snapshot.credits_total - snapshot.credits_used

        with self._lock:
            self._snapshot = snapshot

        logger.info(
            "FortyGuard budget refreshed: plan=%s remaining=%s/%s",
            snapshot.plan, snapshot.credits_remaining, snapshot.credits_total,
        )
        return snapshot

    @property
    def snapshot(self) -> BudgetSnapshot | None:
        return self._snapshot

    def ensure_budget(self) -> None:
        """Raise BudgetExceededError if remaining balance is at/under the floor.

        Call this before any batch operation that will issue live FortyGuard
        calls (e.g. "load a new region"). Does NOT call refresh() itself --
        callers should refresh() on their own schedule (e.g. once per request,
        or once per N minutes) to avoid burning credits on usage checks alone.
        """
        if self._snapshot is None:
            # No snapshot yet -- fail closed rather than assume budget exists.
            raise BudgetExceededError(
                "No budget snapshot available. Call refresh() before ensure_budget()."
            )
        frac = self._snapshot.remaining_fraction
        if frac is not None and frac <= self._floor_fraction:
            raise BudgetExceededError(
                f"Remaining credit budget ({frac:.1%}) is at/below the "
                f"configured floor ({self._floor_fraction:.1%}). Falling back to DEMO MODE."
            )

    # --------------------------------------------------------- calibration

    class _CallTracker:
        def __init__(self, guard: "CreditBudgetGuard", label: str) -> None:
            self._guard = guard
            self._label = label
            self._before: BudgetSnapshot | None = None

        def __enter__(self):
            self._before = self._guard.snapshot
            return self

        def __exit__(self, exc_type, exc, tb):
            if exc_type is not None:
                return False  # don't swallow exceptions; don't log a cost for a failed call
            after = self._guard.refresh()
            before = self._before
            cost = None
            if before and before.credits_remaining is not None and after.credits_remaining is not None:
                cost = before.credits_remaining - after.credits_remaining
            entry = {
                "label": self._label,
                "credits_before": before.credits_remaining if before else None,
                "credits_after": after.credits_remaining,
                "observed_cost": cost,
                "ts": time.time(),
            }
            with self._guard._calibration_log_path.open("a") as fh:
                fh.write(json.dumps(entry) + "\n")
            logger.info("Calibration: %s cost %.2f credits (observed)", self._label, cost or -1)
            return False

    def track_call(self, label: str) -> "CreditBudgetGuard._CallTracker":
       
        return self._CallTracker(self, label)