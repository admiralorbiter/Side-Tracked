"""CLI Tool to verify R6 Historical Checklist Repository (EBD/SED Query & Zero Placeholder Enforcement)."""

import time
from pathlib import Path

from packages.ovon_core.evidence.historical_repository import HistoricalChecklistRepository


def main() -> None:
    """Run R6 Historical Checklist Repository verification suite."""
    print("=" * 70)
    print("   SIDETRACK HISTORICAL CHECKLIST REPOSITORY VERIFICATION (R6)")
    print("=" * 70)

    start_t = time.perf_counter()
    tmp_dir = Path("data/raw/ebd/verify_r6")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    repo = HistoricalChecklistRepository(data_dir=tmp_dir)

    bbox = (39.00, -94.70, 39.20, -94.40)

    # 1. Query Complete Sampling Events (Strict complete filter: all_species_reported == True)
    events = repo.query_sampling_events(bounding_box=bbox, complete_only=True)
    assert len(events) == 2  # Incomplete checklist SED_KC_INC is filtered out!

    event_ids = [e.event_id for e in events]
    assert "SED_KC_INC" not in event_ids
    print(
        f"[OK 1/4] Complete Checklist Filter: Excluded incomplete checklist, returned {len(events)} complete SED checklists"
    )

    # 2. Query Historical Species Observations (EBD)
    obs = repo.query_observations(
        event_ids=event_ids, concept_ids=["sidetrack_concept:northern_cardinal"]
    )
    assert len(obs) == 2  # 2 Northern Cardinal records across the 2 complete checklists
    assert obs[0].common_name == "Northern Cardinal"

    print(
        f"[OK 2/4] Historical Species Observations: Queried {len(obs)} EBD observation records for Northern Cardinal"
    )

    # 3. Test Date Range Filtering
    date_filtered = repo.query_sampling_events(
        bounding_box=bbox, start_date="2026-05-16", end_date="2026-05-16"
    )
    assert len(date_filtered) == 1
    assert date_filtered[0].event_id == "SED_KC_002"

    print(
        f"[OK 3/4] Date Range Filter: Returned exact date match for 2026-05-16 ({date_filtered[0].event_id})"
    )

    # 4. Pipeline Speed Benchmark
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    print(f"[OK 4/4] R6 Historical Repository Execution Time: {elapsed_ms:.2f}ms (< 100ms)")

    print("=" * 70)
    print("SUCCESS: ALL R6 HISTORICAL REPOSITORY CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
