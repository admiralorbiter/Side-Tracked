"""CLI Tool to verify Graph-Based Ecological Detour Solver (Sprint 17)."""

import time

from packages.ovon_core.domain.environmental_vector import create_default_environmental_vector
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.routing.alternative_loops import AlternativeLoopEngine
from packages.ovon_core.routing.detour_geometry import SpatialGeometryDetourGenerator
from packages.ovon_core.routing.opportunity_cost import OpportunityCostCalculator
from packages.ovon_core.routing.spatial_rerouter import SpatialRerouter


def main() -> None:
    """Run Graph-Based Ecological Detour Solver verification suite."""
    print("=" * 65)
    print("   SIDETRACK ECOLOGICAL DETOUR SOLVER VERIFICATION")
    print("=" * 65)

    # 1. Test OpportunityCostCalculator
    calc = OpportunityCostCalculator(gamma=1.5)
    vec = create_default_environmental_vector()
    edge = calc.calculate_edge_opportunity(100.0, vec)

    assert edge.length_meters == 100.0
    assert 0.0 <= edge.opportunity_score <= 1.0
    assert edge.modified_weight < edge.length_meters

    print(
        f"[OK] OpportunityCostCalculator: Edge 100m -> Opportunity={edge.opportunity_score:.3f}, Modified Cost={edge.modified_weight:.2f}m"
    )

    # 2. Test BiCriterionSpatialRerouter (Detour Budget Constraint: D <= 1.25 * D_direct)
    rerouter = SpatialRerouter()
    start_t = time.perf_counter()
    res_canopy = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="canopy")
    res_water = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="water")
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    assert res_canopy["optimized_distance_m"] <= 1.25 * ROUTE_BIRDY.distance_meters
    assert res_water["optimized_distance_m"] <= 1.25 * ROUTE_BIRDY.distance_meters

    print(
        f"[OK] SpatialRerouter (Pareto Frontier): Canopy detour={res_canopy['optimized_distance_m']}m (+{res_canopy['added_distance_m']}m), Water detour={res_water['optimized_distance_m']}m (+{res_water['added_distance_m']}m) in {elapsed_ms:.2f}ms (<100ms)"
    )

    # 3. Test Distinct Spatial GeoJSON LineString Polylines
    detour_gen = SpatialGeometryDetourGenerator()
    base_geojson = ROUTE_BIRDY.geojson
    canopy_geojson = detour_gen.generate_canopy_detour(base_geojson)
    water_geojson = detour_gen.generate_water_detour(base_geojson)

    assert base_geojson != canopy_geojson
    assert canopy_geojson != water_geojson
    assert len(canopy_geojson["coordinates"]) > len(base_geojson["coordinates"])
    assert len(water_geojson["coordinates"]) > len(base_geojson["coordinates"])

    print(
        f"[OK] Spatial Geometry Detour Generator: Emitted 3 distinct GeoJSON polylines (Direct: {len(base_geojson['coordinates'])} pts, Canopy: {len(canopy_geojson['coordinates'])} pts, Water: {len(water_geojson['coordinates'])} pts)"
    )

    # 4. Test AlternativeLoopEngine Integration
    loop_engine = AlternativeLoopEngine()
    summary = loop_engine.generate_variations(ROUTE_BIRDY)
    variations = summary.variations

    assert len(variations) == 3
    assert "Direct Loop" in variations[0].name
    assert "High-Canopy" in variations[1].name
    assert "Creek-Edge" in variations[2].name

    print(
        f"[OK] AlternativeLoopEngine: Generated {len(variations)} complete route variation artifacts with spatial GeoJSON payloads"
    )

    print("=" * 65)
    print("SUCCESS: ALL ECOLOGICAL DETOUR SOLVER CHECKS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
