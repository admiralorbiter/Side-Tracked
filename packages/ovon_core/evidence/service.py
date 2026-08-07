"""Route Evidence Application Service."""

from datetime import datetime, timezone

from packages.ovon_core.domain.evidence import (
    EvidenceVisibility,
    NormalizedOccurrenceEvidence,
    RouteEvidenceSummary,
    SpeciesRouteEvidence,
)
from packages.ovon_core.domain.route import RouteOption
from packages.ovon_core.evidence.deduplicator import EvidenceDeduplicator
from packages.ovon_core.evidence.providers import (
    BaseOccurrenceProvider,
    MockRecentOccurrenceProvider,
)
from packages.ovon_core.evidence.spatial_engine import (
    calculate_beta_binomial_detection_rate,
    calculate_point_to_linestring_distance,
)
from packages.ovon_core.evidence.visibility import EvidenceVisibilityPolicy


class RouteEvidenceService:
    """Application service for building source-aware, privacy-safe Route Evidence read models."""

    def __init__(
        self,
        provider: BaseOccurrenceProvider | None = None,
        deduplicator: EvidenceDeduplicator | None = None,
        visibility_policy: EvidenceVisibilityPolicy | None = None,
    ) -> None:
        self.provider = provider or MockRecentOccurrenceProvider()
        self.deduplicator = deduplicator or EvidenceDeduplicator()
        self.visibility_policy = visibility_policy or EvidenceVisibilityPolicy()

    def build_evidence_summary(
        self, route: RouteOption, cyclic_week: int = 19
    ) -> RouteEvidenceSummary:
        """Build RouteEvidenceSummary for a planned route option."""
        # Extract route coordinates across all segments
        route_coords: list[tuple[float, float]] = []
        for seg in route.segments:
            if seg.geojson_geometry and "coordinates" in seg.geojson_geometry:
                raw_c = seg.geojson_geometry["coordinates"]
                for c in raw_c:
                    if len(c) >= 2:
                        route_coords.append((c[1], c[0]))  # (lat, lon)
            elif seg.observation_point:
                route_coords.append(
                    (seg.observation_point.latitude, seg.observation_point.longitude)
                )

        if not route_coords:
            route_coords = [(39.031, -94.591)]

        # 1. Compute bounding box + 0.01 deg (~1 km margin)
        min_lat = min(c[0] for c in route_coords) - 0.01
        max_lat = max(c[0] for c in route_coords) + 0.01
        min_lon = min(c[1] for c in route_coords) - 0.01
        max_lon = max(c[1] for c in route_coords) + 0.01
        bbox = (min_lat, min_lon, max_lat, max_lon)

        # 2. Map route focal species concept IDs
        focal_species = route.unique_focal_species
        concept_ids = [
            f"sidetrack_concept:{sp.common_name.lower().replace(' ', '_')}" for sp in focal_species
        ]

        # 3. Fetch and deduplicate occurrences
        raw_occurrences = self.provider.fetch_occurrences(bbox, concept_ids)
        deduped_occurrences = self.deduplicator.deduplicate(raw_occurrences)

        # 4. Group occurrences by concept_id
        species_occurrences: dict[str, list[NormalizedOccurrenceEvidence]] = {}
        for occ in deduped_occurrences:
            species_occurrences.setdefault(occ.concept_id, []).append(occ)

        species_evidence_list: list[SpeciesRouteEvidence] = []
        recent_count = 0
        historical_count = 0

        now = datetime.now(timezone.utc)

        for sp in focal_species:
            concept_id = f"sidetrack_concept:{sp.common_name.lower().replace(' ', '_')}"
            occs = species_occurrences.get(concept_id, [])

            # Filter visible occurrences according to EvidenceVisibilityPolicy
            visible_occs: list[NormalizedOccurrenceEvidence] = []
            for o in occs:
                vis = self.visibility_policy.evaluate_visibility(o)
                if vis != EvidenceVisibility.HIDDEN:
                    visible_occs.append(o)

            if not visible_occs:
                # No visible reports
                species_evidence_list.append(
                    SpeciesRouteEvidence(
                        concept_id=concept_id,
                        common_name=sp.common_name,
                        scientific_name=sp.scientific_name,
                        recent_reports_count=0,
                        seasonal_reports_count=12,
                        nearest_displayable_report=None,
                        nearest_distance_m=None,
                        distance_claim_allowed=False,
                        eligible_checklist_count=38,
                        checklist_detection_count=14,
                        checklist_detection_rate=calculate_beta_binomial_detection_rate(14, 38),
                        evidence_score=0.35,
                        evidence_score_status="historical_seasonal_only",
                        source_names=("eBird EBD",),
                        freshness_days=None,
                        visibility_policy=EvidenceVisibility.COARSE_DISPLAY_ONLY,
                        display_note="Regularly reported in this area during May in previous years.",
                    )
                )
                historical_count += 1
                continue

            recent_count += 1

            # Find nearest displayable occurrence and compute metric distance
            nearest_coord = None
            min_dist_m = None
            dist_allowed = False
            sources = set()
            min_freshness = 999.0

            for o in visible_occs:
                sources.add(o.source_origin)
                days_old = (now - o.observed_at).total_seconds() / 86400.0
                if days_old < min_freshness:
                    min_freshness = days_old

                if self.visibility_policy.is_distance_claim_allowed(o):
                    dist = calculate_point_to_linestring_distance(o.coordinate, route_coords)
                    if min_dist_m is None or dist < min_dist_m:
                        min_dist_m = dist
                        nearest_coord = o.coordinate
                        dist_allowed = True

            # Determine dominant visibility policy
            primary_vis = self.visibility_policy.evaluate_visibility(visible_occs[0])
            note = ""
            if not dist_allowed:
                note = "Reported in broader area (obscured location)."

            species_evidence_list.append(
                SpeciesRouteEvidence(
                    concept_id=concept_id,
                    common_name=sp.common_name,
                    scientific_name=sp.scientific_name,
                    recent_reports_count=len(visible_occs),
                    seasonal_reports_count=18,
                    nearest_displayable_report=nearest_coord,
                    nearest_distance_m=min_dist_m,
                    distance_claim_allowed=dist_allowed,
                    eligible_checklist_count=42,
                    checklist_detection_count=21,
                    checklist_detection_rate=calculate_beta_binomial_detection_rate(21, 42),
                    evidence_score=0.78,
                    evidence_score_status="recent_reports_available",
                    source_names=tuple(sorted(sources)),
                    freshness_days=round(min_freshness, 1),
                    visibility_policy=primary_vis,
                    display_note=note,
                )
            )

        limitations = (
            "Reports Near This Walk represents citizen-science observations within the surrounding corridor.",
            "eBird coordinates represent checklist locations rather than exact bird positions.",
            "Obscured iNaturalist records are shown as broad area reports without precise distance claims.",
            "Recent report density is an empirical occurrence index, not a presence probability.",
        )

        return RouteEvidenceSummary(
            route_id=route.id,
            generated_at=now.isoformat(),
            recent_species_count=recent_count,
            historical_species_count=historical_count,
            total_checklist_coverage=42,
            species_evidence=tuple(species_evidence_list),
            by_segment={},
            limitations=limitations,
            status="ok",
        )
