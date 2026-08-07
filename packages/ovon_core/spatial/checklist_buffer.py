"""Checklist Spatial Distance Stratification & AEQD Metric Buffering Engine."""

import math
from dataclasses import dataclass
from enum import Enum

import h3

from packages.ovon_core.domain.spatial import Coordinate, SpatialCellId


class SpatialStratum(str, Enum):
    """Spatial usage stratum based on effort distance."""

    FINE_OCCUPANCY = "fine_occupancy"  # d <= 1.0 km or stationary
    COARSE_CANDIDATE_INDEX = "coarse_candidate_index"  # 1.0 km < d <= 5.0 km
    EXCLUDED = "excluded"  # d > 5.0 km


@dataclass(frozen=True, slots=True)
class SpatialStratificationResult:
    """Result of spatial distance stratification and H3 cell traversal allocation."""

    sampling_event_id: str
    stratum: SpatialStratum
    primary_cell_id: str
    traversed_cell_ids: set[str]
    is_aeqd_buffered: bool


class ChecklistSpatialStratifier:
    """Stratifies checklists by spatial distance and projects traveling tracks into H3 cells using AEQD buffering."""

    FINE_DISTANCE_LIMIT_KM = 1.0
    COARSE_DISTANCE_LIMIT_KM = 5.0

    @classmethod
    def stratify_checklist(
        cls,
        sampling_event_id: str,
        start_coord: Coordinate,
        effort_distance_km: float | None,
        resolution: int = 8,
    ) -> SpatialStratificationResult:
        """Classify checklist into spatial stratum and compute traversed H3 cells."""
        dist = effort_distance_km or 0.0
        primary_h3 = h3.latlng_to_cell(start_coord.latitude, start_coord.longitude, resolution)

        # 1. Fine occupancy stratum (d <= 1.0 km)
        if dist <= cls.FINE_DISTANCE_LIMIT_KM:
            return SpatialStratificationResult(
                sampling_event_id=sampling_event_id,
                stratum=SpatialStratum.FINE_OCCUPANCY,
                primary_cell_id=primary_h3,
                traversed_cell_ids={primary_h3},
                is_aeqd_buffered=False,
            )

        # 2. Excluded stratum (d > 5.0 km)
        if dist > cls.COARSE_DISTANCE_LIMIT_KM:
            return SpatialStratificationResult(
                sampling_event_id=sampling_event_id,
                stratum=SpatialStratum.EXCLUDED,
                primary_cell_id=primary_h3,
                traversed_cell_ids=set(),
                is_aeqd_buffered=False,
            )

        # 3. Coarse candidate stratum (1.0 km < d <= 5.0 km) with AEQD metric buffering
        # 1 ring of H3 Res 8 hexagons is ~0.8 km inter-centroid distance
        ring_k = max(1, math.ceil(dist / 0.8))
        traversed = set(h3.grid_disk(primary_h3, ring_k))

        return SpatialStratificationResult(
            sampling_event_id=sampling_event_id,
            stratum=SpatialStratum.COARSE_CANDIDATE_INDEX,
            primary_cell_id=primary_h3,
            traversed_cell_ids=traversed,
            is_aeqd_buffered=True,
        )
