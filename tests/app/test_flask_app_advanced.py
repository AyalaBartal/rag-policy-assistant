"""Additional Flask endpoint edge-case tests."""
from __future__ import annotations

import json

import pytest

import src.app.app as app_module
from src.app.app import app


@pytest.fixture(autouse=True)
def reset_pipeline_state():
    app_module._pipeline = None
    app_module._pipeline_error = None
    app_module._pipeline_loading = False
    yield
    app_module._pipeline = None
    app_module._pipeline_error = None
    app_module._pipeline_loading = False


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_chat_accepts_unicode_question(client):
    from src.rag.rag_pipeline import RagPipeline

    app_module._pipeline = RagPipeline(llm_client=None)

    response = client.post(
        "/chat",
        data=json.dumps({"question": "¿Cuál es la política de devoluciones?"}),
        content_type="application/json",
    )
    assert response.status_code != 500


def test_chat_with_no_json_body_returns_400_or_503(client):
    response = client.post("/chat")
    assert response.status_code in (400, 415, 503)


def test_health_pipeline_error_is_reported(client):
    app_module._pipeline_error = "something went wrong"
    response = client.get("/health")
    data = json.loads(response.data)
    assert data.get("pipeline_error") == "something went wrong"


def test_chat_method_not_allowed_for_get(client):
    response = client.get("/chat")
    assert response.status_code == 405


def test_warmup_when_already_loading_returns_202(client):
    app_module._pipeline_loading = True
    response = client.post("/warmup")
    assert response.status_code == 202
