"""Complete-Checklist Zero-Filling Matrix Engine with Sidetrack Taxon Concept Rollup & Masking."""

from dataclasses import dataclass
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

        # 1. Strict Event Identity Validation
        if effort.sampling_event_id != event.sampling_event_id:
            raise ValueError(
                f"Event identity mismatch: effort sampling_event_id '{effort.sampling_event_id}' "
                f"does not match event sampling_event_id '{event.sampling_event_id}'"
            )

        for obs in observations:
            if obs.sampling_event_id != event.sampling_event_id:
                raise ValueError(
                    f"Event identity mismatch: observation sampling_event_id '{obs.sampling_event_id}' "
                    f"does not match event sampling_event_id '{event.sampling_event_id}'"
                )

        # 2. Enforce zero-filling non-detection boundary validation
        is_complete = event.all_species_reported
        is_valid_effort = effort.is_effort_valid

        detected_concept_ids: set[UUID] = set()
        masked_concept_ids: set[UUID] = set()
        cell_map: dict[UUID, MatrixObservationCell] = {}

        for obs in observations:
            is_slash_obs = obs.is_slash or ("/" in obs.raw_species_code)

            if is_slash_obs:
                # Resolve candidate concepts for slash (e.g. dowwoo/haiwoo -> {Downy, Hairy})
                candidates = self.registry.get_slash_candidate_concepts(obs.raw_species_code)
                slash_concept = self.registry.get_concept_for_ebird_code(obs.raw_species_code)
                if slash_concept:
                    masked_concept_ids.add(slash_concept.concept_id)

                for cand in candidates:
                    masked_concept_ids.add(cand.concept_id)
                    if cand.concept_id not in detected_concept_ids:
                        cell_map[cand.concept_id] = MatrixObservationCell(
                            sampling_event_id=event.sampling_event_id,
                            concept_id=cand.concept_id,
                            detected=None,
                            raw_species_code=obs.raw_species_code,
                            is_zero_filled=False,
                        )
            else:
                concept = self.registry.get_concept_for_ebird_code(obs.raw_species_code)
                if not concept:
                    continue

                # Collect target concepts (concept itself + parent concept if subspecies/ISSF)
                target_concepts = [concept]
                if concept.parent_concept_id:
                    parent = self.registry.get_by_id(concept.parent_concept_id)
                    if parent:
                        target_concepts.append(parent)

                for target in target_concepts:
                    detected_concept_ids.add(target.concept_id)
                    cell_map[target.concept_id] = MatrixObservationCell(
                        sampling_event_id=event.sampling_event_id,
                        concept_id=target.concept_id,
                        detected=1,
                        raw_species_code=obs.raw_species_code,
                        is_zero_filled=False,
                    )

        # 3. Zero-filling non-detections (only if complete checklist and effort valid)
        if is_complete and is_valid_effort:
            EvidenceBoundaryValidator.validate_non_detection(
                EvidenceTier.EBIRD_COMPLETE_CHECKLIST,
                is_complete_checklist=True,
                is_effort_valid=True,
            )
            for cid in candidate_concept_ids:
                if cid not in detected_concept_ids and cid not in masked_concept_ids:
                    cell_map[cid] = MatrixObservationCell(
                        sampling_event_id=event.sampling_event_id,
                        concept_id=cid,
                        detected=0,
                        raw_species_code="non_detection",
                        is_zero_filled=True,
                    )

        return list(cell_map.values())
