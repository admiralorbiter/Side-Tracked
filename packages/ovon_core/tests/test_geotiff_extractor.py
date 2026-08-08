"""Unit tests for Real GeoTIFF File Acquisition & 3DHP Hydrography Extraction via Rasterio."""

from packages.ovon_core.fixtures.spatial.synthetic_fixture_builder import (
    SyntheticSpatialFixtureBuilder,
)
from packages.ovon_core.spatial.real_environmental_extractor import (
    RasterioEnvironmentalProvider,
    RealEnvironmentalFeatureExtractor,
)


def test_build_kc_spatial_datasets(tmp_path):
    manifest = SyntheticSpatialFixtureBuilder.build_test_spatial_fixtures(tmp_path)
    assert manifest["status"] == "fixture_source_manifest_verified"
    assert (tmp_path / "nlcd" / "canopy_2023.tif").exists()
    assert (tmp_path / "nlcd" / "impervious_2025.tif").exists()
    assert (tmp_path / "3dep" / "dem_10m.tif").exists()
    assert (tmp_path / "3dhp" / "hydrography.geojson").exists()


def test_real_geotiff_raster_dataset(tmp_path):
    SyntheticSpatialFixtureBuilder.build_test_spatial_fixtures(tmp_path)
    provider = RasterioEnvironmentalProvider(
        canopy_path=tmp_path / "nlcd" / "canopy_2023.tif",
        impervious_path=tmp_path / "nlcd" / "impervious_2025.tif",
        dem_path=tmp_path / "3dep" / "dem_10m.tif",
    )

    val = provider.sample_pixel(tmp_path / "nlcd" / "canopy_2023.tif", 39.025, -94.60)
    assert val is not None and 20.0 <= val <= 75.0

    out_val = provider.sample_pixel(tmp_path / "nlcd" / "canopy_2023.tif", 10.0, 10.0)
    assert out_val is None


def test_real_environmental_extractor_geotiff(tmp_path):
    SyntheticSpatialFixtureBuilder.build_test_spatial_fixtures(tmp_path)
    extractor = RealEnvironmentalFeatureExtractor(raw_spatial_dir=tmp_path)

    coords = [(39.0347, -94.5906), (39.0325, -94.5960)]
    vec = extractor.extract_feature_vector(coords)

    assert vec.status in ("nlcd_3dep_3dhp_extracted", "fixture_spatial_sampled")
    assert vec.canopy_cover_percent > 0.0
    assert vec.elevation_m > 200.0
    assert vec.water_edge_distance_m >= 0.0
