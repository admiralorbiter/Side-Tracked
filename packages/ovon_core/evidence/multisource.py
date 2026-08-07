"""Multi-source presence observation normalization and DOI lineage engine for GBIF, iNaturalist, and eBird."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


class SourceDataOrigin(str, Enum):
    """External or internal source of occurrence evidence."""

    GBIF = "gbif"
    INATURALIST = "inaturalist"
    EBIRD_RECENT = "ebird_recent"
    SIDETRACK_WALK = "sidetrack_walk"


@dataclass(frozen=True, slots=True)
class SourceLineageRecord:
    """Source provenance and academic DOI attribution lineage record."""

    provider_name: str
    dataset_name: str
    dataset_version: str
    doi: str | None = None
    retrieval_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    license_terms: str = "CC-BY 4.0"


@dataclass(frozen=True, slots=True)
class NormalizedMultiSourceOccurrence:
    """Normalized multi-source species occurrence record bound to Sidetrack concept_id."""

    occurrence_id: UUID
    concept_id: UUID
    observed_at: datetime
    latitude: float
    longitude: float
    spatial_cell_id: str
    origin: SourceDataOrigin
    is_presence_only: bool
    lineage: SourceLineageRecord


class GBIFOccurrenceAdapter:
    """Normalizes raw GBIF species occurrence records into Sidetrack concept UUIDs."""

    def __init__(self, registry: TaxonConceptRegistry | None = None) -> None:
        self.registry = registry or TaxonConceptRegistry()

    def normalize_gbif_record(
        self,
        gbif_taxon_id: str,
        observed_at: datetime,
        lat: float,
        lon: float,
        spatial_cell_id: str,
        doi: str | None = None,
    ) -> NormalizedMultiSourceOccurrence | None:
        """Normalize a GBIF occurrence record to a canonical TaxonConcept UUID."""
        # Query concept registry for GBIF authority
        concept = self.registry.resolve_authority(
            authority="gbif_backbone", authority_taxon_id=f"gbif:taxon:{gbif_taxon_id}"
        )
        if not concept:
            # Fall back to eBird code resolution if passed as fallback
            concept = self.registry.get_concept_for_ebird_code(gbif_taxon_id)

        if not concept:
            return None

        lineage = SourceLineageRecord(
            provider_name="GBIF Secretariat",
            dataset_name="GBIF Occurrence Download",
            dataset_version="2026-v1",
            doi=doi,
        )

        return NormalizedMultiSourceOccurrence(
            occurrence_id=uuid4(),
            concept_id=concept.concept_id,
            observed_at=observed_at,
            latitude=lat,
            longitude=lon,
            spatial_cell_id=spatial_cell_id,
            origin=SourceDataOrigin.GBIF,
            is_presence_only=True,
            lineage=lineage,
        )


class INaturalistOccurrenceAdapter:
    """Normalizes Research Grade iNaturalist observations into Sidetrack concept UUIDs."""

    def __init__(self, registry: TaxonConceptRegistry | None = None) -> None:
        self.registry = registry or TaxonConceptRegistry()

    def normalize_inat_record(
        self,
        inat_taxon_id: str,
        observed_at: datetime,
        lat: float,
        lon: float,
        spatial_cell_id: str,
        quality_grade: str = "research",
    ) -> NormalizedMultiSourceOccurrence | None:
        """Normalize an iNaturalist observation record to a canonical TaxonConcept UUID."""
        if quality_grade != "research":
            return None

        concept = self.registry.resolve_authority(
            authority="inaturalist", authority_taxon_id=f"inat:taxon:{inat_taxon_id}"
        )
        if not concept:
            concept = self.registry.get_concept_for_ebird_code(inat_taxon_id)

        if not concept:
            return None

        lineage = SourceLineageRecord(
            provider_name="iNaturalist",
            dataset_name="iNaturalist Research-grade Observations",
            dataset_version="2026-v1",
        )

        return NormalizedMultiSourceOccurrence(
            occurrence_id=uuid4(),
            concept_id=concept.concept_id,
            observed_at=observed_at,
            latitude=lat,
            longitude=lon,
            spatial_cell_id=spatial_cell_id,
            origin=SourceDataOrigin.INATURALIST,
            is_presence_only=True,
            lineage=lineage,
        )


class MultiSourceOccurrenceDeduplicator:
    """Deduplicates overlapping multi-source occurrences within spatial-temporal resolution windows."""

    @classmethod
    def deduplicate(
        cls,
        records: list[NormalizedMultiSourceOccurrence],
        time_window_minutes: float = 60.0,
    ) -> list[NormalizedMultiSourceOccurrence]:
        """Deduplicate records sharing same concept_id, spatial_cell_id, and close time window."""
        deduped: list[NormalizedMultiSourceOccurrence] = []
        seen_keys: set[tuple[UUID, str, int]] = set()

        for rec in sorted(records, key=lambda r: r.observed_at):
            # Bin time to 1-hour windows
            time_bin = int(rec.observed_at.timestamp() // (time_window_minutes * 60))
            key = (rec.concept_id, rec.spatial_cell_id, time_bin)

            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(rec)

        return deduped
