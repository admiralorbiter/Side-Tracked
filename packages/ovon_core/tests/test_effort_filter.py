"""Unit tests for EffortFilterPipeline normalization and protocol validation."""

from packages.ovon_core.pipeline.ebd_ingest import SamplingEvent
from packages.ovon_core.pipeline.effort_filter import EffortFilterPipeline


def test_valid_traveling_effort():
    ev = SamplingEvent(
        "S100", None, "Traveling", True, "2026-05-15", "07:30:00", 45.0, 2.0, None, 2, 39.0, -94.5
    )
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    assert effort.is_effort_valid is True
    assert effort.duration_minutes == 45.0
    assert effort.distance_km == 2.0
    assert effort.hours_past_sunrise == 1.5
    assert effort.rejection_reason is None


def test_traveling_missing_distance_rejection():
    # Traveling protocol with missing distance must be rejected
    ev = SamplingEvent(
        "S102", None, "Traveling", True, "2026-05-15", "07:30:00", 45.0, None, None, 1, 39.0, -94.5
    )
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    assert effort.is_effort_valid is False
    assert "requires non-null effort_distance_km" in effort.rejection_reason


def test_area_protocol_validation():
    # Area protocol requiring effort_area_ha
    ev_valid = SamplingEvent(
        "S103", None, "Area", True, "2026-05-15", "07:30:00", 45.0, 0.0, 50.0, 1, 39.0, -94.5
    )
    effort_valid = EffortFilterPipeline.filter_and_normalize(ev_valid)
    assert effort_valid.is_effort_valid is True

    ev_exceeded = SamplingEvent(
        "S104", None, "Area", True, "2026-05-15", "07:30:00", 45.0, 0.0, 150.0, 1, 39.0, -94.5
    )
    effort_exceeded = EffortFilterPipeline.filter_and_normalize(ev_exceeded)
    assert effort_exceeded.is_effort_valid is False
    assert "exceeds max limit" in effort_exceeded.rejection_reason
