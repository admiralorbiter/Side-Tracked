"""Unit tests for Species Media Foundation (Sprint 3)."""

import pytest

from packages.ovon_core.domain import (
    LicenseType,
    MediaAsset,
    MediaType,
    MissingAttributionError,
    TaxonRef,
)
from packages.ovon_core.media import (
    LocalMediaRepository,
    normalize_and_validate_license,
)


def test_license_allowlist_validation():
    assert normalize_and_validate_license("CC BY 4.0") == LicenseType.CC_BY_4_0
    assert normalize_and_validate_license("cc-by-nc-4.0") == LicenseType.CC_BY_NC_4_0
    assert normalize_and_validate_license("Public Domain") == LicenseType.PUBLIC_DOMAIN

    with pytest.raises(MissingAttributionError):
        normalize_and_validate_license("All Rights Reserved")


def test_media_repository_register_and_query():
    repo = LocalMediaRepository()
    taxon = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")

    photo = MediaAsset(
        asset_id="wm-101",
        taxon_ref=taxon,
        media_type=MediaType.PHOTO,
        url="https://example.com/jay.jpg",
        creator="Test Photographer",
        license=LicenseType.CC_BY_SA_4_0,
        attribution_text="Test Photographer (CC BY-SA 4.0)",
    )
    repo.register_asset(photo)

    assets = repo.get_assets_for_taxon(taxon)
    assert len(assets) == 1
    assert assets[0].asset_id == "wm-101"
    assert assets[0].media_type == MediaType.PHOTO


def test_media_manifest_roundtrip(tmp_path):
    manifest_file = tmp_path / "test_manifest.json"
    repo = LocalMediaRepository()
    taxon = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")

    audio = MediaAsset(
        asset_id="xc-202",
        taxon_ref=taxon,
        media_type=MediaType.AUDIO,
        url="https://example.com/robin.mp3",
        creator="Recordist A",
        license=LicenseType.CC_BY_NC_4_0,
        attribution_text="Recordist A (CC BY-NC 4.0)",
    )
    repo.register_asset(audio)
    repo.save_manifest(manifest_file)

    assert manifest_file.exists()

    # Load into fresh repository
    new_repo = LocalMediaRepository(manifest_file)
    loaded_assets = new_repo.get_assets_for_taxon(taxon)
    assert len(loaded_assets) == 1
    assert loaded_assets[0].asset_id == "xc-202"
    assert loaded_assets[0].creator == "Recordist A"
