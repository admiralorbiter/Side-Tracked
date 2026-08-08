"""Parquet Exporter and Metadata Manifest Writer for Analytical Modeling Datasets."""

import hashlib
import json
from pathlib import Path
from typing import Sequence

import pyarrow as pa
import pyarrow.parquet as pq

from packages.ovon_core.modeling.dataset_builder import AnalyticalSamplingRow


class ParquetDatasetExporter:
    """Exporter for saving immutable analytical modeling tables and cryptographic manifests."""

    def __init__(self, output_dir: Path | str = "data/analytical_table") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_dataset(
        self,
        rows: Sequence[AnalyticalSamplingRow],
        dataset_name: str = "kc_analytical_modeling_table",
    ) -> tuple[Path, Path]:
        row_dicts = [r.to_dict() for r in rows]

        # 1. Write binary Parquet dataset file
        table = pa.Table.from_pylist(row_dicts) if row_dicts else pa.Table.from_batches([])

        parquet_file = self.output_dir / f"{dataset_name}.parquet"
        pq.write_table(table, parquet_file)

        # 2. Write structured JSON dataset file
        data_file = self.output_dir / f"{dataset_name}.json"
        data_file.write_text(json.dumps(row_dicts, indent=2), encoding="utf-8")

        # 3. Calculate SHA-256 schema & content hash
        schema_hash = hashlib.sha256(
            json.dumps(row_dicts, sort_keys=True).encode("utf-8")
        ).hexdigest()

        # 3. Compute manifest summary statistics
        positive_counts: dict[str, int] = {}
        spatial_blocks = set()
        dates = set()

        for r in rows:
            spatial_blocks.add(r.spatial_block_id)
            dates.add(r.date)
            if r.detected == 1:
                positive_counts[r.concept_id] = positive_counts.get(r.concept_id, 0) + 1

        min_date = min(dates) if dates else "2026-05-01"
        max_date = max(dates) if dates else "2026-05-31"

        manifest = {
            "dataset_name": dataset_name,
            "row_count": len(rows),
            "positive_counts_by_concept": positive_counts,
            "spatial_block_count": len(spatial_blocks),
            "spatial_block_ids": sorted(list(spatial_blocks)),
            "date_range": {"min": min_date, "max": max_date},
            "source_release_id": rows[0].data_release_id if rows else "EBD-2026.07_SED-2026.07",
            "environment_release_id": "NLCD-2025.1_3DEP-10M_3DHP-2026.07",
            "schema_hash": schema_hash,
            "status": "immutable_analytical_table",
        }

        manifest_file = self.output_dir / "dataset_manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return (data_file, manifest_file)
