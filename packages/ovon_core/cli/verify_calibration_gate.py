"""CLI Tool to verify Empirical Model Fitting & Calibration Gate (Sprint 16.9)."""

import time

from packages.ovon_core.modeling.calibration_gate import CalibrationGate
from packages.ovon_core.modeling.spatial_cross_validator import SpatialHoldoutCrossValidator


def main() -> None:
    """Run Empirical Model Fitting & Calibration Gate verification suite."""
    print("=" * 65)
    print("   SIDETRACK SCIENTIFIC CALIBRATION GATE VERIFICATION")
    print("=" * 65)

    # 1. Test Spatial Holdout Cross-Validator
    rows = [{"event_id": f"E{i}", "spatial_block_id": f"cell_{i % 5}", "val": i} for i in range(50)]

    validator = SpatialHoldoutCrossValidator(test_ratio=0.3, random_seed=42)
    split = validator.split_rows(rows)

    train_blocks = set(split.training_block_ids)
    test_blocks = set(split.test_block_ids)

    # Verify zero overlap between train and test spatial blocks
    assert len(train_blocks.intersection(test_blocks)) == 0
    print(
        f"[OK] SpatialHoldoutCrossValidator: Split 50 rows across {len(train_blocks.union(test_blocks))} spatial cells -> {len(split.training_rows)} train rows vs {len(split.test_rows)} holdout test rows (Disjoint Block Check: PASSED)"
    )

    # 2. Test Calibration Gate (Passing Case: Brier <= 0.15, ECE <= 0.08)
    gate = CalibrationGate(max_brier_score=0.15, max_ece=0.08)
    well_calibrated_preds = [0.96, 0.04, 0.94, 0.02, 0.98, 0.05, 0.92, 0.03, 0.95, 0.01]
    actual_outcomes = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

    start_t = time.perf_counter()
    metrics_pass = gate.evaluate(well_calibrated_preds, actual_outcomes)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    assert metrics_pass.is_calibrated is True
    assert metrics_pass.status == "calibrated_promoted"
    assert metrics_pass.brier_score <= 0.15
    assert metrics_pass.ece <= 0.08

    print(
        f"[OK] CalibrationGate (Promoted Pass): Brier={metrics_pass.brier_score:.4f} (<=0.15), ECE={metrics_pass.ece:.4f} (<=0.08) -> status='{metrics_pass.status}' in {elapsed_ms:.2f}ms"
    )

    # 3. Test Calibration Gate (Failing Case -> Fail Closed to provisional_heuristic)
    poor_calibrated_preds = [0.95, 0.90, 0.85, 0.92, 0.88, 0.99]
    failed_outcomes = [0, 0, 0, 0, 0, 0]  # Overconfident failure

    metrics_fail = gate.evaluate(poor_calibrated_preds, failed_outcomes)
    assert metrics_fail.is_calibrated is False
    assert metrics_fail.status == "provisional_heuristic"
    assert len(metrics_fail.rejection_reasons) > 0

    print(
        f"[OK] CalibrationGate (Fail-Closed Safety): Brier={metrics_fail.brier_score:.4f}, ECE={metrics_fail.ece:.4f} -> Fails Closed to status='{metrics_fail.status}'"
    )
    print(f"     Rejection Reason: {metrics_fail.rejection_reasons[0]}")

    print("=" * 65)
    print("SUCCESS: ALL SCIENTIFIC CALIBRATION GATE CHECKS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
