from flask import Blueprint, make_response, render_template, request, session

from apps.web.app.services import PlanLoopPreview
from packages.ovon_core.domain import (
    Coordinate,
    InvalidCoordinateError,
    InvalidTimeBudgetError,
    LoopRequest,
)

planner_bp = Blueprint("planner", __name__)

MOCK_COORDINATE = Coordinate(39.0347, -94.5906)


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
        loop_req = LoopRequest(
            origin=MOCK_COORDINATE,
            origin_name=origin_loc,
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
