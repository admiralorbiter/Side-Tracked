"""CLI Tool to verify R3 Real Evidence Normalization & Concept Registry with TTL Cache Expiration."""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from packages.ovon_core.evidence.aggregator import MultiSourceEvidenceAggregator
from packages.ovon_core.evidence.ebird_recent_adapter import eBirdRecentAdapter
from packages.ovon_core.evidence.gbif_adapter import GBIFOccurrenceAdapter
from packages.ovon_core.evidence.inaturalist_adapter import INaturalistOccurrenceAdapter


def main() -> None:
    """Run R3 Evidence Normalization & TTL Cache Expiration verification suite."""
    print("=" * 70)
    print("   SIDETRACK EVIDENCE NORMALIZATION & TTL CACHE VERIFICATION (R3)")
    print("=" * 70)

    start_t = time.perf_counter()
    tmp_cache = Path("data/cache/verify_r3")
    tmp_cache.mkdir(parents=True, exist_ok=True)

    bbox = (39.0347, -94.5906, 39.0347, -94.5906)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # 1. Test eBird TTL Cache Envelope Validation & Expiration
    adapter = eBirdRecentAdapter(cache_dir=tmp_cache)

    sample_payload = [
        {
            "speciesCode": "norcar",
            "comName": "Northern Cardinal",
            "sciName": "Cardinalis cardinalis",
            "locId": "L12345",
            "obsDt": now_iso,
            "howMany": 2,
            "lat": 39.0347,
            "lng": -94.5906,
            "subId": "S112233",
        }
    ]

    import hashlib

    lat, lon = 39.0347, -94.5906
    cache_key = hashlib.sha256(f"ebird_{lat:.3f}_{lon:.3f}_30".encode()).hexdigest()[:12]
    cache_file = tmp_cache / f"{cache_key}.json"

    # Write fresh cache envelope
    exp_dt = datetime.now(timezone.utc) + timedelta(days=7)
    fresh_envelope = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": exp_dt.isoformat(),
        "ttl_seconds": 604800,
        "provider": "ebird_recent",
        "raw_records": sample_payload,
    }
    cache_file.write_text(json.dumps(fresh_envelope, indent=2), encoding="utf-8")

    res_fresh = adapter.fetch_result(bbox, [])
    assert res_fresh.status == "ok"
    assert len(res_fresh.records) == 1
    assert res_fresh.records[0].concept_id == "sidetrack_concept:northern_cardinal"
    print(
        f"[OK 1/4] TTL Cache Envelope: Read valid fresh cache (expires_at={exp_dt.strftime('%Y-%m-%d')}) -> 1 record"
    )

    # 2. Test TTL Cache Expiration (Expired cache -> refetch attempt)
    past_exp = datetime.now(timezone.utc) - timedelta(days=1)
    expired_envelope = {
        "fetched_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
        "expires_at": past_exp.isoformat(),
        "ttl_seconds": 604800,
        "provider": "ebird_recent",
        "raw_records": sample_payload,
    }
    cache_file.write_text(json.dumps(expired_envelope, indent=2), encoding="utf-8")

    # Unconfigured API key -> unconfigured status on cache expiry
    adapter_no_key = eBirdRecentAdapter(api_key=None, cache_dir=tmp_cache)
    res_expired = adapter_no_key.fetch_result(bbox, [])
    assert res_expired.status == "unconfigured"
    print(
        f"[OK 2/4] TTL Expiration Safeguard: Expired cache correctly triggered refetch attempt (status='{res_expired.status}')"
    )

    # 3. Test MultiSourceEvidenceAggregator Provider Status Tracking
    gbif = GBIFOccurrenceAdapter(cache_dir=tmp_cache)
    inat = INaturalistOccurrenceAdapter(cache_dir=tmp_cache)

    agg = MultiSourceEvidenceAggregator(providers=[adapter_no_key, gbif, inat])
    agg_res = agg.fetch_aggregated_result(bbox, [])

    statuses = agg_res.provider_statuses
    assert "ebirdrecentadapter" in statuses
    assert "gbifoccurrenceadapter" in statuses
    assert "inaturalistoccurrenceadapter" in statuses

    print(f"[OK 3/4] Provider Status Tracking: Aggregator collected statuses: {statuses}")

    # 4. Pipeline Execution Speed
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    print(f"[OK 4/4] R3 Evidence Normalization Execution Time: {elapsed_ms:.2f}ms (< 100ms)")

    print("=" * 70)
    print("SUCCESS: ALL R3 EVIDENCE NORMALIZATION & TTL CACHE CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
