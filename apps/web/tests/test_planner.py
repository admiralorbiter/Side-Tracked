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


# Step 3: Duration Screen & POST Address Privacy
def test_duration_screen_htmx_post(client):
    response = client.post(
        "/planner/duration",
        data={"origin": "Loose Park, Kansas City, MO"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "HX-Push-Url" in response.headers
    assert b"How long do you want to get sidetracked?" in response.data
    assert b"Loose Park" in response.data


# Step 3: Invalid Location Error Handling
def test_origin_resolution_error_handling(client):
    response = client.post(
        "/planner/duration",
        data={"origin": "1234 invalid non-existent street name xyz"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    assert (
        b"supported location" in response.data.lower()
        or b"kansas city pilot" in response.data.lower()
    )


# Step 4: Planning Animated State
def test_planning_state_htmx(client):
    response = client.post(
        "/planner/planning",
        data={"origin": "Loose Park", "duration": "45"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert b"Planning your Nature Loop" in response.data
    assert b"Searching pedestrian trail networks" in response.data


# Step 5: Route Comparison & Domain Model Output
def test_results_domain_routes(client):
    response = client.post(
        "/planner/results",
        data={"duration": "45"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Push-Url") == "/planner/results"
    assert b"The Easy One" in response.data
    assert b"The Birdy One" in response.data
    assert b"The Weird One" in response.data


def test_results_get_refresh_support(client):
    client.post("/planner/results", data={"duration": "45"})
    get_resp = client.get("/planner/results")
    assert get_resp.status_code == 200
    assert b"The Easy One" in get_resp.data


# Step 5 Error Handling: Invalid Duration
def test_results_invalid_duration_error(client):
    response = client.post(
        "/planner/results",
        data={"duration": "999"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    assert b"unsupported" in response.data.lower() or b"error" in response.data.lower()


# Step 6: Plan-Scoped Route Detail
def test_plan_scoped_route_details(client):
    res = client.post("/planner/results", data={"duration": "45"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    assert len(plans) > 0
    plan_id = plans[-1]

    easy_resp = client.get(f"/plans/{plan_id}/routes/easy-1")
    assert easy_resp.status_code == 200
    assert b"The Easy One" in easy_resp.data
    assert b"Lowest Effort" in easy_resp.data


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


def test_species_detail_unknown_404(client):
    response = client.get("/species/banana")
    assert response.status_code == 404


def test_plan_isolation_rejects_invalid_or_expired_plan_id(client):
    # Invalid or non-existent plan ID must yield 404/410, never another user's plan or fallback fixture
    resp = client.get("/plans/invalidplan123/routes/easy-1")
    assert resp.status_code == 404


def test_all_plan_scoped_route_walk_and_recap_screens(client):
    res = client.post("/planner/results", data={"duration": "45"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]
    routes = RoutePlanRepository.get_plan_routes(plan_id)
    assert routes is not None

    for r in routes:
        # Test route detail page contains correct plan-scoped walk link
        detail_resp = client.get(f"/plans/{plan_id}/routes/{r.id}")
        assert detail_resp.status_code == 200
        assert f"/plans/{plan_id}/routes/{r.id}/walk".encode("utf-8") in detail_resp.data

        # Test active walk screen
        walk_resp = client.get(f"/plans/{plan_id}/routes/{r.id}/walk")
        assert walk_resp.status_code == 200
        assert b"Walk Mode Active" in walk_resp.data

        # Test recap screen
        recap_resp = client.get(f"/plans/{plan_id}/routes/{r.id}/recap")
        assert recap_resp.status_code == 200
        assert b"Walk Completed" in recap_resp.data


