from flask import Blueprint, render_template, abort
from packages.ovon_core.domain import (
    Coordinate,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
    FieldCue,
    MediaAsset,
    MediaType,
    LicenseType,
    RouteFieldPack,
)

routes_bp = Blueprint("routes", __name__)

# Domain Data Fixtures for Routes
WOODPECKER = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
TITMOUSE = TaxonRef.create("Tufted Titmouse", "Baeolophus bicolor", "tuftit")
WREN = TaxonRef.create("Carolina Wren", "Thryothorus ludovicianus", "carwre")
CARDINAL = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
BLUE_JAY = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")

CUE_BIRDY_1 = FieldCue(CARDINAL, "Scan low dogwood shrubs near pond edge.", "Listen for sharp metallic 'chip' call.")
CUE_BIRDY_2 = FieldCue(WOODPECKER, "Inspect dead tree snags near Brush Creek.", "Listen for loud rolling churring calls.")

SEGMENT_BIRDY_1 = RouteSegment(
    index=1, name="Park Perimeter & Pond Edge", habitat_name="Pond & Grassland",
    distance_meters=800.0, duration_minutes=15.0,
    focal_species=(CARDINAL, BLUE_JAY), field_cue=CUE_BIRDY_1
)

SEGMENT_BIRDY_2 = RouteSegment(
    index=2, name="Brush Creek Canopy Trail", habitat_name="Mature Hardwood Forest",
    distance_meters=1400.0, duration_minutes=30.0,
    focal_species=(WOODPECKER, TITMOUSE, WREN), field_cue=CUE_BIRDY_2
)

ROUTE_BIRDY_DOMAIN = RouteOption(
    id="birdy-1", persona=RoutePersona.BIRDY, name="The Birdy One",
    tagline="Diverges into dense tree canopy and creek bed edge habitat.",
    duration_minutes=45, distance_meters=2200.0, badge_label="Best bird opportunity",
    tradeoff_description="Adds 400m of dirt trail near Brush Creek for double species diversity.",
    segments=(SEGMENT_BIRDY_1, SEGMENT_BIRDY_2)
)

MEDIA_WOODPECKER_AUDIO = MediaAsset(
    asset_id="xc-123456",
    taxon_ref=WOODPECKER,
    media_type=MediaType.AUDIO,
    url="https://xeno-canto.org/sounds/uploaded/sample.mp3",
    creator="Jane Smith",
    license=LicenseType.CC_BY_NC_4_0,
    attribution_text="Jane Smith (CC BY-NC 4.0 via Xeno-Canto #123456)",
    source_name="Xeno-Canto"
)

FIELD_PACK_BIRDY = RouteFieldPack(
    route_id="birdy-1",
    focal_species=(CARDINAL, BLUE_JAY, WOODPECKER, TITMOUSE, WREN),
    field_cues=(CUE_BIRDY_1, CUE_BIRDY_2),
    media_assets=(MEDIA_WOODPECKER_AUDIO,)
)

ROUTES_DB = {
    "birdy-1": (ROUTE_BIRDY_DOMAIN, FIELD_PACK_BIRDY),
    "easy-1": (ROUTE_BIRDY_DOMAIN, FIELD_PACK_BIRDY),
    "weird-1": (ROUTE_BIRDY_DOMAIN, FIELD_PACK_BIRDY)
}


@routes_bp.route("/routes/<route_id>")
def detail(route_id):
    """Step 6 & 7: Route Detail & Text-Equivalent Field Pack."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain, field_pack = ROUTES_DB[route_id]
    return render_template("routes/detail.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/in-route")
def in_route(route_id):
    """Step 8: In-Route Segment Tracking View."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain, field_pack = ROUTES_DB[route_id]
    return render_template("routes/in_route.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/recap")
def recap(route_id):
    """Step 9: After-Route Walk Recap."""
    if route_id not in ROUTES_DB:
        abort(404)
    route_domain, field_pack = ROUTES_DB[route_id]
    return render_template("routes/recap.html", route=route_domain, field_pack=field_pack)
