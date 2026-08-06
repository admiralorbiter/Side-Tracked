from flask import Blueprint, render_template, abort
from packages.ovon_core.domain import (
    TaxonRef,
    FieldCue,
    MediaAsset,
    MediaType,
    LicenseType,
)

species_bp = Blueprint("species", __name__)

WOODPECKER_DOMAIN = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
WOODPECKER_CUE = FieldCue(
    WOODPECKER_DOMAIN,
    where_to_look="Look high on dead tree trunks or limbs without bark. Often flies out to catch insects mid-air.",
    what_to_listen_for="A harsh, raspy 'tchur-tchur' call and rhythmic, resonant drumming on hollow wood.",
    look_alikes="Red-bellied Woodpecker (has only a red crown, not full crimson head)."
)
WOODPECKER_AUDIO = MediaAsset(
    asset_id="xc-123456",
    taxon_ref=WOODPECKER_DOMAIN,
    media_type=MediaType.AUDIO,
    url="https://xeno-canto.org/sounds/uploaded/sample.mp3",
    creator="Jane Smith",
    license=LicenseType.CC_BY_NC_4_0,
    attribution_text="Jane Smith (CC BY-NC 4.0 via Xeno-Canto #123456)",
    source_name="Xeno-Canto"
)

SPECIES_DB = {
    "rehwoo": (WOODPECKER_DOMAIN, WOODPECKER_CUE, WOODPECKER_AUDIO),
    "red_headed_woodpecker": (WOODPECKER_DOMAIN, WOODPECKER_CUE, WOODPECKER_AUDIO)
}

@species_bp.route("/species/<taxon_id>")
def detail(taxon_id):
    """Species Field Guide View."""
    if taxon_id not in SPECIES_DB:
        # Return fallback wood-pecker domain model for testing
        species_domain, cue, media = WOODPECKER_DOMAIN, WOODPECKER_CUE, WOODPECKER_AUDIO
    else:
        species_domain, cue, media = SPECIES_DB[taxon_id]

    return render_template("species/detail.html", species=species_domain, cue=cue, media=media)
