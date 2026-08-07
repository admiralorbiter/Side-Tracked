"""Modeling Dataset Builder and Survey Matrix Assembly."""

from dataclasses import dataclass

from packages.ovon_core.domain.environmental_vector import (
    SIDETRACK_ENV_SCHEMA_V1,
    EnvironmentalFeatureVector,
)


@dataclass(frozen=True, slots=True)
class ModelingSample:
    """Individual survey event training sample with environmental features, label, and spatial block."""

    sample_id: str
    concept_id: str
    detected: int  # 1 for detection, 0 for non-detection on eligible complete checklist
    feature_vector: EnvironmentalFeatureVector
    spatial_block_id: str  # H3 res-6 spatial cell for spatial block holdout cross-validation
    survey_duration_minutes: float = 45.0


class ModelingDatasetBuilder:
    """Compiles complete-checklist survey events into training dataset matrices."""

    def build_dataset_for_concept(
        self, concept_id: str, sample_count: int = 120
    ) -> list[ModelingSample]:
        """Build deterministic training dataset for a focal species concept."""
        samples: list[ModelingSample] = []

        # Generate realistic spatial samples across 4 H3 spatial blocks in Kansas City pilot area
        blocks = ["86265672fffffff", "8626560d3ffffff", "8626560deffffff", "86265660effffff"]

        for i in range(sample_count):
            block_id = blocks[i % len(blocks)]

            if "woodpecker" in concept_id:
                if i % 2 == 0:
                    # Forest canopy sample -> Woodpecker Present
                    canopy, impervious, water_dist, elevation, slope = 75.0, 5.0, 200.0, 280.0, 5.0
                    detected = 1
                else:
                    # Open lawn sample -> Woodpecker Absent
                    canopy, impervious, water_dist, elevation, slope = 10.0, 30.0, 450.0, 250.0, 1.0
                    detected = 0
            else:
                # American Robin & Northern Cardinal
                if i % 2 == 0:
                    # Park & Water Edge sample -> Present
                    canopy, impervious, water_dist, elevation, slope = 30.0, 10.0, 50.0, 260.0, 2.0
                    detected = 1
                else:
                    # Dense commercial urban sample -> Absent
                    canopy, impervious, water_dist, elevation, slope = 5.0, 75.0, 600.0, 240.0, 1.0
                    detected = 0

            vec = EnvironmentalFeatureVector(
                schema=SIDETRACK_ENV_SCHEMA_V1,
                values=(canopy, impervious, water_dist, elevation, slope),
            )

            samples.append(
                ModelingSample(
                    sample_id=f"sample_{concept_id}_{i}",
                    concept_id=concept_id,
                    detected=detected,
                    feature_vector=vec,
                    spatial_block_id=block_id,
                )
            )

        return samples
