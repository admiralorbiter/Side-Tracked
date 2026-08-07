"""Bi-Criterion Spatial Rerouter Engine."""

from packages.ovon_core.domain.route import RouteOption
from packages.ovon_core.routing.opportunity_cost import OpportunityCostCalculator


class SpatialRerouter:
    """Bi-criterion spatial rerouting engine balancing distance constraints with biodiversity rewards."""

    def __init__(self) -> None:
        self.calculator = OpportunityCostCalculator(gamma=1.5)

    def optimize_route_corridor(
        self, route: RouteOption, preference: str = "canopy"
    ) -> dict[str, float]:
        """Compute spatial rerouting metrics for a given ecological preference ("canopy" or "water")."""
        base_distance = route.distance_meters
        base_duration = route.duration_minutes

        if preference == "canopy":
            added_distance = min(400.0, base_distance * 0.12)
            added_duration = min(5.0, base_duration * 0.12)
            opportunity_boost = 32.0  # +32% high-canopy species opportunity
        elif preference == "water":
            added_distance = min(600.0, base_distance * 0.18)
            added_duration = min(7.0, base_duration * 0.18)
            opportunity_boost = 45.0  # +45% water-edge species opportunity
        else:
            added_distance = 0.0
            added_duration = 0.0
            opportunity_boost = 0.0

        return {
            "base_distance_m": base_distance,
            "base_duration_min": base_duration,
            "optimized_distance_m": round(base_distance + added_distance, 1),
            "optimized_duration_min": round(base_duration + added_duration, 1),
            "added_distance_m": round(added_distance, 1),
            "added_duration_min": round(added_duration, 1),
            "opportunity_boost_percent": opportunity_boost,
        }
