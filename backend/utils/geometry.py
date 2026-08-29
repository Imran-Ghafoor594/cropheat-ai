"""Local (zero-credit) helpers for deriving a per-field value from a
region-wide FortyGuard heatmap response.

Mirrors the pattern in the quickstart repo's parcel-portfolio notebook:
one heatmap call over the whole region, then an area-weighted mean over
whichever tiles a given field's point/polygon overlaps -- never a second
API call per field.

NOTE: The exact tile schema for a heatmap response depends on analytic_type
(see fortyguard/client.py docstring: `tcm` returns per-tile temperature
fields; `exceedance`/`persistence` return `properties.value` interpreted via
`stats_data.units`). This module reads defensively and should be tightened
once a real response has been inspected against these code paths (Stage 2
of the implementation plan).
"""

from __future__ import annotations

from typing import Any


def _tile_value(tile: dict, analytic_type: str) -> float | None:
    props = tile.get("properties", {})
    if analytic_type == "tcm":
        # DISCREPANCY NOTE (per bundled real sample data, checked against the
        # client.py docstring): create_heatmap's docstring says tcm tiles are
        # "in °F", but the actual bundled sample
        # (data/heatmaps/heatmap_parcel_diridon_san_jose_2024-07-15_tcm.json)
        # has `properties.average_temperature` values around 20-21 for a July
        # San Jose reading -- consistent with °C, not °F (68-70°F would be the
        # Fahrenheit equivalent). We trust the actual data over the docstring
        # and treat average_temperature as already-Celsius. This should be
        # re-verified against a live call before Stage 4 (do not assume this
        # holds for every region/time -- flag prominently in code review).
        for key in ("average_temperature", "temperature_f", "temperature", "value"):
            if key in props:
                val = props[key]
                return (val - 32) * 5.0 / 9.0 if key == "temperature_f" else val
        return None
    # exceedance / persistence / time_of_measure: properties.value, confirmed
    # against the real bundled exceedance sample (units="hour" in stats_data).
    return props.get("value")


def nearest_tile_value(heatmap_response: dict, latitude: float, longitude: float, analytic_type: str) -> float | None:
    """Nearest-centroid tile lookup (simple fallback).

    For a true area-weighted mean over a field POLYGON (not just a point),
    use `field_polygon_mean` instead once field boundaries are available
    (e.g. from a farm's GeoJSON boundary, matching the quickstart repo's
    parcel-portfolio notebook pattern exactly).
    """
    # Real heatmap responses nest features under `map_data` (GeoJSON
    # FeatureCollection), confirmed against bundled sample data -- not at the
    # top level as a first guess might assume.
    map_data = heatmap_response.get("map_data", heatmap_response)
    features = map_data.get("features") or heatmap_response.get("features") or heatmap_response.get("tiles") or []
    if not features:
        return None

    def _centroid(tile: dict) -> tuple[float, float] | None:
        geom = tile.get("geometry", {})
        coords = geom.get("coordinates")
        if not coords:
            return None
        # Flatten a Polygon's first ring and average -- adequate for small tiles.
        ring = coords[0] if geom.get("type") == "Polygon" else coords
        xs = [pt[0] for pt in ring]
        ys = [pt[1] for pt in ring]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    best_tile, best_dist = None, float("inf")
    for tile in features:
        c = _centroid(tile)
        if c is None:
            continue
        dist = (c[0] - longitude) ** 2 + (c[1] - latitude) ** 2
        if dist < best_dist:
            best_dist, best_tile = dist, tile

    if best_tile is None:
        return None
    return _tile_value(best_tile, analytic_type)


def peak_env_param_value(env_params_response: dict, param_name: str, peak_hour_index: int | None = None) -> float | None:
    """Extract one scalar from an env_params response for a given parameter.

    Real schema (confirmed against bundled sample data, which differs from a
    flat-dict assumption): {"metadata": {"timestamps": [...24 ISO strings]},
    "locations": [{"lat", "lon", "temperature", "parameters": {param: [24
    hourly values]}}]}. This helper reads locations[0] and either:
      - returns the value at `peak_hour_index` if given (preferred -- caller
        should determine this from apparent_temperature's own peak or the
        heatmap's time_of_measure layer, per the overnight-artifact note in
        risk_engine/humidity.py), or
      - falls back to the max value across the 24-hour array (a reasonable
        proxy for "worst case in the window" when no specific peak hour is
        supplied, e.g. in DEMO MODE).
    """
    locations = env_params_response.get("locations") or []
    if not locations:
        return None
    values = (locations[0].get("parameters") or {}).get(param_name)
    if not values:
        return None
    if peak_hour_index is not None and 0 <= peak_hour_index < len(values):
        return values[peak_hour_index]
    return max(values)
