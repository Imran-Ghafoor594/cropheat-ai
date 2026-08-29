"""SQLite cache for FortyGuard responses.

Design goal (per the 2M-credit hackathon budget): never call FortyGuard twice
for the same (region, date, analytic_type, threshold/params) combination.

Cache policy:
- Past dates (before "today" in the user's local context): cached indefinitely.
  A historical exceedance/persistence result for 2026-07-15 will never change.
- "Today": short TTL (default 1 hour) since conditions are still evolving.
- Simulation (`/simulate`) NEVER reads or writes this cache -- it operates
  purely on values already fetched, doing local arithmetic only.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("data/cropheat_cache.sqlite3")
TODAY_TTL_SECONDS = 3600  # 1 hour


def _connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fortyguard_cache (
            cache_key TEXT PRIMARY KEY,
            request_summary TEXT NOT NULL,
            response_json TEXT NOT NULL,
            request_date TEXT,
            fetched_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def make_cache_key(
    *,
    aoi_or_point: dict,
    request_date: str,
    analytic_type: str,
    threshold: float | None = None,
    extra: dict | None = None,
) -> str:
    """Deterministic cache key for a FortyGuard request.

    aoi_or_point: the polygon_aoi dict (heatmap) or {"lat": .., "lon": ..} (env_params).
    Hashing the AOI/point ensures identical geometry always maps to the same key,
    regardless of field ordering.
    """
    payload = {
        "aoi_or_point": aoi_or_point,
        "request_date": request_date,
        "analytic_type": analytic_type,
        "threshold": threshold,
        "extra": extra or {},
    }
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class FortyGuardCache:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH, today_ttl_seconds: int = TODAY_TTL_SECONDS):
        self._db_path = db_path
        self._today_ttl = today_ttl_seconds

    def get(self, cache_key: str) -> dict | None:
        conn = _connect(self._db_path)
        try:
            row = conn.execute(
                "SELECT response_json, request_date, fetched_at FROM fortyguard_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        response_json, request_date, fetched_at = row
        if self._is_today(request_date) and self._is_stale(fetched_at):
            return None  # expired "today" entry -- caller should re-fetch
        return json.loads(response_json)

    def set(self, cache_key: str, response: dict, request_date: str, request_summary: str = "") -> None:
        conn = _connect(self._db_path)
        try:
            conn.execute(
                """
                INSERT INTO fortyguard_cache (cache_key, request_summary, response_json, request_date, fetched_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    response_json=excluded.response_json,
                    fetched_at=excluded.fetched_at
                """,
                (cache_key, request_summary, json.dumps(response), request_date, dt.datetime.utcnow().timestamp()),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _is_today(request_date: str | None) -> bool:
        if not request_date:
            return False
        try:
            d = dt.date.fromisoformat(request_date[:10])
        except ValueError:
            return False
        return d == dt.date.today()

    def _is_stale(self, fetched_at: float) -> bool:
        return (dt.datetime.utcnow().timestamp() - fetched_at) > self._today_ttl
