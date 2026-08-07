"""Integration tests for Scientific Survey Mode UI flow and telemetry header."""

import pytest

from apps.web.app import create_app
from apps.web.app.config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_survey_mode_opt_in_renders_telemetry_banner_and_recap_modal(client):
    # 1. Post planner results with survey_mode=on
    res = client.post("/planner/results", data={"duration": "30", "survey_mode": "on"})
    assert res.status_code == 200

    from apps.web.app.services.planner_service import RoutePlanRepository

    plans = list(RoutePlanRepository._plans.keys())
    plan_id = plans[-1]

    # 2. Access Walk Mode -> renders SURVEY MODE ACTIVE telemetry banner
    walk_res = client.get(f"/plans/{plan_id}/routes/easy-1/walk")
    assert walk_res.status_code == 200
    assert b"SURVEY MODE ACTIVE" in walk_res.data
    assert b"eBird Traveling Protocol" in walk_res.data

    # 3. Access Recap screen -> renders Scientific Protocol Checklist Verification
    recap_res = client.get(f"/plans/{plan_id}/routes/easy-1/recap")
    assert recap_res.status_code == 200
    assert b"Scientific Protocol Checklist Verification" in recap_res.data
    assert b"Complete Checklist:" in recap_res.data
