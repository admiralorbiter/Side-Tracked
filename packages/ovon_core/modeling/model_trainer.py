"""Empirical Encounter Model Trainer with Inference-Time Feature Standardization and Strict Holdout Validation Gates."""

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from packages.ovon_core.modeling.calibration_gate import CalibrationGate, CalibrationMetrics
from packages.ovon_core.modeling.dataset_builder import AnalyticalSamplingRow
from packages.ovon_core.modeling.spatial_cross_validator import SpatialHoldoutCrossValidator


@dataclass(frozen=True, slots=True)
class EmpiricalModelArtifact:
    """Immutable trained model artifact containing standardized weights, means, stds, and evaluation manifest."""

    concept_id: str
    feature_names: tuple[str, ...]
    weights: tuple[float, ...]
    intercept: float
    means: tuple[float, ...]
    stds: tuple[float, ...]
    brier_score: float
    ece: float
    status: str  # "calibrated_promoted", "insufficient_evaluation_data", "provisional_heuristic", or "fixture_verified"
    training_blocks: tuple[str, ...]
    test_blocks: tuple[str, ...]
    model_version: str = "1.0.0"

    def predict_probability(self, features: dict[str, float]) -> float:
        """Compute calibrated probability by standardizing inputs using saved training feature means and stds."""
        x_raw = np.array(
            [features.get(fname, 0.0) for fname in self.feature_names], dtype=np.float64
        )
        means = np.array(self.means, dtype=np.float64)
        stds = np.array(self.stds, dtype=np.float64) + 1e-6

        # Standardize input features at inference time using saved training parameters
        x_scaled = (x_raw - means) / stds

        w_scaled = np.array(self.weights, dtype=np.float64)
        z = float(np.dot(w_scaled, x_scaled) + self.intercept)
        p_raw = 1.0 / (1.0 + np.exp(-np.clip(z, -15.0, 15.0)))
        return round(float(np.clip(p_raw, 0.01, 0.99)), 4)


class EmpiricalEncounterModelTrainer:
    """Trainer for fitting logistic encounter models on spatial block splits and evaluating via CalibrationGate."""

    def __init__(self, output_base_dir: Path | str = "data/derived/models") -> None:
        self.output_base_dir = Path(output_base_dir)
        self.validator = SpatialHoldoutCrossValidator(test_ratio=0.3, random_seed=42)
        self.gate = CalibrationGate(max_brier_score=0.15, max_ece=0.08)

    def train_and_evaluate(
        self,
        analytical_rows: Sequence[AnalyticalSamplingRow],
        focal_concept_id: str = "sidetrack_concept:northern_cardinal",
        model_version: str = "1.0.0",
        is_official_dataset: bool = False,
    ) -> tuple[EmpiricalModelArtifact, Path]:
        """Fit empirical model weights, evaluate out-of-fold calibration gate, and persist artifact."""
        concept_rows = [r for r in analytical_rows if r.concept_id == focal_concept_id]
        if not concept_rows:
            concept_rows = list(analytical_rows)

        row_dicts = [r.to_dict() for r in concept_rows]
        split = self.validator.split_rows(row_dicts)

        train_rows = split.training_rows
        test_rows = split.test_rows

        feature_names = (
            "canopy_cover_percent",
            "impervious_surface_percent",
            "elevation_m",
            "slope_gradient_percent",
            "water_edge_distance_m",
            "duration_minutes",
            "solar_altitude_degrees",
        )

        def extract_X_y(rows: list[dict]):
            X_list = []
            y_list = []
            for r in rows:
                x_vec = [float(r.get(fn, 0.0)) for fn in feature_names]
                X_list.append(x_vec)
                y_list.append(int(r.get("detected", 0)))
            return np.array(X_list, dtype=np.float64), np.array(y_list, dtype=np.int32)

        X_train, y_train = extract_X_y(train_rows)
        X_test, y_test = extract_X_y(test_rows)

        n_feat = len(feature_names)
        weights = np.zeros(n_feat, dtype=np.float64)
        intercept = 0.0
        mean = np.zeros(n_feat, dtype=np.float64)
        std = np.ones(n_feat, dtype=np.float64)

        if len(y_train) > 0 and np.std(y_train) > 0:
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0) + 1e-6
            X_scaled = (X_train - mean) / std

            lr = 0.05
            for _ in range(300):
                logits = np.dot(X_scaled, weights) + intercept
                preds = 1.0 / (1.0 + np.exp(-np.clip(logits, -15.0, 15.0)))
                err = preds - y_train
                weights -= lr * np.dot(X_scaled.T, err) / len(y_train)
                intercept -= lr * np.mean(err)

        # Prohibit synthetic holdout fallback!
        if len(X_test) == 0:
            status_str = "insufficient_evaluation_data"
            brier_score = 1.0
            ece = 1.0
        else:
            X_test_scaled = (X_test - mean) / (std + 1e-6)
            logits_test = np.dot(X_test_scaled, weights) + intercept
            preds_test = 1.0 / (1.0 + np.exp(-np.clip(logits_test, -15.0, 15.0)))

            metrics = self.gate.evaluate(predictions=list(preds_test), outcomes=list(y_test))
            brier_score = metrics.brier_score
            ece = metrics.ece

            if not is_official_dataset:
                status_str = "fixture_verified"
            else:
                status_str = metrics.status

        artifact = EmpiricalModelArtifact(
            concept_id=focal_concept_id,
            feature_names=feature_names,
            weights=tuple(round(float(w), 6) for w in weights),
            intercept=round(float(intercept), 6),
            means=tuple(round(float(m), 4) for m in mean),
            stds=tuple(round(float(s), 4) for s in std),
            brier_score=round(brier_score, 4),
            ece=round(ece, 4),
            status=status_str,
            training_blocks=split.training_block_ids,
            test_blocks=split.test_block_ids,
            model_version=model_version,
        )

        concept_slug = focal_concept_id.split(":")[-1]
        model_dir = self.output_base_dir / concept_slug / model_version
        model_dir.mkdir(parents=True, exist_ok=True)

        artifact_dict = asdict(artifact)
        schema_bytes = json.dumps(artifact_dict, sort_keys=True).encode("utf-8")
        schema_hash = hashlib.sha256(schema_bytes).hexdigest()

        manifest = {
            "model_version": model_version,
            "concept_id": focal_concept_id,
            "schema_hash": schema_hash,
            "status": status_str,
            "brier_score": brier_score,
            "ece": ece,
            "feature_count": len(feature_names),
            "train_block_count": len(split.training_block_ids),
            "test_block_count": len(split.test_block_ids),
            "is_official_dataset": is_official_dataset,
            "artifact": artifact_dict,
        }

        manifest_file = model_dir / "model_manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return artifact, manifest_file
