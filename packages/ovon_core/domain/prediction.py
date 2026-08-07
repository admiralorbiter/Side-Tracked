"""Prediction Domain Models and Provenance Tracking."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class PredictionProvenance:
    """Explicit metadata tracking prediction provenance and empirical calibration status."""

    model_id: str
    model_version: str
    training_cutoff_date: str
    calibration_status: str  # "platt_calibrated", "uncalibrated", "degraded_fallback"
    brier_score: float | None = None
    ece_score: float | None = None
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, slots=True)
class CalibratedSpeciesPrediction:
    """Empirical encounter probability prediction for a focal species."""

    concept_id: str
    common_name: str
    scientific_name: str
    encounter_probability: float  # P(Y_s = 1 | x, t) calibrated in [0.0, 1.0]
    relative_opportunity_score: float  # Normalized score for UI ranking
    confidence_tier: str  # "high", "medium", "low"
    provenance: PredictionProvenance

    def __post_init__(self) -> None:
        if not (0.0 <= self.encounter_probability <= 1.0):
            raise ValueError(
                f"Encounter probability ({self.encounter_probability}) must be in [0.0, 1.0]."
            )


@dataclass(frozen=True, slots=True)
class RoutePredictionSummary:
    """Read model containing empirical calibrated predictions for a planned route option."""

    route_id: str
    generated_at: str
    predictions: tuple[CalibratedSpeciesPrediction, ...]
    overall_calibration_status: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert prediction summary to JSON dictionary."""
        return {
            "route_id": self.route_id,
            "generated_at": self.generated_at,
            "overall_calibration_status": self.overall_calibration_status,
            "prediction_count": len(self.predictions),
            "predictions": [
                {
                    "concept_id": p.concept_id,
                    "common_name": p.common_name,
                    "encounter_probability": round(p.encounter_probability, 3),
                    "confidence_tier": p.confidence_tier,
                    "model_id": p.provenance.model_id,
                    "calibration_status": p.provenance.calibration_status,
                }
                for p in self.predictions
            ],
            "limitations": list(self.limitations),
        }
