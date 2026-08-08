from flask import Blueprint, abort, render_template

from apps.web.app.services import BuildFieldPack, GetRouteDetail

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/routes/<route_id>")
def detail(route_id):
    """Step 6 & 7: Route Detail & Text-Equivalent Field Pack & Route Evidence."""
    from packages.ovon_core.evidence.aggregator import MultiSourceEvidenceAggregator
    from packages.ovon_core.evidence.ebird_recent_adapter import eBirdRecentAdapter
    from packages.ovon_core.evidence.gbif_adapter import GBIFOccurrenceAdapter
    from packages.ovon_core.evidence.inaturalist_adapter import INaturalistOccurrenceAdapter
    from packages.ovon_core.evidence.providers import MockRecentOccurrenceProvider
    from packages.ovon_core.evidence.service import RouteEvidenceService
    from packages.ovon_core.modeling.joint_service import JointModelService
    from packages.ovon_core.routing.alternative_loops import AlternativeLoopEngine

    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    # Multi-source evidence aggregator with real eBird, GBIF, and iNat adapters
    evidence_aggregator = MultiSourceEvidenceAggregator(
        providers=[
            eBirdRecentAdapter(),
            GBIFOccurrenceAdapter(),
            INaturalistOccurrenceAdapter(),
        ]
    )

    evidence_service = RouteEvidenceService(provider=evidence_aggregator)
    model_service = JointModelService()
    variation_engine = AlternativeLoopEngine()

    route_domain = route_service.execute(None, route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    route_evidence = evidence_service.build_evidence_summary(route_domain)
    route_predictions = model_service.predict_for_route(route_domain)
    route_variations = variation_engine.generate_variations(route_domain)

    return render_template(
        "routes/detail.html",
        route=route_domain,
        field_pack=field_pack,
        route_evidence=route_evidence,
        route_predictions=route_predictions,
        route_variations=route_variations,
    )


@routes_bp.route("/routes/<route_id>/in-route")
def in_route(route_id):
    """Step 8: In-Route Segment Tracking View."""
    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    route_domain = route_service.execute(None, route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    return render_template("routes/in_route.html", route=route_domain, field_pack=field_pack)


@routes_bp.route("/routes/<route_id>/recap")
def recap(route_id):
    """Step 9: After-Route Walk Recap."""
    route_service = GetRouteDetail()
    field_pack_service = BuildFieldPack()

    route_domain = route_service.execute(None, route_id)
    if not route_domain:
        abort(404)

    field_pack = field_pack_service.execute(route_domain)
    return render_template("routes/recap.html", route=route_domain, field_pack=field_pack)
