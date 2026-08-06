import pytest
from apps.web.app import create_app
from apps.web.app.config import TestingConfig

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    return app.test_client()

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"How do you want to get sidetracked?" in response.data
    assert b"Take a loop from here" in response.data

def test_origin_htmx_partial(client):
    response = client.get("/planner/origin", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert b"Where should we start?" in response.data
    assert b"Loose Park, Kansas City" in response.data

def test_duration_htmx_partial(client):
    response = client.post("/planner/duration", data={"origin": "Loose Park, KC"}, headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert b"How long do you want to get sidetracked?" in response.data
    assert b"45 minutes" in response.data

def test_results_htmx_partial(client):
    response = client.post("/planner/results", data={"origin": "Loose Park, KC", "duration": "45"}, headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert b"The Easy One" in response.data
    assert b"The Birdy One" in response.data
    assert b"The Weird One" in response.data
    assert b"Brush Creek Canopy Trail" in response.data or b"Red-headed Woodpecker" in response.data

def test_route_detail(client):
    response = client.get("/routes/birdy-1")
    assert response.status_code == 200
    assert b"The Birdy One" in response.data
    assert b"WHERE TO LOOK" in response.data
    assert b"WHAT TO LISTEN FOR" in response.data

def test_species_detail(client):
    response = client.get("/species/red_headed_woodpecker")
    assert response.status_code == 200
    assert b"Red-headed Woodpecker" in response.data
    assert b"Melanerpes erythrocephalus" in response.data
