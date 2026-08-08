"""Occurrence Evidence Providers and Repository Adapters."""

from datetime import datetime, timedelta, timezone
from typing import Sequence

from packages.ovon_core.domain.evidence import (
    EvidenceLocation,
    NormalizedOccurrenceEvidence,
)
from packages.ovon_core.fixtures.routes_fixtures import CARDINAL, ROBIN, WOODPECKER


class BaseOccurrenceProvider:
    """Base interface for occurrence evidence providers."""

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        """Fetch normalized occurrences within spatial bounding box and time window."""
        raise NotImplementedError


class NoConfiguredEvidenceProvider(BaseOccurrenceProvider):
    """Production fallback provider when no live occurrence database is configured."""

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        return []


class MockRecentOccurrenceProvider(BaseOccurrenceProvider):
    """Provider adapter serving deterministic recent occurrence reports for pilot region."""

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        now = datetime.now(timezone.utc)
        min_lat, min_lon, max_lat, max_lon = bounding_box

        mid_lat = (min_lat + max_lat) / 2.0
        mid_lon = (min_lon + max_lon) / 2.0

        records: list[NormalizedOccurrenceEvidence] = []

        # 1. American Robin (eBird Recent API checklist location)
        robin_concept = "sidetrack_concept:american_robin"
        if not concept_ids or robin_concept in concept_ids:
            records.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id="occ_ebird_amerob_01",
                    concept_id=robin_concept,
                    source_origin="ebird_recent",
                    source_occurrence_id="wm-audio-2144744",
                    original_scientific_name=ROBIN.scientific_name,
                    taxonomy_authority="eBird-2025",
                    observed_at=now - timedelta(days=2),
                    latitude=mid_lat + 0.003,
                    longitude=mid_lon + 0.002,
                    location_semantics=EvidenceLocation.CHECKLIST_LOCATION,
                    geoprivacy="open",
                    coordinate_uncertainty_m=50.0,
                    source_dataset_id="eBird Recent Nearby API",
                    is_presence_only=True,
                    observation_license="CC BY-SA 3.0",
                )
            )

        # 2. Northern Cardinal (iNaturalist Open Record)
        cardinal_concept = "sidetrack_concept:northern_cardinal"
        if not concept_ids or cardinal_concept in concept_ids:
            records.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id="occ_inat_norcar_01",
                    concept_id=cardinal_concept,
                    source_origin="inat",
                    source_occurrence_id="inat-obs-981247",
                    original_scientific_name=CARDINAL.scientific_name,
                    taxonomy_authority="iNaturalist-2026",
                    observed_at=now - timedelta(days=5),
                    latitude=mid_lat - 0.002,
                    longitude=mid_lon - 0.001,
                    location_semantics=EvidenceLocation.OBSERVATION_POINT,
                    geoprivacy="open",
                    coordinate_uncertainty_m=15.0,
                    source_dataset_id="iNaturalist Research Grade",
                    is_presence_only=True,
                    observation_license="CC-BY 4.0",
                )
            )

        # 3. Downy Woodpecker (iNaturalist Obscured Record)
        dowwoo_concept = "sidetrack_concept:downy_woodpecker"
        if not concept_ids or dowwoo_concept in concept_ids:
            records.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id="occ_inat_dowwoo_obs",
                    concept_id=dowwoo_concept,
                    source_origin="inat",
                    source_occurrence_id="inat-obs-102938",
                    original_scientific_name=WOODPECKER.scientific_name,
                    taxonomy_authority="iNaturalist-2026",
                    observed_at=now - timedelta(days=7),
                    latitude=mid_lat + 0.015,  # Randomized within 0.2deg cell
                    longitude=mid_lon + 0.012,
                    location_semantics=EvidenceLocation.OBSCURED_PUBLIC_POINT,
                    geoprivacy="obscured",
                    coordinate_uncertainty_m=15000.0,
                    source_dataset_id="iNaturalist Research Grade",
                    is_presence_only=True,
                    observation_license="CC-BY-NC 4.0",
                )
            )

        # 4. Cedar Waxwing (GBIF Duplicate of iNat Cardinal to test deduplication)
        if not concept_ids or cardinal_concept in concept_ids:
            records.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id="occ_gbif_norcar_dup",
                    concept_id=cardinal_concept,
                    source_origin="gbif",
                    source_occurrence_id="gbif-norcar-981247",
                    original_scientific_name=CARDINAL.scientific_name,
                    taxonomy_authority="GBIF-2026",
                    observed_at=now - timedelta(days=5),
                    latitude=mid_lat - 0.002,
                    longitude=mid_lon - 0.001,
                    location_semantics=EvidenceLocation.OBSERVATION_POINT,
                    geoprivacy="open",
                    coordinate_uncertainty_m=20.0,
                    source_dataset_id="GBIF Occurrence Download",
                    is_presence_only=True,
                    observation_license="CC-BY 4.0",
                )
            )

        return records
