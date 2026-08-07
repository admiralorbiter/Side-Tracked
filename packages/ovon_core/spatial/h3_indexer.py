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


def polyline_to_h3_cells(geojson_geometry: dict | None, resolution: int = 8) -> set[SpatialCellId]:
    """Rasterize/sample GeoJSON LineString coordinates into traversed H3 spatial cells."""
    if not geojson_geometry or "coordinates" not in geojson_geometry:
        return set()

    coords = geojson_geometry.get("coordinates", [])
    if not coords:
        return set()

    cells: set[SpatialCellId] = set()

    # Process each vertex and interpolate points at ~100m step intervals along long edges
    for i in range(len(coords)):
        lon, lat = coords[i][0], coords[i][1]
        c1 = Coordinate(lat, lon)
        cells.add(lat_lng_to_h3_cell(c1, resolution=resolution))

        if i < len(coords) - 1:
            next_lon, next_lat = coords[i + 1][0], coords[i + 1][1]
            c2 = Coordinate(next_lat, next_lon)
            edge_length_m = c1.haversine_distance_meters(c2)

            # Sample intermediate points every ~100 meters
            if edge_length_m > 100.0:
                steps = int(edge_length_m // 100.0) + 1
                for step in range(1, steps):
                    frac = step / float(steps)
                    interp_lat = lat + (next_lat - lat) * frac
                    interp_lon = lon + (next_lon - lon) * frac
                    interp_c = Coordinate(interp_lat, interp_lon)
                    cells.add(lat_lng_to_h3_cell(interp_c, resolution=resolution))
            else:
                mid_c = Coordinate((lat + next_lat) / 2.0, (lon + next_lon) / 2.0)
                cells.add(lat_lng_to_h3_cell(mid_c, resolution=resolution))

    return cells


def is_within_us_bounds(coord: Coordinate) -> bool:
    """Return True if coordinate lies within US national bounding region."""
    return US_NATIONAL_BOUNDS.contains(coord)


def is_within_kc_pilot_bounds(coord: Coordinate) -> bool:
    """Return True if coordinate lies within Greater Kansas City Pilot bounding region."""
    return KC_PILOT_BOUNDS.contains(coord)
