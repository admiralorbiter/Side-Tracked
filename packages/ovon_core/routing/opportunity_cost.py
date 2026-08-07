"""Spatial Opportunity Cost Calculator and Modified Graph Edge Weighting."""

from dataclasses import dataclass

from packages.ovon_core.domain.environmental_vector import EnvironmentalFeatureVector


@dataclass(frozen=True, slots=True)
class OpportunityWeightedEdge:
    """Graph edge with distance and biodiversity opportunity weight."""

    edge_id: str
    length_meters: float
    environmental_vector: EnvironmentalFeatureVector
    opportunity_score: float  # Normalized ecological opportunity R(e) in [0.0, 1.0]
    modified_weight: float  # Modified graph weight c(e) = length / (1 + gamma * R(e))


class OpportunityCostCalculator:
    """Calculates modified graph edge weights based on continuous environmental rasters."""

    def __init__(self, gamma: float = 1.5) -> None:
        self.gamma = gamma

    def calculate_edge_opportunity(
        self, length_meters: float, env_vector: EnvironmentalFeatureVector
    ) -> OpportunityWeightedEdge:
        """Calculate opportunity score R(e) and modified routing weight c(e)."""
        canopy = env_vector.canopy_cover_percent
        water_dist = env_vector.water_edge_distance_m
        impervious = env_vector.impervious_surface_percent

        # Normalized ecological opportunity calculation
        canopy_factor = min(1.0, canopy / 60.0)
        water_factor = max(0.0, 1.0 - (water_dist / 300.0))
        impervious_penalty = min(1.0, impervious / 50.0)

        raw_opportunity = (canopy_factor * 0.5 + water_factor * 0.5) * (
            1.0 - 0.5 * impervious_penalty
        )
        opportunity_score = max(0.05, min(1.0, raw_opportunity))

        # Bi-criterion modified edge cost: c(e) = length / (1 + gamma * R(e))
        modified_weight = length_meters / (1.0 + self.gamma * opportunity_score)

        return OpportunityWeightedEdge(
            edge_id=f"edge_{int(length_meters)}_{int(canopy)}",
            length_meters=length_meters,
            environmental_vector=env_vector,
            opportunity_score=round(opportunity_score, 3),
            modified_weight=round(modified_weight, 2),
        )
