"""Astronomical Solar Elevation Angle Calculator."""

import math
from datetime import datetime, timezone


def calculate_sun_altitude_degrees(lat: float, lon: float, dt: datetime | None = None) -> float:
    """Calculate real-time astronomical solar elevation angle in degrees for a coordinate and timestamp."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Day of year N (1..365)
    day_of_year = dt.timetuple().tm_yday

    # Solar declination angle delta (radians)
    declination_rad = math.radians(
        23.45 * math.sin(math.radians((360.0 / 365.0) * (day_of_year - 81)))
    )

    # Universal Time in hours
    utc_hours = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)

    # Solar hour angle H (radians) based on longitude
    solar_time_hours = (utc_hours + (lon / 15.0)) % 24.0
    hour_angle_rad = math.radians(15.0 * (solar_time_hours - 12.0))

    # Convert latitude to radians
    lat_rad = math.radians(lat)

    # Solar elevation angle alpha_sun (radians)
    sin_elevation = math.sin(lat_rad) * math.sin(declination_rad) + math.cos(lat_rad) * math.cos(
        declination_rad
    ) * math.cos(hour_angle_rad)

    # Clamp sin_elevation to [-1.0, 1.0] to prevent domain errors
    clamped_sin = max(-1.0, min(1.0, sin_elevation))
    elevation_deg = math.degrees(math.asin(clamped_sin))

    return round(elevation_deg, 1)
