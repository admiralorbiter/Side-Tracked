"""Lineage-Aware Multi-Source Occurrence Deduplicator."""

from collections import defaultdict
from typing import Sequence

from packages.ovon_core.domain.evidence import NormalizedOccurrenceEvidence


class EvidenceDeduplicator:
    """Deduplicates multi-platform occurrences (e.g. iNaturalist research-grade records exported to GBIF)."""

    def deduplicate(
        self, occurrences: Sequence[NormalizedOccurrenceEvidence]
    ) -> list[NormalizedOccurrenceEvidence]:
        """Group occurrence records by lineage and return deduplicated occurrences with duplicate_cluster_id set."""
        if not occurrences:
            return []

        # 1. Exact external linkage grouping (e.g. iNat observation ID in GBIF source_occurrence_id)
        clusters: dict[str, list[NormalizedOccurrenceEvidence]] = defaultdict(list)

        for occ in occurrences:
            # Generate lineage key: matching concept, day, and 3-decimal rounded coordinate (~110m)
            date_key = occ.observed_at.strftime("%Y-%m-%d")
            lat_round = round(occ.latitude, 3)
            lon_round = round(occ.longitude, 3)
            cluster_key = f"{occ.concept_id}_{date_key}_{lat_round}_{lon_round}"
            clusters[cluster_key].append(occ)

        deduplicated: list[NormalizedOccurrenceEvidence] = []

        for c_key, items in clusters.items():
            cluster_id = f"cluster_{c_key}"

            # Prefer native source origin: ebird_recent > inat > gbif > ebd
            origin_priority = {
                "ebird_recent": 0,
                "inat": 1,
                "sidetrack_discovery": 2,
                "ebd": 3,
                "gbif": 4,
            }
            sorted_items = sorted(items, key=lambda x: origin_priority.get(x.source_origin, 5))
            canonical = sorted_items[0]

            # Re-instantiate canonical object with duplicate_cluster_id set if items > 1
            updated = NormalizedOccurrenceEvidence(
                occurrence_id=canonical.occurrence_id,
                concept_id=canonical.concept_id,
                source_origin=canonical.source_origin,
                source_occurrence_id=canonical.source_occurrence_id,
                original_scientific_name=canonical.original_scientific_name,
                taxonomy_authority=canonical.taxonomy_authority,
                observed_at=canonical.observed_at,
                latitude=canonical.latitude,
                longitude=canonical.longitude,
                location_semantics=canonical.location_semantics,
                geoprivacy=canonical.geoprivacy,
                coordinate_uncertainty_m=canonical.coordinate_uncertainty_m,
                source_event_id=canonical.source_event_id,
                source_dataset_id=canonical.source_dataset_id,
                source_record_url=canonical.source_record_url,
                is_presence_only=canonical.is_presence_only,
                sensitive=canonical.sensitive,
                observation_license=canonical.observation_license,
                lineage_id=canonical.lineage_id,
                duplicate_cluster_id=cluster_id if len(items) > 1 else None,
            )
            deduplicated.append(updated)

        return deduplicated
