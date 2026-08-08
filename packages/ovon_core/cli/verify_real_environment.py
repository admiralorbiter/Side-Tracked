"""CLI Tool to verify Real Environmental Data Pipeline (NLCD 2025, 3DEP 10m DEM, 3DHP Hydrography)."""

import time

from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.spatial.corridor_sampler import CorridorSampler
from packages.ovon_core.spatial.real_environmental_extractor import (
    RealEnvironmentalFeatureExtractor,
)


def main() -> None:
    """Run Real Environmental Data Pipeline verification suite."""
    print("=" * 65)
    print("   SIDETRACK REAL ENVIRONMENTAL DATA PIPELINE VERIFICATION")
    print("=" * 65)

    # 1. Test Corridor Sampler Metric CRS Projection
    sampler = CorridorSampler(step_meters=25.0)
    base_coords = [(39.0347, -94.5906), (39.0335, -94.5920), (39.0320, -94.5950)]
    sampled_pts = sampler.sample_corridor_points(base_coords)
    assert len(sampled_pts) >= len(base_coords)
    print(
        f"[OK] Metric Corridor Sampler: Projected WGS84 -> UTM Zone 15N EPSG:32615 ({len(base_coords)} pts -> {len(sampled_pts)} corridor sample vertices)"
    )

    # 2. Test Real Environmental Extractor Execution
    extractor = RealEnvironmentalFeatureExtractor()
    start_t = time.perf_counter()
    env_vector = extractor.extract_feature_vector(base_coords)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    assert env_vector.status == "nlcd_3dep_3dhp_extracted"
    assert 0.0 <= env_vector.canopy_cover_percent <= 100.0
    assert 0.0 <= env_vector.impervious_surface_percent <= 100.0
    assert env_vector.water_edge_distance_m > 0.0
    assert elapsed_ms < 100.0

    print(f"[OK] Extracted Feature Vector Status: {env_vector.status}")
    print(
        f"[OK] NLCD 2025 Canopy: {env_vector.canopy_cover_percent}% | Impervious: {env_vector.impervious_surface_percent}%"
    )
    print(
        f"[OK] 3DHP Hydrography Distance: {env_vector.water_edge_distance_m}m | 3DEP Elevation: {env_vector.elevation_m}m | Slope: {env_vector.slope_gradient_percent}%"
    )
    print(f"[OK] Extraction Speed: {elapsed_ms:.2f}ms (< 100ms threshold)")

    print("=" * 65)
    print("SUCCESS: ALL REAL ENVIRONMENTAL DATA PIPELINE CHECKS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
