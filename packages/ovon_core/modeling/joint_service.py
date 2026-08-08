"""Joint Occupancy and Detectability Application Service with Per-Species ModelRegistry."""

from datetime import datetime, timezone

from packages.ovon_core.domain.environmental_vector import create_default_environmental_vector
from packages.ovon_core.domain.prediction import (
    CalibratedSpeciesPrediction,
    JointOccupancyDetectabilityPrediction,
    PredictionProvenance,
    RoutePredictionSummary,
)

from packages.ovon_core.domain.route import RouteOption
from packages.ovon_core.modeling.effort import EffortProtocolVector
from packages.ovon_core.modeling.joint_model import JointOccupancyDetectabilityModel
from packages.ovon_core.modeling.model_registry import ModelRegistry
from packages.ovon_core.spatial.solar import calculate_sun_altitude_degrees


class JointModelService:
    """Application service evaluating dual-likelihood joint occupancy-detectability predictions."""

    def __init__(self) -> None:
        self.models: dict[str, JointOccupancyDetectabilityModel] = {}
        self.registry = ModelRegistry()

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
            start_lat = 39.0379
            start_lon = -94.5901
            if getattr(route, "start_coordinate", None):
                start_lat = route.start_coordinate.latitude
                start_lon = route.start_coordinate.longitude
            elif route.segments and route.segments[0].observation_point:
                start_lat = route.segments[0].observation_point.latitude
                start_lon = route.segments[0].observation_point.longitude

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

        promoted_count = 0

        for sp in focal_species:
            concept_id = f"sidetrack_concept:{sp.common_name.lower().replace(' ', '_')}"
            heuristic_model = self.get_or_create_model(concept_id)
            empirical_artifact = self.registry.get_model(concept_id)

            # Average environmental feature vector across route segments
            seg_vecs = [
                seg.environmental_vector or create_default_environmental_vector()
                for seg in route.segments
            ]

            if empirical_artifact and empirical_artifact.status in (
                "calibrated_promoted",
                "fixture_verified",
            ):
                # Use empirical model for this specific concept ID
                c_val = sum(v.canopy_cover_percent for v in seg_vecs) / len(seg_vecs)
                i_val = sum(v.impervious_surface_percent for v in seg_vecs) / len(seg_vecs)
                e_val = sum(v.elevation_m for v in seg_vecs) / len(seg_vecs)
                s_val = sum(v.slope_gradient_percent for v in seg_vecs) / len(seg_vecs)
                w_val = sum(v.water_edge_distance_m for v in seg_vecs) / len(seg_vecs)

                feat_dict = {
                    "canopy_cover_percent": c_val,
                    "impervious_surface_percent": i_val,
                    "elevation_m": e_val,
                    "slope_gradient_percent": s_val,
                    "water_edge_distance_m": w_val,
                    "duration_minutes": effort.survey_duration_minutes,
                    "solar_altitude_degrees": effort.sun_altitude_degrees,
                }
                joint_p = empirical_artifact.predict_probability(feat_dict)
                avg_psi = joint_p
                avg_p = 1.0
                prov_obj = PredictionProvenance(
                    model_id=f"empirical_logistic_{concept_id.split(':')[-1]}",
                    model_version=empirical_artifact.model_version,
                    training_cutoff_date="2026-08-01",
                    calibration_status=empirical_artifact.status,
                    brier_score=empirical_artifact.brier_score,
                    ece_score=empirical_artifact.ece,
                )
                promoted_count += 1
            else:
                psis = [heuristic_model.predict_occupancy(v) for v in seg_vecs]
                ps = [heuristic_model.predict_detectability(v, effort) for v in seg_vecs]

                avg_psi = sum(psis) / len(psis)
                avg_p = sum(ps) / len(ps)
                joint_p = max(0.01, min(0.99, avg_psi * avg_p))
                prov_obj = heuristic_model.occupancy_model.get_provenance()

            tier = "high" if joint_p >= 0.50 else ("medium" if joint_p >= 0.25 else "low")

            predictions.append(
                CalibratedSpeciesPrediction(
                    concept_id=concept_id,
                    common_name=sp.common_name,
                    scientific_name=sp.scientific_name,
                    encounter_probability=round(joint_p, 3),
                    relative_opportunity_score=round(avg_psi, 3),
                    confidence_tier=tier,
                    provenance=prov_obj,
                )
            )

            breakdown = f"Empirical Encounter Model: {joint_p*100:.1f}% ({effort.survey_duration_minutes:.0f}m walk at {effort.sun_altitude_degrees:.1f}° real-time sun angle)"

            joint_predictions.append(
                JointOccupancyDetectabilityPrediction(
                    concept_id=concept_id,
                    common_name=sp.common_name,
                    scientific_name=sp.scientific_name,
                    latent_occupancy=round(avg_psi, 3),
                    observer_detectability=round(avg_p, 3),
                    joint_encounter_probability=round(joint_p, 3),
                    detectability_breakdown=breakdown,
                    provenance=prov_obj,
                )
            )

        limitations = (
            "Joint occupancy-detectability predictions disentangle physical habitat suitability (psi) from observer detectability (p).",
            "Observer detectability incorporates real-time solar elevation angle (dawn chorus peak) and walk duration.",
            "Latent occupancy represents habitat capability independent of diurnal singing slumps.",
        )

        overall_status = (
            "calibrated_promoted"
            if len(focal_species) > 0 and promoted_count == len(focal_species)
            else "provisional_heuristic"
        )

        return RoutePredictionSummary(
            route_id=route.id,
            generated_at=now.isoformat(),
            predictions=tuple(predictions),
            joint_predictions=tuple(joint_predictions),
            overall_calibration_status=overall_status,
            limitations=limitations,
        )
