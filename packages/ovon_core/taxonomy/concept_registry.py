"""Taxon Concept Registry for multi-authority crosswalking and versioned taxonomic concepts."""

from uuid import UUID, uuid5, NAMESPACE_DNS

from packages.ovon_core.domain.concept import (
    AuthorityName,
    TaxonConcept,
    TaxonCrosswalkEntry,
    TaxonomicRank,
)
from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA

# Deterministic Sidetrack Namespace for canonical TaxonConcept UUID generation
SIDETRACK_TAXON_NAMESPACE = uuid5(NAMESPACE_DNS, "sidetrack.ovon.bio")


class TaxonConceptRegistry:
    """Registry managing canonical Sidetrack Taxon Concept UUIDs and multi-authority crosswalks."""

    def __init__(self) -> None:
        self._concepts_by_id: dict[UUID, TaxonConcept] = {}
        self._authority_index: dict[tuple[AuthorityName, str], UUID] = {}
        self._seed_default_kc_concepts()

    def register_concept(self, concept: TaxonConcept) -> None:
        """Register a canonical TaxonConcept and index its crosswalk entries."""
        self._concepts_by_id[concept.concept_id] = concept
        for entry in concept.crosswalk_entries:
            key = (entry.authority, entry.authority_taxon_id)
            self._authority_index[key] = concept.concept_id

    def get_by_id(self, concept_id: UUID) -> TaxonConcept | None:
        """Retrieve a TaxonConcept by its canonical Sidetrack UUID."""
        return self._concepts_by_id.get(concept_id)

    def resolve_authority(
        self, authority: AuthorityName, authority_taxon_id: str
    ) -> TaxonConcept | None:
        """Resolve a Sidetrack TaxonConcept using an external authority identifier."""
        key = (authority, authority_taxon_id)
        cid = self._authority_index.get(key)
        return self.get_by_id(cid) if cid else None

    def get_concept_for_ebird_code(self, ebird_code: str) -> TaxonConcept | None:
        """Convenience resolver for eBird species codes."""
        auth_id = f"species:ebird:{ebird_code.lower().strip()}"
        return self.resolve_authority(AuthorityName.EBIRD_CLEMENTS, auth_id)

    def _seed_default_kc_concepts(self) -> None:
        """Seed the 30 Kansas City species with deterministic TaxonConcept UUIDs and crosswalk entries."""
        for taxon in ALL_KC_TAXA:
            # Generate deterministic Sidetrack UUID based on ebird_code
            cid = uuid5(SIDETRACK_TAXON_NAMESPACE, f"taxon:{taxon.ebird_code}")

            ebird_entry = TaxonCrosswalkEntry(
                authority=AuthorityName.EBIRD_CLEMENTS,
                authority_taxon_id=f"species:ebird:{taxon.ebird_code}",
                authority_version="Clements_2023_v2",
                rank=TaxonomicRank.SPECIES,
                canonical_scientific_name=taxon.scientific_name,
            )

            concept = TaxonConcept(
                concept_id=cid,
                scientific_name=taxon.scientific_name,
                common_name=taxon.common_name,
                rank=TaxonomicRank.SPECIES,
                taxonomy_version="ST_TAXONOMY_2026_1",
                crosswalk_entries=(ebird_entry,),
                is_active=True,
            )
            self.register_concept(concept)
