"""Unit tests for Spatial Optimization and Dynamic Rerouting Engine."""

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.routing.alternative_loops import AlternativeLoopEngine
from packages.ovon_core.routing.opportunity_cost import OpportunityCostCalculator
from packages.ovon_core.routing.spatial_rerouter import SpatialRerouter


def test_opportunity_cost_calculator():
    calc = OpportunityCostCalculator(gamma=1.5)
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(60.0, 10.0, 50.0, 260.0, 2.0),
    )
    edge = calc.calculate_edge_opportunity(200.0, vec)

    assert edge.length_meters == 200.0
    assert 0.0 <= edge.opportunity_score <= 1.0
    assert edge.modified_weight < edge.length_meters


def test_spatial_rerouter():
    rerouter = SpatialRerouter()
    metrics = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="canopy")

    assert metrics["base_distance_m"] == ROUTE_BIRDY.distance_meters
    assert metrics["added_duration_min"] > 0.0
    assert metrics["opportunity_boost_percent"] > 0.0


def test_alternative_loop_engine():
    engine = AlternativeLoopEngine()
    summary = engine.generate_variations(ROUTE_BIRDY)

    assert summary.route_id == ROUTE_BIRDY.id
    assert len(summary.variations) == 3
    assert summary.variations[0].is_baseline is True
    assert summary.variations[1].is_baseline is False
    assert summary.variations[2].is_baseline is False

    g0 = summary.variations[0].geojson_geometry["coordinates"]
    g1 = summary.variations[1].geojson_geometry["coordinates"]
    g2 = summary.variations[2].geojson_geometry["coordinates"]

    assert g0 != g1
    assert g0 != g2
    assert g1 != g2
