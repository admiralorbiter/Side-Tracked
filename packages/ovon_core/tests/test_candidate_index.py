"""Unit tests for CandidateTaxaIndex spatial H3 and cyclic week candidate queries."""

from uuid import uuid4

from packages.ovon_core.spatial.candidate_index import CandidateTaxaIndex


def test_cyclic_week_distance():
    assert CandidateTaxaIndex.cyclic_week_distance(1, 2) == 1
    assert CandidateTaxaIndex.cyclic_week_distance(52, 1) == 1
    assert CandidateTaxaIndex.cyclic_week_distance(20, 25) == 5


def test_candidate_index_query_and_h3_expansion():
    index = CandidateTaxaIndex()
    cid = uuid4()

    # Add candidate for explicit cell "882685623ffffff" week 32
    index.add_candidate("882685623ffffff", 32, cid)

    # Query for week 32 -> should retrieve concept_id
    results = index.query_candidates("882685623ffffff", week=32)
    assert cid in results

    # Query for cyclic neighbor week 31 -> should retrieve concept_id within tolerance 1
    results_w31 = index.query_candidates("882685623ffffff", week=31)
    assert cid in results_w31


def test_candidate_index_query_with_spatial_cell_id_object():
    from packages.ovon_core.domain.spatial import Coordinate
    from packages.ovon_core.spatial import lat_lng_to_h3_cell

    index = CandidateTaxaIndex()
    cid = uuid4()

    cell_obj = lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8)
    index.add_candidate(cell_obj, week=20, concept_id=cid)

    results = index.query_candidates(cell_obj, week=20)
    assert cid in results
