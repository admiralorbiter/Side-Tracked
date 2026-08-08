"""Multi-Source Evidence Aggregator and Lineage Deduplicator."""

from dataclasses import dataclass, field
from typing import Sequence

from packages.ovon_core.domain.evidence import NormalizedOccurrenceEvidence
from packages.ovon_core.evidence.deduplicator import EvidenceDeduplicator
from packages.ovon_core.evidence.providers import BaseOccurrenceProvider, ProviderFetchResult


@dataclass(frozen=True, slots=True)
class AggregatedEvidenceResult:
    """Aggregated result containing deduplicated occurrences and structured provider status metadata."""

    records: tuple[NormalizedOccurrenceEvidence, ...]
    provider_results: dict[str, ProviderFetchResult] = field(default_factory=dict)

    @property
    def provider_statuses(self) -> dict[str, str]:
        """Return dict of provider statuses."""
        return {name: res.status for name, res in self.provider_results.items()}


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
        agg = self.fetch_aggregated_result(bounding_box, concept_ids, days_window=days_window)
        return list(agg.records)

    def fetch_aggregated_result(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> AggregatedEvidenceResult:
        """Fetch structured AggregatedEvidenceResult collecting records and provider statuses."""
        all_records: list[NormalizedOccurrenceEvidence] = []
        provider_results: dict[str, ProviderFetchResult] = {}

        for p in self.providers:
            provider_name = p.__class__.__name__.lower()
            try:
                res = p.fetch_result(bounding_box, concept_ids, days_window=days_window)
                provider_results[provider_name] = res
                all_records.extend(res.records)
            except Exception as exc:
                provider_results[provider_name] = ProviderFetchResult(
                    records=(), status="error", error_kind=str(exc)
                )

        # Deduplicate records across eBird, GBIF, and iNaturalist
        deduped = self.deduplicator.deduplicate(all_records)
        return AggregatedEvidenceResult(records=tuple(deduped), provider_results=provider_results)
