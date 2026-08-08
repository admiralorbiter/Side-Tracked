"""Unit tests for Real Observation Evidence Adapters (eBird, GBIF, iNaturalist)."""

from packages.ovon_core.evidence.aggregator import MultiSourceEvidenceAggregator
from packages.ovon_core.evidence.ebird_recent_adapter import eBirdRecentAdapter
from packages.ovon_core.evidence.gbif_adapter import GBIFOccurrenceAdapter
from packages.ovon_core.evidence.inaturalist_adapter import INaturalistOccurrenceAdapter


def test_ebird_recent_adapter():
    adapter = eBirdRecentAdapter()
    bbox = (39.02, -94.61, 39.05, -94.57)
    recs = adapter.fetch_occurrences(bbox, [])
    assert isinstance(recs, list)


def test_gbif_occurrence_adapter():
    adapter = GBIFOccurrenceAdapter()
    bbox = (39.02, -94.61, 39.05, -94.57)
    recs = adapter.fetch_occurrences(bbox, [])
    assert isinstance(recs, list)


def test_inaturalist_occurrence_adapter():
    adapter = INaturalistOccurrenceAdapter()
    bbox = (39.02, -94.61, 39.05, -94.57)
    recs = adapter.fetch_occurrences(bbox, [])
    assert isinstance(recs, list)


def test_multisource_aggregator():
    ebird = eBirdRecentAdapter()
    gbif = GBIFOccurrenceAdapter()
    inat = INaturalistOccurrenceAdapter()

    agg = MultiSourceEvidenceAggregator(providers=[ebird, gbif, inat])
    bbox = (39.02, -94.61, 39.05, -94.57)
    recs = agg.fetch_occurrences(bbox, [])
    assert isinstance(recs, list)
