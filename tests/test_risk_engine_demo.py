"""Risk engine test using bundled real FortyGuard sample data (DEMO MODE) --
no live API key or network access required, that the risk engine be testable without real API calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models.schemas import FieldLocation
from backend.services.fortyguard_service import FortyGuardService
from backend.services.risk_service import RiskService

REGION_AOI = {
    "type": "Polygon",
    "coordinates": [[[-121.91, 37.32], [-121.89, 37.32], [-121.89, 37.34], [-121.91, 37.34], [-121.91, 37.32]]],
}


def _build_demo_risk_service() -> RiskService:
    return RiskService(FortyGuardService(client=None))


def test_wheat_flowering_produces_high_or_critical_risk():

    risk = _build_demo_risk_service()
    result = risk.compute_region_risk(
        region_polygon_aoi=REGION_AOI,
        fields=[FieldLocation(latitude=37.3257, longitude=-121.9057, label="Field A")],
        date="2024-07-15", crop="wheat", growth_stage="flowering", demo_mode=True,
    )
    field = result.fields[0]
    assert field.risk_level in ("HIGH", "CRITICAL")
    assert field.data_source == "DEMO_DATA"
    assert result.region_data_source == "DEMO_DATA"


def test_every_component_has_a_source_and_explanation():

    risk = _build_demo_risk_service()
    result = risk.compute_region_risk(
        region_polygon_aoi=REGION_AOI,
        fields=[FieldLocation(latitude=37.3257, longitude=-121.9057)],
        date="2024-07-15", crop="rice", growth_stage="flowering", demo_mode=True,
    )
    for component in result.fields[0].components:
        assert component.source, f"component {component.name} missing source"
        assert component.explanation, f"component {component.name} missing explanation"


def test_unsampled_fields_beyond_top_n_are_flagged_not_faked():

    risk = _build_demo_risk_service()
    fields = [FieldLocation(latitude=37.3257 + i * 0.001, longitude=-121.9057, label=f"F{i}") for i in range(6)]
    result = risk.compute_region_risk(
        region_polygon_aoi=REGION_AOI, fields=fields, date="2024-07-15",
        crop="maize", growth_stage="silking", demo_mode=True,
    )
    not_sampled = [
        f for f in result.fields
        if any(c.name == "humidity_wetbulb" and "not sampled" in c.source for c in f.components)
    ]
    assert len(not_sampled) >= 1, "expected at least one field beyond top-N to be explicitly marked not-sampled"


def test_invalid_crop_raises():
    from backend.services.crop_service import CropNotFoundError
    import pytest
    risk = _build_demo_risk_service()
    with pytest.raises(CropNotFoundError):
        risk.compute_region_risk(
            region_polygon_aoi=REGION_AOI,
            fields=[FieldLocation(latitude=37.3257, longitude=-121.9057)],
            date="2024-07-15", crop="banana", growth_stage="flowering", demo_mode=True,
        )


if __name__ == "__main__":
    test_wheat_flowering_produces_high_or_critical_risk()
    test_every_component_has_a_source_and_explanation()
    test_unsampled_fields_beyond_top_n_are_flagged_not_faked()
   
          
