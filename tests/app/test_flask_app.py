"""
Smoke tests for the Flask web application.

These tests use Flask's built-in test client to verify that all endpoints
return the expected status codes and response shapes without starting a
real server or calling an LLM.
"""
from __future__ import annotations

import json
import pytest

import src.app.app as app_module
from src.app.app import app


@pytest.fixture(autouse=True)
def reset_pipeline_state():
    """Reset the global pipeline state before each test."""
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


# ---------------------------------------------------------------------------
# GET / — chat interface
# ---------------------------------------------------------------------------

def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_returns_html(client):
    response = client.get("/")
    content_type = response.content_type
    assert "text/html" in content_type


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "ok"


def test_health_reports_pipeline_not_ready_initially(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert data["pipeline_ready"] is False


# ---------------------------------------------------------------------------
# POST /chat — before pipeline is ready
# ---------------------------------------------------------------------------

def test_chat_returns_503_when_pipeline_not_ready(client):
    response = client.post(
        "/chat",
        data=json.dumps({"question": "What is the return policy?"}),
        content_type="application/json",
    )
    assert response.status_code == 503


def test_chat_returns_error_message_when_pipeline_not_ready(client):
    response = client.post(
        "/chat",
        data=json.dumps({"question": "What is the return policy?"}),
        content_type="application/json",
    )
    data = json.loads(response.data)
    assert "error" in data


def test_chat_returns_400_when_question_is_missing(client):
    response = client.post(
        "/chat",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code in (400, 503)


def test_chat_returns_400_for_empty_question_when_pipeline_ready(client):
    """Even with a ready pipeline, an empty question must return 400."""
    from src.rag.rag_pipeline import RagPipeline

    app_module._pipeline = RagPipeline(llm_client=None)

    response = client.post(
        "/chat",
        data=json.dumps({"question": "   "}),
        content_type="application/json",
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /chat — with mock pipeline
# ---------------------------------------------------------------------------

def test_chat_returns_answer_with_mock_pipeline(client):
    """With a CI-mode pipeline, /chat must return answer + citations + latency."""
    from src.rag.rag_pipeline import RagPipeline

    app_module._pipeline = RagPipeline(llm_client=None)

    response = client.post(
        "/chat",
        data=json.dumps({"question": "What is the return policy?"}),
        content_type="application/json",
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "answer" in data
    assert "citations" in data
    assert "latency_ms" in data
    assert isinstance(data["citations"], list)
    assert isinstance(data["latency_ms"], int)


def test_chat_answer_is_string(client):
    from src.rag.rag_pipeline import RagPipeline

    app_module._pipeline = RagPipeline(llm_client=None)

    response = client.post(
        "/chat",
        data=json.dumps({"question": "Do you ship internationally?"}),
        content_type="application/json",
    )
    data = json.loads(response.data)
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


# ---------------------------------------------------------------------------
# POST /warmup
# ---------------------------------------------------------------------------

def test_warmup_returns_202_or_200(client):
    response = client.post("/warmup")
    assert response.status_code in (200, 202)


def test_warmup_returns_json(client):
    response = client.post("/warmup")
    data = json.loads(response.data)
    assert "status" in data
