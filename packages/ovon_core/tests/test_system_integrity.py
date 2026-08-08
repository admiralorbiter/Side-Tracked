"""Unit tests for Phase R8 End-to-End System Reproducibility & Integrity Proof."""

from packages.ovon_core.cli.system_integrity_manifest import generate_system_integrity_manifest
from packages.ovon_core.domain.concept import AuthorityName
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


def test_30_species_focal_catalog():
    assert len(ALL_KC_TAXA) == 30
    registry = TaxonConceptRegistry()

    # Test resolving focal concepts via AuthorityName enum
    concept_cardinal = registry.resolve_authority(
        AuthorityName.EBIRD_CLEMENTS, "species:ebird:norcar"
    )
    assert concept_cardinal is not None
    assert concept_cardinal.common_name == "Northern Cardinal"

    concept_robin = registry.resolve_authority(AuthorityName.EBIRD_CLEMENTS, "species:ebird:amerob")
    assert concept_robin is not None
    assert concept_robin.common_name == "American Robin"


def test_system_integrity_manifest_generation(tmp_path):
    manifest = generate_system_integrity_manifest(output_dir=tmp_path)
    assert manifest["status"] == "system_integrity_manifest_verified"
    assert manifest["focal_species_count"] == 30
    assert len(manifest["focal_species_catalog"]) == 30
    assert (tmp_path / "system_integrity_manifest.json").exists()
