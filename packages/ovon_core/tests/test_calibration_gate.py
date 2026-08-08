"""Unit tests for Spatial Cross-Validation and Scientific Calibration Gate (Sprint 16.9)."""

from packages.ovon_core.modeling.calibration_gate import CalibrationGate
from packages.ovon_core.modeling.spatial_cross_validator import SpatialHoldoutCrossValidator


def test_spatial_holdout_cross_validator_disjoint_blocks():
    validator = SpatialHoldoutCrossValidator(test_ratio=0.3, random_seed=42)
    rows = [{"event_id": f"E{i}", "spatial_block_id": f"block_{i % 4}"} for i in range(20)]
    split = validator.split_rows(rows)

    train_blocks = set(split.training_block_ids)
    test_blocks = set(split.test_block_ids)

    # Disjoint spatial blocks check
    assert len(train_blocks.intersection(test_blocks)) == 0
    assert len(split.training_rows) + len(split.test_rows) == 20


def test_calibration_gate_pass_and_fail_closed():
    gate = CalibrationGate(max_brier_score=0.15, max_ece=0.08)

    # Pass case
    preds_pass = [0.96, 0.04, 0.94, 0.02, 0.98, 0.05]
    outs_pass = [1, 0, 1, 0, 1, 0]
    res_pass = gate.evaluate(preds_pass, outs_pass)

    assert res_pass.is_calibrated is True
    assert res_pass.status == "calibrated_promoted"
    assert res_pass.brier_score <= 0.15

    # Fail case (overconfident wrong predictions)
    preds_fail = [0.95, 0.90, 0.85, 0.99]
    outs_fail = [0, 0, 0, 0]
    res_fail = gate.evaluate(preds_fail, outs_fail)

    assert res_fail.is_calibrated is False
    assert res_fail.status == "provisional_heuristic"
    assert len(res_fail.rejection_reasons) > 0
