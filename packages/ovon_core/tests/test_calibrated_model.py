"""Unit tests for Calibrated Species Model, Platt scaling, dataset builder, and evaluator."""

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.modeling.calibrated_model import CalibratedSpeciesModel, PlattCalibrator
from packages.ovon_core.modeling.dataset import ModelingDatasetBuilder
from packages.ovon_core.modeling.evaluator import SpatialBlockEvaluator
from packages.ovon_core.modeling.service import CalibratedModelService


def test_platt_calibrator():
    calibrator = PlattCalibrator(a=-1.0, b=0.0)
    prob_mid = calibrator.calibrate(0.0)
    assert abs(prob_mid - 0.5) < 0.01

    prob_high = calibrator.calibrate(3.0)
    assert prob_high < 0.1

    prob_low = calibrator.calibrate(-3.0)
    assert prob_low > 0.9


def test_modeling_dataset_builder():
    builder = ModelingDatasetBuilder()
    samples = builder.build_dataset_for_concept("sidetrack_concept:cardinal", sample_count=60)
    assert len(samples) == 60
    assert all(s.detected in (0, 1) for s in samples)


def test_calibrated_species_model():
    model = CalibratedSpeciesModel("sidetrack_concept:woodpecker")
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(70.0, 5.0, 200.0, 275.0, 4.0),
    )
    prob = model.predict_proba(vec)
    assert 0.0 <= prob <= 1.0

    prov = model.get_provenance()
    assert prov.model_id == "sidetrack_occupancy_v1"
    assert prov.calibration_status == "platt_calibrated"


def test_spatial_block_evaluator():
    builder = ModelingDatasetBuilder()
    samples = builder.build_dataset_for_concept(
        "sidetrack_concept:american_robin", sample_count=100
    )

    model = CalibratedSpeciesModel("sidetrack_concept:american_robin")
    evaluator = SpatialBlockEvaluator()

    metrics = evaluator.evaluate_model(model, samples)
    assert "brier_score" in metrics
    assert "ece_score" in metrics
    assert metrics["brier_score"] < 0.15
    assert metrics["ece_score"] < 0.25


def test_calibrated_model_service():
    service = CalibratedModelService()
    summary = service.predict_for_route(ROUTE_BIRDY)

    assert summary.overall_calibration_status == "platt_calibrated"
    assert len(summary.predictions) > 0
    assert all(0.0 <= p.encounter_probability <= 1.0 for p in summary.predictions)
