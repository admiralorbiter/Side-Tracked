"""Segment-Species Recommendation Contract for OVON Core."""

from dataclasses import dataclass
from typing import Protocol

from packages.ovon_core.domain.spatial import SpatialCellId
from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.ecology.habitat import HabitatType
from packages.ovon_core.ecology.species_surface import ProvisionalSpeciesSurface
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA


@dataclass(frozen=True, slots=True)
class SegmentContext:
    """Context for evaluating species opportunities on a route segment."""

    traversed_h3_cells: set[SpatialCellId]
    habitat_type: HabitatType = HabitatType.OPEN_PARKLAND
    season_week: int = 20


@dataclass(frozen=True, slots=True)
class SpeciesOpportunity:
    """Evaluated species opportunity score on a segment."""

    taxon: TaxonRef
    score: float
    habitat_alignment: float


class SegmentSpeciesRecommenderProtocol(Protocol):
    """Protocol contract for recommending species for route segments."""

    def recommend_species(
        self, context: SegmentContext, limit: int = 3
    ) -> list[SpeciesOpportunity]:
        ...


class DefaultSegmentSpeciesRecommender:
    """Default implementation of SegmentSpeciesRecommender using ProvisionalSpeciesSurface."""

    def __init__(self, species_surface: ProvisionalSpeciesSurface | None = None):
        self.surface = species_surface or ProvisionalSpeciesSurface()
        self.candidate_pool: tuple[TaxonRef, ...] = ALL_KC_TAXA

    def recommend_species(
        self, context: SegmentContext, limit: int = 3
    ) -> list[SpeciesOpportunity]:
        """Rank and return candidate species based on traversed H3 cells and segment habitat."""
        results: list[SpeciesOpportunity] = []
        for taxon in self.candidate_pool:
            if context.traversed_h3_cells:
                cell_scores = [
                    self.surface.get_relative_score(taxon, context.habitat_type, cell)
                    for cell in context.traversed_h3_cells
                ]
                avg_score = sum(cell_scores) / len(cell_scores)
            else:
                avg_score = self.surface.get_relative_score(taxon, context.habitat_type)

            results.append(
                SpeciesOpportunity(
                    taxon=taxon,
                    score=round(avg_score, 3),
                    habitat_alignment=round(avg_score, 3),
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
