from pathlib import Path

from flask import Blueprint, render_template

from packages.ovon_core.domain import (
    FieldCue,
    MediaType,
    TaxonRef,
)
from packages.ovon_core.media import LocalMediaRepository

species_bp = Blueprint("species", __name__)

# Initialize Media Repository with data/media_manifest.json
MANIFEST_PATH = Path("data/media_manifest.json")
media_repo = LocalMediaRepository(MANIFEST_PATH if MANIFEST_PATH.exists() else None)

WOODPECKER_DOMAIN = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
WOODPECKER_CUE = FieldCue(
    WOODPECKER_DOMAIN,
    where_to_look="Look high on dead tree trunks or limbs without bark. Often flies out to catch insects mid-air.",
    what_to_listen_for="A harsh, raspy 'tchur-tchur' call and rhythmic, resonant drumming on hollow wood.",
    look_alikes="Red-bellied Woodpecker (has only a red crown, not full crimson head).",
)

ROBIN_DOMAIN = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")
ROBIN_CUE = FieldCue(
    ROBIN_DOMAIN,
    where_to_look="Scan low lawns, open park paths, and fruiting bushes.",
    what_to_listen_for="Cheery, liquid warbling song: 'cheerily, cheer up, cheerily'.",
    look_alikes="Eastern Bluebird (has blue back rather than gray/brown).",
)

CARDINAL_DOMAIN = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
CARDINAL_CUE = FieldCue(
    CARDINAL_DOMAIN,
    where_to_look="Scan low thickets, dogwood shrubs, and woodland edges.",
    what_to_listen_for="Loud, clear whistling: 'birdy, birdy, birdy' or metallic 'chip' call.",
    look_alikes="Summer Tanager (all red without black facial mask).",
)

SPECIES_MAP = {
    "rehwoo": (WOODPECKER_DOMAIN, WOODPECKER_CUE),
    "red_headed_woodpecker": (WOODPECKER_DOMAIN, WOODPECKER_CUE),
    "amerob": (ROBIN_DOMAIN, ROBIN_CUE),
    "american_robin": (ROBIN_DOMAIN, ROBIN_CUE),
    "norcar": (CARDINAL_DOMAIN, CARDINAL_CUE),
    "northern_cardinal": (CARDINAL_DOMAIN, CARDINAL_CUE),
}


@species_bp.route("/species/<taxon_id>")
def detail(taxon_id):
    """Species Field Guide View."""
    clean_id = taxon_id.lower().strip()
    if clean_id not in SPECIES_MAP:
        species_domain, cue = WOODPECKER_DOMAIN, WOODPECKER_CUE
    else:
        species_domain, cue = SPECIES_MAP[clean_id]

    # Fetch cached audio and photo assets from media repository
    audio_assets = media_repo.get_assets_for_taxon(species_domain, media_type=MediaType.AUDIO)
    photo_assets = media_repo.get_assets_for_taxon(species_domain, media_type=MediaType.PHOTO)

    media_audio = audio_assets[0] if audio_assets else None
    media_photo = photo_assets[0] if photo_assets else None

    return render_template(
        "species/detail.html", species=species_domain, cue=cue, media=media_audio, photo=media_photo
    )
