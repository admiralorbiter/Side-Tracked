"""Taxon Concept Registry for multi-authority crosswalking and versioned taxonomic concepts."""

from uuid import NAMESPACE_DNS, UUID, uuid5

from packages.ovon_core.domain.concept import (
    AuthorityName,
    TaxonConcept,
    TaxonConceptCollisionError,
    TaxonCrosswalkEntry,
    TaxonomicRank,
)
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA

# Deterministic Sidetrack Namespace for canonical TaxonConcept UUID generation
SIDETRACK_TAXON_NAMESPACE = uuid5(NAMESPACE_DNS, "sidetrack.ovon.bio")


class TaxonConceptRegistry:
    """Registry managing canonical Sidetrack Taxon Concept UUIDs and multi-authority crosswalks."""

    DEFAULT_AUTHORITY_VERSION = "Clements-2025"

    def __init__(self) -> None:
        self._concepts_by_id: dict[UUID, TaxonConcept] = {}
        # Multi-authority index: (authority, authority_version, authority_taxon_id) -> concept_id
        self._authority_index: dict[tuple[AuthorityName, str, str], UUID] = {}
        self._seed_default_kc_concepts()

    def register_concept(self, concept: TaxonConcept) -> None:
        """Register a canonical TaxonConcept and index its crosswalk entries with collision checking."""
        self._concepts_by_id[concept.concept_id] = concept
        for entry in concept.crosswalk_entries:
            key = (entry.authority, entry.authority_version, entry.authority_taxon_id)
            if key in self._authority_index and self._authority_index[key] != concept.concept_id:
                raise TaxonConceptCollisionError(
                    f"Crosswalk collision for key {key}: mapped to {self._authority_index[key]}, "
                    f"attempting to map to {concept.concept_id}"
                )
            self._authority_index[key] = concept.concept_id

    def get_by_id(self, concept_id: UUID) -> TaxonConcept | None:
        """Retrieve a TaxonConcept by its canonical Sidetrack UUID."""
        return self._concepts_by_id.get(concept_id)

    def resolve_authority(
        self,
        authority: AuthorityName,
        authority_taxon_id: str,
        authority_version: str | None = None,
    ) -> TaxonConcept | None:
        """Resolve a Sidetrack TaxonConcept using an external authority identifier and version."""
        version = authority_version or self.DEFAULT_AUTHORITY_VERSION
        key = (authority, version, authority_taxon_id)
        cid = self._authority_index.get(key)

        if not cid and authority_version is None:
            # Fall back across any version registered for this authority and taxon_id
            for (auth, _ver, tid), registered_cid in self._authority_index.items():
                if auth == authority and tid == authority_taxon_id:
                    cid = registered_cid
                    break

        return self.get_by_id(cid) if cid else None

    def get_concept_for_ebird_code(
        self, ebird_code: str, authority_version: str | None = None
    ) -> TaxonConcept | None:
        """Convenience resolver for eBird species codes."""
        auth_id = f"species:ebird:{ebird_code.lower().strip()}"
        return self.resolve_authority(
            AuthorityName.EBIRD_CLEMENTS, auth_id, authority_version=authority_version
        )

    def get_slash_candidate_concepts(
        self, ebird_slash_code: str, authority_version: str | None = None
    ) -> list[TaxonConcept]:
        """Resolve a slash species code (e.g. 'dowwoo/haiwoo') to its set of candidate species concepts."""
        slash_concept = self.get_concept_for_ebird_code(
            ebird_slash_code, authority_version=authority_version
        )
        if slash_concept and slash_concept.slash_candidate_concept_ids:
            return [
                self.get_by_id(cid)
                for cid in slash_concept.slash_candidate_concept_ids
                if self.get_by_id(cid) is not None
            ]

        # Fallback: parse 'code1/code2' directly if unseeded
        codes = ebird_slash_code.lower().strip().split("/")
        candidates: list[TaxonConcept] = []
        for code in codes:
            c = self.get_concept_for_ebird_code(code, authority_version=authority_version)
            if c:
                candidates.append(c)
        return candidates

    def _seed_default_kc_concepts(self) -> None:
        """Seed Kansas City species concepts with independent Sidetrack UUIDs and versioned crosswalk entries."""
        for taxon in ALL_KC_TAXA:
            # Sidetrack concept UUID minted independently of eBird codes
            slug = taxon.common_name.lower().replace(" ", "_").replace("'", "")
            cid = uuid5(SIDETRACK_TAXON_NAMESPACE, f"sidetrack_concept:{slug}")

            ebird_entry = TaxonCrosswalkEntry(
                authority=AuthorityName.EBIRD_CLEMENTS,
                authority_taxon_id=f"species:ebird:{taxon.ebird_code}",
                authority_version=self.DEFAULT_AUTHORITY_VERSION,
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

        # Seed Downy/Hairy Woodpecker slash concept
        dowwoo_concept = self.get_concept_for_ebird_code("dowwoo")
        haiwoo_concept = self.get_concept_for_ebird_code("haiwoo")
        # Ensure a candidate concept exists for haiwoo if not seeded
        if not haiwoo_concept:
            haiwoo_cid = uuid5(SIDETRACK_TAXON_NAMESPACE, "sidetrack_concept:hairy_woodpecker")
            haiwoo_concept = TaxonConcept(
                concept_id=haiwoo_cid,
                scientific_name="Dryobates villosus",
                common_name="Hairy Woodpecker",
                rank=TaxonomicRank.SPECIES,
                taxonomy_version="ST_TAXONOMY_2026_1",
                crosswalk_entries=(
                    TaxonCrosswalkEntry(
                        authority=AuthorityName.EBIRD_CLEMENTS,
                        authority_taxon_id="species:ebird:haiwoo",
                        authority_version=self.DEFAULT_AUTHORITY_VERSION,
                        rank=TaxonomicRank.SPECIES,
                        canonical_scientific_name="Dryobates villosus",
                    ),
                ),
                is_active=True,
            )
            self.register_concept(haiwoo_concept)

        slash_cid = uuid5(
            SIDETRACK_TAXON_NAMESPACE, "sidetrack_concept:downy_hairy_woodpecker_slash"
        )
        slash_entry = TaxonCrosswalkEntry(
            authority=AuthorityName.EBIRD_CLEMENTS,
            authority_taxon_id="species:ebird:dowwoo/haiwoo",
            authority_version=self.DEFAULT_AUTHORITY_VERSION,
            rank=TaxonomicRank.SLASH,
            canonical_scientific_name="Dryobates pubescens/villosus",
        )
        slash_concept = TaxonConcept(
            concept_id=slash_cid,
            scientific_name="Dryobates pubescens/villosus",
            common_name="Downy/Hairy Woodpecker",
            rank=TaxonomicRank.SLASH,
            taxonomy_version="ST_TAXONOMY_2026_1",
            slash_candidate_concept_ids=(
                dowwoo_concept.concept_id,
                haiwoo_concept.concept_id,
            ),
            crosswalk_entries=(slash_entry,),
            is_active=True,
        )
        self.register_concept(slash_concept)
