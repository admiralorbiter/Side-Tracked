"""CLI Tool to verify Calibrated Focal Species Models and Spatial Holdout Metrics."""

import sys

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.modeling.calibrated_model import CalibratedSpeciesModel
from packages.ovon_core.modeling.dataset import ModelingDatasetBuilder
from packages.ovon_core.modeling.evaluator import SpatialBlockEvaluator
from packages.ovon_core.modeling.service import CalibratedModelService


def main() -> None:
    """Run Calibrated Species Model verification suite."""
    print("=" * 60)
    print("   SIDETRACK CALIBRATED FOCAL SPECIES MODEL VERIFICATION")
    print("=" * 60)

    # 1. Test Dataset Assembly
    builder = ModelingDatasetBuilder()
    samples = builder.build_dataset_for_concept(
        "sidetrack_concept:american_robin", sample_count=120
    )
    assert len(samples) == 120
    print(
        f"[OK] Dataset Builder: Assembled {len(samples)} complete-checklist survey samples across 4 spatial blocks"
    )

    # 2. Test Model Training & Calibration
    model = CalibratedSpeciesModel("sidetrack_concept:american_robin")
    model.fit(samples)
    assert model.is_fitted
    print(f"[OK] Model Engine: Fitted '{model.model_id}' v{model.model_version}")

    # 3. Test Feature Vector Probability Prediction
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(65.0, 10.0, 50.0, 270.0, 3.0),
    )
    prob = model.predict_proba(vec)
    assert 0.0 <= prob <= 1.0
    print(f"[OK] Platt Calibrator: Predicted P(Y=1 | x, t) = {prob*100:.1f}% (Calibrated)")

    # 4. Test Spatial Block Holdout Evaluator
    evaluator = SpatialBlockEvaluator()
    metrics = evaluator.evaluate_model(model, samples)
    assert metrics["brier_score"] < 0.15
    assert metrics["ece_score"] < 0.25
    assert metrics["spatial_roc_auc"] >= 0.70

    print(
        f"[OK] Spatial Holdout Evaluator: Brier={metrics['brier_score']}, ECE={metrics['ece_score']}, AUC={metrics['spatial_roc_auc']}"
    )

    # 5. Test Service Execution & Provenance
    service = CalibratedModelService()
    summary = service.predict_for_route(ROUTE_BIRDY)
    assert summary.overall_calibration_status == "platt_calibrated"
    assert len(summary.predictions) > 0
    prov = summary.predictions[0].provenance
    assert prov.calibration_status == "platt_calibrated"
    print(
        f"[OK] CalibratedModelService Verified: Summary generated for {len(summary.predictions)} species with explicit provenance"
    )

    print("=" * 60)
    print("SUCCESS: ALL CALIBRATED SPECIES MODEL VERIFICATION CHECKS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
