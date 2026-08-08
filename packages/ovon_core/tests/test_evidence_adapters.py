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


def test_ebird_recent_adapter_frozen_payload(tmp_path):
    import json
    from datetime import datetime, timezone

    adapter = eBirdRecentAdapter(cache_dir=tmp_path)
    bbox = (39.0347, -94.5906, 39.0347, -94.5906)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    sample_payload = [
        {
            "speciesCode": "norcar",
            "comName": "Northern Cardinal",
            "sciName": "Cardinalis cardinalis",
            "locId": "L12345",
            "locName": "Loose Park",
            "obsDt": now_iso,
            "howMany": 3,
            "lat": 39.0347,
            "lng": -94.5906,
            "subId": "S998877",
        }
    ]

    # Pre-populate cache envelope with valid TTL
    import hashlib
    from datetime import timedelta

    lat, lon = 39.0347, -94.5906
    cache_key = hashlib.sha256(f"ebird_{lat:.3f}_{lon:.3f}_30".encode()).hexdigest()[:12]
    cache_file = tmp_path / f"{cache_key}.json"

    now_dt = datetime.now(timezone.utc)
    exp_dt = now_dt + timedelta(days=7)
    cache_envelope = {
        "fetched_at": now_dt.isoformat(),
        "expires_at": exp_dt.isoformat(),
        "ttl_seconds": 604800,
        "provider": "ebird_recent",
        "raw_records": sample_payload,
    }
    cache_file.write_text(json.dumps(cache_envelope, indent=2), encoding="utf-8")

    recs = adapter.fetch_occurrences(bbox, [])
    assert len(recs) == 1
    assert recs[0].concept_id == "sidetrack_concept:northern_cardinal"
    assert recs[0].original_scientific_name == "Cardinalis cardinalis"
    assert recs[0].latitude == 39.0347
    assert recs[0].source_occurrence_id == "S998877"


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
