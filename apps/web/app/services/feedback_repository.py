"""SQLite Persistence Repository for Versioned User Walk Observation Feedback."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any


class WalkFeedbackRepository:
    """SQLite-backed repository for saving versioned user walk feedback and observations."""

    _db_path: str = "data/walk_feedback.db"

    @classmethod
    def set_db_path(cls, path: str) -> None:
        cls._db_path = path

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        if cls._db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(cls._db_path)), exist_ok=True)
        conn = sqlite3.connect(cls._db_path)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS walk_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    route_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    duration_minutes INTEGER,
                    observations_json TEXT NOT NULL,
                    notes TEXT
                )
                """
            )
        return conn

    @classmethod
    def save_feedback(
        cls,
        plan_id: str,
        route_id: str,
        outcome: str,
        observations: dict[str, str],
        duration_minutes: int | None = None,
        notes: str | None = None,
    ) -> str:
        """Save a versioned user observation feedback record."""
        feedback_id = uuid.uuid4().hex[:12]
        now_iso = datetime.now(timezone.utc).isoformat()
        obs_json = json.dumps(observations)

        try:
            conn = cls._get_connection()
            with conn:
                conn.execute(
                    """
                    INSERT INTO walk_feedback (feedback_id, plan_id, route_id, created_at, outcome, duration_minutes, observations_json, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        feedback_id,
                        plan_id,
                        route_id,
                        now_iso,
                        outcome,
                        duration_minutes,
                        obs_json,
                        notes or "",
                    ),
                )
            conn.close()
        except Exception:
            pass

        return feedback_id

    @classmethod
    def get_feedback_for_plan(cls, plan_id: str, route_id: str) -> list[dict[str, Any]]:
        """Retrieve historical feedback records for a plan and route ID."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT feedback_id, plan_id, route_id, created_at, outcome, duration_minutes, observations_json, notes
                FROM walk_feedback
                WHERE plan_id = ? AND route_id = ?
                ORDER BY created_at DESC
                """,
                (plan_id, route_id),
            )
            rows = cursor.fetchall()
            conn.close()

            results = []
            for r in rows:
                results.append(
                    {
                        "feedback_id": r["feedback_id"],
                        "plan_id": r["plan_id"],
                        "route_id": r["route_id"],
                        "created_at": r["created_at"],
                        "outcome": r["outcome"],
                        "duration_minutes": r["duration_minutes"],
                        "observations": json.loads(r["observations_json"]),
                        "notes": r["notes"],
                    }
                )
            return results
        except Exception:
            return []
