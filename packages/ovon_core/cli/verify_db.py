"""Read-only database verification CLI script for Sidetrack SQLite repositories."""

import sqlite3
import sys
from pathlib import Path


def verify_databases(data_dir: Path | None = None) -> bool:
    """Read-only verification of database schemas without executing mutations."""
    if data_dir is None:
        data_dir = Path("data")

    print("=" * 60)
    print("       SIDETRACK DATABASE SCHEMA VERIFICATION (READ-ONLY)")
    print("=" * 60)

    dbs = {
        "route_plans.db": {
            "table": "route_plans",
            "expected_cols": {
                "plan_id",
                "created_at",
                "expires_at",
                "routes_json",
                "model_version",
                "data_version",
                "request_json",
                "routing_provenance_json",
                "media_manifest_version",
            },
        },
        "walk_feedback.db": {
            "table": "walk_feedback",
            "expected_cols": {
                "feedback_id",
                "plan_id",
                "route_id",
                "created_at",
                "outcome",
                "duration_minutes",
                "observations_json",
                "notes",
                "evidence_eligibility",
                "walk_session_id",
            },
        },
        "discovery.db": {
            "table": "discovery_records",
            "expected_cols": {
                "discovery_id",
                "user_id",
                "concept_id",
                "taxonomic_version_at_discovery",
                "original_taxon_ref",
                "observed_at",
                "latitude",
                "longitude",
                "spatial_cell_id",
                "source_role",
                "evidence_type",
                "confidence",
                "count",
                "associated_plan_id",
                "associated_route_id",
                "privacy_level",
                "is_sensitive",
                "notes",
                "created_at",
            },
        },
    }

    all_passed = True

    for db_name, meta in dbs.items():
        db_path = data_dir / db_name
        print(f"\nVerifying {db_name}...")

        if not db_path.exists():
            print(
                f"[INFO] Database file {db_path} does not exist yet (will be initialized on first write)."
            )
            continue

        try:
            # Connect in read-only URI mode to ensure no DB modifications
            uri = f"file:{db_path.resolve()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            cursor = conn.cursor()
            table_name = meta["table"]
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols = {row[1] for row in cursor.fetchall()}
            conn.close()

            missing = meta["expected_cols"] - cols
            if missing:
                print(f"[FAIL] {db_name} ({table_name}) missing required columns: {missing}")
                all_passed = False
            else:
                print(f"[OK] {db_name} ({table_name}) verified with {len(cols)} columns.")
        except Exception as err:
            print(f"[FAIL] Read-only verification failed for {db_name}: {err}")
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("SUCCESS: ALL READ-ONLY DATABASE CHECKS PASSED!")
    else:
        print("FAILURE: ONE OR MORE DATABASE VERIFICATION CHECKS FAILED.")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    ok = verify_databases()
    sys.exit(0 if ok else 1)
