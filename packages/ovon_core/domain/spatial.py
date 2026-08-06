from dataclasses import dataclass
import math
from packages.ovon_core.domain.errors import InvalidCoordinateError

@dataclass(frozen=True, slots=True)
class Coordinate:
    """Immutable WGS84 Geographic Coordinate (latitude, longitude)."""
    latitude: float
    longitude: float
    allow_zero: bool = False

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise InvalidCoordinateError(f"Latitude {self.latitude} must be between -90.0 and 90.0.")
        if not (-180.0 <= self.longitude <= 180.0):
            raise InvalidCoordinateError(f"Longitude {self.longitude} must be between -180.0 and 180.0.")
        if not self.allow_zero and self.latitude == 0.0 and self.longitude == 0.0:
            raise InvalidCoordinateError("Coordinate cannot default to (0.0, 0.0) without explicit allow_zero=True.")

    def haversine_distance_meters(self, other: "Coordinate") -> float:
        """Calculate great-circle distance to another coordinate in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(self.latitude)
        phi2 = math.radians(other.latitude)
        delta_phi = math.radians(other.latitude - self.latitude)
        delta_lambda = math.radians(other.longitude - self.longitude)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
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
            raise InvalidCoordinateError(f"min_latitude ({self.min_latitude}) cannot exceed max_latitude ({self.max_latitude}).")
        if self.min_longitude > self.max_longitude:
            raise InvalidCoordinateError(f"min_longitude ({self.min_longitude}) cannot exceed max_longitude ({self.max_longitude}).")

    def contains(self, coord: Coordinate) -> bool:
        """Return True if the coordinate is within this bounding box."""
        return (self.min_latitude <= coord.latitude <= self.max_latitude and
                self.min_longitude <= coord.longitude <= self.max_longitude)
