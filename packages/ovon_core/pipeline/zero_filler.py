"""Complete-Checklist Zero-Filling Matrix Engine with Sidetrack Taxon Concept Rollup & Masking."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from packages.ovon_core.evidence.boundary import EvidenceBoundaryValidator, EvidenceTier
from packages.ovon_core.pipeline.ebd_ingest import SamplingEvent, SpeciesObservation
from packages.ovon_core.pipeline.effort_filter import NormalizedEffortVector
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


@dataclass(frozen=True, slots=True)
class MatrixObservationCell:
    """Single cell entry in the species presence/absence zero-filling matrix."""

    sampling_event_id: str
    concept_id: UUID
    detected: int | None  # 1 = presence, 0 = non-detection, None = masked slash/spuh
    raw_species_code: str
    is_zero_filled: bool


class ZeroFillingMatrixEngine:
    """Generates complete-checklist detection/non-detection matrices bound to canonical TaxonConcept UUIDs."""

    def __init__(self, registry: TaxonConceptRegistry | None = None) -> None:
        self.registry = registry or TaxonConceptRegistry()

    def generate_event_matrix(
        self,
        event: SamplingEvent,
        effort: NormalizedEffortVector,
        observations: list[SpeciesObservation],
        candidate_concept_ids: set[UUID],
    ) -> list[MatrixObservationCell]:
        """Generate presence/absence records for an event across candidate species concepts."""

        # 1. Enforce zero-filling non-detection boundary validation
        is_complete = event.all_species_reported
        is_valid_effort = effort.is_effort_valid

        # Map observations to concept IDs
        detected_concept_ids: set[UUID] = set()
        masked_concept_ids: set[UUID] = set()
        result_cells: list[MatrixObservationCell] = []

        for obs in observations:
            concept = self.registry.get_concept_for_ebird_code(obs.raw_species_code)
            if not concept:
                continue

            if obs.is_slash:
                # Mask slashes to prevent false presences/absences
                masked_concept_ids.add(concept.concept_id)
                result_cells.append(
                    MatrixObservationCell(
                        sampling_event_id=event.sampling_event_id,
                        concept_id=concept.concept_id,
                        detected=None,
                        raw_species_code=obs.raw_species_code,
                        is_zero_filled=False,
                    )
                )
            else:
                # Subspecies / ISSF rollup -> 1
                detected_concept_ids.add(concept.concept_id)
                result_cells.append(
                    MatrixObservationCell(
                        sampling_event_id=event.sampling_event_id,
                        concept_id=concept.concept_id,
                        detected=1,
                        raw_species_code=obs.raw_species_code,
                        is_zero_filled=False,
                    )
                )

        # Zero-filling non-detections (only if complete checklist and effort valid)
        if is_complete and is_valid_effort:
            EvidenceBoundaryValidator.validate_non_detection(
                EvidenceTier.EBIRD_COMPLETE_CHECKLIST,
                is_complete_checklist=True,
                is_effort_valid=True,
            )
            for cid in candidate_concept_ids:
                if cid not in detected_concept_ids and cid not in masked_concept_ids:
                    result_cells.append(
                        MatrixObservationCell(
                            sampling_event_id=event.sampling_event_id,
                            concept_id=cid,
                            detected=0,
                            raw_species_code="non_detection",
                            is_zero_filled=True,
                        )
                    )

        return result_cells
