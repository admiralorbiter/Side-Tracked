import pytest
from apps.web.app import create_app
from apps.web.app.config import TestingConfig

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    return app.test_client()

# Step 1: Home Intent
def test_home_intent_screen(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"How do you want to get sidetracked?" in response.data
    assert b"Take a loop from here" in response.data

# Step 2: Origin Screen & HX-Push-Url
def test_origin_screen_htmx(client):
    response = client.get("/planner/origin", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert response.headers.get("HX-Push-Url") == "/planner/origin"
    assert b"Where should we start?" in response.data

# Step 3: Duration Screen & HX-Push-Url
def test_duration_screen_htmx(client):
    response = client.get("/planner/duration?origin=Loose+Park", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "HX-Push-Url" in response.headers
    assert b"How long do you want to get sidetracked?" in response.data

# Step 4: Planning Animated State
def test_planning_state_htmx(client):
    response = client.post(
        "/planner/planning",
        data={"origin": "Loose Park", "duration": "45"},
        headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert b"Planning your Nature Loop" in response.data
    assert b"Searching Greater Kansas City" in response.data

# Step 5: Route Comparison & Domain Model Output
def test_results_domain_routes(client):
    response = client.post(
        "/planner/results",
        data={"origin": "Loose Park", "duration": "45"},
        headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Push-Url") is not None
    assert b"The Easy One" in response.data
    assert b"The Birdy One" in response.data
    assert b"The Weird One" in response.data
    assert b"1.8 km" in response.data or b"2.2 km" in response.data

# Step 5 Error Handling: Invalid Duration
def test_results_invalid_duration_error(client):
    response = client.post(
        "/planner/results",
        data={"origin": "Loose Park", "duration": "999"},
        headers={"HX-Request": "true"}
    )
    assert response.status_code == 400
    assert b"unsupported" in response.data.lower() or b"error" in response.data.lower()

# Step 6 & 7: Route Detail & Text Timeline
def test_route_detail_and_text_timeline(client):
    response = client.get("/routes/birdy-1")
    assert response.status_code == 200
    assert b"The Birdy One" in response.data
    assert b"Text-Equivalent Route Timeline" in response.data
    assert b"WHERE TO LOOK" in response.data
    assert b"WHAT TO LISTEN FOR" in response.data
    assert b"Play call for Red-headed Woodpecker" in response.data  # ARIA label check

# Step 8: In-Route Segment View
def test_in_route_tracking_screen(client):
    response = client.get("/routes/birdy-1/in-route")
    assert response.status_code == 200
    assert b"Walk Mode Active" in response.data
    assert b"WHERE TO LOOK" in response.data

# Step 9: Walk Recap Screen
def test_walk_recap_screen(client):
    response = client.get("/routes/birdy-1/recap")
    assert response.status_code == 200
    assert b"Walk Completed" in response.data
    assert b"Habitats Explored" in response.data

# Species Detail Page
def test_species_detail_domain_page(client):
    response = client.get("/species/rehwoo")
    assert response.status_code == 200
    assert b"Red-headed Woodpecker" in response.data
    assert b"Melanerpes erythrocephalus" in response.data
