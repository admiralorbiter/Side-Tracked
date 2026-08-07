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


def test_app_is_testing(app):
    assert app.config["TESTING"] is True
    assert app.config["PROJECT_NAME"] == "Sidetrack"


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "ok"
    assert json_data["app"] == "Sidetrack"


def test_admin_status(client):
    response = client.get("/admin/status")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert "Greater Kansas City" in json_data["region"]
    assert json_data["components"]["web"] == "ready"
    assert json_data["components"]["routing"] == "osmnx_igraph_ready"
    assert json_data["components"]["geocoding"] == "nominatim_ready"
    assert json_data["components"]["ecology"] == "deterministic_surface"
