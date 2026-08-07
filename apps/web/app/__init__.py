from pathlib import Path

from flask import Flask

from apps.web.app.config import DevelopmentConfig
from packages.ovon_core.media import LocalMediaRepository


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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000)
