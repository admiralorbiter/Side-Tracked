"""Taxon Concept domain models for Sidetrack authority crosswalking."""

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4


class TaxonomicRank(str, Enum):
    """Taxonomic ranks supported by Sidetrack concept registry."""

    SPECIES = "species"
    SUBSPECIES = "subspecies"
    ISSF = "issf"  # Identifiable Subspecies Group (eBird)
    SLASH = "slash"
    SPUH = "spuh"
    HYBRID = "hybrid"
    GENUS = "genus"
    FAMILY = "family"


class AuthorityName(str, Enum):
    """Taxonomic authorities crosswalked by Sidetrack."""

    EBIRD_CLEMENTS = "ebird_clements"
    GBIF_BACKBONE = "gbif_backbone"
    INATURALIST = "inaturalist"


class TaxonConceptCollisionError(Exception):
    """Raised when registering a crosswalk entry that collides with an existing mapping."""

    pass


@dataclass(frozen=True, slots=True)
class TaxonCrosswalkEntry:
    """External authority mapping entry."""

    authority: AuthorityName
    authority_taxon_id: str  # e.g., "species:ebird:ambcro" or "gbif:taxon:2480398"
    authority_version: str  # e.g., "Clements-2025"
    rank: TaxonomicRank
    canonical_scientific_name: str
    is_primary_match: bool = True


@dataclass(frozen=True, slots=True)
class TaxonConcept:
    """Canonical Sidetrack Taxon Concept UUID."""

    concept_id: UUID
    scientific_name: str
    common_name: str
    rank: TaxonomicRank
    taxonomy_version: str  # Current active Sidetrack concept version (e.g. "ST_TAXONOMY_2026_1")
    parent_concept_id: UUID | None = None
    slash_candidate_concept_ids: tuple[UUID, ...] = field(default_factory=tuple)
    crosswalk_entries: tuple[TaxonCrosswalkEntry, ...] = field(default_factory=tuple)
    is_active: bool = True

    @classmethod
    def create(
        cls,
        common_name: str,
        scientific_name: str,
        rank: TaxonomicRank = TaxonomicRank.SPECIES,
        taxonomy_version: str = "ST_TAXONOMY_2026_1",
        parent_concept_id: UUID | None = None,
        crosswalk_entries: tuple[TaxonCrosswalkEntry, ...] = (),
    ) -> "TaxonConcept":
        """Factory method for creating a TaxonConcept with a deterministic or generated UUID."""
        concept_id = uuid4()
        return cls(
            concept_id=concept_id,
            scientific_name=scientific_name,
            common_name=common_name,
            rank=rank,
            taxonomy_version=taxonomy_version,
            parent_concept_id=parent_concept_id,
            crosswalk_entries=crosswalk_entries,
            is_active=True,
        )
