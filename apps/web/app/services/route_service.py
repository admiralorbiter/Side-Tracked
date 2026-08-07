"""Route Application Services."""

from flask import current_app

from packages.ovon_core.domain import (
    MediaType,
    RouteFieldPack,
    RouteOption,
)
from packages.ovon_core.ecology import ProvisionalSpeciesSurface
from packages.ovon_core.fixtures import ALL_FIXTURE_ROUTES
from packages.ovon_core.media import MediaRepository
from packages.ovon_core.spatial import polyline_to_h3_cells


class GetRouteDetail:
    """Application Service for retrieving a RouteOption by plan_id and route_id."""

    def execute(self, plan_id: str | None, route_id: str) -> RouteOption | None:
        """Retrieve distinct route option scoped to plan_id, or None if missing/expired."""
        from apps.web.app.services.planner_service import RoutePlanRepository

        clean_route_id = route_id.lower().strip()

        if plan_id:
            return RoutePlanRepository.get_route(plan_id, clean_route_id)

        if current_app and "active_routes" in current_app.extensions:
            active: RouteOption | None = current_app.extensions["active_routes"].get(clean_route_id)
            if active and isinstance(active, RouteOption):
                return active

        return ALL_FIXTURE_ROUTES.get(clean_route_id)


class BuildFieldPack:
    """Application Service for building a route-specific RouteFieldPack with dynamic H3 ecological scoring."""

    def __init__(
        self,
        media_repository: MediaRepository | None = None,
        species_surface: ProvisionalSpeciesSurface | None = None,
    ):
        self._media_repo = media_repository
        self.species_surface = species_surface or ProvisionalSpeciesSurface()

    @property
    def media_repo(self) -> MediaRepository | None:
        if self._media_repo:
            return self._media_repo
        if current_app and "media_repository" in current_app.extensions:
            repo: MediaRepository = current_app.extensions["media_repository"]
            return repo
        return None

    def execute(self, route: RouteOption) -> RouteFieldPack:
        """Construct a route-specific field pack with focal species, cues, and media assets."""
        focal_taxa = []
        cues = []
        media_assets = []

        repo = self.media_repo

        # Sample route geometry into H3 spatial cells for dynamic ecological opportunity ranking
        traversed_cells = polyline_to_h3_cells(route.geojson_geometry, resolution=8)

        from packages.ovon_core.ecology.recommender import DefaultSegmentSpeciesRecommender, SegmentContext

        recommender = DefaultSegmentSpeciesRecommender(species_surface=self.species_surface)
        rec_opportunities = recommender.recommend_species(
            SegmentContext(traversed_h3_cells=traversed_cells)
        )

        for opp in rec_opportunities:
            if opp.taxon not in focal_taxa:
                focal_taxa.append(opp.taxon)

        for seg in route.segments:
            for sp in seg.focal_species:
                if sp not in focal_taxa:
                    focal_taxa.append(sp)

                if repo:
                    # Query both photos and audio assets for each species
                    photos = repo.get_assets_for_taxon(sp, media_type=MediaType.PHOTO)
                    audio = repo.get_assets_for_taxon(sp, media_type=MediaType.AUDIO)

                    for asset in photos + audio:
                        if asset not in media_assets:
                            media_assets.append(asset)

            if seg.field_cue and seg.field_cue not in cues:
                cues.append(seg.field_cue)

        return RouteFieldPack(
            route_id=route.id,
            focal_species=tuple(focal_taxa),
            field_cues=tuple(cues),
            media_assets=tuple(media_assets),
        )
