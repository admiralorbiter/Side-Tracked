from flask import Blueprint, abort, render_template

from apps.web.app.services import GetSpeciesProfile

species_bp = Blueprint("species", __name__)


@species_bp.route("/species/<taxon_id>")
def detail(taxon_id):
    """Species Field Guide View."""
    service = GetSpeciesProfile()
    profile = service.execute(taxon_id)

    if not profile:
        abort(404)

    return render_template(
        "species/detail.html",
        species=profile.species,
        cue=profile.cue,
        media=profile.audio_asset,
        photo=profile.photo_asset,
    )
