"""Species Application Service."""

from dataclasses import dataclass

from flask import current_app

from packages.ovon_core.domain import (
    FieldCue,
    MediaAsset,
    MediaType,
    TaxonRef,
)
from packages.ovon_core.domain import (
    FieldCue,
    MediaAsset,
    MediaType,
    TaxonRef,
)
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA, KC_FIELD_CUES
from packages.ovon_core.media import MediaRepository

# Master Species Fixture Map for all 30 KC Taxa
SPECIES_FIXTURE_MAP: dict[str, tuple[TaxonRef, FieldCue]] = {}
for _taxon in ALL_KC_TAXA:
    _cue = KC_FIELD_CUES[_taxon.ebird_code]
    SPECIES_FIXTURE_MAP[_taxon.ebird_code] = (_taxon, _cue)
    SPECIES_FIXTURE_MAP[_taxon.taxon_id] = (_taxon, _cue)
    _clean_common = _taxon.common_name.lower().replace(" ", "_").replace("'", "")
    SPECIES_FIXTURE_MAP[_clean_common] = (_taxon, _cue)


@dataclass(frozen=True)
class SpeciesProfile:
    """Read model for species field guide presentation."""

    species: TaxonRef
    cue: FieldCue
    audio_asset: MediaAsset | None = None
    photo_asset: MediaAsset | None = None


class GetSpeciesProfile:
    """Application Service for retrieving species profiles."""

    def __init__(self, media_repository: MediaRepository | None = None):
        self._media_repo = media_repository

    @property
    def media_repo(self) -> MediaRepository | None:
        if self._media_repo:
            return self._media_repo
        if current_app and "media_repository" in current_app.extensions:
            repo: MediaRepository = current_app.extensions["media_repository"]
            return repo
        return None

    def execute(self, taxon_id: str) -> SpeciesProfile | None:
        """Retrieve species profile or None if taxon_id is unknown."""
        clean_id = taxon_id.lower().strip()
        if clean_id not in SPECIES_FIXTURE_MAP:
            return None  # Unknown species returns None -> 404

        species_domain, cue = SPECIES_FIXTURE_MAP[clean_id]
        repo = self.media_repo

        audio_asset = None
        photo_asset = None

        if repo:
            audios = repo.get_assets_for_taxon(species_domain, media_type=MediaType.AUDIO)
            photos = repo.get_assets_for_taxon(species_domain, media_type=MediaType.PHOTO)
            if audios:
                audio_asset = audios[0]
            if photos:
                photo_asset = photos[0]

        return SpeciesProfile(
            species=species_domain,
            cue=cue,
            audio_asset=audio_asset,
            photo_asset=photo_asset,
        )
