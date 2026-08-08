"""Synthetic Spatial Fixture Builder for unit test harness only.

This builder creates lightweight synthetic raster files in tests/fixtures/ using rasterio.
It must NEVER be invoked automatically by production providers when real source data is absent.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds


class SyntheticSpatialFixtureBuilder:
    """Synthetic GeoTIFF and vector fixture builder for unit testing."""

    @staticmethod
    def create_minimal_geotiff(
        output_path: Path,
        data_array: np.ndarray,
        min_lat: float = 38.90,
        min_lon: float = -94.75,
        max_lat: float = 39.15,
        max_lon: float = -94.45,
    ) -> None:
        """Generate valid georeferenced GeoTIFF raster file for unit test fixtures."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rows, cols = data_array.shape
        transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=rows,
            width=cols,
            count=1,
            dtype=data_array.dtype,
            crs="EPSG:4326",
            transform=transform,
        ) as ds:
            ds.write(data_array, 1)

    @classmethod
    def build_test_spatial_fixtures(cls, target_dir: Path | str) -> dict:
        """Build test spatial fixtures in specified test directory."""
        base_dir = Path(target_dir)
        nlcd_dir = base_dir / "nlcd"
        dep_dir = base_dir / "3dep"
        dhp_dir = base_dir / "3dhp"

        nlcd_dir.mkdir(parents=True, exist_ok=True)
        dep_dir.mkdir(parents=True, exist_ok=True)
        dhp_dir.mkdir(parents=True, exist_ok=True)

        np.random.seed(42)
        grid_shape = (50, 50)

        canopy_data = np.linspace(20.0, 75.0, 50 * 50).reshape(grid_shape).astype(np.float32)
        canopy_path = nlcd_dir / "canopy_2023.tif"
        cls.create_minimal_geotiff(canopy_path, canopy_data)

        impervious_data = np.linspace(35.0, 10.0, 50 * 50).reshape(grid_shape).astype(np.float32)
        impervious_path = nlcd_dir / "impervious_2025.tif"
        cls.create_minimal_geotiff(impervious_path, impervious_data)

        dem_data = np.linspace(240.0, 280.0, 50 * 50).reshape(grid_shape).astype(np.float32)
        dem_path = dep_dir / "dem_10m.tif"
        cls.create_minimal_geotiff(dem_path, dem_data)

        hydro_geojson = {
            "type": "FeatureCollection",
            "name": "USGS_3DHP_Kansas_City_Hydrography_Fixture",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "feature_id": "3DHP_KC_001",
                        "gnis_name": "Loose Creek Fixture",
                        "feature_type": "StreamRiver",
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-94.5920, 39.0320],
                            [-94.5900, 39.0350],
                            [-94.5880, 39.0390],
                        ],
                    },
                }
            ],
        }

        hydro_path = dhp_dir / "hydrography.geojson"
        hydro_path.write_text(json.dumps(hydro_geojson, indent=2), encoding="utf-8")

        def get_sha256(p: Path) -> str:
            return hashlib.sha256(p.read_bytes()).hexdigest()

        manifest = {
            "source_kind": "test_fixture",
            "region": "Kansas City Metro Test Fixture",
            "extent_wgs84": {
                "min_lat": 38.90,
                "min_lon": -94.75,
                "max_lat": 39.15,
                "max_lon": -94.45,
            },
            "crs": "EPSG:4326 / EPSG:32615",
            "datasets": {
                "canopy_2023": {
                    "filename": "nlcd/canopy_2023.tif",
                    "sha256": get_sha256(canopy_path),
                },
                "impervious_2025": {
                    "filename": "nlcd/impervious_2025.tif",
                    "sha256": get_sha256(impervious_path),
                },
                "dem_10m": {
                    "filename": "3dep/dem_10m.tif",
                    "sha256": get_sha256(dem_path),
                },
                "hydrography_3dhp": {
                    "filename": "3dhp/hydrography.geojson",
                    "sha256": get_sha256(hydro_path),
                },
            },
            "status": "fixture_source_manifest_verified",
        }

        manifest_path = base_dir / "source_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
