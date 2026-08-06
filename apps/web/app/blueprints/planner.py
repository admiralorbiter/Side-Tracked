from flask import Blueprint, render_template, request, make_response
from packages.ovon_core.domain import (
    Coordinate,
    LoopRequest,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
    FieldCue,
    InvalidCoordinateError,
    InvalidTimeBudgetError,
)

planner_bp = Blueprint("planner", __name__)

# Domain Fixtures for Sprint 2 Prototype
MOCK_COORDINATE = Coordinate(39.0347, -94.5906)

ROBIN = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")
CARDINAL = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
BLUE_JAY = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")
WOODPECKER = TaxonRef.create("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo")
TITMOUSE = TaxonRef.create("Tufted Titmouse", "Baeolophus bicolor", "tuftit")
WREN = TaxonRef.create("Carolina Wren", "Thryothorus ludovicianus", "carwre")
WAXWING = TaxonRef.create("Cedar Waxwing", "Bombycilla cedrorum", "cedwax")

CUE_EASY = FieldCue(ROBIN, "Scan low lawn areas and open park paths.", "Listen for cheery liquid warbling songs.")
CUE_BIRDY = FieldCue(WOODPECKER, "Inspect dead tree snags near Brush Creek.", "Listen for loud rolling churring calls.")
CUE_WEIRD = FieldCue(WAXWING, "Look high in fruiting cedar tree branches.", "Listen for high-pitched thin lisping whistles.")

SEGMENT_EASY_1 = RouteSegment(
    index=1, name="Loose Park Lawn Loop", habitat_name="Open Parkland",
    distance_meters=1800.0, duration_minutes=45.0,
    focal_species=(ROBIN, CARDINAL, BLUE_JAY), field_cue=CUE_EASY
)

SEGMENT_BIRDY_1 = RouteSegment(
    index=1, name="Park Perimeter Pond Edge", habitat_name="Pond & Wetlands",
    distance_meters=800.0, duration_minutes=15.0,
    focal_species=(CARDINAL, BLUE_JAY), field_cue=CUE_EASY
)

SEGMENT_BIRDY_2 = RouteSegment(
    index=2, name="Brush Creek Canopy Trail", habitat_name="Mature Hardwood Canopy",
    distance_meters=1400.0, duration_minutes=30.0,
    focal_species=(WOODPECKER, TITMOUSE, WREN), field_cue=CUE_BIRDY
)

SEGMENT_WEIRD_1 = RouteSegment(
    index=1, name="Old Orchard Tree Line", habitat_name="Overgrown Orchard Edge",
    distance_meters=2100.0, duration_minutes=45.0,
    focal_species=(WAXWING, TITMOUSE), field_cue=CUE_WEIRD
)

ROUTE_EASY = RouteOption(
    id="easy-1", persona=RoutePersona.EASY, name="The Easy One",
    tagline="Shortest path with paved trails and low elevation change.",
    duration_minutes=45, distance_meters=1800.0, badge_label="Lowest effort",
    tradeoff_description="Paved park paths with standard suburban bird activity.",
    segments=(SEGMENT_EASY_1,)
)

ROUTE_BIRDY = RouteOption(
    id="birdy-1", persona=RoutePersona.BIRDY, name="The Birdy One",
    tagline="Diverges into dense tree canopy and creek bed edge habitat.",
    duration_minutes=45, distance_meters=2200.0, badge_label="Best bird opportunity",
    tradeoff_description="Adds 400m of dirt trail near Brush Creek for double species diversity.",
    segments=(SEGMENT_BIRDY_1, SEGMENT_BIRDY_2)
)

ROUTE_WEIRD = RouteOption(
    id="weird-1", persona=RoutePersona.WEIRD, name="The Weird One",
    tagline="Explores lesser-known perimeter tree line and old orchard edge.",
    duration_minutes=45, distance_meters=2100.0, badge_label="Unusual habitat",
    tradeoff_description="Uneven terrain along forgotten overgrown fence line.",
    segments=(SEGMENT_WEIRD_1,)
)


@planner_bp.route("/")
def index():
    """Step 1: Home intent selection screen."""
    return render_template("planner/index.html")


@planner_bp.route("/planner/origin", methods=["GET"])
def origin():
    """Step 2: Choose starting origin."""
    if request.headers.get("HX-Request"):
        resp = make_response(render_template("planner/origin.html"))
        resp.headers["HX-Push-Url"] = "/planner/origin"
        return resp
    return render_template("planner/index.html", step="origin")


@planner_bp.route("/planner/duration", methods=["GET", "POST"])
def duration():
    """Step 3: Choose duration budget & preferences."""
    origin_location = request.values.get("origin", "Loose Park, Kansas City")
    if request.headers.get("HX-Request"):
        resp = make_response(render_template("planner/duration.html", origin=origin_location))
        resp.headers["HX-Push-Url"] = f"/planner/duration?origin={origin_location}"
        return resp
    return render_template("planner/index.html", step="duration", origin=origin_location)


@planner_bp.route("/planner/planning", methods=["POST"])
def planning():
    """Step 4: Animated planning / loading state."""
    origin_loc = request.form.get("origin", "Loose Park, Kansas City")
    minutes = request.form.get("duration", "45")
    paved_only = request.form.get("paved_only") == "true"
    quiet_mode = request.form.get("quiet_mode") == "true"

    if request.headers.get("HX-Request"):
        return render_template(
            "planner/planning.html",
            origin=origin_loc,
            duration=minutes,
            paved_only=paved_only,
            quiet_mode=quiet_mode
        )
    return render_template("planner/index.html", step="planning", origin=origin_loc, minutes=minutes)


@planner_bp.route("/planner/results", methods=["POST"])
def results():
    """Step 5: Display domain-backed Easy, Birdy, and Weird route options."""
    origin_loc = request.form.get("origin", "Loose Park, Kansas City")
    minutes_raw = request.form.get("duration", "45")

    try:
        minutes = int(minutes_raw)
        # Instantiate domain model LoopRequest
        loop_req = LoopRequest(
            origin=MOCK_COORDINATE,
            origin_name=origin_loc,
            duration_minutes=minutes,
            paved_only=request.form.get("paved_only") == "true",
            quiet_mode=request.form.get("quiet_mode") == "true"
        )
    except (ValueError, InvalidTimeBudgetError, InvalidCoordinateError) as err:
        error_msg = str(err)
        if request.headers.get("HX-Request"):
            return render_template("planner/duration.html", origin=origin_loc, error=error_msg), 400
        return render_template("planner/index.html", step="duration", origin=origin_loc, error=error_msg), 400

    domain_routes = [ROUTE_EASY, ROUTE_BIRDY, ROUTE_WEIRD]

    if request.headers.get("HX-Request"):
        resp = make_response(
            render_template(
                "planner/routes_preview.html",
                routes=domain_routes,
                loop_request=loop_req
            )
        )
        resp.headers["HX-Push-Url"] = f"/planner/results?origin={origin_loc}&duration={minutes}"
        return resp

    return render_template("planner/index.html", routes=domain_routes, loop_request=loop_req)
