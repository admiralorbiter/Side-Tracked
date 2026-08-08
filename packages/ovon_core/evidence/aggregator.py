"""Multi-Source Evidence Aggregator and Lineage Deduplicator."""

from typing import Sequence

from packages.ovon_core.domain.evidence import NormalizedOccurrenceEvidence
from packages.ovon_core.evidence.deduplicator import EvidenceDeduplicator
from packages.ovon_core.evidence.providers import BaseOccurrenceProvider


class MultiSourceEvidenceAggregator(BaseOccurrenceProvider):
    """Aggregates occurrence streams across multiple adapters and collapses syndicated duplicates."""

    def __init__(self, providers: Sequence[BaseOccurrenceProvider] | None = None) -> None:
        self.providers = tuple(providers) if providers else ()
        self.deduplicator = EvidenceDeduplicator()

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        """Fetch and combine normalized occurrence records across all active providers."""
        all_records: list[NormalizedOccurrenceEvidence] = []

        for p in self.providers:
            try:
                recs = p.fetch_occurrences(bounding_box, concept_ids, days_window=days_window)
                all_records.extend(recs)
            except Exception:
                continue

        # Deduplicate records across eBird, GBIF, and iNaturalist
        return self.deduplicator.deduplicate(all_records)
