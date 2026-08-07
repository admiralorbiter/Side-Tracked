"""Unit tests for ZeroFillingMatrixEngine subspecies rollup, slash masking, and non-detections."""

import pytest

from packages.ovon_core.pipeline.ebd_ingest import SamplingEvent, SpeciesObservation
from packages.ovon_core.pipeline.effort_filter import EffortFilterPipeline
from packages.ovon_core.pipeline.zero_filler import ZeroFillingMatrixEngine
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


def test_zero_filling_matrix_generation():
    registry = TaxonConceptRegistry()
    engine = ZeroFillingMatrixEngine(registry)

    # Valid event + observations
    ev = SamplingEvent(
        "S200", None, "Stationary", True, "2026-05-15", "07:00:00", 30.0, 0.0, None, 1, 39.0, -94.5
    )
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    obs = [
        SpeciesObservation("S200", "amerob", "Turdus migratorius", "American Robin", "3"),
        SpeciesObservation(
            "S200", "dowwoo/haiwoo", "Picoides sp.", "Downy/Hairy Woodpecker", "1", is_slash=True
        ),
    ]

    robin_concept = registry.get_concept_for_ebird_code("amerob")
    cardinal_concept = registry.get_concept_for_ebird_code("norcar")
    downy_concept = registry.get_concept_for_ebird_code("dowwoo")
    hairy_concept = registry.get_concept_for_ebird_code("haiwoo")

    candidate_cids = {
        robin_concept.concept_id,
        cardinal_concept.concept_id,
        downy_concept.concept_id,
        hairy_concept.concept_id,
    }

    matrix = engine.generate_event_matrix(ev, effort, obs, candidate_cids)

    robin_cells = [c for c in matrix if c.concept_id == robin_concept.concept_id]
    cardinal_cells = [c for c in matrix if c.concept_id == cardinal_concept.concept_id]
    downy_cells = [c for c in matrix if c.concept_id == downy_concept.concept_id]
    hairy_cells = [c for c in matrix if c.concept_id == hairy_concept.concept_id]

    # 1. Detected Robin
    assert len(robin_cells) == 1
    assert robin_cells[0].detected == 1

    # 2. Zero-filled Cardinal
    assert len(cardinal_cells) == 1
    assert cardinal_cells[0].detected == 0
    assert cardinal_cells[0].is_zero_filled is True

    # 3. Masked slash candidates (Downy and Hairy must both be masked, NOT zero-filled absent)
    assert len(downy_cells) == 1
    assert downy_cells[0].detected is None
    assert downy_cells[0].is_zero_filled is False

    assert len(hairy_cells) == 1
    assert hairy_cells[0].detected is None
    assert hairy_cells[0].is_zero_filled is False


def test_event_identity_mismatch_raises_error():
    registry = TaxonConceptRegistry()
    engine = ZeroFillingMatrixEngine(registry)

    ev = SamplingEvent(
        "S200", None, "Stationary", True, "2026-05-15", "07:00:00", 30.0, 0.0, None, 1, 39.0, -94.5
    )
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    mismatched_obs = [
        SpeciesObservation("S999", "amerob", "Turdus migratorius", "American Robin", "3"),
    ]
    robin_concept = registry.get_concept_for_ebird_code("amerob")

    with pytest.raises(ValueError, match="Event identity mismatch"):
        engine.generate_event_matrix(ev, effort, mismatched_obs, {robin_concept.concept_id})


def test_duplicate_detection_collapsing():
    registry = TaxonConceptRegistry()
    engine = ZeroFillingMatrixEngine(registry)

    ev = SamplingEvent(
        "S200", None, "Stationary", True, "2026-05-15", "07:00:00", 30.0, 0.0, None, 1, 39.0, -94.5
    )
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    obs = [
        SpeciesObservation("S200", "amerob", "Turdus migratorius", "American Robin", "3"),
        SpeciesObservation("S200", "amerob", "Turdus migratorius", "American Robin", "1"),
    ]
    robin_concept = registry.get_concept_for_ebird_code("amerob")

    matrix = engine.generate_event_matrix(ev, effort, obs, {robin_concept.concept_id})
    robin_cells = [c for c in matrix if c.concept_id == robin_concept.concept_id]

    assert len(robin_cells) == 1
    assert robin_cells[0].detected == 1
