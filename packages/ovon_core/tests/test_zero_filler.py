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
    ev = SamplingEvent("S200", None, "Stationary", True, "2026-05-15", "07:00:00", 30.0, 0.0, None, 1, 39.0, -94.5)
    effort = EffortFilterPipeline.filter_and_normalize(ev)

    obs = [
        SpeciesObservation("S200", "amerob", "Turdus migratorius", "American Robin", "3"),
        SpeciesObservation("S200", "dowwoo/haiwoo", "Picoides sp.", "Downy/Hairy Woodpecker", "1", is_slash=True),
    ]

    robin_concept = registry.get_concept_for_ebird_code("amerob")
    cardinal_concept = registry.get_concept_for_ebird_code("norcar")
    candidate_cids = {robin_concept.concept_id, cardinal_concept.concept_id}

    matrix = engine.generate_event_matrix(ev, effort, obs, candidate_cids)

    # 1 detected robin cell, 1 masked slash cell, 1 zero-filled cardinal cell
    robin_cells = [c for c in matrix if c.concept_id == robin_concept.concept_id]
    cardinal_cells = [c for c in matrix if c.concept_id == cardinal_concept.concept_id]

    assert len(robin_cells) == 1
    assert robin_cells[0].detected == 1

    assert len(cardinal_cells) == 1
    assert cardinal_cells[0].detected == 0
    assert cardinal_cells[0].is_zero_filled is True
