"""Model Registry managing per-species empirical model artifact loading and inference."""

import json
from pathlib import Path

from packages.ovon_core.modeling.model_trainer import EmpiricalModelArtifact


class ModelRegistry:
    """Registry managing species-level empirical model artifacts."""

    def __init__(self, models_base_dir: Path | str = "data/derived/models") -> None:
        self.models_base_dir = Path(models_base_dir)
        self._artifacts_cache: dict[str, EmpiricalModelArtifact | None] = {}

    def get_model(
        self, concept_id: str, model_version: str = "1.0.0"
    ) -> EmpiricalModelArtifact | None:
        """Retrieve promoted EmpiricalModelArtifact for a specific concept ID, or None if unpromoted."""
        cache_key = f"{concept_id}:{model_version}"
        if cache_key in self._artifacts_cache:
            return self._artifacts_cache[cache_key]

        concept_slug = concept_id.split(":")[-1]
        manifest_path = self.models_base_dir / concept_slug / model_version / "model_manifest.json"

        if not manifest_path.exists():
            self._artifacts_cache[cache_key] = None
            return None

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            art_dict = manifest.get("artifact", {})
            if not art_dict:
                self._artifacts_cache[cache_key] = None
                return None

            artifact = EmpiricalModelArtifact(
                concept_id=art_dict.get("concept_id", concept_id),
                feature_names=tuple(art_dict.get("feature_names", ())),
                weights=tuple(art_dict.get("weights", ())),
                intercept=float(art_dict.get("intercept", 0.0)),
                means=tuple(art_dict.get("means", ())),
                stds=tuple(art_dict.get("stds", ())),
                brier_score=float(art_dict.get("brier_score", 1.0)),
                ece=float(art_dict.get("ece", 1.0)),
                status=art_dict.get("status", "provisional_heuristic"),
                training_blocks=tuple(art_dict.get("training_blocks", ())),
                test_blocks=tuple(art_dict.get("test_blocks", ())),
                model_version=model_version,
            )

            self._artifacts_cache[cache_key] = artifact
            return artifact
        except Exception:
            self._artifacts_cache[cache_key] = None
            return None
