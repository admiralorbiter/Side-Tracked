"""Unit tests for DiscoveryRepository SQLite persistence."""

import os
from uuid import uuid4

import pytest
from apps.web.app.services.discovery_repository import DiscoveryRepository
from packages.ovon_core.domain.discovery import (
    DetectionEvidenceType,
    DiscoveryConfidence,
    DiscoveryRecord,
    DiscoverySourceRole,
)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_file = tmp_path / "test_discovery.db"
    DiscoveryRepository.set_db_path(str(db_file))
    yield
    DiscoveryRepository.set_db_path("data/discovery.db")


def test_save_and_retrieve_discovery_record():
    cid = uuid4()
    rec = DiscoveryRecord.create(
        user_id="user_123",
        concept_id=cid,
        original_taxon_ref="species:ebird:amerob",
        latitude=39.0355,
        longitude=-94.5920,
        spatial_cell_id="882685623ffffff",
        source_role=DiscoverySourceRole.IN_ROUTE_WALK,
        evidence_type=DetectionEvidenceType.SEEN,
        confidence=DiscoveryConfidence.CERTAIN,
        count=2,
        notes="Saw two robins on Loose Park lawn.",
    )

    discovery_id = DiscoveryRepository.save_discovery(rec)
    assert discovery_id == str(rec.discovery_id)

    records = DiscoveryRepository.get_discoveries_for_user("user_123")
    assert len(records) == 1
    assert records[0]["concept_id"] == str(cid)
    assert records[0]["spatial_cell_id"] == "882685623ffffff"
    assert records[0]["count"] == 2
