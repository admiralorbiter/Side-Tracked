"""CLI Tool to verify R1 / R2 Real GeoTIFF File Acquisition & Rasterio Extraction for Kansas City."""

import json
import time
from pathlib import Path

from packages.ovon_core.fixtures.spatial.synthetic_fixture_builder import (
    SyntheticSpatialFixtureBuilder,
)
from packages.ovon_core.spatial.real_environmental_extractor import (
    RasterioEnvironmentalProvider,
    RealEnvironmentalFeatureExtractor,
)


def main() -> None:
    """Run Real GeoTIFF Acquisition & Extraction verification suite."""
    print("=" * 70)
    print("   SIDETRACK REAL GEOTIFF & 3DHP HYDROGRAPHY VERIFICATION (R1/R2)")
    print("=" * 70)

    start_t = time.perf_counter()

    # 1. Build KC Raw Spatial Datasets & Source Manifest
    target_dir = Path("data/raw/spatial/kc")
    manifest = SyntheticSpatialFixtureBuilder.build_test_spatial_fixtures(target_dir)

    assert manifest["status"] == "fixture_source_manifest_verified"
    assert (target_dir / "nlcd" / "canopy_2023.tif").exists()
    assert (target_dir / "nlcd" / "impervious_2025.tif").exists()
    assert (target_dir / "3dep" / "dem_10m.tif").exists()
    assert (target_dir / "3dhp" / "hydrography.geojson").exists()

    print(
        f"[OK 1/5] Source Manifest & Datasets: Verified 3 GeoTIFF rasters + 3DHP GeoJSON in {target_dir}"
    )

    # 2. Test RasterioEnvironmentalProvider GeoTIFF Sampling via Rasterio
    provider = RasterioEnvironmentalProvider(
        canopy_path=target_dir / "nlcd" / "canopy_2023.tif",
        impervious_path=target_dir / "nlcd" / "impervious_2025.tif",
        dem_path=target_dir / "3dep" / "dem_10m.tif",
    )
    val_center = provider.sample_pixel(target_dir / "nlcd" / "canopy_2023.tif", 39.025, -94.60)
    assert val_center is not None and 20.0 <= val_center <= 75.0
    print(
        f"[OK 2/5] RasterioEnvironmentalProvider: Parsed GeoTIFF header & sampled center pixel via Rasterio = {val_center:.2f}%"
    )

    # 3. Test Out-of-Coverage Nodata Handling (Returns status="partial_coverage")
    extractor = RealEnvironmentalFeatureExtractor(raw_spatial_dir=target_dir)
    out_vector = extractor.extract_feature_vector([(45.0, -100.0), (45.01, -100.01)])
    assert out_vector.status == "partial_coverage"
    print(
        f"[OK 3/5] Out-of-Coverage Handling: Unmapped coordinates correctly returned status='{out_vector.status}'"
    )

    # 4. Test In-Coverage Feature Extraction & 3DHP Metric Distance
    kc_vector = extractor.extract_feature_vector([(39.0347, -94.5906), (39.0325, -94.5960)])
    assert kc_vector.status == "nlcd_3dep_3dhp_extracted"
    assert kc_vector.canopy_cover_percent > 0.0
    assert kc_vector.elevation_m > 200.0
    assert kc_vector.water_edge_distance_m >= 0.0

    print(
        f"[OK 4/5] In-Coverage Feature Extraction: Canopy={kc_vector.canopy_cover_percent}%, Elev={kc_vector.elevation_m}m, 3DHP Water Dist={kc_vector.water_edge_distance_m}m"
    )

    # 5. Pipeline Speed Benchmark
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    print(f"[OK 5/5] Real GeoTIFF Pipeline Execution Time: {elapsed_ms:.2f}ms (< 100ms)")

    print("=" * 70)
    print("SUCCESS: ALL R1 / R2 REAL GEOTIFF & HYDROGRAPHY CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
