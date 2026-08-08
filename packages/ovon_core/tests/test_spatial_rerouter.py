"""Unit tests for Graph-Based Ecological Detour Solver (Sprint 17)."""

from packages.ovon_core.domain.environmental_vector import create_default_environmental_vector
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.routing.alternative_loops import AlternativeLoopEngine
from packages.ovon_core.routing.detour_geometry import SpatialGeometryDetourGenerator
from packages.ovon_core.routing.opportunity_cost import OpportunityCostCalculator
from packages.ovon_core.routing.spatial_rerouter import SpatialRerouter


def test_opportunity_cost_calculator():
    calc = OpportunityCostCalculator(gamma=1.5)
    vec = create_default_environmental_vector()
    edge = calc.calculate_edge_opportunity(200.0, vec)

    assert edge.length_meters == 200.0
    assert 0.0 <= edge.opportunity_score <= 1.0
    assert edge.modified_weight < edge.length_meters


def test_spatial_rerouter_detour_budget():
    rerouter = SpatialRerouter()
    res_canopy = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="canopy")
    res_water = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="water")

    # Max detour constraint D <= 1.25 * D_direct
    assert res_canopy["optimized_distance_m"] <= 1.25 * ROUTE_BIRDY.distance_meters
    assert res_water["optimized_distance_m"] <= 1.25 * ROUTE_BIRDY.distance_meters


def test_detour_geometry_distinct_polylines():
    detour_gen = SpatialGeometryDetourGenerator()
    base_geojson = ROUTE_BIRDY.geojson
    canopy_geojson = detour_gen.generate_canopy_detour(base_geojson)
    water_geojson = detour_gen.generate_water_detour(base_geojson)

    assert base_geojson != canopy_geojson
    assert canopy_geojson != water_geojson
    assert len(canopy_geojson["coordinates"]) > len(base_geojson["coordinates"])
    assert len(water_geojson["coordinates"]) > len(base_geojson["coordinates"])


def test_alternative_loop_engine():
    engine = AlternativeLoopEngine()
    summary = engine.generate_variations(ROUTE_BIRDY)
    variations = summary.variations

    assert len(variations) == 3
    assert "Direct Loop" in variations[0].name
    assert "High-Canopy" in variations[1].name
    assert "Creek-Edge" in variations[2].name
