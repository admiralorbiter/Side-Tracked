import re
from flask import Blueprint, current_app, make_response, render_template, request, session

from apps.web.app.services import PlanLoopPreview
from packages.ovon_core.domain import (
    Coordinate,
    InvalidCoordinateError,
    InvalidTimeBudgetError,
    LoopRequest,
)
from packages.ovon_core.spatial import (
    PRESETS_BY_ID,
    GeocoderProvider,
    NominatimGeocoderProvider,
    is_within_us_bounds,
)

planner_bp = Blueprint("planner", __name__)

DEFAULT_COORDINATE = Coordinate(39.0347, -94.5906)


def _resolve_origin_coordinate(origin_str: str) -> tuple[Coordinate, str]:
    """Resolve an input origin string into a validated Coordinate and clean public display name."""
    clean_str = origin_str.strip()
    if not clean_str:
        return DEFAULT_COORDINATE, "Loose Park, Kansas City, MO"

    # Check Preset catalog
    preset_key = clean_str.lower().replace(" ", "-")
    if preset_key in PRESETS_BY_ID:
        p = PRESETS_BY_ID[preset_key]
        return p.coordinate, f"{p.name}, {p.city_state}"

    # Check Current Location pattern: "Current Location (39.0347, -94.5906)"
    coords_match = re.search(r"Current Location \((-?\d+\.\d+),\s*(-?\d+\.\d+)\)", clean_str)
    if coords_match:
        try:
            lat = float(coords_match.group(1))
            lon = float(coords_match.group(2))
            c = Coordinate(lat, lon)
            if is_within_us_bounds(c):
                return c, f"Current Location ({lat:.3f}, {lon:.3f})"
        except ValueError:
            pass

    # Attempt Nominatim Geocoding via application extension
    geocoder: GeocoderProvider | None = None
    if current_app and "geocoder_provider" in current_app.extensions:
        geocoder = current_app.extensions["geocoder_provider"]
    else:
        geocoder = NominatimGeocoderProvider()

    if geocoder:
        res = geocoder.geocode(clean_str)
        if res and is_within_us_bounds(res.coordinate):
            # Privacy Scrub: Extract coarse city/park name rather than exact street number
            clean_display = res.display_name.split(",")[0].strip()
            return res.coordinate, clean_display

    return DEFAULT_COORDINATE, "Loose Park, Kansas City, MO"


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
    origin_location = request.values.get("origin") or session.get(
        "origin", "Loose Park, Kansas City, MO"
    )
    session["origin"] = origin_location

    if request.headers.get("HX-Request"):
        resp = make_response(render_template("planner/duration.html", origin=origin_location))
        resp.headers["HX-Push-Url"] = "/planner/duration"
        return resp
    return render_template("planner/index.html", step="duration", origin=origin_location)


@planner_bp.route("/planner/planning", methods=["POST"])
def planning():
    """Step 4: Animated planning / loading state."""
    origin_loc = request.form.get("origin") or session.get("origin", "Loose Park, Kansas City, MO")
    minutes = request.form.get("duration", "45")
    paved_only = request.form.get("paved_only") == "true"
    quiet_mode = request.form.get("quiet_mode") == "true"

    session["origin"] = origin_loc
    session["duration"] = minutes
    session["paved_only"] = paved_only
    session["quiet_mode"] = quiet_mode

    if request.headers.get("HX-Request"):
        return render_template(
            "planner/planning.html",
            origin=origin_loc,
            duration=minutes,
            paved_only=paved_only,
            quiet_mode=quiet_mode,
        )
    return render_template(
        "planner/index.html", step="planning", origin=origin_loc, minutes=minutes
    )


@planner_bp.route("/planner/results", methods=["GET", "POST"])
def results():
    """Step 5: Display domain-backed Easy, Birdy, and Weird route options."""
    if request.method == "POST":
        origin_loc = request.form.get("origin") or session.get(
            "origin", "Loose Park, Kansas City, MO"
        )
        minutes_raw = request.form.get("duration") or session.get("duration", "45")
        paved_only = request.form.get("paved_only") == "true"
        quiet_mode = request.form.get("quiet_mode") == "true"
    else:
        origin_loc = session.get("origin", "Loose Park, Kansas City, MO")
        minutes_raw = session.get("duration", "45")
        paved_only = session.get("paved_only", False)
        quiet_mode = session.get("quiet_mode", False)

    try:
        minutes = int(minutes_raw)
        resolved_coord, clean_name = _resolve_origin_coordinate(origin_loc)

        loop_req = LoopRequest(
            origin=resolved_coord,
            origin_name=clean_name,
            duration_minutes=minutes,
            paved_only=paved_only,
            quiet_mode=quiet_mode,
        )
    except (ValueError, InvalidTimeBudgetError, InvalidCoordinateError) as err:
        error_msg = str(err)
        if request.headers.get("HX-Request"):
            return render_template("planner/duration.html", origin=origin_loc, error=error_msg), 400
        return render_template(
            "planner/index.html", step="duration", origin=origin_loc, error=error_msg
        ), 400

    service = PlanLoopPreview()
    domain_routes = service.execute(loop_req)

    if request.headers.get("HX-Request"):
        resp = make_response(
            render_template(
                "planner/routes_preview.html", routes=domain_routes, loop_request=loop_req
            )
        )
        resp.headers["HX-Push-Url"] = "/planner/results"
        return resp

    return render_template("planner/index.html", routes=domain_routes, loop_request=loop_req)
