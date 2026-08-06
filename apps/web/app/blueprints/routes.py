from pathlib import Path

from flask import Blueprint, abort, render_template

from packages.ovon_core.domain import (
    FieldCue,
    MediaType,
    RouteFieldPack,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
)
from packages.ovon_core.media import LocalMediaRepository

routes_bp = Blueprint("routes", __name__)

# Initialize Media Repository with data/media_manifest.json
MANIFEST_PATH = Path("data/media_manifest.json")
media_repo = LocalMediaRepository(MANIFEST_PATH if MANIFEST_PATH.exists() else None)

# Domain Data Fixtures for Routes
WOODPECKER = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
TITMOUSE = TaxonRef.create("Tufted Titmouse", "Baeolophus bicolor", "tuftit")
WREN = TaxonRef.create("Carolina Wren", "Thryothorus ludovicianus", "carwre")
CARDINAL = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
BLUE_JAY = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")

CUE_BIRDY_1 = FieldCue(
    CARDINAL, "Scan low dogwood shrubs near pond edge.", "Listen for sharp metallic 'chip' call."
)
CUE_BIRDY_2 = FieldCue(
    WOODPECKER,
    "Inspect dead tree snags near Brush Creek.",
    "Listen for loud rolling churring calls.",
)

SEGMENT_BIRDY_1 = RouteSegment(
    index=1,
    name="Park Perimeter & Pond Edge",
    habitat_name="Pond & Grassland",
    distance_meters=800.0,
    duration_minutes=15.0,
    focal_species=(CARDINAL, BLUE_JAY),
    field_cue=CUE_BIRDY_1,
)

SEGMENT_BIRDY_2 = RouteSegment(
    index=2,
    name="Brush Creek Canopy Trail",
    habitat_name="Mature Hardwood Forest",
    distance_meters=1400.0,
    duration_minutes=30.0,
    focal_species=(WOODPECKER, TITMOUSE, WREN),
    field_cue=CUE_BIRDY_2,
)

ROUTE_BIRDY_DOMAIN = RouteOption(
    id="birdy-1",
    persona=RoutePersona.BIRDY,
    name="The Birdy One",
    tagline="Diverges into dense tree canopy and creek bed edge habitat.",
    duration_minutes=45,
    distance_meters=2200.0,
    badge_label="Best bird opportunity",
    tradeoff_description="Adds 400m of dirt trail near Brush Creek for double species diversity.",
    segments=(SEGMENT_BIRDY_1, SEGMENT_BIRDY_2),
)


def get_field_pack_for_route(route_id: str) -> RouteFieldPack:
    """Dynamically construct field pack with media assets from local repository."""
    cardinal_media = media_repo.get_assets_for_taxon(CARDINAL, media_type=MediaType.AUDIO)
    woodpecker_media = media_repo.get_assets_for_taxon(WOODPECKER, media_type=MediaType.AUDIO)

    media_assets = []
    if cardinal_media:
        media_assets.append(cardinal_media[0])
    if woodpecker_media:
        media_assets.append(woodpecker_media[0])

    return RouteFieldPack(
        route_id=route_id,
        focal_species=(CARDINAL, BLUE_JAY, WOODPECKER, TITMOUSE, WREN),
        field_cues=(CUE_BIRDY_1, CUE_BIRDY_2),
        media_assets=tuple(media_assets),
    )


ROUTES_DB = {
    "birdy-1": ROUTE_BIRDY_DOMAIN,
    "easy-1": ROUTE_BIRDY_DOMAIN,
    "weird-1": ROUTE_BIRDY_DOMAIN,
}


@routes_bp.route("/routes/<route_id>")
def detail(route_id):
    """Step 6 & 7: Route Detail & Text-Equivalent Field Pack."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain = ROUTES_DB[route_id]
    field_pack = get_field_pack_for_route(route_id)
    return render_template("routes/detail.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/in-route")
def in_route(route_id):
    """Step 8: In-Route Segment Tracking View."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain = ROUTES_DB[route_id]
    field_pack = get_field_pack_for_route(route_id)
    return render_template("routes/in_route.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/recap")
def recap(route_id):
    """Step 9: After-Route Walk Recap."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain = ROUTES_DB[route_id]
    field_pack = get_field_pack_for_route(route_id)
    return render_template("routes/recap.html", route=route_domain, field_pack=field_pack)
