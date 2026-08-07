"""Spatial indexing, geocoding, and GIS helpers for OVON Core."""

from packages.ovon_core.spatial.geocoder import (
    GeocodeResult,
    GeocoderProvider,
    NominatimGeocoderProvider,
)
from packages.ovon_core.spatial.h3_indexer import (
    KC_PILOT_BOUNDS,
    US_NATIONAL_BOUNDS,
    is_within_kc_pilot_bounds,
    is_within_us_bounds,
    lat_lng_to_h3_cell,
)
from packages.ovon_core.spatial.presets import (
    ENGLISH_LANDING_PARK,
    LOOSE_PARK,
    MILL_CREEK_PARK,
    OVERLAND_PARK_ARBORETUM,
    PILOT_PARK_PRESETS,
    PRESETS_BY_ID,
    SWOPE_PARK,
    PublicParkPreset,
)

__all__ = [
    "US_NATIONAL_BOUNDS",
    "KC_PILOT_BOUNDS",
    "lat_lng_to_h3_cell",
    "is_within_us_bounds",
    "is_within_kc_pilot_bounds",
    "GeocoderProvider",
    "NominatimGeocoderProvider",
    "GeocodeResult",
    "PublicParkPreset",
    "PILOT_PARK_PRESETS",
    "PRESETS_BY_ID",
    "LOOSE_PARK",
    "MILL_CREEK_PARK",
    "SWOPE_PARK",
    "OVERLAND_PARK_ARBORETUM",
    "ENGLISH_LANDING_PARK",
]
