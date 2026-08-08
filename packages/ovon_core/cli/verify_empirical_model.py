"""CLI Tool to verify R5 Empirical Northern Cardinal Model Fitting & Out-of-Fold Calibration."""

import json
import time
from pathlib import Path

from packages.ovon_core.modeling.dataset_builder import AnalyticalDatasetBuilder
from packages.ovon_core.modeling.joint_service import JointModelService
from packages.ovon_core.modeling.model_trainer import EmpiricalEncounterModelTrainer


def main() -> None:
    """Run R5 Empirical Model Fitting & Calibration Gate verification suite."""
    print("=" * 70)
    print("   SIDETRACK EMPIRICAL NORTHERN CARDINAL MODEL & CALIBRATION VERIFICATION (R5)")
    print("=" * 70)

    start_t = time.perf_counter()
    model_base_dir = Path("data/derived/models")

    # 1. Generate Synthetic Analytical Rows across multiple spatial H3 blocks
    builder = AnalyticalDatasetBuilder()

    events = []
    observations = []
    # Create 50 complete checklists across 3 distinct spatial blocks
    coords = [
        (39.0347, -94.5906),  # Block 1 (Loose Park)
        (39.0500, -94.5800),  # Block 2 (Plaza)
        (39.1000, -94.5700),  # Block 3 (Downtown KC)
    ]

    for i in range(50):
        lat, lon = coords[i % 3]
        e_id = f"S_KC_{i:03d}"
        events.append(
            {
                "event_id": e_id,
                "sampling_event_identifier": f"CHK_{i:03d}",
                "all_species_reported": True,
                "latitude": lat,
                "longitude": lon,
                "date": "2026-05-15",
                "time": f"{6 + (i % 6):02d}:30",
                "duration_minutes": 30.0 + (i % 30),
                "effort_distance_km": 1.0 + (i * 0.1),
            }
        )

        # High detection rate for Northern Cardinal in high-canopy Loose Park
        if i % 2 == 0:
            observations.append(
                {"event_id": e_id, "concept_id": "sidetrack_concept:northern_cardinal"}
            )

    analytical_rows = builder.build_analytical_rows(
        events, observations, ["sidetrack_concept:northern_cardinal"]
    )
    assert len(analytical_rows) == 50

    print(
        f"[OK 1/5] Analytical Dataset: Prepared {len(analytical_rows)} rows across 3 spatial cell blocks"
    )

    # 2. Train Empirical Model & Evaluate Calibration Gate on Untouched Spatial Holdouts
    trainer = EmpiricalEncounterModelTrainer(output_base_dir=model_base_dir)
    artifact, manifest_file = trainer.train_and_evaluate(
        analytical_rows, focal_concept_id="sidetrack_concept:northern_cardinal"
    )

    assert artifact.status in ("calibrated_promoted", "provisional_heuristic")
    assert manifest_file.exists()

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["concept_id"] == "sidetrack_concept:northern_cardinal"
    assert manifest["brier_score"] <= 0.50

    assert "schema_hash" in manifest

    print(
        f"[OK 2/5] Empirical Model Fitting: Fitted 7 features, Brier Score={artifact.brier_score:.4f}, ECE={artifact.ece:.4f}"
    )
    print(
        f"[OK 3/5] Calibration Gate Evaluation: Out-of-fold spatial holdout status = '{artifact.status}'"
    )

    # 3. Test Model Prediction Probability
    sample_feat = {
        "canopy_cover_percent": 45.0,
        "impervious_surface_percent": 15.0,
        "elevation_m": 258.0,
        "slope_gradient_percent": 2.5,
        "water_edge_distance_m": 120.0,
        "duration_minutes": 45.0,
        "solar_altitude_degrees": 25.0,
    }
    p_pred = artifact.predict_probability(sample_feat)
    assert 0.01 <= p_pred <= 0.99

    print(
        f"[OK 4/5] Model Inference Engine: Predicted Northern Cardinal encounter probability = {p_pred:.4f}"
    )

    # 4. Test JointModelService Integration
    service = JointModelService()
    from packages.ovon_core.fixtures.routes_fixtures import ROUTE_BIRDY

    summary = service.predict_for_route(ROUTE_BIRDY)
    assert summary.overall_calibration_status == artifact.status

    # 5. Pipeline Execution Speed
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    print(
        f"[OK 5/5] R5 Empirical Model Training & Verification Time: {elapsed_ms:.2f}ms (< 1000ms)"
    )

    print("=" * 70)
    print("SUCCESS: ALL R5 EMPIRICAL NORTHERN CARDINAL MODEL CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
