"""Unit tests for EffortFilterPipeline normalization and protocol validation."""

import pytest
from packages.ovon_core.pipeline.ebd_ingest import SamplingEvent
from packages.ovon_core.pipeline.effort_filter import EffortFilterPipeline


def test_valid_traveling_effort():
    ev = SamplingEvent("S100", None, "Traveling", True, "2026-05-15", "07:30:00", 45.0, 2.0, None, 2, 39.0, -94.5)
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    assert effort.is_effort_valid is True
    assert effort.duration_minutes == 45.0
    assert effort.distance_km == 2.0
    assert effort.hours_past_sunrise == 1.5
    assert effort.rejection_reason is None


def test_exceeded_distance_rejection():
    ev = SamplingEvent("S101", None, "Traveling", True, "2026-05-15", "07:30:00", 45.0, 10.0, None, 1, 39.0, -94.5)
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    assert effort.is_effort_valid is False
    assert "exceeds max limit" in effort.rejection_reason
