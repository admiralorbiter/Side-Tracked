from flask import Blueprint, abort, render_template

from apps.web.app.services import BuildFieldPack, GetRouteDetail

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/routes/<route_id>")
def detail(route_id):
    """Step 6 & 7: Route Detail & Text-Equivalent Field Pack."""
    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    route_domain = route_service.execute(route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    return render_template("routes/detail.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/in-route")
def in_route(route_id):
    """Step 8: In-Route Segment Tracking View."""
    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    route_domain = route_service.execute(route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    return render_template("routes/in_route.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/recap")
def recap(route_id):
    """Step 9: After-Route Walk Recap."""
    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    route_domain = route_service.execute(route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    return render_template("routes/recap.html", route=route_domain, field_pack=field_pack)
