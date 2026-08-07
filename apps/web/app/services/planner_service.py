"""Planner Application Service and Plan-Scoped Repository."""

import uuid

from flask import current_app

from packages.ovon_core.domain import (
    LoopRequest,
    RouteOption,
    RoutePersona,
    RouteSegment,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY, ROUTE_EASY, ROUTE_WEIRD
from packages.ovon_core.fixtures.routes_fixtures import (
    CARDINAL,
    CUE_CARDINAL,
    CUE_ROBIN,
    CUE_WAXWING,
    ROBIN,
    WAXWING,
    WOODPECKER,
)
from packages.ovon_core.routing import (
    OSMnxIgraphRoutingProvider,
    RouteMenuResult,
    RoutingProvider,
    TradeoffExplanationGenerator,
)


class RoutePlanRepository:
    """In-memory plan-scoped repository for multi-user isolated route plans."""

    _plans: dict[str, tuple[RouteOption, ...]] = {}

    @classmethod
    def save_plan(cls, routes: tuple[RouteOption, ...]) -> str:
        plan_id = uuid.uuid4().hex[:10]
        cls._plans[plan_id] = routes
        return plan_id

    @classmethod
    def get_route(cls, plan_id: str, route_id: str) -> RouteOption | None:
        routes = cls._plans.get(plan_id)
        if not routes:
            return None
        for r in routes:
            if r.id == route_id:
                return r
        return None

    @classmethod
    def get_plan_routes(cls, plan_id: str) -> tuple[RouteOption, ...] | None:
        return cls._plans.get(plan_id)


class PlanLoopPreview:
    """Application Service for evaluating LoopRequest and returning available RouteOptions with truthful provenance."""

    def __init__(
        self,
        routing_provider: RoutingProvider | None = None,
        explanation_generator: TradeoffExplanationGenerator | None = None,
    ):
        self._routing_provider = routing_provider
        self.explanation_generator = explanation_generator or TradeoffExplanationGenerator()

    @property
    def routing_provider(self) -> RoutingProvider:
        if self._routing_provider:
            return self._routing_provider
        if current_app and "routing_provider" in current_app.extensions:
            provider: RoutingProvider = current_app.extensions["routing_provider"]
            return provider
        return OSMnxIgraphRoutingProvider()

    def execute(self, request: LoopRequest) -> RouteMenuResult:
        """Return distinct route options and truthfulness provenance for a LoopRequest."""
        try:
            result = self.routing_provider.calculate_loop(request)
            options: list[RouteOption] = []
            easy_baseline: RouteOption | None = None

            for cand in result.candidates:
                if cand.persona == RoutePersona.EASY:
                    focal = (ROBIN, CARDINAL)
                    cue = CUE_ROBIN
                elif cand.persona == RoutePersona.BIRDY:
                    focal = (CARDINAL, WOODPECKER)
                    cue = CUE_CARDINAL
                else:
                    focal = (WAXWING, WOODPECKER)
                    cue = CUE_WAXWING

                segments_list = []
                if cand.segment_metrics and len(cand.segment_metrics) >= 2:
                    m1 = cand.segment_metrics[0]
                    m2 = cand.segment_metrics[1]

                    # Distribute total candidate distance cleanly across segments so sum == total_dist exactly
                    d1 = float(m1.get("distance_meters", cand.distance_meters * 0.4))
                    d2 = round(cand.distance_meters - d1, 1)

                    t1 = float(m1.get("duration_minutes", cand.duration_minutes * 0.4))
                    t2 = round(float(cand.duration_minutes) - t1, 1)

                    obs_pt1 = (
                        cand.waypoints[1] if cand.waypoints and len(cand.waypoints) > 1 else None
                    )
                    obs_pt2 = (
                        cand.waypoints[2] if cand.waypoints and len(cand.waypoints) > 2 else None
                    )

                    seg1 = RouteSegment(
                        index=1,
                        name=m1.get("name", f"{cand.name} Outbound Leg"),
                        habitat_name=m1.get("habitat_name", "Woodland Edge & Parkland"),
                        distance_meters=d1,
                        duration_minutes=t1,
                        focal_species=(focal[0],),
                        field_cue=cue,
                        geojson_geometry=m1.get("geojson_geometry"),
                        observation_point=obs_pt1,
                        navigation_instruction=m1.get(
                            "navigation_instruction",
                            f"Depart {request.origin_name} heading along primary park path.",
                        ),
                    )

                    seg2 = RouteSegment(
                        index=2,
                        name=m2.get("name", f"{cand.name} Return Loop Leg"),
                        habitat_name=m2.get("habitat_name", "Canopy & Meadow Boundary"),
                        distance_meters=d2,
                        duration_minutes=t2,
                        focal_species=focal,
                        field_cue=cue,
                        geojson_geometry=m2.get("geojson_geometry"),
                        observation_point=obs_pt2,
                        navigation_instruction=m2.get(
                            "navigation_instruction",
                            f"Bear right onto return loop trail back to {request.origin_name}.",
                        ),
                    )
                    segments_list = [seg1, seg2]
                else:
                    d1 = round(cand.distance_meters * 0.4, 1)
                    d2 = round(cand.distance_meters - d1, 1)
                    t1 = round(float(cand.duration_minutes) * 0.4, 1)
                    t2 = round(float(cand.duration_minutes) - t1, 1)

                    seg1 = RouteSegment(
                        index=1,
                        name=f"{cand.name} Outbound Leg",
                        habitat_name="Woodland Edge & Parkland",
                        distance_meters=d1,
                        duration_minutes=t1,
                        focal_species=(focal[0],),
                        field_cue=cue,
                        geojson_geometry=cand.geojson_geometry,
                        observation_point=cand.waypoints[1]
                        if cand.waypoints and len(cand.waypoints) > 1
                        else None,
                        navigation_instruction=f"Depart {request.origin_name} heading along primary park path.",
                    )

                    seg2 = RouteSegment(
                        index=2,
                        name=f"{cand.name} Return Loop Leg",
                        habitat_name="Canopy & Meadow Boundary",
                        distance_meters=d2,
                        duration_minutes=t2,
                        focal_species=focal,
                        field_cue=cue,
                        geojson_geometry=cand.geojson_geometry,
                        observation_point=cand.waypoints[2]
                        if cand.waypoints and len(cand.waypoints) > 2
                        else None,
                        navigation_instruction=f"Bear right onto return trail back to {request.origin_name}.",
                    )
                    segments_list = [seg1, seg2]

                opt = RouteOption(
                    id=f"{cand.persona.name.lower()}-1"
                    if cand.persona == RoutePersona.EASY
                    else f"{cand.persona.name.lower()}-{len(options) + 1}",
                    persona=cand.persona,
                    name=cand.name,
                    tagline=cand.tagline,
                    duration_minutes=cand.duration_minutes,
                    distance_meters=cand.distance_meters,
                    badge_label=cand.badge_label,
                    tradeoff_description=cand.tradeoff_description,
                    segments=tuple(segments_list),
                    geojson_geometry=cand.geojson_geometry,
                )

                if cand.persona == RoutePersona.EASY:
                    easy_baseline = opt

                options.append(opt)

            final_options = []
            for opt in options:
                tradeoff_text = self.explanation_generator.generate_tradeoff_description(
                    opt, easy_baseline
                )
                updated_opt = RouteOption(
                    id=opt.id,
                    persona=opt.persona,
                    name=opt.name,
                    tagline=opt.tagline,
                    duration_minutes=opt.duration_minutes,
                    distance_meters=opt.distance_meters,
                    badge_label=opt.badge_label,
                    tradeoff_description=tradeoff_text,
                    segments=opt.segments,
                    geojson_geometry=opt.geojson_geometry,
                )
                final_options.append(updated_opt)

            routes_tuple = tuple(final_options)
            return RouteMenuResult(
                routes=routes_tuple,
                source="live_osm",
                warning=None,
            )
        except Exception as e:
            # Explicit degraded fallback with warning
            return RouteMenuResult(
                routes=(ROUTE_EASY, ROUTE_BIRDY, ROUTE_WEIRD),
                source="prototype_fixture",
                warning=f"Live routing graph solver was unable to solve candidates ({e}). Displaying demonstration routes.",
            )
