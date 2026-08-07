from pathlib import Path

from flask import Flask

from apps.web.app.config import DevelopmentConfig
from packages.ovon_core.media import LocalMediaRepository
from packages.ovon_core.routing import OSMnxIgraphRoutingProvider
from packages.ovon_core.spatial import NominatimGeocoderProvider


def create_app(config_class=DevelopmentConfig):
    """Flask Application Factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize and inject Media Repository extension
    manifest_path = Path(app.root_path).parent.parent.parent / "data" / "media_manifest.json"
    if not manifest_path.exists():
        manifest_path = Path("data/media_manifest.json")
    app.extensions["media_repository"] = LocalMediaRepository(
        manifest_path if manifest_path.exists() else None
    )

    # Initialize and inject Routing Provider & Geocoder extensions
    app.extensions["routing_provider"] = OSMnxIgraphRoutingProvider()
    app.extensions["geocoder_provider"] = NominatimGeocoderProvider()

    # Configure isolated database paths for testing mode
    if app.config.get("TESTING"):
        from apps.web.app.services.feedback_repository import WalkFeedbackRepository
        from apps.web.app.services.planner_service import RoutePlanRepository

        RoutePlanRepository.set_db_path(app.config.get("PLANNER_DB_PATH", ":memory:"))
        WalkFeedbackRepository.set_db_path(app.config.get("FEEDBACK_DB_PATH", ":memory:"))

    # Register Blueprints
    from apps.web.app.blueprints.admin import admin_bp
    from apps.web.app.blueprints.planner import planner_bp
    from apps.web.app.blueprints.routes import routes_bp
    from apps.web.app.blueprints.search_lab import search_lab_bp
    from apps.web.app.blueprints.species import species_bp

    app.register_blueprint(planner_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(species_bp)
    app.register_blueprint(search_lab_bp)
    app.register_blueprint(admin_bp)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok", "app": app.config["PROJECT_NAME"]}

    @app.route("/media/cached/<path:filename>")
    def serve_cached_media(filename):
        from flask import send_from_directory

        media_dir = Path(app.root_path).parents[2] / "media" / "cached"
        return send_from_directory(media_dir, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000)
