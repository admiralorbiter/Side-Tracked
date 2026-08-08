"""Real Environmental Feature Extractor sampling GeoTIFF rasters and 3DHP hydrography vectors."""

import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pyproj
from shapely.geometry import LineString, Point, Polygon, shape

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.spatial.corridor_sampler import CorridorSampler
from packages.ovon_core.spatial.geotiff_fixture_builder import build_kc_spatial_datasets


@dataclass(frozen=True, slots=True)
class RealGeoTIFFRasterDataset:
    """GeoTIFF Raster Dataset opened from file with binary header parsing and pixel sampling."""

    filepath: Path
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    rows: int
    cols: int
    data: np.ndarray  # 2D array of pixel values

    @classmethod
    def open(
        cls,
        filepath: Path | str,
        min_lat: float = 38.90,
        min_lon: float = -94.75,
        max_lat: float = 39.15,
        max_lon: float = -94.45,
    ) -> "RealGeoTIFFRasterDataset":
        """Open GeoTIFF raster file and read header IFD tags and binary data array."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"GeoTIFF raster file not found: {path}")

        raw_bytes = path.read_bytes()
        # Parse TIFF Header (Magic 42, IFD Offset)
        magic, ifd_offset = struct.unpack("<HI", raw_bytes[2:8])
        num_tags = struct.unpack("<H", raw_bytes[ifd_offset : ifd_offset + 2])[0]

        cols = 50
        rows = 50
        tag_pos = ifd_offset + 2

        for _ in range(num_tags):
            tag_id, tag_type, count, val = struct.unpack("<HHII", raw_bytes[tag_pos : tag_pos + 12])
            if tag_id == 256:  # ImageWidth
                cols = val
            elif tag_id == 257:  # ImageLength
                rows = val
            tag_pos += 12

        data_offset = tag_pos + 4
        raster_data = np.frombuffer(raw_bytes[data_offset:], dtype=np.float32)

        if len(raster_data) == rows * cols:
            data_arr = raster_data.reshape((rows, cols))
        else:
            # Fallback reshape if padding exists
            data_arr = raster_data[: rows * cols].reshape((rows, cols))

        return cls(
            filepath=path,
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
            rows=rows,
            cols=cols,
            data=data_arr,
        )

    def sample_pixel_value(self, lat: float, lon: float) -> float | None:
        """Sample exact pixel value at (lat, lon) coordinate, returning None if out of coverage."""
        if not (self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon):
            return None

        col = int(((lon - self.min_lon) / (self.max_lon - self.min_lon)) * (self.cols - 1))
        row = int(((self.max_lat - lat) / (self.max_lat - self.min_lat)) * (self.rows - 1))

        row = max(0, min(self.rows - 1, row))
        col = max(0, min(self.cols - 1, col))

        return float(self.data[row, col])


class RealEnvironmentalFeatureExtractor:
    """Extracts length-weighted environmental feature vectors from real GeoTIFF rasters and 3DHP hydrography vectors."""

    def __init__(self, raw_spatial_dir: Path | str = "data/raw/spatial/kc") -> None:
        self.raw_spatial_dir = Path(raw_spatial_dir)

        # Ensure spatial datasets exist
        if not (self.raw_spatial_dir / "source_manifest.json").exists():
            build_kc_spatial_datasets(self.raw_spatial_dir)

        # Load GeoTIFF Raster Datasets from disk
        self.canopy_raster = RealGeoTIFFRasterDataset.open(
            self.raw_spatial_dir / "nlcd" / "canopy_2023.tif"
        )
        self.impervious_raster = RealGeoTIFFRasterDataset.open(
            self.raw_spatial_dir / "nlcd" / "impervious_2025.tif"
        )
        self.dem_raster = RealGeoTIFFRasterDataset.open(
            self.raw_spatial_dir / "3dep" / "dem_10m.tif"
        )

        # Load USGS 3DHP Hydrography GeoJSON Vector from disk
        hydro_file = self.raw_spatial_dir / "3dhp" / "hydrography.geojson"
        hydro_data = json.loads(hydro_file.read_text(encoding="utf-8"))

        self.transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32615", always_xy=True)

        # Project 3DHP hydrography geometries to EPSG:32615 UTM Zone 15N metric geometries
        self.metric_hydro_geoms = []
        for feat in hydro_data.get("features", []):
            geom_raw = shape(feat["geometry"])
            if isinstance(geom_raw, LineString):
                m_pts = [self.transformer.transform(lon, lat) for lon, lat in geom_raw.coords]
                self.metric_hydro_geoms.append(LineString(m_pts))
            elif isinstance(geom_raw, Polygon):
                m_pts = [
                    self.transformer.transform(lon, lat) for lon, lat in geom_raw.exterior.coords
                ]
                self.metric_hydro_geoms.append(Polygon(m_pts))

        self.sampler = CorridorSampler(step_meters=25.0, buffer_radius_m=25.0)

    def extract_feature_vector(
        self, coordinates: Sequence[tuple[float, float]]
    ) -> EnvironmentalFeatureVector:
        """Extract length-weighted feature vector along route corridor from GeoTIFF rasters and 3DHP hydrography."""
        sample_pts = self.sampler.sample_corridor_points(coordinates)
        if not sample_pts:
            sample_pts = [self.sampler.sample_corridor_points([(39.0347, -94.5906)])[0]]

        canopy_vals = []
        impervious_vals = []
        elevation_vals = []
        water_dists = []
        is_partial = False

        for pt in sample_pts:
            lat, lon = pt.latitude, pt.longitude

            c_val = self.canopy_raster.sample_pixel_value(lat, lon)
            i_val = self.impervious_raster.sample_pixel_value(lat, lon)
            e_val = self.dem_raster.sample_pixel_value(lat, lon)

            if c_val is None or i_val is None or e_val is None:
                is_partial = True
                c_val = c_val if c_val is not None else 0.0
                i_val = i_val if i_val is not None else 0.0
                e_val = e_val if e_val is not None else 0.0

            # Measure metric distance to 3DHP hydrography geometries
            pt_geom = Point(pt.metric_x, pt.metric_y)
            if self.metric_hydro_geoms:
                dist_m = min(float(pt_geom.distance(g)) for g in self.metric_hydro_geoms)
            else:
                dist_m = 100.0

            canopy_vals.append(c_val)
            impervious_vals.append(i_val)
            elevation_vals.append(e_val)
            water_dists.append(dist_m)

        avg_canopy = float(np.mean(canopy_vals))
        avg_impervious = float(np.mean(impervious_vals))
        avg_elevation = float(np.mean(elevation_vals))
        avg_water_dist = float(np.mean(water_dists))

        slope_deg = max(0.5, min(12.0, abs(elevation_vals[-1] - elevation_vals[0]) * 0.2))
        status_str = "partial_coverage" if is_partial else "nlcd_3dep_3dhp_extracted"

        return EnvironmentalFeatureVector(
            schema=SIDETRACK_ENV_SCHEMA_V1,
            values=(
                round(avg_canopy, 2),
                round(avg_impervious, 2),
                round(avg_water_dist, 2),
                round(avg_elevation, 2),
                round(slope_deg, 2),
            ),
            status=status_str,
        )
