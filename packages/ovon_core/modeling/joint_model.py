"""Dual-Likelihood Joint Occupancy and Detectability Model Engine."""

from packages.ovon_core.domain.environmental_vector import EnvironmentalFeatureVector
from packages.ovon_core.modeling.calibrated_model import CalibratedSpeciesModel
from packages.ovon_core.modeling.effort import EffortProtocolVector
from packages.ovon_core.modeling.phenology import DiurnalPhenologyKernel


class JointOccupancyDetectabilityModel:
    """Disentangles latent occupancy psi_s(x) from observer detectability p_s(x, t, u)."""

    def __init__(self, concept_id: str) -> None:
        self.concept_id = concept_id
        self.occupancy_model = CalibratedSpeciesModel(concept_id=concept_id)
        self.phenology_kernel = DiurnalPhenologyKernel()

    def predict_occupancy(self, env_vector: EnvironmentalFeatureVector) -> float:
        """Predict latent species occupancy / habitat suitability psi_s(x) in [0.0, 1.0]."""
        raw_prob = self.occupancy_model.predict_proba(env_vector)
        # Latent occupancy is independent of observer effort or time-of-day slump
        return max(0.05, min(0.98, raw_prob * 1.15))

    def predict_detectability(
        self, env_vector: EnvironmentalFeatureVector, effort: EffortProtocolVector
    ) -> float:
        """Predict observer detectability p_s(x, t, u) given effort and solar elevation angle."""
        group = "nocturnal" if "owl" in self.concept_id else "songbird"
        diurnal_mult = self.phenology_kernel.calculate_vocal_detectability(
            effort.sun_altitude_degrees, species_group=group
        )
        effort_scaling = effort.calculate_effort_scaling_factor(baseline_minutes=45.0)

        # Detectability combines diurnal vocal behavior and survey duration
        p_det = diurnal_mult * (0.6 + 0.4 * effort_scaling)
        return max(0.20, min(0.95, p_det))

    def predict_joint(
        self, env_vector: EnvironmentalFeatureVector, effort: EffortProtocolVector
    ) -> dict[str, float]:
        """Compute dual-likelihood breakdown: latent occupancy (psi), detectability (p), and joint probability (P)."""
        psi = self.predict_occupancy(env_vector)
        p_det = self.predict_detectability(env_vector, effort)
        encounter_prob = max(0.01, min(0.99, psi * p_det))

        return {
            "latent_occupancy": round(psi, 3),
            "observer_detectability": round(p_det, 3),
            "joint_encounter_probability": round(encounter_prob, 3),
        }
