"""Unit tests for Joint Occupancy and Detectability Architecture."""

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.modeling.effort import EffortProtocolVector
from packages.ovon_core.modeling.joint_model import JointOccupancyDetectabilityModel
from packages.ovon_core.modeling.joint_service import JointModelService
from packages.ovon_core.modeling.phenology import DiurnalPhenologyKernel


def test_effort_protocol_vector():
    effort1 = EffortProtocolVector(survey_duration_minutes=60.0)
    effort2 = EffortProtocolVector(survey_duration_minutes=15.0)

    s1 = effort1.calculate_effort_scaling_factor()
    s2 = effort2.calculate_effort_scaling_factor()
    assert s1 > s2


def test_diurnal_phenology_kernel():
    kernel = DiurnalPhenologyKernel()
    p_dawn = kernel.calculate_vocal_detectability(5.0, "songbird")
    p_midday = kernel.calculate_vocal_detectability(50.0, "songbird")
    assert p_dawn > p_midday

    p_owl_night = kernel.calculate_vocal_detectability(-12.0, "nocturnal")
    p_owl_day = kernel.calculate_vocal_detectability(40.0, "nocturnal")
    assert p_owl_night > p_owl_day


def test_joint_occupancy_detectability_model():
    model = JointOccupancyDetectabilityModel("sidetrack_concept:american_robin")
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(60.0, 10.0, 50.0, 260.0, 2.0),
    )
    effort = EffortProtocolVector(survey_duration_minutes=45.0, sun_altitude_degrees=10.0)

    res = model.predict_joint(vec, effort)
    assert 0.0 <= res["latent_occupancy"] <= 1.0
    assert 0.0 <= res["observer_detectability"] <= 1.0
    assert 0.0 <= res["joint_encounter_probability"] <= 1.0
    assert res["joint_encounter_probability"] <= res["latent_occupancy"]


def test_joint_model_service():
    service = JointModelService()
    summary = service.predict_for_route(ROUTE_BIRDY)

    assert summary.overall_calibration_status in ("provisional_heuristic", "calibrated_promoted")

    assert len(summary.predictions) > 0
    assert len(summary.joint_predictions) > 0

    jp = summary.joint_predictions[0]
    assert 0.0 <= jp.latent_occupancy <= 1.0
    assert 0.0 <= jp.observer_detectability <= 1.0
    assert "Habitat Quality" in jp.detectability_breakdown
