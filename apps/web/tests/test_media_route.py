"""Integration test for media asset static routing and resolution."""

import pytest

from apps.web.app import create_app
from apps.web.app.config import TestingConfig


@pytest.fixture
def app():
    return create_app(TestingConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_serve_cached_media_assets(client):
    # Test serving cached JPEG image asset
    img_res = client.get("/media/cached/wm-147440408.jpg")
    assert img_res.status_code == 200
    assert img_res.content_type == "image/jpeg"
    assert len(img_res.data) > 0

    # Test serving cached OGG audio asset
    aud_res = client.get("/media/cached/wm-audio-2144744.ogg")
    assert aud_res.status_code == 200
    assert aud_res.content_type == "audio/ogg"
    assert len(aud_res.data) > 0


def test_species_detail_view_renders_media(client):
    res = client.get("/species/amerob")
    assert res.status_code == 200
    assert b"/media/cached/wm-147440408.jpg" in res.data
    assert b"/media/cached/wm-audio-2144744.ogg" in res.data
