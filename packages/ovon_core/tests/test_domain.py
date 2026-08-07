import pytest

from packages.ovon_core.domain import (
    BoundingBox,
    Coordinate,
    FieldCue,
    InvalidCoordinateError,
    InvalidTimeBudgetError,
    JourneyIntent,
    LicenseType,
    LoopRequest,
    MediaAsset,
    MediaType,
    MissingAttributionError,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
)


# 1. Spatial Tests
def test_coordinate_valid():
    coord = Coordinate(39.0347, -94.5906)
    assert coord.latitude == 39.0347
    assert coord.longitude == -94.5906
    assert coord.to_tuple() == (39.0347, -94.5906)


def test_coordinate_disallow_zero_by_default():
    with pytest.raises(InvalidCoordinateError, match="Coordinate cannot default to"):
        Coordinate(0.0, 0.0)


def test_coordinate_allow_zero_explicit():
    coord = Coordinate(0.0, 0.0, allow_zero=True)
    assert coord.latitude == 0.0


def test_coordinate_bounds_validation():
    with pytest.raises(InvalidCoordinateError):
        Coordinate(95.0, -94.0)
    with pytest.raises(InvalidCoordinateError):
        Coordinate(39.0, -185.0)


def test_haversine_distance():
    loose_park = Coordinate(39.0347, -94.5906)
    swope_park = Coordinate(38.9950, -94.5292)
    dist = loose_park.haversine_distance_meters(swope_park)
    # Distance between Loose Park & Swope Park is approx 6.8 km (6800m)
    assert 6000.0 < dist < 8000.0


def test_bounding_box():
    bbox = BoundingBox(38.9, -94.6, 39.1, -94.4)
    inside = Coordinate(39.0347, -94.5906)
    outside = Coordinate(40.0, -94.5)
    assert bbox.contains(inside) is True
    assert bbox.contains(outside) is False


def test_bounding_box_invalid():
    with pytest.raises(InvalidCoordinateError):
        BoundingBox(39.5, -94.6, 39.1, -94.4)


def test_spatial_cell_id_h3():
    from packages.ovon_core.domain import SpatialCellId
    from packages.ovon_core.spatial import is_within_kc_pilot_bounds, lat_lng_to_h3_cell

    # Authentic Uber H3 Res 8 index for Loose Park, Kansas City (39.0347, -94.5906)
    kc_coord = Coordinate(39.0347, -94.5906)
    kc_cell = lat_lng_to_h3_cell(kc_coord, resolution=8)

    assert kc_cell.resolution == 8
    assert kc_cell.to_string().startswith("h3_res8:")

    parsed = SpatialCellId.from_h3_string(kc_cell.to_string())
    assert parsed.cell_index == kc_cell.cell_index
    assert parsed.resolution == 8

    # Invalid H3 index string raises InvalidCoordinateError
    with pytest.raises(InvalidCoordinateError):
        SpatialCellId.from_h3_string("h3_res8:invalid_hex_string")

    # Mismatched resolution raises InvalidCoordinateError
    with pytest.raises(InvalidCoordinateError, match="Declared resolution"):
        SpatialCellId(resolution=7, cell_index=kc_cell.cell_index)

    assert is_within_kc_pilot_bounds(kc_coord) is True


# 2. Taxonomy Tests
def test_taxon_ref_factory():
    taxon = TaxonRef.create(
        common_name="Red-headed Woodpecker",
        scientific_name="Melanerpes erythrocephalus",
        ebird_code="rehwoo",
    )
    assert taxon.taxon_id == "species:ebird:rehwoo"
    assert taxon.common_name == "Red-headed Woodpecker"
    assert taxon.ebird_code == "rehwoo"
    assert taxon.taxonomy_version == "Clements-2025"


def test_taxon_ref_empty_validation():
    with pytest.raises(ValueError):
        TaxonRef(taxon_id="", common_name="Bird", scientific_name="Aves", ebird_code="bird")


# 3. Request Tests
def test_loop_request_valid():
    origin = Coordinate(39.0347, -94.5906)
    req1 = LoopRequest(origin=origin, origin_name="Loose Park", duration_minutes=45)
    req2 = LoopRequest(origin=origin, origin_name="Loose Park", duration_minutes=45)
    assert req1.duration_minutes == 45
    assert req1.intent == JourneyIntent.LOOP_FROM_HERE
    assert req1 == req2


def test_loop_request_invalid_duration():
    origin = Coordinate(39.0347, -94.5906)
    with pytest.raises(InvalidTimeBudgetError):
        LoopRequest(origin=origin, origin_name="Loose Park", duration_minutes=25)


# 4. Media & Licensing Tests
def test_media_asset_valid():
    taxon = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")
    asset = MediaAsset(
        asset_id="asset-123",
        taxon_ref=taxon,
        media_type=MediaType.PHOTO,
        url="https://example.com/jay.jpg",
        creator="John Doe",
        license=LicenseType.CC_BY_4_0,
        attribution_text="John Doe (CC BY 4.0)",
    )
    assert asset.asset_id == "asset-123"
    assert asset.license == LicenseType.CC_BY_4_0


def test_media_asset_missing_attribution_raises():
    taxon = TaxonRef.create("Blue Jay", "Cyanocitta cristata", "blujay")
    with pytest.raises(MissingAttributionError):
        MediaAsset(
            asset_id="asset-123",
            taxon_ref=taxon,
            media_type=MediaType.PHOTO,
            url="https://example.com/jay.jpg",
            creator="",  # Empty creator
            license=LicenseType.CC_BY_4_0,
            attribution_text="John Doe (CC BY 4.0)",
        )


# 5. Route Tests
def test_route_option_valid():
    taxon = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    cue = FieldCue(taxon, "Look in low bushes", "Listen for sharp metallic chip")
    segment = RouteSegment(
        index=1,
        name="Park Perimeter",
        habitat_name="Woodland Edge",
        distance_meters=2200.0,
        duration_minutes=45.0,
        focal_species=(taxon,),
        field_cue=cue,
    )
    route = RouteOption(
        id="route-birdy-1",
        persona=RoutePersona.BIRDY,
        name="The Birdy One",
        tagline="Best nature route",
        duration_minutes=45,
        distance_meters=2200.0,
        badge_label="Best bird opportunity",
        tradeoff_description="Adds 400m dirt trail",
        segments=(segment,),
    )
    assert route.formatted_distance == "2.2 km"
    assert route.formatted_duration == "45 min"
    assert segment.formatted_distance == "2.2 km"


def test_route_segment_cue_mismatch_raises():
    cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    robin = TaxonRef.create("American Robin", "Turdus migratorius", "amerob")
    robin_cue = FieldCue(robin, "Look on lawns", "Listen for cheery song")

    with pytest.raises(ValueError, match="must belong to segment focal_species"):
        RouteSegment(
            index=1,
            name="Pond Edge",
            habitat_name="Grassland",
            distance_meters=800.0,
            duration_minutes=15.0,
            focal_species=(cardinal,),
            field_cue=robin_cue,
        )


def test_kc_30_species_catalog_fixtures():
    from packages.ovon_core.fixtures.kc_species_fixtures import (
        ALL_KC_TAXA,
        KC_FIELD_CUE_PROFILES,
        KC_FIELD_CUES,
    )

    assert len(ALL_KC_TAXA) == 30
    assert len(KC_FIELD_CUES) == 30
    assert len(KC_FIELD_CUE_PROFILES) == 30

    for taxon in ALL_KC_TAXA:
        assert taxon.ebird_code in KC_FIELD_CUES
        cue = KC_FIELD_CUES[taxon.ebird_code]
        assert cue.taxon_ref == taxon
        profile = KC_FIELD_CUE_PROFILES[taxon.ebird_code]
        assert profile.taxon_id == taxon.taxon_id

