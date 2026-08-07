"""Route Application Services."""

from flask import current_app

from packages.ovon_core.domain import (
    MediaType,
    RouteFieldPack,
    RouteOption,
)
from packages.ovon_core.fixtures import ALL_FIXTURE_ROUTES
from packages.ovon_core.media import MediaRepository


class GetRouteDetail:
    """Application Service for retrieving a RouteOption by ID."""

    def execute(self, route_id: str) -> RouteOption | None:
        """Retrieve distinct route option or None if not found."""
        return ALL_FIXTURE_ROUTES.get(route_id.lower().strip())


class BuildFieldPack:
    """Application Service for building a route-specific RouteFieldPack."""

    def __init__(self, media_repository: MediaRepository | None = None):
        self._media_repo = media_repository

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

        for seg in route.segments:
            for sp in seg.focal_species:
                if sp not in focal_taxa:
                    focal_taxa.append(sp)
                if repo:
                    audio = repo.get_assets_for_taxon(sp, media_type=MediaType.AUDIO)
                    if audio and audio[0] not in media_assets:
                        media_assets.append(audio[0])

            if seg.field_cue and seg.field_cue not in cues:
                cues.append(seg.field_cue)

        return RouteFieldPack(
            route_id=route.id,
            focal_species=tuple(focal_taxa),
            field_cues=tuple(cues),
            media_assets=tuple(media_assets),
        )
