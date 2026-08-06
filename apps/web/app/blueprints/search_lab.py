from flask import Blueprint, render_template

search_lab_bp = Blueprint("search_lab", __name__)

@search_lab_bp.route("/search-lab")
def index():
    """Species Search Lab placeholder view."""
    return render_template("search_lab/index.html")
