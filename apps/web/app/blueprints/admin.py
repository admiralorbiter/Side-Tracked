from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/status")
def status():
    """System health and component status endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "region": "Greater Kansas City (Pilot)",
            "components": {
                "web": "ready",
                "media": "prototype",
                "routing": "osmnx_igraph_ready",
                "geocoding": "nominatim_ready",
                "ecology": "deterministic_surface",
            },
            "manifest_version": "0.1-prototype",
        }
    )
