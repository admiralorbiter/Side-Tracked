from flask import Blueprint, render_template, request

planner_bp = Blueprint("planner", __name__)

@planner_bp.route("/")
def index():
    """Home intent selection screen."""
    return render_template("planner/index.html")

@planner_bp.route("/planner/origin", methods=["GET", "POST"])
def origin():
    """Step 2: Choose starting origin (address, pin, current location)."""
    if request.headers.get("HX-Request"):
        return render_template("planner/origin.html")
    return render_template("planner/index.html", step="origin")

@planner_bp.route("/planner/duration", methods=["GET", "POST"])
def duration():
    """Step 3: Choose duration budget (default 45 min)."""
    origin_location = request.form.get("origin", "Current Location")
    if request.headers.get("HX-Request"):
        return render_template("planner/duration.html", origin=origin_location)
    return render_template("planner/index.html", step="duration", origin=origin_location)

@planner_bp.route("/planner/results", methods=["POST"])
def results():
    """Step 4: Display Easy, Birdy, and Weird route options."""
    origin_loc = request.form.get("origin", "Loose Park, Kansas City")
    minutes = request.form.get("duration", "45")
    
    # Mock route options for initial UI prototype
    mock_routes = [
        {
            "id": "easy-1",
            "name": "The Easy One",
            "tagline": "Shortest path with paved trails and low elevation change.",
            "duration": f"{minutes} min",
            "distance": "1.8 km",
            "bird_count": 8,
            "badge": "Lowest effort",
            "species_highlights": ["American Robin", "Northern Cardinal", "Blue Jay"],
            "tradeoff": "Paved park paths with standard suburban bird activity."
        },
        {
            "id": "birdy-1",
            "name": "The Birdy One",
            "tagline": "Diverges into dense tree canopy and creek bed edge habitat.",
            "duration": f"{minutes} min",
            "distance": "2.2 km",
            "bird_count": 16,
            "badge": "Best bird opportunity",
            "species_highlights": ["Red-headed Woodpecker", "Tufted Titmouse", "Carolina Wren", "Barred Owl"],
            "tradeoff": "Adds 400m of dirt trail near Brush Creek for double the species diversity."
        },
        {
            "id": "weird-1",
            "name": "The Weird One",
            "tagline": "Explores lesser-known perimeter tree line and old orchard edge.",
            "duration": f"{minutes} min",
            "distance": "2.1 km",
            "bird_count": 12,
            "badge": "Unusual habitat",
            "species_highlights": ["Cedar Waxwing", "White-breasted Nuthatch", "Cooper's Hawk"],
            "tradeoff": "Uneven terrain along forgotten overgrown fence line."
        }
    ]
    
    if request.headers.get("HX-Request"):
        return render_template("planner/routes_preview.html", routes=mock_routes, origin=origin_loc, minutes=minutes)
    return render_template("planner/index.html", routes=mock_routes, origin=origin_loc, minutes=minutes)
