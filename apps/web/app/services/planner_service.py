"""Planner Application Service and Plan-Scoped Repository."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from flask import current_app

from packages.ovon_core.domain import (
    Coordinate,
    FieldCue,
    LoopRequest,
    RouteOption,
    RoutePersona,
    RouteSegment,
    TaxonRef,
)
from packages.ovon_core.fixtures import ROUTE_BIRDY, ROUTE_EASY, ROUTE_WEIRD
from packages.ovon_core.fixtures.routes_fixtures import (
    CARDINAL,
    CUE_CARDINAL,
    CUE_ROBIN,
    CUE_WAXWING,
    ROBIN,
    WAXWING,
    WOODPECKER,
)
from packages.ovon_core.routing import (
    OSMnxIgraphRoutingProvider,
    RouteMenuResult,
    RoutingProvider,
    TradeoffExplanationGenerator,
)


class RoutePlanRepository:
    """SQLite-backed plan-scoped repository for multi-user isolated route plans."""

    _db_path: str = "data/route_plans.db"
    _plans: dict[str, tuple[RouteOption, ...]] = {}

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
                CREATE TABLE IF NOT EXISTS route_plans (
                    plan_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    routes_json TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    data_version TEXT NOT NULL,
                    request_json TEXT,
                    routing_provenance_json TEXT,
                    media_manifest_version TEXT
                )
                """
            )
            # Automatic schema migration for existing SQLite databases
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(route_plans)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            if "request_json" not in existing_cols:
                conn.execute("ALTER TABLE route_plans ADD COLUMN request_json TEXT")
            if "routing_provenance_json" not in existing_cols:
                conn.execute("ALTER TABLE route_plans ADD COLUMN routing_provenance_json TEXT")
            if "media_manifest_version" not in existing_cols:
                conn.execute("ALTER TABLE route_plans ADD COLUMN media_manifest_version TEXT")
            conn.commit()
        return conn

    @classmethod
    def _serialize_routes(cls, routes: tuple[RouteOption, ...]) -> str:
        serialized = []
        for r in routes:
            seg_list = []
            for s in r.segments:
                seg_dict = {
                    "index": s.index,
                    "name": s.name,
                    "habitat_name": s.habitat_name,
                    "habitat_type": s.habitat_type.value
                    if hasattr(s, "habitat_type") and s.habitat_type
                    else "Open Parkland",
                    "distance_meters": s.distance_meters,
                    "duration_minutes": s.duration_minutes,
                    "focal_species": [
                        {
                            "common_name": sp.common_name,
                            "scientific_name": sp.scientific_name,
                            "ebird_code": sp.ebird_code,
                            "category": sp.category,
                            "taxonomy_version": sp.taxonomy_version,
                            "taxon_id": sp.taxon_id,
                        }
                        for sp in s.focal_species
                    ],
                    "field_cue": {
                        "taxon_ref": {
                            "common_name": s.field_cue.taxon_ref.common_name,
                            "scientific_name": s.field_cue.taxon_ref.scientific_name,
                            "ebird_code": s.field_cue.taxon_ref.ebird_code,
                            "category": s.field_cue.taxon_ref.category,
                            "taxonomy_version": s.field_cue.taxon_ref.taxonomy_version,
                            "taxon_id": s.field_cue.taxon_ref.taxon_id,
                        },
                        "where_to_look": getattr(s.field_cue, "where_to_look", ""),
                        "what_to_listen_for": getattr(s.field_cue, "what_to_listen_for", ""),
                        "look_alikes": getattr(s.field_cue, "look_alikes", ""),
                    }
                    if s.field_cue
                    else None,
                    "geojson_geometry": s.geojson_geometry,
                    "observation_point": {
                        "latitude": s.observation_point.latitude,
                        "longitude": s.observation_point.longitude,
                    }
                    if s.observation_point
                    else None,
                    "navigation_instruction": s.navigation_instruction,
                }
                seg_list.append(seg_dict)

            r_dict = {
                "id": r.id,
                "persona": r.persona.value,
                "name": r.name,
                "tagline": r.tagline,
                "duration_minutes": r.duration_minutes,
                "distance_meters": r.distance_meters,
                "badge_label": r.badge_label,
                "tradeoff_description": r.tradeoff_description,
                "segments": seg_list,
                "geojson_geometry": r.geojson_geometry,
            }
            serialized.append(r_dict)
        return json.dumps(serialized)

    @classmethod
    def _deserialize_routes(cls, json_str: str) -> tuple[RouteOption, ...]:
        raw_list = json.loads(json_str)
        routes = []
        for r_dict in raw_list:
            segments = []
            for s_dict in r_dict.get("segments", []):
                focal_species = tuple(
                    TaxonRef(
                        taxon_id=sp["taxon_id"],
                        common_name=sp["common_name"],
                        scientific_name=sp["scientific_name"],
                        ebird_code=sp["ebird_code"],
                        category=sp.get("category", "Bird"),
                        taxonomy_version=sp.get("taxonomy_version", "Clements-2025"),
                    )
                    for sp in s_dict.get("focal_species", [])
                )
                fc_raw = s_dict.get("field_cue")
                field_cue = None
                if fc_raw and "taxon_ref" in fc_raw:
                    sp_ref = fc_raw["taxon_ref"]
                    t_ref = TaxonRef(
                        taxon_id=sp_ref["taxon_id"],
                        common_name=sp_ref["common_name"],
                        scientific_name=sp_ref["scientific_name"],
                        ebird_code=sp_ref["ebird_code"],
                        category=sp_ref.get("category", "Bird"),
                        taxonomy_version=sp_ref.get("taxonomy_version", "Clements-2025"),
                    )
                    field_cue = FieldCue(
                        taxon_ref=t_ref,
                        where_to_look=fc_raw.get("where_to_look", fc_raw.get("description", "")),
                        what_to_listen_for=fc_raw.get("what_to_listen_for", ""),
                        look_alikes=fc_raw.get("look_alikes", ""),
                    )

                obs_raw = s_dict.get("observation_point")
                obs_pt = Coordinate(obs_raw["latitude"], obs_raw["longitude"]) if obs_raw else None

                # Extract continuous environmental feature vector
                from packages.ovon_core.spatial.environmental_extractor import (
                    EnvironmentalFeatureExtractor,
                )

                extractor = EnvironmentalFeatureExtractor()
                seg_coords = []
                g_geom = s_dict.get("geojson_geometry")
                if g_geom and "coordinates" in g_geom:
                    raw_coords = g_geom["coordinates"]
                    seg_coords = [(c[1], c[0]) for c in raw_coords if len(c) >= 2]
                elif obs_pt:
                    seg_coords = [(obs_pt.latitude, obs_pt.longitude)]

                env_vec = extractor.extract_for_segment(seg_coords)
                derived_ht = env_vec.derive_habitat_type()

                seg = RouteSegment(
                    index=s_dict["index"],
                    name=s_dict["name"],
                    habitat_name=s_dict["habitat_name"],
                    distance_meters=float(s_dict["distance_meters"]),
                    duration_minutes=float(s_dict["duration_minutes"]),
                    focal_species=focal_species,
                    field_cue=field_cue,
                    geojson_geometry=s_dict.get("geojson_geometry"),
                    observation_point=obs_pt,
                    navigation_instruction=s_dict.get("navigation_instruction", ""),
                    habitat_type=derived_ht,
                    environmental_vector=env_vec,
                )
                segments.append(seg)

            # Match persona enum
            p_val = r_dict.get("persona")
            matched_p = RoutePersona.EASY
            for p in RoutePersona:
                if p.value == p_val or p.name.lower() == str(p_val).lower():
                    matched_p = p
                    break

            opt = RouteOption(
                id=r_dict["id"],
                persona=matched_p,
                name=r_dict["name"],
                tagline=r_dict["tagline"],
                duration_minutes=int(r_dict["duration_minutes"]),
                distance_meters=float(r_dict["distance_meters"]),
                badge_label=r_dict["badge_label"],
                tradeoff_description=r_dict["tradeoff_description"],
                segments=tuple(segments),
                geojson_geometry=r_dict.get("geojson_geometry"),
            )
            routes.append(opt)

        return tuple(routes)

    @classmethod
    def save_plan(
        cls,
        routes: tuple[RouteOption, ...],
        ttl_hours: int = 24,
        loop_request: LoopRequest | None = None,
        routing_provenance: dict | None = None,
    ) -> str:
        plan_id = uuid.uuid4().hex[:10]
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=ttl_hours)

        cls._plans[plan_id] = (routes, expires_at)
        routes_json = cls._serialize_routes(routes)

        req_json = (
            json.dumps(
                {
                    "origin": {
                        "lat": loop_request.origin.latitude,
                        "lon": loop_request.origin.longitude,
                    }
                    if loop_request
                    else None,
                    "target_duration_minutes": loop_request.duration_minutes
                    if loop_request
                    else None,
                    "paved_only": loop_request.paved_only if loop_request else False,
                    "quiet_mode": loop_request.quiet_mode if loop_request else False,
                    "survey_mode": loop_request.survey_mode if loop_request else False,
                }
            )
            if loop_request
            else None
        )

        prov_json = json.dumps(routing_provenance) if routing_provenance else None

        try:
            conn = cls._get_connection()
            with conn:
                conn.execute(
                    """
                    INSERT INTO route_plans (plan_id, created_at, expires_at, routes_json, model_version, data_version, request_json, routing_provenance_json, media_manifest_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        plan_id,
                        now.isoformat(),
                        expires_at.isoformat(),
                        routes_json,
                        "v1.0-kc",
                        "2026.1",
                        req_json,
                        prov_json,
                        "v1.0-media",
                    ),
                )
            conn.close()
        except Exception as err:
            import logging

            logging.getLogger(__name__).error(
                "Failed to persist route plan '%s' to SQLite database: %s", plan_id, err
            )

        return plan_id

    @classmethod
    def get_plan_routes(cls, plan_id: str) -> tuple[RouteOption, ...] | None:
        if not plan_id:
            return None

        now = datetime.now(timezone.utc)

        # Check in-memory process cache first with explicit expiration verification
        if plan_id in cls._plans:
            routes, expires_at = cls._plans[plan_id]
            if now > expires_at:
                del cls._plans[plan_id]
                return None
            return routes

        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT routes_json, expires_at FROM route_plans WHERE plan_id = ?", (plan_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            expires_at = datetime.fromisoformat(row["expires_at"])
            if now > expires_at:
                return None

            routes = cls._deserialize_routes(row["routes_json"])
            cls._plans[plan_id] = (routes, expires_at)
            return routes
        except Exception:
            return None

    @classmethod
    def get_route(cls, plan_id: str, route_id: str) -> RouteOption | None:
        if not plan_id or not route_id:
            return None
        routes = cls.get_plan_routes(plan_id)
        if not routes:
            return None
        clean_route_id = route_id.lower().strip()
        for r in routes:
            if r.id.lower() == clean_route_id:
                return r
        return None

    @classmethod
    def get_plan_request(cls, plan_id: str) -> dict | None:
        if not plan_id:
            return None
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT request_json FROM route_plans WHERE plan_id = ?", (plan_id,))
            row = cursor.fetchone()
            conn.close()
            if row and row["request_json"]:
                return json.loads(row["request_json"])
        except Exception:
            pass
        return None


class PlanLoopPreview:
    """Application Service for evaluating LoopRequest and returning available RouteOptions with truthful provenance."""

    def __init__(
        self,
        routing_provider: RoutingProvider | None = None,
        explanation_generator: TradeoffExplanationGenerator | None = None,
    ):
        self._routing_provider = routing_provider
        self.explanation_generator = explanation_generator or TradeoffExplanationGenerator()

    @property
    def routing_provider(self) -> RoutingProvider:
        if self._routing_provider:
            return self._routing_provider
        if current_app and "routing_provider" in current_app.extensions:
            provider: RoutingProvider = current_app.extensions["routing_provider"]
            return provider
        return OSMnxIgraphRoutingProvider()

    def execute(self, request: LoopRequest) -> RouteMenuResult:
        """Return distinct route options and truthfulness provenance for a LoopRequest."""
        try:
            result = self.routing_provider.calculate_loop(request)
            options: list[RouteOption] = []
            easy_baseline: RouteOption | None = None

            for cand in result.candidates:
                if cand.persona == RoutePersona.EASY:
                    focal = (ROBIN, CARDINAL)
                    cue = CUE_ROBIN
                elif cand.persona == RoutePersona.BIRDY:
                    focal = (CARDINAL, WOODPECKER)
                    cue = CUE_CARDINAL
                else:
                    focal = (WAXWING, WOODPECKER)
                    cue = CUE_WAXWING

                from packages.ovon_core.domain.habitat import HabitatType

                if cand.persona == RoutePersona.EASY:
                    ht1 = HabitatType.OPEN_PARKLAND
                    ht2 = HabitatType.OPEN_PARKLAND
                elif cand.persona == RoutePersona.BIRDY:
                    ht1 = HabitatType.MATURE_CANOPY
                    ht2 = HabitatType.POND_WATER_EDGE
                else:
                    ht1 = HabitatType.ORCHARD_EDGE
                    ht2 = HabitatType.MATURE_CANOPY

                segments_list = []
                if cand.segment_metrics and len(cand.segment_metrics) >= 2:
                    m1 = cand.segment_metrics[0]
                    m2 = cand.segment_metrics[1]

                    # Distribute total candidate distance cleanly across segments so sum == total_dist exactly
                    d1 = float(m1.get("distance_meters", cand.distance_meters * 0.4))
                    d2 = round(cand.distance_meters - d1, 1)

                    t1 = float(m1.get("duration_minutes", cand.duration_minutes * 0.4))
                    t2 = round(float(cand.duration_minutes) - t1, 1)

                    obs_pt1 = (
                        cand.waypoints[1] if cand.waypoints and len(cand.waypoints) > 1 else None
                    )
                    obs_pt2 = (
                        cand.waypoints[2] if cand.waypoints and len(cand.waypoints) > 2 else None
                    )

                    seg1 = RouteSegment(
                        index=1,
                        name=m1.get("name", f"{cand.name} Outbound Leg"),
                        habitat_name=m1.get("habitat_name", "Woodland Edge & Parkland"),
                        distance_meters=d1,
                        duration_minutes=t1,
                        focal_species=(focal[0],),
                        field_cue=cue,
                        geojson_geometry=m1.get("geojson_geometry"),
                        observation_point=obs_pt1,
                        navigation_instruction=m1.get(
                            "navigation_instruction",
                            f"Depart {request.origin_name} heading along primary park path.",
                        ),
                        habitat_type=ht1,
                    )

                    seg2 = RouteSegment(
                        index=2,
                        name=m2.get("name", f"{cand.name} Return Loop Leg"),
                        habitat_name=m2.get("habitat_name", "Canopy & Meadow Boundary"),
                        distance_meters=d2,
                        duration_minutes=t2,
                        focal_species=focal,
                        field_cue=cue,
                        geojson_geometry=m2.get("geojson_geometry"),
                        observation_point=obs_pt2,
                        navigation_instruction=m2.get(
                            "navigation_instruction",
                            f"Bear right onto return loop trail back to {request.origin_name}.",
                        ),
                        habitat_type=ht2,
                    )
                    segments_list = [seg1, seg2]
                else:
                    d1 = round(cand.distance_meters * 0.4, 1)
                    d2 = round(cand.distance_meters - d1, 1)
                    t1 = round(float(cand.duration_minutes) * 0.4, 1)
                    t2 = round(float(cand.duration_minutes) - t1, 1)

                    seg1 = RouteSegment(
                        index=1,
                        name=f"{cand.name} Outbound Leg",
                        habitat_name="Woodland Edge & Parkland",
                        distance_meters=d1,
                        duration_minutes=t1,
                        focal_species=(focal[0],),
                        field_cue=cue,
                        geojson_geometry=cand.geojson_geometry,
                        observation_point=cand.waypoints[1]
                        if cand.waypoints and len(cand.waypoints) > 1
                        else None,
                        navigation_instruction=f"Depart {request.origin_name} heading along primary park path.",
                        habitat_type=ht1,
                    )

                    seg2 = RouteSegment(
                        index=2,
                        name=f"{cand.name} Return Loop Leg",
                        habitat_name="Canopy & Meadow Boundary",
                        distance_meters=d2,
                        duration_minutes=t2,
                        focal_species=focal,
                        field_cue=cue,
                        geojson_geometry=cand.geojson_geometry,
                        observation_point=cand.waypoints[2]
                        if cand.waypoints and len(cand.waypoints) > 2
                        else None,
                        navigation_instruction=f"Bear right onto return trail back to {request.origin_name}.",
                        habitat_type=ht2,
                    )
                    segments_list = [seg1, seg2]

                opt = RouteOption(
                    id=f"{cand.persona.name.lower()}-1"
                    if cand.persona == RoutePersona.EASY
                    else f"{cand.persona.name.lower()}-{len(options) + 1}",
                    persona=cand.persona,
                    name=cand.name,
                    tagline=cand.tagline,
                    duration_minutes=cand.duration_minutes,
                    distance_meters=cand.distance_meters,
                    badge_label=cand.badge_label,
                    tradeoff_description=cand.tradeoff_description,
                    segments=tuple(segments_list),
                    geojson_geometry=cand.geojson_geometry,
                )

                if cand.persona == RoutePersona.EASY:
                    easy_baseline = opt

                options.append(opt)

            final_options = []
            for opt in options:
                tradeoff_text = self.explanation_generator.generate_tradeoff_description(
                    opt, easy_baseline
                )
                updated_opt = RouteOption(
                    id=opt.id,
                    persona=opt.persona,
                    name=opt.name,
                    tagline=opt.tagline,
                    duration_minutes=opt.duration_minutes,
                    distance_meters=opt.distance_meters,
                    badge_label=opt.badge_label,
                    tradeoff_description=tradeoff_text,
                    segments=opt.segments,
                    geojson_geometry=opt.geojson_geometry,
                )
                final_options.append(updated_opt)

            routes_tuple = tuple(final_options)
            return RouteMenuResult(
                routes=routes_tuple,
                source="live_osm",
                warning=None,
            )
        except Exception as e:
            # Explicit degraded fallback with warning
            return RouteMenuResult(
                routes=(ROUTE_EASY, ROUTE_BIRDY, ROUTE_WEIRD),
                source="prototype_fixture",
                warning=f"Live routing graph solver was unable to solve candidates ({e}). Displaying demonstration routes.",
            )
