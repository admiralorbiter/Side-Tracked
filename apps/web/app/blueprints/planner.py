import re

from flask import Blueprint, current_app, jsonify, make_response, render_template, request, session

from apps.web.app.services import BuildFieldPack, GetRouteDetail
from apps.web.app.services.planner_service import PlanLoopPreview, RoutePlanRepository
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
    is_within_kc_pilot_bounds,
)

planner_bp = Blueprint("planner", __name__)

DEFAULT_COORDINATE = Coordinate(39.0347, -94.5906)


class OriginResolutionError(Exception):
    """Raised when an origin location query cannot be resolved to a valid location."""

    pass


def _resolve_origin_coordinate(origin_str: str) -> tuple[Coordinate, str]:
    """Resolve an input origin string into a validated Coordinate and clean public display name."""
    clean_str = origin_str.strip()
    if not clean_str:
        return DEFAULT_COORDINATE, "Loose Park, Kansas City, MO"

    clean_lower = clean_str.lower()
    for p_id, p in PRESETS_BY_ID.items():
        if (
            p_id in clean_lower
            or p.name.lower() in clean_lower
            or p_id.replace("-", " ") in clean_lower
        ):
            return p.coordinate, f"{p.name}, {p.city_state}"

    coords_match = re.search(r"Current Location \((-?\d+\.\d+),\s*(-?\d+\.\d+)\)", clean_str)
    if coords_match:
        try:
            lat = float(coords_match.group(1))
            lon = float(coords_match.group(2))
            c = Coordinate(lat, lon)
            if is_within_kc_pilot_bounds(c):
                return c, f"Current Location ({lat:.3f}, {lon:.3f})"
        except ValueError:
            pass

    geocoder: GeocoderProvider | None = None
    if current_app and "geocoder_provider" in current_app.extensions:
        geocoder = current_app.extensions["geocoder_provider"]
    else:
        geocoder = NominatimGeocoderProvider()

    if geocoder:
        res = geocoder.geocode(clean_str)
        if res and is_within_kc_pilot_bounds(res.coordinate):
            clean_display = res.display_name.split(",")[0].strip()
            return res.coordinate, clean_display

    raise OriginResolutionError(
        f"We couldn't find a supported location for '{clean_str}' within the Kansas City pilot area. "
        "Please try a park name (e.g. Loose Park, Swope Park) or select a park preset."
    )


def _resolve_route_with_fallback(plan_id: str, route_id: str):
    """Resolve RouteOption strictly by (plan_id, route_id). Return None if plan expired or missing."""
    return RoutePlanRepository.get_route(plan_id, route_id)


@planner_bp.route("/")
def index():
    """Step 1: Home intent selection screen."""
    return render_template("planner/index.html")


@planner_bp.route("/planner/origin", methods=["GET", "POST"])
def origin():
    """Step 2: Choose starting origin."""
    if request.headers.get("HX-Request"):
        resp = make_response(render_template("planner/origin.html"))
        resp.headers["HX-Push-Url"] = "/planner/origin"
        return resp
    return render_template("planner/index.html", step="origin")


@planner_bp.route("/planner/duration", methods=["GET", "POST"])
def duration():
    """Step 3: Choose duration budget & preferences (Privacy: POST handling)."""
    error_msg = None
    origin_input = (
        request.form.get("origin")
        or request.args.get("origin")
        or session.get("origin_display_name", "Loose Park, Kansas City, MO")
    )

    try:
        coord, clean_name = _resolve_origin_coordinate(origin_input)
        session["origin_lat"] = coord.latitude
        session["origin_lon"] = coord.longitude
        session["origin_display_name"] = clean_name
        origin_display = clean_name
    except OriginResolutionError as err:
        error_msg = str(err)
        origin_display = session.get("origin_display_name", "Loose Park, Kansas City, MO")

    if error_msg and request.headers.get("HX-Request"):
        return render_template("planner/origin.html", error=error_msg), 400

    if request.headers.get("HX-Request"):
        resp = make_response(
            render_template("planner/duration.html", origin=origin_display, error=error_msg)
        )
        resp.headers["HX-Push-Url"] = "/planner/duration"
        return resp
    return render_template(
        "planner/index.html", step="duration", origin=origin_display, error=error_msg
    )


@planner_bp.route("/planner/planning", methods=["POST"])
def planning():
    """Step 4: Animated planning / loading state."""
    origin_display = session.get("origin_display_name", "Loose Park, Kansas City, MO")
    minutes = request.form.get("duration", "45")
    paved_only = request.form.get("paved_only") == "true"
    quiet_mode = request.form.get("quiet_mode") == "true"

    session["duration"] = minutes
    session["paved_only"] = paved_only
    session["quiet_mode"] = quiet_mode

    if request.headers.get("HX-Request"):
        return render_template(
            "planner/planning.html",
            origin=origin_display,
            duration=minutes,
            paved_only=paved_only,
            quiet_mode=quiet_mode,
        )
    return render_template(
        "planner/index.html", step="planning", origin=origin_display, minutes=minutes
    )


@planner_bp.route("/planner/results", methods=["GET", "POST"])
def results():
    """Step 5: Display plan-scoped Easy, Birdy, and Weird route options."""
    if request.method == "POST":
        minutes_raw = request.form.get("duration") or session.get("duration", "45")
        paved_only = request.form.get("paved_only") == "true"
        quiet_mode = request.form.get("quiet_mode") == "true"
    else:
        minutes_raw = session.get("duration", "45")
        paved_only = session.get("paved_only", False)
        quiet_mode = session.get("quiet_mode", False)

    lat = session.get("origin_lat", DEFAULT_COORDINATE.latitude)
    lon = session.get("origin_lon", DEFAULT_COORDINATE.longitude)
    origin_display = session.get("origin_display_name", "Loose Park, Kansas City, MO")

    try:
        minutes = int(minutes_raw)
        resolved_coord = Coordinate(lat, lon)

        loop_req = LoopRequest(
            origin=resolved_coord,
            origin_name=origin_display,
            duration_minutes=minutes,
            paved_only=paved_only,
            quiet_mode=quiet_mode,
        )
    except (ValueError, InvalidTimeBudgetError, InvalidCoordinateError) as err:
        error_msg = str(err)
        if request.headers.get("HX-Request"):
            return render_template(
                "planner/duration.html", origin=origin_display, error=error_msg
            ), 400
        return render_template(
            "planner/index.html", step="duration", origin=origin_display, error=error_msg
        ), 400

    service = PlanLoopPreview()
    menu_result = service.execute(loop_req)
    plan_id = RoutePlanRepository.save_plan(menu_result.routes)

    if request.headers.get("HX-Request"):
        resp = make_response(
            render_template(
                "planner/routes_preview.html",
                routes=menu_result.routes,
                plan_id=plan_id,
                menu_result=menu_result,
                loop_request=loop_req,
            )
        )
        resp.headers["HX-Push-Url"] = "/planner/results"
        return resp

    return render_template(
        "planner/index.html",
        routes=menu_result.routes,
        plan_id=plan_id,
        menu_result=menu_result,
        loop_request=loop_req,
    )


from apps.web.app.services import (
    BuildFieldPack,
    BuildHabitatRadar,
    GetRouteDetail,
    WalkFeedbackRepository,
)


@planner_bp.route("/plans/<plan_id>/routes/<route_id>")
def route_detail(plan_id: str, route_id: str):
    """Step 6: Plan-scoped route detail view with Habitat Radar."""
    route = _resolve_route_with_fallback(plan_id, route_id)
    if not route:
        return render_template("errors/404.html"), 404
    field_pack = BuildFieldPack().execute(route)
    habitat_radar = BuildHabitatRadar().execute(route)
    return render_template(
        "routes/detail.html",
        route=route,
        field_pack=field_pack,
        habitat_radar=habitat_radar,
        plan_id=plan_id,
    )


@planner_bp.route("/plans/<plan_id>/routes/<route_id>/walk")
def route_walk(plan_id: str, route_id: str):
    """Step 8: Plan-scoped active Walk Mode with glanceable Habitat Radar."""
    route = _resolve_route_with_fallback(plan_id, route_id)
    if not route:
        return render_template("errors/404.html"), 404
    field_pack = BuildFieldPack().execute(route)
    habitat_radar = BuildHabitatRadar().execute(route)
    quiet_mode = session.get("quiet_mode", False)
    return render_template(
        "routes/in_route.html",
        route=route,
        field_pack=field_pack,
        habitat_radar=habitat_radar,
        plan_id=plan_id,
        quiet_mode=quiet_mode,
    )


@planner_bp.route("/plans/<plan_id>/routes/<route_id>/recap")
def route_recap(plan_id: str, route_id: str):
    """Step 9: Plan-scoped walk recap."""
    route = _resolve_route_with_fallback(plan_id, route_id)
    if not route:
        return render_template("errors/404.html"), 404
    field_pack = BuildFieldPack().execute(route)
    saved_feedback = WalkFeedbackRepository.get_feedback_for_plan(plan_id, route_id)
    return render_template(
        "routes/recap.html",
        route=route,
        field_pack=field_pack,
        plan_id=plan_id,
        saved_feedback=saved_feedback,
    )


@planner_bp.route("/plans/<plan_id>/routes/<route_id>/feedback", methods=["POST"])
def route_feedback(plan_id: str, route_id: str):
    """Save versioned user walk observation feedback."""
    route = _resolve_route_with_fallback(plan_id, route_id)
    if not route:
        return render_template("errors/404.html"), 404

    outcome = request.form.get("outcome", "completed")
    notes = request.form.get("notes", "").strip()

    duration_raw = request.form.get("actual_duration")
    duration_minutes = int(duration_raw) if duration_raw and duration_raw.isdigit() else route.duration_minutes

    field_pack = BuildFieldPack().execute(route)
    observations = {}
    for sp in field_pack.focal_species:
        obs_key = f"obs_{sp.ebird_code}"
        if obs_key in request.form:
            observations[sp.ebird_code] = request.form[obs_key]

    WalkFeedbackRepository.save_feedback(
        plan_id=plan_id,
        route_id=route.id,
        outcome=outcome,
        observations=observations,
        duration_minutes=duration_minutes,
        notes=notes,
    )

    saved_feedback = WalkFeedbackRepository.get_feedback_for_plan(plan_id, route.id)
    return render_template(
        "routes/recap.html",
        route=route,
        field_pack=field_pack,
        plan_id=plan_id,
        saved_feedback=saved_feedback,
        submitted=True,
    )


@planner_bp.route("/plans/<plan_id>/routes/<route_id>/segments/<int:segment_index>/blocked", methods=["POST"])
def route_segment_blocked(plan_id: str, route_id: str, segment_index: int):
    """Record trail segment obstruction during active Walk Mode."""
    route = _resolve_route_with_fallback(plan_id, route_id)
    if not route:
        return jsonify({"status": "error", "message": "Route not found"}), 404

    note = f"Leg {segment_index} marked blocked by walker."
    WalkFeedbackRepository.save_feedback(
        plan_id=plan_id,
        route_id=route.id,
        outcome="path_blocked",
        observations={},
        duration_minutes=route.duration_minutes,
        notes=note,
    )
    return jsonify({"status": "ok", "message": "Obstruction recorded", "segment_index": segment_index})
