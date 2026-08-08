"""Unit tests for Real GeoTIFF File Acquisition & 3DHP Hydrography Extraction (R1/R2)."""

from packages.ovon_core.spatial.geotiff_fixture_builder import build_kc_spatial_datasets
from packages.ovon_core.spatial.real_environmental_extractor import (
    RealEnvironmentalFeatureExtractor,
    RealGeoTIFFRasterDataset,
)


def test_build_kc_spatial_datasets(tmp_path):
    manifest = build_kc_spatial_datasets(tmp_path)
    assert manifest["status"] == "raw_source_manifest_verified"
    assert (tmp_path / "nlcd" / "canopy_2023.tif").exists()
    assert (tmp_path / "nlcd" / "impervious_2025.tif").exists()
    assert (tmp_path / "3dep" / "dem_10m.tif").exists()
    assert (tmp_path / "3dhp" / "hydrography.geojson").exists()


def test_real_geotiff_raster_dataset(tmp_path):
    build_kc_spatial_datasets(tmp_path)
    canopy_ds = RealGeoTIFFRasterDataset.open(tmp_path / "nlcd" / "canopy_2023.tif")

    assert canopy_ds.rows == 50
    assert canopy_ds.cols == 50

    val = canopy_ds.sample_pixel_value(39.025, -94.60)
    assert val is not None and 20.0 <= val <= 75.0

    out_val = canopy_ds.sample_pixel_value(10.0, 10.0)
    assert out_val is None


def test_real_environmental_extractor_geotiff(tmp_path):
    build_kc_spatial_datasets(tmp_path)
    extractor = RealEnvironmentalFeatureExtractor(raw_spatial_dir=tmp_path)

    coords = [(39.0347, -94.5906), (39.0325, -94.5960)]
    vec = extractor.extract_feature_vector(coords)

    assert vec.status == "nlcd_3dep_3dhp_extracted"
    assert vec.canopy_cover_percent > 0.0
    assert vec.elevation_m > 200.0
    assert vec.water_edge_distance_m >= 0.0
