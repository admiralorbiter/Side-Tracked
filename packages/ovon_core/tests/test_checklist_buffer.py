"""Unit tests for ChecklistSpatialStratifier distance stratification."""

from packages.ovon_core.domain.spatial import Coordinate
from packages.ovon_core.spatial.checklist_buffer import ChecklistSpatialStratifier, SpatialStratum


def test_spatial_distance_stratification():
    coord = Coordinate(39.0355, -94.5920)

    # 1. Fine occupancy (0.5 km)
    res_fine = ChecklistSpatialStratifier.stratify_checklist("S300", coord, 0.5)
    assert res_fine.stratum == SpatialStratum.FINE_OCCUPANCY
    assert len(res_fine.traversed_cell_ids) == 1

    # 2. Coarse candidate index (3.0 km) -> radial uncertainty extent
    res_coarse = ChecklistSpatialStratifier.stratify_checklist("S301", coord, 3.0)
    assert res_coarse.stratum == SpatialStratum.COARSE_CANDIDATE_INDEX
    assert res_coarse.is_aeqd_buffered is False
    assert len(res_coarse.possible_extent_cell_ids) > 1
    assert len(res_coarse.traversed_cell_ids) > 1

    # 3. Excluded (8.0 km)
    res_ex = ChecklistSpatialStratifier.stratify_checklist("S302", coord, 8.0)
    assert res_ex.stratum == SpatialStratum.EXCLUDED
    assert len(res_ex.traversed_cell_ids) == 0
