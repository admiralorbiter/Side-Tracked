"""SQLite-backed DiscoveryRepository for durable personal species encounter collections."""

import os
import sqlite3
from typing import Any

from packages.ovon_core.domain.discovery import (
    DiscoveryRecord,
)


class DiscoverySaveError(Exception):
    """Raised when writing a DiscoveryRecord to SQLite fails."""

    pass


class DiscoveryRepository:
    """Repository for persisting personal DiscoveryRecord collections."""

    _db_path: str = "data/discovery.db"

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
                CREATE TABLE IF NOT EXISTS discovery_records (
                    discovery_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    taxonomic_version_at_discovery TEXT NOT NULL,
                    original_taxon_ref TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    latitude REAL NOT NULL CHECK (latitude BETWEEN -90.0 AND 90.0),
                    longitude REAL NOT NULL CHECK (longitude BETWEEN -180.0 AND 180.0),
                    spatial_cell_id TEXT NOT NULL,
                    source_role TEXT NOT NULL CHECK (source_role IN ('user_recall_only', 'opportunistic_detection', 'ebird_complete_checklist', 'in_route_walk')),
                    evidence_type TEXT NOT NULL CHECK (evidence_type IN ('seen', 'heard', 'seen_and_heard', 'photo_verified', 'audio_recorded')),
                    confidence TEXT NOT NULL DEFAULT 'certain' CHECK (confidence IN ('certain', 'unsure')),
                    count INTEGER NOT NULL DEFAULT 1 CHECK (count >= 1),
                    associated_plan_id TEXT,
                    associated_route_id TEXT,
                    privacy_level TEXT NOT NULL DEFAULT 'private_only' CHECK (privacy_level IN ('public_exact', 'public_obfuscated', 'private_only')),
                    is_sensitive INTEGER NOT NULL DEFAULT 0 CHECK (is_sensitive IN (0, 1)),
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS taxon_concept_migrations (
                    migration_id TEXT PRIMARY KEY,
                    migration_type TEXT NOT NULL CHECK (migration_type IN ('SPLIT', 'LUMP', 'RENAME', 'REASSIGN')),
                    source_concept_id TEXT NOT NULL,
                    target_concept_id TEXT NOT NULL,
                    effective_taxonomy_version TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        return conn

    @classmethod
    def save_discovery(cls, record: DiscoveryRecord) -> str:
        """Persist a DiscoveryRecord to SQLite."""
        try:
            conn = cls._get_connection()
            with conn:
                conn.execute(
                    """
                    INSERT INTO discovery_records (
                        discovery_id, user_id, concept_id, taxonomic_version_at_discovery,
                        original_taxon_ref, observed_at, latitude, longitude, spatial_cell_id,
                        source_role, evidence_type, confidence, count, associated_plan_id,
                        associated_route_id, privacy_level, is_sensitive, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(record.discovery_id),
                        record.user_id,
                        str(record.concept_id),
                        record.taxonomic_version_at_discovery,
                        record.original_taxon_ref,
                        record.observed_at.isoformat(),
                        record.latitude,
                        record.longitude,
                        record.spatial_cell_id,
                        record.source_role.value,
                        record.evidence_type.value,
                        record.confidence.value,
                        record.count,
                        record.associated_plan_id,
                        record.associated_route_id,
                        record.privacy_level.value,
                        1 if record.is_sensitive else 0,
                        record.notes or "",
                        record.created_at.isoformat(),
                    ),
                )
                conn.commit()
            conn.close()
            return str(record.discovery_id)
        except Exception as e:
            raise DiscoverySaveError(f"Database write failure in save_discovery: {e}") from e

    @classmethod
    def get_discoveries_for_user(cls, user_id: str) -> list[dict[str, Any]]:
        """Retrieve discovery history records for a user including privacy levels and sensitivity status."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT discovery_id, user_id, concept_id, original_taxon_ref, observed_at,
                       latitude, longitude, spatial_cell_id, source_role, evidence_type,
                       confidence, count, associated_plan_id, associated_route_id,
                       privacy_level, is_sensitive, notes
                FROM discovery_records WHERE user_id = ?
                ORDER BY observed_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
            conn.close()
            results = []
            for r in rows:
                d = dict(r)
                # Compute privacy-enforced export coordinates
                priv = d.get("privacy_level", "private_only")
                sens = bool(d.get("is_sensitive", 0))
                lat, lon = d["latitude"], d["longitude"]

                if sens or priv == "private_only":
                    d["export_latitude"] = None
                    d["export_longitude"] = None
                elif priv == "public_obfuscated":
                    d["export_latitude"] = round(lat, 2)
                    d["export_longitude"] = round(lon, 2)
                else:
                    d["export_latitude"] = lat
                    d["export_longitude"] = lon

                results.append(d)
            return results
        except Exception:
            return []
