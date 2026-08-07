"""Candidate Taxa Index for fast (cell, week) spatial candidate resolution with h3 neighborhood expansion."""

from uuid import UUID

import h3

from packages.ovon_core.domain.spatial import SpatialCellId
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


class CandidateTaxaIndex:
    """Sparse spatial-temporal candidate taxa index backing CandidateTaxaProvider at national scale."""

    def __init__(self, concept_registry: TaxonConceptRegistry | None = None) -> None:
        self.concept_registry = concept_registry or TaxonConceptRegistry()
        # Sparse storage mapping: (cell_h3_index_str, week) -> set[concept_id_uuid]
        self._index: dict[tuple[str, int], set[UUID]] = {}
        self._seed_kc_pilot_index()

    @staticmethod
    def cyclic_week_distance(w1: int, w2: int) -> int:
        """Calculate cyclic temporal week distance: d_T(w1, w2) = min(|w1 - w2|, 52 - |w1 - w2|)."""
        diff = abs(w1 - w2)
        return min(diff, 52 - diff)

    @staticmethod
    def _extract_raw_h3_key(cell: SpatialCellId | str) -> str:
        """Extract canonical raw H3 index string key from SpatialCellId or string representation."""
        if isinstance(cell, SpatialCellId):
            return cell.cell_index
        cell_str = str(cell).strip()
        if ":" in cell_str:
            return cell_str.split(":", 1)[1]
        return cell_str

    def add_candidate(self, cell_id: str | SpatialCellId, week: int, concept_id: UUID) -> None:
        """Associate a canonical TaxonConcept UUID with a (cell, week) key."""
        cell_str = self._extract_raw_h3_key(cell_id)
        key = (cell_str, week)
        if key not in self._index:
            self._index[key] = set()
        self._index[key].add(concept_id)

    def query_candidates(
        self,
        cells: set[SpatialCellId | str] | SpatialCellId | str,
        week: int,
        expand_grid_disk: bool = True,
        week_tolerance: int = 1,
    ) -> set[UUID]:
        """Query canonical TaxonConcept UUID candidates for spatial cell(s) and calendar week."""
        cell_set = {cells} if isinstance(cells, (SpatialCellId, str)) else set(cells)
        target_cells: set[str] = set()

        for c in cell_set:
            cell_str = self._extract_raw_h3_key(c)
            target_cells.add(cell_str)
            if expand_grid_disk and h3.is_valid_cell(cell_str):
                # 7-cell grid disk neighborhood expansion (k=1 ring)
                neighbors = h3.grid_disk(cell_str, 1)
                target_cells.update(neighbors)

        results: set[UUID] = set()
        for c_str in target_cells:
            for w in range(1, 53):
                if self.cyclic_week_distance(week, w) <= week_tolerance:
                    cids = self._index.get((c_str, w))
                    if cids:
                        results.update(cids)

        return results

    def _seed_kc_pilot_index(self) -> None:
        """Seed Kansas City pilot cell candidates across 52 weeks."""
        # Standard Loose Park H3 Res 8 cell: "882685623ffffff"
        kc_cell = "882685623ffffff"
        for cid in self.concept_registry._concepts_by_id.keys():
            for week in range(1, 53):
                self.add_candidate(kc_cell, week, cid)
