"""CLI Tool to verify Joint Occupancy and Detectability Models."""

import sys

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY
from packages.ovon_core.modeling.effort import EffortProtocolVector
from packages.ovon_core.modeling.joint_model import JointOccupancyDetectabilityModel
from packages.ovon_core.modeling.joint_service import JointModelService
from packages.ovon_core.modeling.phenology import DiurnalPhenologyKernel


def main() -> None:
    """Run Joint Occupancy and Detectability Model verification suite."""
    print("=" * 60)
    print("  SIDETRACK JOINT OCCUPANCY & DETECTABILITY VERIFICATION")
    print("=" * 60)

    # 1. Test Observer Effort Protocol Model
    effort_45 = EffortProtocolVector(survey_duration_minutes=45.0, walking_speed_kmh=2.5)
    effort_15 = EffortProtocolVector(survey_duration_minutes=15.0, walking_speed_kmh=2.5)
    scaling_45 = effort_45.calculate_effort_scaling_factor()
    scaling_15 = effort_15.calculate_effort_scaling_factor()
    assert scaling_45 > scaling_15
    print(
        f"[OK] Observer Effort Model: 45m effort scaling ({scaling_45:.3f}) > 15m effort scaling ({scaling_15:.3f})"
    )

    # 2. Test Diurnal Phenology Kernel (Solar Altitude Angle)
    kernel = DiurnalPhenologyKernel()
    p_dawn = kernel.calculate_vocal_detectability(5.0)  # Dawn chorus peak
    p_midday = kernel.calculate_vocal_detectability(50.0)  # Midday slump
    assert p_dawn > p_midday
    print(
        f"[OK] Diurnal Solar Phenology: Dawn chorus detectability ({p_dawn*100:.1f}%) > Midday detectability ({p_midday*100:.1f}%)"
    )

    # 3. Test Dual-Likelihood Model Disentanglement
    model = JointOccupancyDetectabilityModel("sidetrack_concept:american_robin")
    vec = EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(65.0, 10.0, 40.0, 260.0, 2.0),
    )
    result = model.predict_joint(vec, effort_45)
    assert "latent_occupancy" in result
    assert "observer_detectability" in result
    assert "joint_encounter_probability" in result
    assert result["joint_encounter_probability"] <= result["latent_occupancy"]
    print(
        f"[OK] Dual-Likelihood Disentanglement: Latent Occupancy (psi)={result['latent_occupancy']*100:.1f}%, Detectability (p)={result['observer_detectability']*100:.1f}%, Joint P={result['joint_encounter_probability']*100:.1f}%"
    )

    # 4. Test Joint Model Service
    service = JointModelService()
    summary = service.predict_for_route(ROUTE_BIRDY)
    assert summary.overall_calibration_status == "platt_calibrated"
    assert len(summary.joint_predictions) > 0
    jp = summary.joint_predictions[0]
    assert jp.joint_encounter_probability == round(
        jp.latent_occupancy * jp.observer_detectability, 3
    )
    print(
        f"[OK] JointModelService Verified: Generated dual breakdown summary for {len(summary.joint_predictions)} species"
    )

    print("=" * 60)
    print("SUCCESS: ALL JOINT OCCUPANCY & DETECTABILITY CHECKS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
