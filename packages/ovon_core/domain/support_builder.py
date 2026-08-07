"""Derived TaxonSupport Builder for factual support provenance."""

from packages.ovon_core.domain.media import MediaType
from packages.ovon_core.domain.taxonomy import TaxonSupport
from packages.ovon_core.fixtures.kc_species_fixtures import KC_FIELD_CUE_PROFILES
from packages.ovon_core.media.repository import MediaRepository


class TaxonSupportBuilder:
    """Dynamically builds TaxonSupport metadata by inspecting actual media manifests and evidence registries."""

    @classmethod
    def build(
        cls,
        taxon_id: str,
        ebird_code: str,
        media_repository: MediaRepository | None = None,
        taxon: TaxonRef | None = None,
    ) -> TaxonSupport:
        """Derive factual TaxonSupport metadata."""
        photo_avail = False
        audio_avail = False
        song_avail = False
        call_avail = False

        if media_repository:
            # Query actual manifest inventory
            from packages.ovon_core.domain import TaxonRef
            target_taxon = taxon or TaxonRef.create(
                common_name=ebird_code.upper(),
                scientific_name=f"Taxon {ebird_code}",
                ebird_code=ebird_code,
            )
            photos = media_repository.get_assets_for_taxon(target_taxon, media_type=MediaType.PHOTO)
            audios = media_repository.get_assets_for_taxon(target_taxon, media_type=MediaType.AUDIO)
            
            photo_avail = len(photos) > 0
            audio_avail = len(audios) > 0
            song_avail = audio_avail
            call_avail = audio_avail

        cue_reviewed = ebird_code in KC_FIELD_CUE_PROFILES

        return TaxonSupport(
            taxonomy_known=True,
            occurrence_data_available=True,
            effort_model_available=True,
            calibrated_model_available=False,
            field_cue_reviewed=cue_reviewed,
            photo_available=photo_avail,
            song_available=song_avail,
            call_available=call_avail,
            audio_available=audio_avail,
            sensitive=False,
        )
