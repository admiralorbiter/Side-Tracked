import h3

from packages.ovon_core.domain.spatial import (
    BoundingBox,
    Coordinate,
    InvalidCoordinateError,
    SpatialCellId,
)

# Standard US Bounding Box boundary for national geographic validation
US_NATIONAL_BOUNDS = BoundingBox(
    min_latitude=17.0,
    min_longitude=-180.0,
    max_latitude=72.0,
    max_longitude=-65.0,
)

# Greater Kansas City Pilot Region Bounding Box
KC_PILOT_BOUNDS = BoundingBox(
    min_latitude=38.70,
    min_longitude=-94.90,
    max_latitude=39.35,
    max_longitude=-94.35,
)


def lat_lng_to_h3_cell(coord: Coordinate, resolution: int = 8) -> SpatialCellId:
    """Convert WGS84 Coordinate into an authentic H3 SpatialCellId using h3-py."""
    if not (0 <= resolution <= 15):
        raise InvalidCoordinateError(f"H3 resolution must be between 0 and 15, got {resolution}")

    h3_index_str = h3.latlng_to_cell(coord.latitude, coord.longitude, resolution)
    return SpatialCellId(resolution=resolution, cell_index=h3_index_str)


def is_within_us_bounds(coord: Coordinate) -> bool:
    """Return True if coordinate lies within US national bounding region."""
    return US_NATIONAL_BOUNDS.contains(coord)


def is_within_kc_pilot_bounds(coord: Coordinate) -> bool:
    """Return True if coordinate lies within Greater Kansas City Pilot bounding region."""
    return KC_PILOT_BOUNDS.contains(coord)
