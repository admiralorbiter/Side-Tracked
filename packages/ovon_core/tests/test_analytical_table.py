"""Unit tests for Immutable Analytical Parquet Modeling Table (Sprint 16.8)."""

import json

from packages.ovon_core.modeling.dataset_builder import AnalyticalDatasetBuilder
from packages.ovon_core.modeling.parquet_exporter import ParquetDatasetExporter


def test_analytical_dataset_builder_zero_filling():
    builder = AnalyticalDatasetBuilder()

    events = [
        {
            "event_id": "S101",
            "all_species_reported": True,
            "latitude": 39.0347,
            "longitude": -94.5906,
            "date": "2026-05-15",
            "duration_minutes": 45.0,
        }
    ]
    observations = [{"event_id": "S101", "concept_id": "sidetrack_concept:cardinal"}]
    focal_concepts = ["sidetrack_concept:cardinal", "sidetrack_concept:robin"]

    rows = builder.build_analytical_rows(events, observations, focal_concepts)
    assert len(rows) == 2

    # Cardinal should be detected=1, Robin should be zero-filled detected=0
    cardinal_row = next(r for r in rows if r.concept_id == "sidetrack_concept:cardinal")
    robin_row = next(r for r in rows if r.concept_id == "sidetrack_concept:robin")

    assert cardinal_row.detected == 1
    assert robin_row.detected == 0
    assert cardinal_row.spatial_block_id != ""


def test_parquet_exporter_manifest(tmp_path):
    builder = AnalyticalDatasetBuilder()
    events = [
        {
            "event_id": "S102",
            "all_species_reported": True,
            "latitude": 39.0325,
            "longitude": -94.5960,
            "date": "2026-05-16",
        }
    ]
    observations = [{"event_id": "S102", "concept_id": "sidetrack_concept:cardinal"}]
    rows = builder.build_analytical_rows(events, observations, ["sidetrack_concept:cardinal"])

    exporter = ParquetDatasetExporter(output_dir=tmp_path)
    data_file, manifest_file = exporter.export_dataset(rows, dataset_name="test_analytical_table")

    assert data_file.exists()
    assert manifest_file.exists()
    assert (tmp_path / "test_analytical_table.parquet").exists()

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["row_count"] == 1
    assert "schema_hash" in manifest
