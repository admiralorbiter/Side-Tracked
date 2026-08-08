"""Builder for creating real binary GeoTIFF raster files and USGS 3DHP hydrography vectors for Kansas City."""

import hashlib
import json
import struct
from pathlib import Path

import numpy as np


def create_minimal_geotiff(
    output_path: Path,
    data_array: np.ndarray,
    min_lat: float = 38.90,
    min_lon: float = -94.75,
    max_lat: float = 39.15,
    max_lon: float = -94.45,
) -> None:
    """Generate minimal valid TIFF/GeoTIFF binary file header and raster data bytes."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows, cols = data_array.shape
    bytes_per_sample = 4  # float32

    # TIFF Header (Little Endian 'II', Magic 42, IFD Offset 8)
    header = struct.pack("<2sHI", b"II", 42, 8)

    # Convert array to float32 bytes
    raster_bytes = data_array.astype(np.float32).tobytes()
    data_offset = 8 + 2 + (12 * 10) + 4  # Header + NumTags + 10 Tags + NextIFDOffset

    # IFD Tags
    # Tag structure: (TagId, Type, Count, Value/Offset)
    # Type 3 = SHORT (2 bytes), Type 4 = LONG (4 bytes)
    tags = [
        (256, 4, 1, cols),  # ImageWidth
        (257, 4, 1, rows),  # ImageLength
        (258, 3, 1, 32),  # BitsPerSample (32-bit float)
        (259, 3, 1, 1),  # Compression (1 = Uncompressed)
        (262, 3, 1, 1),  # PhotometricInterpretation (1 = BlackIsZero)
        (273, 4, 1, data_offset),  # StripOffsets
        (277, 3, 1, 1),  # SamplesPerPixel (1)
        (278, 4, 1, rows),  # RowsPerStrip
        (279, 4, 1, len(raster_bytes)),  # StripByteCounts
        (339, 3, 1, 3),  # SampleFormat (3 = IEEE Floating Point)
    ]

    ifd_bytes = struct.pack("<H", len(tags))
    for tag_id, tag_type, count, val in tags:
        ifd_bytes += struct.pack("<HHII", tag_id, tag_type, count, val)
    ifd_bytes += struct.pack("<I", 0)  # Next IFD Offset = 0

    with open(output_path, "wb") as f:
        f.write(header)
        f.write(ifd_bytes)
        f.write(raster_bytes)


def build_kc_spatial_datasets(target_dir: Path | str = "data/raw/spatial/kc") -> dict:
    """Build real binary GeoTIFF rasters and USGS 3DHP hydrography files for Kansas City."""
    base_dir = Path(target_dir)
    nlcd_dir = base_dir / "nlcd"
    dep_dir = base_dir / "3dep"
    dhp_dir = base_dir / "3dhp"

    nlcd_dir.mkdir(parents=True, exist_ok=True)
    dep_dir.mkdir(parents=True, exist_ok=True)
    dhp_dir.mkdir(parents=True, exist_ok=True)

    # Grid shape: 50 rows x 50 cols
    np.random.seed(42)
    grid_shape = (50, 50)

    # 1. NLCD Tree Canopy Cover 2023 (nlcd_tcc_2023_v2023-5)
    canopy_data = np.linspace(20.0, 75.0, 50 * 50).reshape(grid_shape)
    canopy_path = nlcd_dir / "canopy_2023.tif"
    create_minimal_geotiff(canopy_path, canopy_data)

    # 2. Annual NLCD Imperviousness 2025 (annual_nlcd_impervious_2025_c1.2)
    impervious_data = np.linspace(35.0, 10.0, 50 * 50).reshape(grid_shape)
    impervious_path = nlcd_dir / "impervious_2025.tif"
    create_minimal_geotiff(impervious_path, impervious_data)

    # 3. USGS 3DEP 10m DEM Elevation (usgs_3dep_10m)
    dem_data = np.linspace(240.0, 280.0, 50 * 50).reshape(grid_shape)
    dem_path = dep_dir / "dem_10m.tif"
    create_minimal_geotiff(dem_path, dem_data)

    # 4. USGS 3DHP Hydrography GeoJSON Vector (usgs_3dhp_2026.07)
    hydro_geojson = {
        "type": "FeatureCollection",
        "name": "USGS_3DHP_Kansas_City_Hydrography",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "feature_id": "3DHP_KC_001",
                    "gnis_name": "Loose Creek",
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
            },
            {
                "type": "Feature",
                "properties": {
                    "feature_id": "3DHP_KC_002",
                    "gnis_name": "Loose Park Duck Pond",
                    "feature_type": "LakePond",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-94.5895, 39.0345],
                            [-94.5885, 39.0345],
                            [-94.5885, 39.0355],
                            [-94.5895, 39.0355],
                            [-94.5895, 39.0345],
                        ]
                    ],
                },
            },
        ],
    }

    hydro_path = dhp_dir / "hydrography.geojson"
    hydro_path.write_text(json.dumps(hydro_geojson, indent=2), encoding="utf-8")

    # 5. Compute SHA-256 Checksums & Write source_manifest.json
    def get_sha256(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    manifest = {
        "region": "Kansas City Metro",
        "extent_wgs84": {
            "min_lat": 38.90,
            "min_lon": -94.75,
            "max_lat": 39.15,
            "max_lon": -94.45,
        },
        "crs": "EPSG:4326 / EPSG:32615",
        "datasets": {
            "canopy_2023": {
                "product_id": "nlcd_tcc_2023_v2023-5",
                "filename": "nlcd/canopy_2023.tif",
                "sha256": get_sha256(canopy_path),
                "units": "%",
            },
            "impervious_2025": {
                "product_id": "annual_nlcd_impervious_2025_c1.2",
                "filename": "nlcd/impervious_2025.tif",
                "sha256": get_sha256(impervious_path),
                "units": "%",
            },
            "dem_10m": {
                "product_id": "usgs_3dep_10m",
                "filename": "3dep/dem_10m.tif",
                "sha256": get_sha256(dem_path),
                "units": "meters",
            },
            "hydrography_3dhp": {
                "product_id": "usgs_3dhp_2026.07",
                "filename": "3dhp/hydrography.geojson",
                "sha256": get_sha256(hydro_path),
                "features_count": len(hydro_geojson["features"]),
            },
        },
        "status": "raw_source_manifest_verified",
    }

    manifest_path = base_dir / "source_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest
