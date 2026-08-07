"""Alternative Loop Variation Engine with Distinct Spatial Detour Geometries."""

from packages.ovon_core.domain.route import (
    RouteOption,
    RouteVariationOption,
    RouteVariationSummary,
)
from packages.ovon_core.routing.detour_geometry import SpatialGeometryDetourGenerator
from packages.ovon_core.routing.spatial_rerouter import SpatialRerouter


class AlternativeLoopEngine:
    """Generates Pareto-optimal loop detours with distinct spatial geometries balancing walk duration against ecological opportunity."""

    def __init__(self) -> None:
        self.rerouter = SpatialRerouter()
        self.geometry_generator = SpatialGeometryDetourGenerator()

    def generate_variations(self, route: RouteOption) -> RouteVariationSummary:
        """Generate RouteVariationSummary containing Direct, High-Canopy, and Creek-Edge loop variations with distinct spatial polylines."""
        canopy_metrics = self.rerouter.optimize_route_corridor(route, preference="canopy")
        water_metrics = self.rerouter.optimize_route_corridor(route, preference="water")

        base_geo = route.geojson_geometry
        canopy_geo = self.geometry_generator.generate_canopy_detour(base_geo)
        water_geo = self.geometry_generator.generate_water_detour(base_geo)

        baseline_var = RouteVariationOption(
            variation_id=f"var_direct_{route.id}",
            name="📍 Direct Loop (Baseline)",
            description="Standard walking loop path optimized for shortest distance.",
            added_distance_m=0.0,
            added_duration_min=0.0,
            opportunity_boost_percent=0.0,
            is_baseline=True,
            geojson_geometry=base_geo,
        )

        canopy_var = RouteVariationOption(
            variation_id=f"var_canopy_{route.id}",
            name="🌲 High-Canopy Detour",
            description="Diverts through mature tree canopy for woodland songbirds & woodpeckers.",
            added_distance_m=canopy_metrics["added_distance_m"],
            added_duration_min=canopy_metrics["added_duration_min"],
            opportunity_boost_percent=canopy_metrics["opportunity_boost_percent"],
            is_baseline=False,
            geojson_geometry=canopy_geo,
        )

        water_var = RouteVariationOption(
            variation_id=f"var_water_{route.id}",
            name="💧 Creek-Edge Detour",
            description="Follows riparian water edge for waterfowl & high biodiversity density.",
            added_distance_m=water_metrics["added_distance_m"],
            added_duration_min=water_metrics["added_duration_min"],
            opportunity_boost_percent=water_metrics["opportunity_boost_percent"],
            is_baseline=False,
            geojson_geometry=water_geo,
        )

        return RouteVariationSummary(
            route_id=route.id,
            variations=(baseline_var, canopy_var, water_var),
        )
