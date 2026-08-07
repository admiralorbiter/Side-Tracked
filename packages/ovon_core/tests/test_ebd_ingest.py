"""Unit tests for eBird EBD/SED parsing and group checklist deduplication."""

import pytest
from packages.ovon_core.pipeline.ebd_ingest import EBDSamplingEventParser, SamplingEvent


def test_group_checklist_deduplication():
    # 2 group checklists sharing G123, 1 standalone checklist
    ev1 = SamplingEvent("S001", "G123", "Traveling", True, "2026-05-15", "07:30:00", 30.0, 1.2, None, 2, 39.0, -94.5)
    ev2 = SamplingEvent("S002", "G123", "Traveling", True, "2026-05-15", "07:30:00", 30.0, 1.2, None, 2, 39.0, -94.5)
    ev3 = SamplingEvent("S003", None, "Stationary", True, "2026-05-15", "08:00:00", 15.0, 0.0, None, 1, 39.1, -94.6)

    raw_list = [ev2, ev1, ev3]
    deduped = EBDSamplingEventParser.deduplicate_group_checklists(raw_list)

    assert len(deduped) == 2
    # Check that S001 (min ID) was chosen for group G123
    g_event = [e for e in deduped if e.group_identifier == "G123"][0]
    assert g_event.sampling_event_id == "S001"
