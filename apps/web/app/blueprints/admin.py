from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/status")
def status():
    """System health and data manifest status endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "region": "Greater Kansas City",
            "routing_engine": "OSMnx + igraph (Native Python)",
            "manifest_version": "1.0-frozen",
        }
    )
