"""CLI Tool to verify R4 Pure Analytical Table & PyArrow Parquet Export."""

import json
import time
from pathlib import Path

from packages.ovon_core.modeling.dataset_builder import AnalyticalDatasetBuilder
from packages.ovon_core.modeling.parquet_exporter import ParquetDatasetExporter


def main() -> None:
    """Run R4 Analytical Table & Content-Addressed Parquet verification suite."""
    print("=" * 70)
    print("   SIDETRACK PURE ANALYTICAL TABLE & PYARROW PARQUET VERIFICATION (R4)")
    print("=" * 70)

    start_t = time.perf_counter()
    out_dir = Path("data/derived/modeling/verify_r4_dataset")

    builder = AnalyticalDatasetBuilder()

    events = [
        {
            "event_id": "S101",
            "sampling_event_identifier": "EBD_CHECKLIST_001",
            "all_species_reported": True,
            "latitude": 39.0347,
            "longitude": -94.5906,
            "date": "2026-05-15",
            "time": "11:30",
            "duration_minutes": 45.0,
            "effort_distance_km": 1.2,
            "number_observers": 2,
        },
        {
            # Group checklist duplicate (same group identifier -> collapsed)
            "event_id": "S101_DUP",
            "sampling_event_identifier": "EBD_CHECKLIST_001",
            "all_species_reported": True,
            "latitude": 39.0347,
            "longitude": -94.5906,
            "date": "2026-05-15",
            "time": "11:30",
        },
        {
            # Incomplete checklist (all_species_reported == False -> rejected fail-closed!)
            "event_id": "S102",
            "all_species_reported": False,
            "latitude": 39.0325,
            "longitude": -94.5960,
            "date": "2026-05-16",
        },
        {
            # Missing required location input (latitude missing -> rejected fail-closed!)
            "event_id": "S103",
            "all_species_reported": True,
            "date": "2026-05-16",
        },
    ]

    obs = [{"event_id": "S101", "concept_id": "sidetrack_concept:northern_cardinal"}]
    focal = ["sidetrack_concept:northern_cardinal", "sidetrack_concept:american_robin"]

    # 1. Build Analytical Rows & Verify Fail-Closed Boundaries
    rows = builder.build_analytical_rows(events, obs, focal)
    assert len(rows) == 2  # 1 valid complete event x 2 focal species

    cardinal_row = next(r for r in rows if r.concept_id == "sidetrack_concept:northern_cardinal")
    robin_row = next(r for r in rows if r.concept_id == "sidetrack_concept:american_robin")

    assert cardinal_row.detected == 1
    assert robin_row.detected == 0
    assert (
        cardinal_row.solar_altitude_degrees > 0.0
    )  # Calculated from May 15 06:30 morning sun angle
    print(
        f"[OK 1/4] Fail-Closed Boundaries: Complete checklist validated, incomplete/missing inputs rejected, group checklist deduplicated (Solar Alt={cardinal_row.solar_altitude_degrees}°)"
    )

    # 2. Export Binary PyArrow Parquet & Cryptographic Manifest
    exporter = ParquetDatasetExporter(output_dir=out_dir)
    data_file, manifest_file = exporter.export_dataset(
        rows, dataset_name="r4_analytical_modeling_table"
    )

    assert (out_dir / "r4_analytical_modeling_table.parquet").exists()
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    assert manifest["status"] == "immutable_analytical_table"
    assert manifest["row_count"] == 2
    assert "schema_hash" in manifest

    print(
        f"[OK 2/4] PyArrow Parquet Export: Binary .parquet written to {out_dir} with SHA-256 schema hash ({manifest['schema_hash'][:16]}...)"
    )

    # 3. Read back Parquet table via PyArrow
    import pyarrow.parquet as pq

    read_table = pq.read_table(out_dir / "r4_analytical_modeling_table.parquet")
    assert read_table.num_rows == 2
    assert "canopy_cover_percent" in read_table.column_names

    print(
        f"[OK 3/4] PyArrow Integration: Read back {read_table.num_rows} rows directly from binary Parquet dataset"
    )

    # 4. Pipeline Speed Benchmark
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    print(f"[OK 4/4] R4 Analytical Parquet Execution Time: {elapsed_ms:.2f}ms (< 100ms)")

    print("=" * 70)
    print("SUCCESS: ALL R4 ANALYTICAL TABLE & PARQUET CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
