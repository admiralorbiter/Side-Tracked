"""Unit tests for Environmental Feature Vector models and extractor."""

import pytest

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
    create_default_environmental_vector,
)
from packages.ovon_core.domain.habitat import HabitatType
from packages.ovon_core.spatial.environmental_extractor import EnvironmentalFeatureExtractor


def test_environmental_schema_properties():
    assert SIDETRACK_ENV_SCHEMA_V1.schema_id == "sidetrack_env_v1"
    assert "canopy_cover_percent" in SIDETRACK_ENV_SCHEMA_V1.feature_names
    assert "water_edge_distance_m" in SIDETRACK_ENV_SCHEMA_V1.feature_names


def test_environmental_feature_vector_getters():
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(60.0, 10.0, 150.0, 270.0, 4.5),
        status="ok",
    )
    assert vec.canopy_cover_percent == 60.0
    assert vec.impervious_surface_percent == 10.0
    assert vec.water_edge_distance_m == 150.0
    assert vec.elevation_m == 270.0
    assert vec.slope_gradient_percent == 4.5
    assert vec.get_feature("canopy_cover_percent") == 60.0


def test_environmental_feature_vector_derived_habitat():
    water_vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(20.0, 5.0, 30.0, 230.0, 1.0),
    )
    assert water_vec.derive_habitat_type() == HabitatType.POND_WATER_EDGE

    canopy_vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(65.0, 5.0, 300.0, 280.0, 5.0),
    )
    assert canopy_vec.derive_habitat_type() == HabitatType.MATURE_CANOPY

    orchard_vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(25.0, 15.0, 200.0, 260.0, 2.0),
    )
    assert orchard_vec.derive_habitat_type() == HabitatType.ORCHARD_EDGE


def test_environmental_extractor():
    extractor = EnvironmentalFeatureExtractor()

    # Empty coordinates fallback
    fallback = extractor.extract_for_coordinates([])
    assert fallback.status == "degraded_fallback"

    # Kansas City coordinate extraction
    vec = extractor.extract_for_coordinates([(39.031, -94.591)])
    assert vec.status == "ok"
    assert len(vec.values) == 5
