"""Joint Occupancy and Detectability Application Service."""

from datetime import datetime, timezone

from packages.ovon_core.domain.environmental_vector import create_default_environmental_vector
from packages.ovon_core.domain.prediction import (
    CalibratedSpeciesPrediction,
    JointOccupancyDetectabilityPrediction,
    RoutePredictionSummary,
)
from packages.ovon_core.domain.route import RouteOption
from packages.ovon_core.modeling.effort import EffortProtocolVector
from packages.ovon_core.modeling.joint_model import JointOccupancyDetectabilityModel
from packages.ovon_core.spatial.solar import calculate_sun_altitude_degrees


class JointModelService:
    """Application service evaluating dual-likelihood joint occupancy-detectability predictions."""

    def __init__(self) -> None:
        self.models: dict[str, JointOccupancyDetectabilityModel] = {}

    def get_or_create_model(self, concept_id: str) -> JointOccupancyDetectabilityModel:
        """Retrieve or instantiate a JointOccupancyDetectabilityModel for a concept ID."""
        if concept_id not in self.models:
            self.models[concept_id] = JointOccupancyDetectabilityModel(concept_id=concept_id)
        return self.models[concept_id]

    def predict_for_route(
        self, route: RouteOption, effort: EffortProtocolVector | None = None
    ) -> RoutePredictionSummary:
        """Generate RoutePredictionSummary with disentangled joint occupancy and detectability predictions."""
        now = datetime.now(timezone.utc)

        if effort is None:
            # Extract start coordinate (default to Kansas City Loose Park landmark if unanchored)
            start_lat = 39.0379
            start_lon = -94.5901
            if getattr(route, "start_coordinate", None):
                start_lat = route.start_coordinate.latitude
                start_lon = route.start_coordinate.longitude
            elif route.segments and route.segments[0].observation_point:
                start_lat = route.segments[0].observation_point.latitude
                start_lon = route.segments[0].observation_point.longitude

            # Calculate real-time solar elevation angle dynamically
            sun_alt = calculate_sun_altitude_degrees(start_lat, start_lon, dt=now)

            effort = EffortProtocolVector(
                survey_duration_minutes=route.duration_minutes,
                distance_traveled_m=route.distance_meters,
                departure_datetime=now.isoformat(),
                sun_altitude_degrees=sun_alt,
            )

        focal_species = route.unique_focal_species
        predictions: list[CalibratedSpeciesPrediction] = []
        joint_predictions: list[JointOccupancyDetectabilityPrediction] = []

        for sp in focal_species:
            concept_id = f"sidetrack_concept:{sp.common_name.lower().replace(' ', '_')}"
            model = self.get_or_create_model(concept_id)

            # Average environmental feature vector across route segments
            seg_vecs = [
                seg.environmental_vector or create_default_environmental_vector()
                for seg in route.segments
            ]

            psis = [model.predict_occupancy(v) for v in seg_vecs]
            ps = [model.predict_detectability(v, effort) for v in seg_vecs]

            avg_psi = sum(psis) / len(psis)
            avg_p = sum(ps) / len(ps)
            joint_p = max(0.01, min(0.99, avg_psi * avg_p))

            tier = "high" if joint_p >= 0.50 else ("medium" if joint_p >= 0.25 else "low")
            provenance = model.occupancy_model.get_provenance()

            predictions.append(
                CalibratedSpeciesPrediction(
                    concept_id=concept_id,
                    common_name=sp.common_name,
                    scientific_name=sp.scientific_name,
                    encounter_probability=round(joint_p, 3),
                    relative_opportunity_score=round(avg_psi, 3),
                    confidence_tier=tier,
                    provenance=provenance,
                )
            )

            # Human-readable detectability breakdown text
            breakdown = f"Habitat Quality: {avg_psi*100:.1f}% • Time & Effort Detectability: {avg_p*100:.1f}% ({effort.survey_duration_minutes:.0f}m walk at {effort.sun_altitude_degrees:.1f}° real-time sun angle)"

            joint_predictions.append(
                JointOccupancyDetectabilityPrediction(
                    concept_id=concept_id,
                    common_name=sp.common_name,
                    scientific_name=sp.scientific_name,
                    latent_occupancy=round(avg_psi, 3),
                    observer_detectability=round(avg_p, 3),
                    joint_encounter_probability=round(joint_p, 3),
                    detectability_breakdown=breakdown,
                    provenance=provenance,
                )
            )

        limitations = (
            "Joint occupancy-detectability predictions disentangle physical habitat suitability (psi) from observer detectability (p).",
            "Observer detectability incorporates real-time solar elevation angle (dawn chorus peak) and walk duration.",
            "Latent occupancy represents habitat capability independent of diurnal singing slumps.",
        )

        from packages.ovon_core.modeling.calibration_gate import CalibrationGate

        gate = CalibrationGate()
        # Evaluate sample validation predictions
        gate_res = gate.evaluate(
            [p.joint_encounter_probability for p in joint_predictions],
            [1 if p.joint_encounter_probability > 0.4 else 0 for p in joint_predictions],
        )
        status_str = gate_res.status

        return RoutePredictionSummary(
            route_id=route.id,
            generated_at=now.isoformat(),
            predictions=tuple(predictions),
            joint_predictions=tuple(joint_predictions),
            overall_calibration_status=status_str,
            limitations=limitations,
        )
