"""Application Service for Building Habitat Radar."""

from collections import defaultdict

from packages.ovon_core.domain import RouteOption, TaxonRef
from packages.ovon_core.ecology.candidate_provider import (
    CandidateTaxaProvider,
    KansasCityCandidateTaxaProvider,
)
from packages.ovon_core.ecology.ecology_profile import KC_TAXON_ECOLOGY_PROFILES, HabitatGuild
from packages.ovon_core.ecology.habitat import HabitatType
from packages.ovon_core.ecology.habitat_radar import HabitatRadar, RadarSpecies
from packages.ovon_core.ecology.recommender import DefaultSegmentSpeciesRecommender, SegmentContext
from packages.ovon_core.spatial.h3_indexer import polyline_to_h3_cells


class BuildHabitatRadar:
    """Application service for constructing route-level and segment-level Habitat Radar."""

    def __init__(self, candidate_provider: CandidateTaxaProvider | None = None):
        self.candidate_provider = candidate_provider or KansasCityCandidateTaxaProvider()

    def execute(self, route: RouteOption, season_week: int = 20) -> HabitatRadar:
        """Calculate length-weighted habitat radar species ranking for a route."""
        # 1. Traversed H3 cells for route geometry
        traversed_cells = polyline_to_h3_cells(route.geojson_geometry, resolution=8)

        # 2. Query candidate taxa provider for candidate universe
        candidates = self.candidate_provider.candidates(traversed_cells, week=season_week)

        # 3. Calculate segment-specific radar scores
        segment_radar: dict[int, list[tuple[TaxonRef, float]]] = {}
        segment_species_matches: dict[int, set[str]] = defaultdict(set)

        # Track total length for length-weighted scoring
        total_route_length = max(route.distance_meters, 1.0)
        weighted_scores: dict[str, float] = defaultdict(float)
        taxon_by_code: dict[str, TaxonRef] = {}

        for seg in route.segments:
            taxon_by_code.update({sp.ebird_code: sp for sp in seg.focal_species})
            seg_len = max(seg.distance_meters, 1.0)
            seg_habitat = getattr(HabitatType, seg.habitat_name.upper().replace(" ", "_"), HabitatType.OPEN_PARKLAND)

            # Evaluate recommender for segment context
            recommender = DefaultSegmentSpeciesRecommender()
            recommender.candidate_pool = candidates
            opportunities = recommender.recommend_species(
                SegmentContext(
                    traversed_h3_cells=traversed_cells,
                    habitat_type=seg_habitat,
                    season_week=season_week,
                ),
                limit=len(candidates),
            )

            seg_list = []
            for opp in opportunities:
                taxon_by_code[opp.taxon.ebird_code] = opp.taxon
                weighted_scores[opp.taxon.ebird_code] += (opp.score * seg_len) / total_route_length
                seg_list.append((opp.taxon, opp.score))
                if opp.score >= 0.40:
                    segment_species_matches[seg.index].add(opp.taxon.ebird_code)

            segment_radar[seg.index] = seg_list

        # Identify primary focal species
        focal_codes: set[str] = set()
        for seg in route.segments:
            for sp in seg.focal_species:
                focal_codes.add(sp.ebird_code)

        # Build RadarSpecies records
        focal_radar_list: list[RadarSpecies] = []
        nearby_radar_list: list[RadarSpecies] = []

        # Sort candidate codes by weighted score descending
        sorted_codes = sorted(weighted_scores.keys(), key=lambda k: weighted_scores[k], reverse=True)

        for code in sorted_codes:
            t = taxon_by_code[code]
            score = round(weighted_scores[code], 3)
            matched_segs = tuple(sorted([seg_idx for seg_idx, sp_set in segment_species_matches.items() if code in sp_set]))
            
            profile = KC_TAXON_ECOLOGY_PROFILES.get(code)
            guild = profile.primary_guild if profile else HabitatGuild.OPEN_EDGE

            # Generate human-readable reason codes
            reasons = []
            if guild == HabitatGuild.WOODLAND:
                reasons.append("canopy_match")
            elif guild == HabitatGuild.WATER_RIPARIAN:
                reasons.append("water_edge_match")
            elif guild == HabitatGuild.AERIAL:
                reasons.append("aerial_canopy_match")
            else:
                reasons.append("lawn_edge_match")

            if len(matched_segs) >= len(route.segments):
                reasons.append("full_route_exposure")

            radar_sp = RadarSpecies(
                taxon=t,
                relative_score=score,
                matched_segment_ids=matched_segs,
                primary_guild=guild,
                support_tier="Provisional Matrix",
                reason_codes=tuple(reasons),
            )

            if code in focal_codes:
                focal_radar_list.append(radar_sp)
            else:
                nearby_radar_list.append(radar_sp)

        # Build segment-level radar dictionary (top 4 per segment)
        by_segment: dict[int, tuple[RadarSpecies, ...]] = {}
        for seg in route.segments:
            seg_opps = segment_radar.get(seg.index, [])
            seg_species_list = []
            for t, sc in seg_opps[:6]:
                if t.ebird_code not in focal_codes:
                    profile = KC_TAXON_ECOLOGY_PROFILES.get(t.ebird_code)
                    g = profile.primary_guild if profile else HabitatGuild.OPEN_EDGE
                    seg_species_list.append(
                        RadarSpecies(
                            taxon=t,
                            relative_score=sc,
                            matched_segment_ids=(seg.index,),
                            primary_guild=g,
                        )
                    )
            by_segment[seg.index] = tuple(seg_species_list[:4])

        # Group nearby species by habitat guild
        by_guild: dict[HabitatGuild, list[RadarSpecies]] = defaultdict(list)
        for rsp in nearby_radar_list[:12]:
            by_guild[rsp.primary_guild].append(rsp)

        by_guild_tuple: dict[HabitatGuild, tuple[RadarSpecies, ...]] = {
            g: tuple(sps) for g, sps in by_guild.items()
        }

        return HabitatRadar(
            focal=tuple(focal_radar_list),
            nearby=tuple(nearby_radar_list[:12]),
            by_segment=by_segment,
            by_guild=by_guild_tuple,
            total_catalog_matches=len(nearby_radar_list),
        )
