"""Metric Spatial, Temporal, and Statistical Evidence Engine."""

import math

from packages.ovon_core.domain.spatial import Coordinate


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in meters between two lat/lon points."""
    r_earth = 6371000.0  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


def point_to_segment_distance_m(
    p_lat: float, p_lon: float, a_lat: float, a_lon: float, b_lat: float, b_lon: float
) -> float:
    """Calculate minimum metric distance from point P to line segment AB."""
    # Local Azimuthal Equidistant projection relative to P
    cos_lat = math.cos(math.radians(p_lat))
    kx = 111000.0 * cos_lat
    ky = 111000.0

    ax = (a_lon - p_lon) * kx
    ay = (a_lat - p_lat) * ky
    bx = (b_lon - p_lon) * kx
    by = (b_lat - p_lat) * ky

    # Projection vector AB
    dx = bx - ax
    dy = by - ay

    if dx == 0.0 and dy == 0.0:
        return math.sqrt(ax * ax + ay * ay)

    # Parameter t of nearest point on segment
    t = -(ax * dx + ay * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    nearest_x = ax + t * dx
    nearest_y = ay + t * dy
    return math.sqrt(nearest_x * nearest_x + nearest_y * nearest_y)


def calculate_point_to_linestring_distance(
    occurrence_coord: Coordinate, line_coords: list[tuple[float, float]]
) -> float:
    """Calculate minimum metric distance in meters from an occurrence coordinate to a LineString geometry."""
    if not line_coords:
        return 999999.0
    if len(line_coords) == 1:
        return haversine_distance_m(
            occurrence_coord.latitude,
            occurrence_coord.longitude,
            line_coords[0][0],
            line_coords[0][1],
        )

    min_dist = float("inf")
    p_lat, p_lon = occurrence_coord.latitude, occurrence_coord.longitude

    for i in range(len(line_coords) - 1):
        a_lat, a_lon = line_coords[i][0], line_coords[i][1]
        b_lat, b_lon = line_coords[i + 1][0], line_coords[i + 1][1]
        dist = point_to_segment_distance_m(p_lat, p_lon, a_lat, a_lon, b_lat, b_lon)
        if dist < min_dist:
            min_dist = dist

    return min_dist


def calculate_spatial_decay_kernel(
    distance_m: float, uncertainty_m: float | None = None, baseline_sigma_m: float = 250.0
) -> float:
    """Calculate spatial decay kernel Kd(i) with coordinate uncertainty propagation."""
    u_i = uncertainty_m if (uncertainty_m is not None and uncertainty_m > 0.0) else 0.0
    sigma_sq = (baseline_sigma_m**2) + (u_i**2)
    return math.exp(-(distance_m**2) / (2.0 * sigma_sq))


def calculate_temporal_decay_kernel(delta_days: float, half_life_days: float = 14.0) -> float:
    """Calculate temporal decay kernel Kt(i) based on days elapsed since report."""
    if delta_days < 0.0:
        delta_days = 0.0
    return math.exp(-delta_days / half_life_days)


def calculate_cyclic_week_distance(w1: int, w2: int) -> int:
    """Calculate annual cyclic week distance dT(w1, w2) across 52 calendar weeks."""
    abs_diff = abs(w1 - w2)
    return min(abs_diff, 52 - abs_diff)


def calculate_seasonal_decay_kernel(w1: int, w2: int, bandwidth_weeks: float = 2.0) -> float:
    """Calculate cyclic-week seasonal decay kernel K_season(i)."""
    d_t = calculate_cyclic_week_distance(w1, w2)
    return math.exp(-(d_t**2) / (2.0 * (bandwidth_weeks**2)))


def calculate_beta_binomial_detection_rate(
    checklist_detections: int, total_checklists: int, alpha: float = 1.0, beta: float = 1.0
) -> float:
    """Calculate Beta-Binomial smoothed checklist detection rate r_tilde = (D_s + alpha) / (N + alpha + beta)."""
    if total_checklists <= 0:
        return 0.0
    return (checklist_detections + alpha) / (total_checklists + alpha + beta)
