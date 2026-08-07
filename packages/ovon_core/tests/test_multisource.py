"""Unit tests for multi-source presence normalization adapters and deduplication."""

from datetime import datetime, timezone

from packages.ovon_core.evidence.multisource import (
    GBIFOccurrenceAdapter,
    INaturalistOccurrenceAdapter,
    MultiSourceOccurrenceDeduplicator,
    SourceDataOrigin,
)
from packages.ovon_core.taxonomy.concept_registry import TaxonConceptRegistry


def test_gbif_occurrence_adapter():
    registry = TaxonConceptRegistry()
    adapter = GBIFOccurrenceAdapter(registry)

    now = datetime.now(timezone.utc)
    rec = adapter.normalize_gbif_record(
        gbif_taxon_id="amerob",
        observed_at=now,
        lat=39.035,
        lon=-94.590,
        spatial_cell_id="882685623ffffff",
        doi="10.15468/39omei",
    )

    assert rec is not None
    assert rec.origin == SourceDataOrigin.GBIF
    assert rec.is_presence_only is True
    assert rec.lineage.doi == "10.15468/39omei"


def test_inaturalist_occurrence_adapter_quality_grade_filter():
    registry = TaxonConceptRegistry()
    adapter = INaturalistOccurrenceAdapter(registry)

    now = datetime.now(timezone.utc)
    # Casual grade observation should be rejected/ignored
    rec_casual = adapter.normalize_inat_record(
        inat_taxon_id="amerob",
        observed_at=now,
        lat=39.035,
        lon=-94.590,
        spatial_cell_id="882685623ffffff",
        quality_grade="casual",
    )
    assert rec_casual is None

    # Research grade observation should normalize cleanly
    rec_research = adapter.normalize_inat_record(
        inat_taxon_id="amerob",
        observed_at=now,
        lat=39.035,
        lon=-94.590,
        spatial_cell_id="882685623ffffff",
        quality_grade="research",
    )
    assert rec_research is not None
    assert rec_research.origin == SourceDataOrigin.INATURALIST


def test_multisource_deduplicator():
    registry = TaxonConceptRegistry()
    gbif_adapter = GBIFOccurrenceAdapter(registry)
    inat_adapter = INaturalistOccurrenceAdapter(registry)

    now = datetime.now(timezone.utc)
    r1 = gbif_adapter.normalize_gbif_record("amerob", now, 39.035, -94.590, "882685623ffffff")
    r2 = inat_adapter.normalize_inat_record(
        "amerob", now, 39.035, -94.590, "882685623ffffff", "research"
    )

    deduped = MultiSourceOccurrenceDeduplicator.deduplicate([r1, r2])
    assert len(deduped) == 1
