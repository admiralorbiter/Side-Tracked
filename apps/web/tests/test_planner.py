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


def test_walk_observation_feedback_submission(client):
    res = client.post("/planner/results", data={"duration": "30"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    post_data = {
        "outcome": "completed",
        "actual_duration": "32",
        "obs_amerob_seen": "1",
        "obs_norcar_heard": "1",
        "notes": "Beautiful morning walk in Loose Park.",
    }
    fb_resp = client.post(f"/plans/{plan_id}/routes/easy-1/feedback", data=post_data)
    assert fb_resp.status_code == 200
    assert b"Observation Saved!" in fb_resp.data

    from apps.web.app.services import WalkFeedbackRepository

    records = WalkFeedbackRepository.get_feedback_for_plan(plan_id, "easy-1")
    assert len(records) > 0
    assert records[0]["outcome"] == "completed"
    assert records[0]["duration_minutes"] == 32
    assert records[0]["evidence_eligibility"] == "user_recall_only"
    assert records[0]["observations"].get("amerob") == {
        "visual_detected": True,
        "audio_detected": False,
        "certainty": "confirmed",
        "not_noticed": False,
    }
    assert records[0]["observations"].get("norcar") == {
        "visual_detected": False,
        "audio_detected": True,
        "certainty": "confirmed",
        "not_noticed": False,
    }


def test_unanswered_observation_form_saves_no_default_not_noticed(client):
    res = client.post("/planner/results", data={"duration": "30"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    post_data = {
        "outcome": "completed",
        "notes": "No birds checked.",
    }
    fb_resp = client.post(f"/plans/{plan_id}/routes/easy-1/feedback", data=post_data)
    assert fb_resp.status_code == 200

    from apps.web.app.services import WalkFeedbackRepository

    records = WalkFeedbackRepository.get_feedback_for_plan(plan_id, "easy-1")
    assert len(records) > 0
    # No species should be present in observations dictionary if unanswered
    assert len(records[0]["observations"]) == 0


def test_walk_segment_blocked_endpoint_and_404_validation(client):
    res = client.post("/planner/results", data={"duration": "30"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    # Valid segment index 1
    blocked_resp = client.post(f"/plans/{plan_id}/routes/easy-1/segments/1/blocked")
    assert blocked_resp.status_code == 200
    data = blocked_resp.get_json()
    assert data["status"] == "ok"
    assert data["segment_index"] == 1

    # Invalid segment index 999 -> returns 404
    bad_resp = client.post(f"/plans/{plan_id}/routes/easy-1/segments/999/blocked")
    assert bad_resp.status_code == 404

    from apps.web.app.services import WalkFeedbackRepository

    records = WalkFeedbackRepository.get_feedback_for_plan(plan_id, "easy-1")
    assert len(records) > 0
    assert records[0]["outcome"] == "path_blocked"


def test_walk_session_lifecycle():
    from apps.web.app.services import WalkFeedbackRepository

    session = WalkFeedbackRepository.start_session("plan-test", "route-test")
    assert session["outcome"] == "active"

    finished = WalkFeedbackRepository.finish_session(session["session_id"], outcome="completed", last_segment_index=2)
    assert finished["outcome"] == "completed"
    assert finished["last_segment_index"] == 2


def test_taxon_support_builder_import_signature():
    from packages.ovon_core.domain.support_builder import TaxonSupportBuilder
    support = TaxonSupportBuilder.build("test_id", "amerob")
    assert support.taxonomy_known is True


def test_route_segment_typed_habitat():
    from packages.ovon_core.domain.route import RouteSegment
    from packages.ovon_core.ecology.habitat import HabitatType
    from packages.ovon_core.fixtures.routes_fixtures import CUE_ROBIN, ROBIN, Coordinate

    seg = RouteSegment(
        index=1,
        name="Canopy Leg",
        habitat_name="Mature Oak Canopy",
        distance_meters=500.0,
        duration_minutes=10.0,
        focal_species=(ROBIN,),
        field_cue=CUE_ROBIN,
        observation_point=Coordinate(39.0, -94.5),
        habitat_type=HabitatType.MATURE_CANOPY,
    )
    assert seg.habitat_type == HabitatType.MATURE_CANOPY


def test_plan_provenance_json_saved(client):
    res = client.post("/planner/results", data={"duration": "30"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    # Verify SQLite record has saved request_json and routing_provenance_json
    conn = RoutePlanRepository._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT request_json, routing_provenance_json FROM route_plans WHERE plan_id = ?", (plan_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["request_json"] is not None
    assert "target_duration_minutes" in row["request_json"]


def test_walk_route_starts_session_and_recap_calculates_duration(client):
    res = client.post("/planner/results", data={"duration": "30"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository
    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    # 1. Start walk route -> creates WalkSession in session
    walk_res = client.get(f"/plans/{plan_id}/routes/easy-1/walk")
    assert walk_res.status_code == 200
    assert b"Walk Mode Active" in walk_res.data

    # 2. Access recap -> computes duration and renders outcome
    recap_res = client.get(f"/plans/{plan_id}/routes/easy-1/recap?outcome=path_blocked")
    assert recap_res.status_code == 200
    assert b"Path Blocked" in recap_res.data



