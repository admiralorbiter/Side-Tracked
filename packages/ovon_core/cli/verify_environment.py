"""CLI tool to verify Environmental Feature Backbone models, schemas, and spatial extractors."""

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    create_default_environmental_vector,
)
from packages.ovon_core.domain.habitat import HabitatType
from packages.ovon_core.spatial.environmental_extractor import EnvironmentalFeatureExtractor


def main() -> None:
    """Run environmental feature backbone verification suite."""
    print("=" * 60)
    print("   SIDETRACK ENVIRONMENTAL FEATURE BACKBONE VERIFICATION")
    print("=" * 60)

    # 1. Verify Environmental Schema
    assert SIDETRACK_ENV_SCHEMA_V1.schema_id == "sidetrack_env_v1"
    assert len(SIDETRACK_ENV_SCHEMA_V1.feature_names) == 5
    print(f"[OK] Schema Verified: {SIDETRACK_ENV_SCHEMA_V1.schema_id}")
    print(f"     Features: {', '.join(SIDETRACK_ENV_SCHEMA_V1.feature_names)}")

    extractor = EnvironmentalFeatureExtractor()

    # 2. Test English Landing Water Edge
    water_coords = [(39.186, -94.708)]
    water_vec = extractor.extract_for_coordinates(water_coords)
    assert water_vec.status == "ok"
    assert water_vec.water_edge_distance_m <= 75.0
    assert water_vec.derive_habitat_type() == HabitatType.POND_WATER_EDGE
    print(
        f"[OK] Water Edge Extraction: Distance={water_vec.water_edge_distance_m:.1f}m -> {water_vec.derive_habitat_type().value}"
    )

    # 3. Test Swope Park Forest Canopy
    forest_coords = [(39.004, -94.530)]
    forest_vec = extractor.extract_for_coordinates(forest_coords)
    assert forest_vec.status == "ok"
    assert forest_vec.canopy_cover_percent >= 45.0
    assert forest_vec.derive_habitat_type() == HabitatType.MATURE_CANOPY
    print(
        f"[OK] Forest Canopy Extraction: Canopy={forest_vec.canopy_cover_percent:.1f}% -> {forest_vec.derive_habitat_type().value}"
    )

    # 4. Test Loose Park Parkland
    park_coords = [(39.031, -94.591)]
    park_vec = extractor.extract_for_coordinates(park_coords)
    assert park_vec.status == "ok"
    assert park_vec.derive_habitat_type() in (
        HabitatType.POND_WATER_EDGE,
        HabitatType.OPEN_PARKLAND,
    )
    print(
        f"[OK] Park Extraction: WaterDist={park_vec.water_edge_distance_m:.1f}m, Canopy={park_vec.canopy_cover_percent:.1f}% -> {park_vec.derive_habitat_type().value}"
    )

    # 5. Test Degraded Fallback Vector
    fallback_vec = create_default_environmental_vector()
    assert fallback_vec.status == "degraded_fallback"
    assert len(fallback_vec.values) == 5
    print(f"[OK] Degraded Fallback Vector Verified: Status='{fallback_vec.status}'")

    print("=" * 60)
    print("SUCCESS: ALL ENVIRONMENTAL FEATURE BACKBONE CHECKS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
