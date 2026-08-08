"""Metric Spatial Corridor Sampler using UTM Zone 15N (EPSG:32615) projection and 25m buffer sampling."""

from dataclasses import dataclass
from typing import Sequence

import pyproj
from shapely.geometry import LineString, Point


@dataclass(frozen=True, slots=True)
class MetricCorridorSamplePoint:
    """Sample point along route corridor with lat/lon and projected metric coordinates."""

    index: int
    latitude: float
    longitude: float
    metric_x: float
    metric_y: float
    distance_along_route_m: float
    buffer_radius_m: float = 25.0


class CorridorSampler:
    """Samples points along route LineStrings using UTM Zone 15N (EPSG:32615) metric projection and 25m corridor buffers."""

    def __init__(
        self,
        ref_crs: str = "EPSG:4326",
        target_crs: str = "EPSG:32615",
        step_meters: float = 25.0,
        buffer_radius_m: float = 25.0,
    ) -> None:
        self.step_meters = step_meters
        self.buffer_radius_m = buffer_radius_m
        self.transformer_to_metric = pyproj.Transformer.from_crs(
            ref_crs, target_crs, always_xy=True
        )
        self.transformer_to_wgs84 = pyproj.Transformer.from_crs(target_crs, ref_crs, always_xy=True)

    def project_to_metric(self, coordinates: Sequence[tuple[float, float]]) -> LineString:
        """Project (lat, lon) coordinates to UTM Zone 15N metric LineString."""
        metric_pts = []
        for lat, lon in coordinates:
            mx, my = self.transformer_to_metric.transform(lon, lat)
            metric_pts.append((mx, my))

        return LineString(metric_pts)

    def sample_corridor_points(
        self, coordinates: Sequence[tuple[float, float]]
    ) -> list[MetricCorridorSamplePoint]:
        """Sample corridor points every 25 meters along route LineString."""
        if not coordinates:
            return []

        if len(coordinates) == 1:
            lat, lon = coordinates[0]
            mx, my = self.transformer_to_metric.transform(lon, lat)
            return [
                MetricCorridorSamplePoint(
                    index=0,
                    latitude=lat,
                    longitude=lon,
                    metric_x=mx,
                    metric_y=my,
                    distance_along_route_m=0.0,
                    buffer_radius_m=self.buffer_radius_m,
                )
            ]

        metric_line = self.project_to_metric(coordinates)
        line_length_m = metric_line.length

        sample_points: list[MetricCorridorSamplePoint] = []
        current_dist = 0.0
        idx = 0

        while current_dist <= line_length_m:
            point_geom = metric_line.interpolate(current_dist)
            mx, my = point_geom.x, point_geom.y
            lon, lat = self.transformer_to_wgs84.transform(mx, my)

            sample_points.append(
                MetricCorridorSamplePoint(
                    index=idx,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    metric_x=round(mx, 2),
                    metric_y=round(my, 2),
                    distance_along_route_m=round(current_dist, 2),
                    buffer_radius_m=self.buffer_radius_m,
                )
            )

            current_dist += self.step_meters
            idx += 1

        # Ensure end point is included if not exact multiple
        if sample_points and sample_points[-1].distance_along_route_m < line_length_m:
            end_geom = metric_line.interpolate(line_length_m)
            mx, my = end_geom.x, end_geom.y
            lon, lat = self.transformer_to_wgs84.transform(mx, my)
            sample_points.append(
                MetricCorridorSamplePoint(
                    index=idx,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    metric_x=round(mx, 2),
                    metric_y=round(my, 2),
                    distance_along_route_m=round(line_length_m, 2),
                    buffer_radius_m=self.buffer_radius_m,
                )
            )

        return sample_points
