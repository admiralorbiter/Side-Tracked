import math
from dataclasses import dataclass

import h3

from packages.ovon_core.domain.errors import InvalidCoordinateError


@dataclass(frozen=True, slots=True)
class Coordinate:
    """Immutable WGS84 Geographic Coordinate (latitude, longitude)."""

    latitude: float
    longitude: float
    allow_zero: bool = False

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise InvalidCoordinateError(
                f"Latitude {self.latitude} must be between -90.0 and 90.0."
            )
        if not (-180.0 <= self.longitude <= 180.0):
            raise InvalidCoordinateError(
                f"Longitude {self.longitude} must be between -180.0 and 180.0."
            )
        if not self.allow_zero and self.latitude == 0.0 and self.longitude == 0.0:
            raise InvalidCoordinateError(
                "Coordinate cannot default to (0.0, 0.0) without explicit allow_zero=True."
            )

    def haversine_distance_meters(self, other: "Coordinate") -> float:
        """Calculate great-circle distance to another coordinate in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(self.latitude)
        phi2 = math.radians(other.latitude)
        delta_phi = math.radians(other.latitude - self.latitude)
        delta_lambda = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def to_tuple(self) -> tuple[float, float]:
        return (self.latitude, self.longitude)


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Immutable spatial bounding box for candidate search regions."""

    min_latitude: float
    min_longitude: float
    max_latitude: float
    max_longitude: float

    def __post_init__(self) -> None:
        if self.min_latitude > self.max_latitude:
            raise InvalidCoordinateError(
                f"min_latitude ({self.min_latitude}) cannot exceed max_latitude ({self.max_latitude})."
            )
        if self.min_longitude > self.max_longitude:
            raise InvalidCoordinateError(
                f"min_longitude ({self.min_longitude}) cannot exceed max_longitude ({self.max_longitude})."
            )

    def contains(self, coord: Coordinate) -> bool:
        """Return True if the coordinate is within this bounding box."""
        return (
            self.min_latitude <= coord.latitude <= self.max_latitude
            and self.min_longitude <= coord.longitude <= self.max_longitude
        )


@dataclass(frozen=True, slots=True)
class SpatialCellId:
    """Immutable spatial grid cell identifier supporting authentic H3 resolution indexing."""

    resolution: int
    cell_index: str
    grid_version: str = "h3_v1"

    def __post_init__(self) -> None:
        if not (0 <= self.resolution <= 15):
            raise InvalidCoordinateError("H3 resolution must be between 0 and 15.")
        if not self.cell_index.strip():
            raise InvalidCoordinateError("cell_index cannot be empty.")
        if not h3.is_valid_cell(self.cell_index):
            raise InvalidCoordinateError(
                f"'{self.cell_index}' is not a valid H3 spatial index string."
            )
        actual_res = h3.get_resolution(self.cell_index)
        if actual_res != self.resolution:
            raise InvalidCoordinateError(
                f"Declared resolution {self.resolution} does not match H3 cell resolution {actual_res} for '{self.cell_index}'."
            )

    @classmethod
    def from_h3_string(cls, h3_str: str) -> "SpatialCellId":
        """Parse 'h3_res8:882685623ffffff' or raw '882685623ffffff' into SpatialCellId."""
        if ":" in h3_str:
            parts = h3_str.split(":", 1)
            prefix, idx = parts[0], parts[1]
            res = (
                int(prefix.replace("h3_res", "")) if "h3_res" in prefix else h3.get_resolution(idx)
            )
            return cls(resolution=res, cell_index=idx)
        res = h3.get_resolution(h3_str) if h3.is_valid_cell(h3_str) else 8
        return cls(resolution=res, cell_index=h3_str)

    def to_string(self) -> str:
        return f"h3_res{self.resolution}:{self.cell_index}"
