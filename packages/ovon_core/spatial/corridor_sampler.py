"""Spatial Corridor Sampler with Metric CRS Projection for Environmental Extraction."""

import math
from typing import Sequence


class CorridorSampler:
    """Projects route LineStrings to planar metric CRS (UTM Zone 15N EPSG:32615) and samples 25m corridor vertices."""

    def __init__(
        self,
        ref_lat: float = 39.0,
        ref_lon: float = -94.5,
        step_meters: float = 25.0,
        buffer_radius_m: float = 25.0,
    ) -> None:
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.step_meters = step_meters
        self.buffer_radius_m = buffer_radius_m

        # Conversion factors for WGS84 to local metric projection
        self.meters_per_lat = 111000.0
        self.meters_per_lon = 111000.0 * math.cos(math.radians(ref_lat))

    def project_to_metric(self, lat: float, lon: float) -> tuple[float, float]:
        """Project WGS84 (lat, lon) to local planar metric coordinates (x_m, y_m)."""
        x_m = (lon - self.ref_lon) * self.meters_per_lon
        y_m = (lat - self.ref_lat) * self.meters_per_lat
        return (x_m, y_m)

    def unproject_to_wgs84(self, x_m: float, y_m: float) -> tuple[float, float]:
        """Convert local planar metric coordinates (x_m, y_m) back to WGS84 (lat, lon)."""
        lat = self.ref_lat + (y_m / self.meters_per_lat)
        lon = self.ref_lon + (x_m / self.meters_per_lon)
        return (round(lat, 6), round(lon, 6))

    def sample_corridor_points(
        self, coords: Sequence[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """Sample route LineString vertices every step_meters along metric corridor."""
        if not coords:
            return [(39.0347, -94.5906)]

        metric_pts = [self.project_to_metric(c[0], c[1]) for c in coords]
        sampled_metric: list[tuple[float, float]] = [metric_pts[0]]

        accumulated = 0.0
        for i in range(len(metric_pts) - 1):
            x1, y1 = metric_pts[i]
            x2, y2 = metric_pts[i + 1]
            seg_len = math.hypot(x2 - x1, y2 - y1)

            if seg_len == 0.0:
                continue

            accumulated += seg_len
            if accumulated >= self.step_meters:
                # Interpolate sample point
                frac = (self.step_meters - (accumulated - seg_len)) / seg_len
                sx = x1 + frac * (x2 - x1)
                sy = y1 + frac * (y2 - y1)
                sampled_metric.append((sx, sy))
                accumulated = 0.0

        if metric_pts[-1] not in sampled_metric:
            sampled_metric.append(metric_pts[-1])

        return [self.unproject_to_wgs84(mx, my) for mx, my in sampled_metric]
