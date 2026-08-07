"""Planner Application Service."""

from typing import Sequence

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
from packages.ovon_core.routing import OSMnxIgraphRoutingProvider, RoutingProvider


class PlanLoopPreview:
    """Application Service for evaluating LoopRequest and returning available RouteOptions."""

    def __init__(self, routing_provider: RoutingProvider | None = None):
        self._routing_provider = routing_provider

    @property
    def routing_provider(self) -> RoutingProvider:
        if self._routing_provider:
            return self._routing_provider
        if current_app and "routing_provider" in current_app.extensions:
            provider: RoutingProvider = current_app.extensions["routing_provider"]
            return provider
        return OSMnxIgraphRoutingProvider()

    def execute(self, request: LoopRequest) -> Sequence[RouteOption]:
        """Return distinct route options matching the LoopRequest."""
        try:
            result = self.routing_provider.calculate_loop(request)
            options: list[RouteOption] = []

            for cand in result.candidates:
                # Map candidate back to domain RouteOption with segments
                if cand.persona == RoutePersona.EASY:
                    base = ROUTE_EASY
                    focal = (ROBIN, CARDINAL)
                    cue = CUE_ROBIN
                elif cand.persona == RoutePersona.BIRDY:
                    base = ROUTE_BIRDY
                    focal = (CARDINAL, WOODPECKER)
                    cue = CUE_CARDINAL
                else:
                    base = ROUTE_WEIRD
                    focal = (WAXWING, WOODPECKER)
                    cue = CUE_WAXWING

                obs_pt1 = cand.waypoints[1] if cand.waypoints and len(cand.waypoints) > 1 else None
                obs_pt2 = cand.waypoints[2] if cand.waypoints and len(cand.waypoints) > 2 else None

                seg1 = RouteSegment(
                    index=1,
                    name=f"{cand.name} Outbound Leg",
                    habitat_name="Woodland Edge & Parkland",
                    distance_meters=round(cand.distance_meters * 0.4, 1),
                    duration_minutes=round(float(cand.duration_minutes) * 0.4, 1),
                    focal_species=(focal[0],),
                    field_cue=cue,
                    geojson_geometry=cand.geojson_geometry,
                    observation_point=obs_pt1,
                )

                seg2 = RouteSegment(
                    index=2,
                    name=f"{cand.name} Return Loop Leg",
                    habitat_name="Canopy & Meadow Boundary",
                    distance_meters=round(cand.distance_meters * 0.6, 1),
                    duration_minutes=round(float(cand.duration_minutes) * 0.6, 1),
                    focal_species=focal,
                    field_cue=cue,
                    geojson_geometry=cand.geojson_geometry,
                    observation_point=obs_pt2,
                )

                opt = RouteOption(
                    id=base.id,
                    persona=cand.persona,
                    name=cand.name,
                    tagline=cand.tagline,
                    duration_minutes=cand.duration_minutes,
                    distance_meters=cand.distance_meters,
                    badge_label=cand.badge_label,
                    tradeoff_description=cand.tradeoff_description,
                    segments=(seg1, seg2),
                    geojson_geometry=cand.geojson_geometry,
                )
                options.append(opt)

            if current_app:
                if "active_routes" not in current_app.extensions:
                    current_app.extensions["active_routes"] = {}
                for opt in options:
                    current_app.extensions["active_routes"][opt.id] = opt

            return tuple(options)
        except Exception:
            # Fall back gracefully to prototype fixtures if graph solver fails
            return (ROUTE_EASY, ROUTE_BIRDY, ROUTE_WEIRD)
