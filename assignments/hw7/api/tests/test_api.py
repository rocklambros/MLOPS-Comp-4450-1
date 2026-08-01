"""Tests for the hw7 prediction service (Assignment 5).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>

The assignment grades one contract above all others: every call to POST /predict
appends one JSON line to the shared log carrying timestamp, request_text,
predicted_sentiment, and true_sentiment. These tests pin that contract field by
field, so a refactor that renames or drops a key fails here instead of silently
blanking the monitoring dashboard.

The rest of the file covers the validation boundary: the 422 paths, the 413 body
ceiling, and the 503 degraded mode.
"""

import json

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def log_path(tmp_path, monkeypatch):
    """Redirect the module-level LOG_PATH at a temp file for the duration of a test."""
    path = tmp_path / "prediction_logs.json"
    monkeypatch.setattr(main, "LOG_PATH", path)
    return path


@pytest.fixture
def client():
    return TestClient(main.app)


def read_log(path):
    """Parse the newline-delimited log the service writes."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# The graded logging contract -------------------------------------------------

def test_predict_logs_exactly_the_four_required_fields(client, log_path):
    response = client.post(
        "/predict",
        json={"text": "A wonderful, moving film.", "true_sentiment": "positive"},
    )

    assert response.status_code == 200
    entries = read_log(log_path)
    assert len(entries) == 1
    # The spec names these four keys. Exact-set equality, so an added or dropped key fails.
    assert set(entries[0]) == {
        "timestamp",
        "request_text",
        "predicted_sentiment",
        "true_sentiment",
    }
    assert entries[0]["request_text"] == "A wonderful, moving film."
    assert entries[0]["true_sentiment"] == "positive"
    assert entries[0]["predicted_sentiment"] in {"positive", "negative"}


def test_each_request_appends_one_new_line(client, log_path):
    for index in range(3):
        client.post("/predict", json={"text": f"Review number {index}."})

    raw = log_path.read_text(encoding="utf-8")
    assert raw.count("\n") == 3
    # Each line must parse on its own, which is what the dashboard's parser assumes.
    assert len(read_log(log_path)) == 3


def test_timestamp_is_iso_8601_utc(client, log_path):
    client.post("/predict", json={"text": "Fine."})

    timestamp = read_log(log_path)[0]["timestamp"]
    from datetime import datetime

    parsed = datetime.fromisoformat(timestamp)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_missing_feedback_is_logged_as_null_not_omitted(client, log_path):
    """The dashboard reads true_sentiment on every row, so the key must always exist."""
    response = client.post("/predict", json={"text": "It was fine, nothing special."})

    assert response.status_code == 200
    entry = read_log(log_path)[0]
    assert "true_sentiment" in entry
    assert entry["true_sentiment"] is None


def test_feedback_is_normalized_before_logging(client, log_path):
    response = client.post(
        "/predict", json={"text": "Great.", "true_sentiment": "  POSITIVE "}
    )

    assert response.status_code == 200
    assert read_log(log_path)[0]["true_sentiment"] == "positive"


def test_response_echoes_the_logged_record(client, log_path):
    response = client.post(
        "/predict", json={"text": "Superb.", "true_sentiment": "positive"}
    )

    body = response.json()
    entry = read_log(log_path)[0]
    assert body["timestamp"] == entry["timestamp"]
    assert body["predicted_sentiment"] == entry["predicted_sentiment"]
    assert body["true_sentiment"] == entry["true_sentiment"]
    assert body["logged"] is True


# Validation boundary ---------------------------------------------------------

@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"text": ""}, id="blank-text"),
        pytest.param({"text": "   "}, id="whitespace-only-text"),
        pytest.param({"true_sentiment": "positive"}, id="missing-text"),
        pytest.param({"text": "ok", "surprise": 1}, id="extra-field"),
        pytest.param({"text": "ok", "true_sentiment": "maybe"}, id="bad-feedback-value"),
        pytest.param({"text": 12345}, id="text-not-a-string"),
    ],
)
def test_invalid_bodies_return_422(client, log_path, payload):
    assert client.post("/predict", json=payload).status_code == 422
    # A rejected request must not reach the log; the dashboard only sees real traffic.
    assert read_log(log_path) == []


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_floats_return_422_not_500(client, log_path, literal):
    """Regression: FastAPI echoes the bad input into the 422 body, and Starlette
    renders JSON with allow_nan=False, so an uncoerced non-finite float turned the
    422 into a 500. _json_safe coerces it. See main.validation_exception_handler."""
    response = client.post(
        "/predict",
        content=f'{{"text":"ok","true_sentiment":{literal}}}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert read_log(log_path) == []


def test_text_over_max_length_returns_422(client, log_path):
    oversized = "word " * (main.MAX_TEXT_LENGTH // 2)
    assert len(oversized) > main.MAX_TEXT_LENGTH

    assert client.post("/predict", json={"text": oversized}).status_code == 422
    assert read_log(log_path) == []


def test_oversized_body_returns_413(client, log_path):
    """Bounds the bytes buffered off the wire, ahead of validation. Without this an
    unbounded request also poisons the dashboard's live length distribution."""
    payload = json.dumps({"text": "a" * (main.MAX_BODY_BYTES + 1024)})
    assert len(payload) > main.MAX_BODY_BYTES

    response = client.post(
        "/predict", content=payload, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 413
    assert read_log(log_path) == []


def test_body_at_the_limit_is_not_rejected_as_too_large(client, log_path):
    """The ceiling must reject only what exceeds it, so a large-but-legal body passes
    the middleware and is then judged on its own merits by validation."""
    payload = json.dumps({"text": "a" * 2000})
    assert len(payload) < main.MAX_BODY_BYTES

    assert client.post(
        "/predict", content=payload, headers={"Content-Type": "application/json"}
    ).status_code == 200


# Health and degraded mode ----------------------------------------------------

def test_health_reports_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_stays_up_when_the_model_is_missing(client, monkeypatch):
    """A missing model is a degraded mode, not a crash: liveness still reports up."""
    monkeypatch.setattr(main, "model", None)

    assert client.get("/health").status_code == 200


def test_predict_returns_503_when_the_model_is_missing(client, log_path, monkeypatch):
    monkeypatch.setattr(main, "model", None)

    response = client.post("/predict", json={"text": "anything"})

    assert response.status_code == 503
    assert response.json()["detail"] == "model not loaded"
    assert read_log(log_path) == []
