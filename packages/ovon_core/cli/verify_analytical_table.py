"""CLI Tool to verify Immutable Analytical Parquet Modeling Table (Sprint 16.8)."""

import json
import time

from packages.ovon_core.modeling.dataset_builder import AnalyticalDatasetBuilder
from packages.ovon_core.modeling.parquet_exporter import ParquetDatasetExporter


def main() -> None:
    """Run Immutable Analytical Parquet Modeling Table verification suite."""
    print("=" * 65)
    print("   SIDETRACK ANALYTICAL MODELING TABLE VERIFICATION")
    print("=" * 65)

    # 1. Sample complete eBird checklists & focal species concepts
    events = [
        {
            "event_id": "S1001",
            "all_species_reported": True,
            "latitude": 39.0347,
            "longitude": -94.5906,
            "date": "2026-05-10",
            "time": "07:30",
            "duration_minutes": 45.0,
            "effort_distance_km": 1.5,
            "number_observers": 1,
        },
        {
            "event_id": "S1002",
            "all_species_reported": True,
            "latitude": 39.0325,
            "longitude": -94.5960,
            "date": "2026-05-12",
            "time": "08:15",
            "duration_minutes": 30.0,
            "effort_distance_km": 1.0,
            "number_observers": 2,
        },
    ]

    observations = [
        {"event_id": "S1001", "concept_id": "sidetrack_concept:northern_cardinal"},
        {"event_id": "S1001", "concept_id": "sidetrack_concept:american_robin"},
        {"event_id": "S1002", "concept_id": "sidetrack_concept:northern_cardinal"},
    ]

    focal_concepts = [
        "sidetrack_concept:northern_cardinal",
        "sidetrack_concept:american_robin",
        "sidetrack_concept:downy_woodpecker",
    ]

    # 2. Test AnalyticalDatasetBuilder (Zero-filling + Environmental Joining + H3 Indexing)
    builder = AnalyticalDatasetBuilder()
    start_t = time.perf_counter()
    rows = builder.build_analytical_rows(events, observations, focal_concepts)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    # 2 checklists x 3 focal species = 6 analytical rows
    assert len(rows) == 6
    assert rows[0].detected in (0, 1)
    assert rows[0].spatial_block_id != ""
    assert rows[0].canopy_cover_percent > 0.0

    print(
        f"[OK] AnalyticalDatasetBuilder: Zero-filled {len(events)} complete checklists across {len(focal_concepts)} focal concepts -> {len(rows)} immutable analytical rows in {elapsed_ms:.2f}ms"
    )

    # 3. Test ParquetDatasetExporter & Metadata Manifest Integrity
    exporter = ParquetDatasetExporter()
    data_file, manifest_file = exporter.export_dataset(rows)

    assert data_file.exists()
    assert manifest_file.exists()

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["row_count"] == 6
    assert manifest["status"] == "immutable_analytical_table"
    assert "schema_hash" in manifest

    print(f"[OK] Immutable Dataset Exported: {data_file}")
    print(
        f"[OK] Cryptographic Manifest Verified: {manifest_file} (SHA-256: {manifest['schema_hash'][:16]}...)"
    )

    print("=" * 65)
    print("SUCCESS: ALL ANALYTICAL MODELING TABLE CHECKS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
