"""Database migration and initialization CLI script for Sidetrack SQLite repositories."""

import sys
from pathlib import Path

from apps.web.app.services.feedback_repository import WalkFeedbackRepository
from apps.web.app.services.planner_service import RoutePlanRepository


def migrate_databases(data_dir: Path | None = None) -> bool:
    """Run schema migration and verification across all SQLite databases."""
    if data_dir is None:
        data_dir = Path("data")

    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("       SIDETRACK DATABASE MIGRATION & SCHEMA INITIALIZATION")
    print("=" * 60)

    route_plans_db = str(data_dir / "route_plans.db")
    walk_feedback_db = str(data_dir / "walk_feedback.db")

    success = True

    # 1. Migrate RoutePlanRepository
    print(f"\n[1/2] Migrating Route Plans Database ({route_plans_db})...")
    try:
        RoutePlanRepository.set_db_path(route_plans_db)
        conn = RoutePlanRepository._get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(route_plans)")
        cols = {row[1] for row in cursor.fetchall()}
        expected_cols = {
            "plan_id",
            "created_at",
            "expires_at",
            "routes_json",
            "model_version",
            "data_version",
            "request_json",
            "routing_provenance_json",
            "media_manifest_version",
        }
        missing = expected_cols - cols
        if missing:
            print(f"[FAIL] Missing columns in route_plans: {missing}")
            success = False
        else:
            print(f"[OK] route_plans table verified with {len(cols)} columns.")
        conn.close()
    except Exception as e:
        print(f"[FAIL] Route plans migration failed: {e}")
        success = False

    # 2. Migrate WalkFeedbackRepository
    print(f"\n[2/3] Migrating Walk Feedback Database ({walk_feedback_db})...")
    try:
        WalkFeedbackRepository.set_db_path(walk_feedback_db)
        conn = WalkFeedbackRepository._get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(walk_sessions)")
        session_cols = {row[1] for row in cursor.fetchall()}

        cursor.execute("PRAGMA table_info(walk_feedback)")
        feedback_cols = {row[1] for row in cursor.fetchall()}

        expected_feedback = {
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
        }
        missing_feedback = expected_feedback - feedback_cols
        if missing_feedback:
            print(f"[FAIL] Missing columns in walk_feedback: {missing_feedback}")
            success = False
        else:
            print(
                f"[OK] walk_sessions ({len(session_cols)} cols) and walk_feedback ({len(feedback_cols)} cols) verified."
            )
        conn.close()
    except Exception as e:
        print(f"[FAIL] Walk feedback migration failed: {e}")
        success = False

    # 3. Migrate DiscoveryRepository
    discovery_db = str(data_dir / "discovery.db")
    print(f"\n[3/3] Migrating Discovery Database ({discovery_db})...")
    try:
        from apps.web.app.services.discovery_repository import DiscoveryRepository

        DiscoveryRepository.set_db_path(discovery_db)
        conn = DiscoveryRepository._get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(discovery_records)")
        disc_cols = {row[1] for row in cursor.fetchall()}
        expected_disc = {
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
        }
        missing_disc = expected_disc - disc_cols
        if missing_disc:
            print(f"[FAIL] Missing columns in discovery_records: {missing_disc}")
            success = False
        else:
            print(f"[OK] discovery_records table verified with {len(disc_cols)} columns.")
        conn.close()
    except Exception as e:
        print(f"[FAIL] Discovery database migration failed: {e}")
        success = False

    print("=" * 60)
    if success:
        print("SUCCESS: ALL DATABASE MIGRATIONS AND SCHEMA CHECKS PASSED!")
    else:
        print("FAILURE: DATABASE MIGRATION CHECKS FAILED.")
    print("=" * 60)
    return success


if __name__ == "__main__":
    ok = migrate_databases()
    sys.exit(0 if ok else 1)
