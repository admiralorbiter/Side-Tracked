"""Candidate Taxa Provider boundary for national expansion."""

from typing import Protocol

from packages.ovon_core.domain import SpatialCellId, TaxonRef
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA


class CandidateTaxaProvider(Protocol):
    """Abstraction boundary for retrieving seasonally & spatially plausible candidate taxa."""

    def candidates(
        self, cells: set[SpatialCellId] | None = None, week: int = 20
    ) -> tuple[TaxonRef, ...]:
        ...


class KansasCityCandidateTaxaProvider:
    """Sprint 10 local candidate provider returning the 30-species Greater Kansas City catalog."""

    def __init__(self, catalog: tuple[TaxonRef, ...] = ALL_KC_TAXA):
        self._catalog = catalog

    def candidates(
        self, cells: set[SpatialCellId] | None = None, week: int = 20
    ) -> tuple[TaxonRef, ...]:
        """Return candidate taxa for the given H3 cells and seasonal week."""
        return self._catalog
