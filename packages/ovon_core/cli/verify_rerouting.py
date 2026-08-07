"""CLI Tool to verify Spatial Optimization and Dynamic Rerouting Engine."""

import time

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.routing.alternative_loops import AlternativeLoopEngine
from packages.ovon_core.routing.opportunity_cost import OpportunityCostCalculator
from packages.ovon_core.routing.spatial_rerouter import SpatialRerouter


def main() -> None:
    """Run Spatial Optimization & Dynamic Rerouting verification suite."""
    print("=" * 60)
    print("   SIDETRACK SPATIAL REROUTING OPTIMIZATION VERIFICATION")
    print("=" * 60)

    # 1. Test Opportunity Cost Calculator
    calc = OpportunityCostCalculator(gamma=1.5)
    vec_high = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(75.0, 5.0, 40.0, 270.0, 3.0),
    )
    edge_high = calc.calculate_edge_opportunity(100.0, vec_high)
    assert edge_high.opportunity_score >= 0.70
    assert edge_high.modified_weight < edge_high.length_meters
    print(
        f"[OK] Opportunity Edge Weighting: 100m edge with high canopy/water -> Modified weight = {edge_high.modified_weight}m (R={edge_high.opportunity_score})"
    )

    # 2. Test Bi-Criterion Spatial Rerouter Engine
    rerouter = SpatialRerouter()
    metrics = rerouter.optimize_route_corridor(ROUTE_BIRDY, preference="canopy")
    assert metrics["added_duration_min"] > 0
    assert metrics["opportunity_boost_percent"] == 32.0
    print(
        f"[OK] Bi-Criterion Spatial Rerouter: High-Canopy Detour adds +{metrics['added_duration_min']}m for +{metrics['opportunity_boost_percent']}% opportunity boost"
    )

    # 3. Test Alternative Loop Engine & Execution Speed (< 300ms)
    start_t = time.perf_counter()
    engine = AlternativeLoopEngine()
    summary = engine.generate_variations(ROUTE_BIRDY)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    assert len(summary.variations) == 3
    assert summary.variations[0].is_baseline
    assert not summary.variations[1].is_baseline

    geo_base = summary.variations[0].geojson_geometry["coordinates"]
    geo_canopy = summary.variations[1].geojson_geometry["coordinates"]
    geo_water = summary.variations[2].geojson_geometry["coordinates"]

    assert len(geo_canopy) > len(geo_base)
    assert len(geo_water) > len(geo_base)
    assert geo_canopy != geo_water
    assert elapsed_ms < 300.0

    print(
        f"[OK] AlternativeLoopEngine Verified: Generated {len(summary.variations)} distinct Pareto detour geometries ({len(geo_base)} pts -> {len(geo_canopy)} pts -> {len(geo_water)} pts) in {elapsed_ms:.2f}ms (< 300ms threshold)"
    )

    print("=" * 60)
    print("SUCCESS: ALL SPATIAL OPTIMIZATION & REROUTING CHECKS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
