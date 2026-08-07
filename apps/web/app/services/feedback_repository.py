"""SQLite Persistence Repository for Versioned User Walk Observation Feedback."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any


class FeedbackSaveError(Exception):
    """Raised when user feedback persistence fails."""

    pass


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
                CREATE TABLE IF NOT EXISTS walk_sessions (
                    session_id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    route_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    last_segment_index INTEGER DEFAULT 0,
                    outcome TEXT NOT NULL DEFAULT 'active'
                )
                """
            )
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
                    notes TEXT,
                    evidence_eligibility TEXT NOT NULL DEFAULT 'user_recall_only',
                    walk_session_id TEXT
                )
                """
            )
            # Automatic schema migration for existing SQLite databases
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(walk_feedback)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            if "evidence_eligibility" not in existing_cols:
                conn.execute(
                    "ALTER TABLE walk_feedback ADD COLUMN evidence_eligibility TEXT NOT NULL DEFAULT 'user_recall_only'"
                )
            if "walk_session_id" not in existing_cols:
                conn.execute("ALTER TABLE walk_feedback ADD COLUMN walk_session_id TEXT")
            conn.commit()
        return conn

    @classmethod
    def get_active_session(cls, plan_id: str, route_id: str) -> dict[str, Any] | None:
        """Retrieve the currently active WalkSession for a plan and route if one exists."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, plan_id, route_id, started_at, finished_at, last_segment_index, outcome
                FROM walk_sessions WHERE plan_id = ? AND route_id = ? AND outcome = 'active'
                ORDER BY started_at DESC LIMIT 1
                """,
                (plan_id, route_id),
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            return {
                "session_id": row["session_id"],
                "plan_id": row["plan_id"],
                "route_id": row["route_id"],
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
                "last_segment_index": row["last_segment_index"],
                "outcome": row["outcome"],
            }
        except Exception:
            return None

    @classmethod
    def get_or_start_active_session(cls, plan_id: str, route_id: str) -> dict[str, Any]:
        """Idempotently retrieve an existing active session or start a new WalkSession."""
        active = cls.get_active_session(plan_id, route_id)
        if active:
            return active
        return cls.start_session(plan_id, route_id)

    @classmethod
    def start_session(cls, plan_id: str, route_id: str) -> dict[str, Any]:
        """Start an active WalkSession."""
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            conn = cls._get_connection()
            with conn:
                conn.execute(
                    """
                    INSERT INTO walk_sessions (session_id, plan_id, route_id, started_at, outcome)
                    VALUES (?, ?, ?, ?, 'active')
                    """,
                    (session_id, plan_id, route_id, now_iso),
                )
                conn.commit()
            conn.close()
            return {
                "session_id": session_id,
                "plan_id": plan_id,
                "route_id": route_id,
                "started_at": now_iso,
                "outcome": "active",
                "last_segment_index": 0,
            }
        except Exception as e:
            raise FeedbackSaveError(f"Failed starting walk session: {e}") from e

    @classmethod
    def finish_session(
        cls, session_id: str, outcome: str, last_segment_index: int = 0
    ) -> dict[str, Any] | None:
        """Complete an active WalkSession with an explicit final outcome state."""
        finished_at = datetime.now(timezone.utc).isoformat()
        try:
            conn = cls._get_connection()
            with conn:
                conn.execute(
                    """
                    UPDATE walk_sessions
                    SET finished_at = ?, outcome = ?, last_segment_index = ?
                    WHERE session_id = ?
                    """,
                    (finished_at, outcome, last_segment_index, session_id),
                )
                conn.commit()
            conn.close()
            return cls.get_session(session_id)
        except Exception as e:
            raise FeedbackSaveError(f"Failed finishing walk session {session_id}: {e}") from e

    @classmethod
    def get_session(cls, session_id: str) -> dict[str, Any] | None:
        """Retrieve a WalkSession by ID."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, plan_id, route_id, started_at, finished_at, last_segment_index, outcome
                FROM walk_sessions WHERE session_id = ?
                """,
                (session_id,),
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            return {
                "session_id": row["session_id"],
                "plan_id": row["plan_id"],
                "route_id": row["route_id"],
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
                "last_segment_index": row["last_segment_index"],
                "outcome": row["outcome"],
            }
        except Exception:
            return None

    @classmethod
    def save_feedback(
        cls,
        plan_id: str,
        route_id: str,
        outcome: str,
        observations: dict[str, Any],
        duration_minutes: int | None = None,
        notes: str | None = None,
        walk_session_id: str | None = None,
        evidence_eligibility: str = "user_recall_only",
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
                    INSERT INTO walk_feedback (feedback_id, plan_id, route_id, created_at, outcome, duration_minutes, observations_json, notes, evidence_eligibility, walk_session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        evidence_eligibility,
                        walk_session_id,
                    ),
                )
                conn.commit()
            conn.close()
            return feedback_id
        except Exception as e:
            raise FeedbackSaveError(f"Database write failure in save_feedback: {e}") from e

    @classmethod
    def get_feedback_for_plan(cls, plan_id: str, route_id: str) -> list[dict[str, Any]]:
        """Retrieve historical feedback records for a plan and route ID."""
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT feedback_id, plan_id, route_id, created_at, outcome, duration_minutes, observations_json, notes, evidence_eligibility, walk_session_id
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
            obs_dict = json.loads(r["observations_json"])
            results.append(
                {
                    "feedback_id": r["feedback_id"],
                    "plan_id": r["plan_id"],
                    "route_id": r["route_id"],
                    "created_at": r["created_at"],
                    "outcome": r["outcome"],
                    "duration_minutes": r["duration_minutes"],
                    "observations": obs_dict,
                    "notes": r["notes"],
                    "evidence_eligibility": r["evidence_eligibility"],
                    "walk_session_id": r["walk_session_id"],
                }
            )
        return results
