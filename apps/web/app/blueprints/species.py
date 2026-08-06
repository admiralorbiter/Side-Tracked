from flask import Blueprint, render_template

species_bp = Blueprint("species", __name__)

@species_bp.route("/species/<taxon_id>")
def detail(taxon_id):
    """Species field guide card detail."""
    mock_species = {
        "taxon_id": taxon_id,
        "common_name": "Red-headed Woodpecker",
        "scientific_name": "Melanerpes erythrocephalus",
        "category": "Woodpecker",
        "habitat": "Open oak woodlands, dead snags, park edges",
        "where_to_look": "Look high on dead tree trunks or limbs without bark. Often flies out to catch insects mid-air.",
        "what_to_listen_for": "A harsh, raspy 'tchur-tchur' call and rhythmic, resonant drumming on hollow wood.",
        "look_alikes": "Red-bellied Woodpecker (has only a red crown, not full crimson head).",
        "attribution": "Photo by John Doe (CC BY 4.0). Audio by Jane Smith (CC BY-NC 4.0)."
    }
    return render_template("species/detail.html", species=mock_species)
