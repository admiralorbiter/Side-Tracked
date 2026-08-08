"""Unit tests for Real Environmental Data Pipeline (NLCD 2025, 3DEP 10m DEM, 3DHP Hydrography)."""

from packages.ovon_core.spatial.corridor_sampler import CorridorSampler
from packages.ovon_core.spatial.real_environmental_extractor import (
    RealEnvironmentalFeatureExtractor,
)


def test_corridor_sampler():
    sampler = CorridorSampler(step_meters=25.0)
    coords = [(39.0347, -94.5906), (39.0325, -94.5960)]

    sampled = sampler.sample_corridor_points(coords)
    assert len(sampled) >= len(coords)
    assert sampled[0] == coords[0]


def test_real_environmental_feature_extractor():
    extractor = RealEnvironmentalFeatureExtractor()
    coords = [(39.0347, -94.5906), (39.0325, -94.5960)]

    vec = extractor.extract_feature_vector(coords)
    assert vec.status == "nlcd_3dep_3dhp_extracted"
    assert 0.0 <= vec.canopy_cover_percent <= 100.0
    assert 0.0 <= vec.impervious_surface_percent <= 100.0
    assert vec.water_edge_distance_m > 0.0
    assert vec.elevation_m > 0.0
