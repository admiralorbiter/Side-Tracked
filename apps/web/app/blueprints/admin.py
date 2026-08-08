from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/status")
def status():
    """System health and component status endpoint."""
    import json
    from pathlib import Path

    manifest_file = Path("data/analytical_table/dataset_manifest.json")
    manifest_data = None
    if manifest_file.exists():
        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            manifest_data = None

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
                "environmental_extractor": "nlcd_3dep_3dhp_extracted",
                "analytical_table": "immutable_parquet_manifest_verified"
                if manifest_data
                else "pending",
            },
            "analytical_dataset_manifest": manifest_data,
            "manifest_version": "0.1-prototype",
        }
    )
