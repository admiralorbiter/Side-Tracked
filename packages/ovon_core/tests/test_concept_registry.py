"""Unit tests for TaxonConceptRegistry and TaxonConcept models."""

from packages.ovon_core.domain.concept import AuthorityName, TaxonConcept, TaxonomicRank
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


def test_taxon_concept_creation():
    concept = TaxonConcept.create("American Robin", "Turdus migratorius", TaxonomicRank.SPECIES)
    assert concept.common_name == "American Robin"
    assert concept.rank == TaxonomicRank.SPECIES
    assert concept.is_active is True


def test_concept_registry_seed_and_authority_resolution():
    registry = TaxonConceptRegistry()

    # Resolve eBird code 'amerob'
    concept = registry.get_concept_for_ebird_code("amerob")
    assert concept is not None
    assert concept.common_name == "American Robin"

    # Resolve direct authority key
    resolved = registry.resolve_authority(AuthorityName.EBIRD_CLEMENTS, "species:ebird:norcar")
    assert resolved is not None
    assert resolved.common_name == "Northern Cardinal"
