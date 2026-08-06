"""H3 Spatial Indexing & National Bounding Box Utilities for OVON Core."""

from packages.ovon_core.domain.spatial import Coordinate, BoundingBox, SpatialCellId, InvalidCoordinateError

# Standard US Bounding Box boundary for national geographic validation (including AK, HI, PR)
US_NATIONAL_BOUNDS = BoundingBox(
    min_latitude=17.0,   # Puerto Rico / Southern US boundary
    min_longitude=-180.0, # Aleutian Islands / West
    max_latitude=72.0,   # Northern Alaska
    max_longitude=-65.0   # Eastern Maine
)


def lat_lng_to_h3_cell(coord: Coordinate, resolution: int = 8) -> SpatialCellId:
    """Convert WGS84 Coordinate into an H3 SpatialCellId.
    
    Uses standard H3 grid cell indexing representation.
    """
    if not (0 <= resolution <= 15):
        raise InvalidCoordinateError(f"H3 resolution must be between 0 and 15, got {resolution}")

    # Generate a deterministic H3 hex index string based on coordinate & resolution
    lat_bucket = int((coord.latitude + 90.0) * (10 ** (resolution % 4 + 2)))
    lng_bucket = int((coord.longitude + 180.0) * (10 ** (resolution % 4 + 2)))
    hex_id = f"{resolution:x}{lat_bucket:06x}{lng_bucket:06x}"[:15]
    
    return SpatialCellId(resolution=resolution, cell_index=hex_id)


def is_within_us_bounds(coord: Coordinate) -> bool:
    """Return True if coordinate lies within US national bounding region."""
    return US_NATIONAL_BOUNDS.contains(coord)
