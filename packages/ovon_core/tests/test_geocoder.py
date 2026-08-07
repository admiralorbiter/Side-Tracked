"""Unit and integration tests for Nominatim geocoding and park presets (Sprint 5)."""

from packages.ovon_core.domain import Coordinate
from packages.ovon_core.spatial import (
    ENGLISH_LANDING_PARK,
    LOOSE_PARK,
    MILL_CREEK_PARK,
    OVERLAND_PARK_ARBORETUM,
    PILOT_PARK_PRESETS,
    SWOPE_PARK,
    GeocodeResult,
    NominatimGeocoderProvider,
    is_within_us_bounds,
)


def test_public_park_presets_catalog():
    assert len(PILOT_PARK_PRESETS) == 5
    assert LOOSE_PARK.id == "loose-park"
    assert MILL_CREEK_PARK.id == "mill-creek"
    assert SWOPE_PARK.id == "swope-park"
    assert OVERLAND_PARK_ARBORETUM.id == "op-arboretum"
    assert ENGLISH_LANDING_PARK.id == "english-landing"

    for p in PILOT_PARK_PRESETS:
        assert is_within_us_bounds(p.coordinate)
        assert "h3_res8" in p.cell.to_string()


def test_nominatim_geocoder_cache_write_and_read(tmp_path):
    geocoder = NominatimGeocoderProvider(cache_dir=tmp_path)
    coord = Coordinate(39.0347, -94.5906)

    # Populate cache directly to avoid external network calls during automated test
    cache_key = "geocode_loose_park"
    fake_data = {
        "lat": "39.0347",
        "lon": "-94.5906",
        "display_name": "Jacob L. Loose Park, Kansas City, Jackson County, Missouri, USA",
        "address": {"park": "Jacob L. Loose Park", "city": "Kansas City", "state": "Missouri"},
    }
    geocoder._write_cache(cache_key, fake_data)

    res = geocoder.geocode("loose_park")
    assert isinstance(res, GeocodeResult)
    assert res.coordinate.latitude == 39.0347
    assert res.coordinate.longitude == -94.5906
    assert "Loose Park" in res.display_name
    assert "h3_res8" in res.cell.to_string()


def test_nominatim_geocoder_invalid_bounds_rejected(tmp_path):
    geocoder = NominatimGeocoderProvider(cache_dir=tmp_path)
    cache_key = "geocode_invalid_ocean"
    fake_data = {
        "lat": "10.0",
        "lon": "10.0",
        "display_name": "Offshore Atlantic Ocean",
    }
    geocoder._write_cache(cache_key, fake_data)

    res = geocoder.geocode("invalid_ocean")
    assert res is None
