from flask import Blueprint, render_template, abort

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/routes/<route_id>")
def detail(route_id):
    """Detailed view for a specific route including field guide pack."""
    # Fixture route data for prototype
    mock_detail = {
        "id": route_id,
        "name": "The Birdy One",
        "duration": "45 min",
        "distance": "2.2 km",
        "segments": [
            {
                "index": 1,
                "name": "Park Perimeter & Pond Edge",
                "habitat": "Pond & Grassland",
                "distance": "700m",
                "birds": ["Mallard", "Red-winged Blackbird", "Canada Goose"],
                "cue_look": "Look along the reed edges and overhanging willow branches.",
                "cue_listen": "Listen for sharp 'conk-la-ree!' calls from high perches."
            },
            {
                "index": 2,
                "name": "Brush Creek Canopy Trail",
                "habitat": "Mature Hardwood Forest",
                "distance": "1.0 km",
                "birds": ["Red-headed Woodpecker", "Tufted Titmouse", "Carolina Wren"],
                "cue_look": "Inspect dead snags and mid-story oak branches.",
                "cue_listen": "Listen for loud rolling churring calls and rapid tapping."
            },
            {
                "index": 3,
                "name": "Return Loop via South Meadow",
                "habitat": "Open Parkland",
                "distance": "500m",
                "birds": ["American Robin", "Eastern Bluebird"],
                "cue_look": "Scan low turf and fence posts for perching bluebirds.",
                "cue_listen": "Soft cheerful warble from open lawn trees."
            }
        ]
    }
    return render_template("routes/detail.html", route=mock_detail)
