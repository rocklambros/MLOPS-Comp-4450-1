"""API tests for the FastAPI sentiment backend.

These tests are not required by the assignment spec; they verify the four endpoints,
the Pydantic validation paths (422), and the degraded-mode behavior so the API can be
checked without a running server. Run from this folder with:

    pip install -r requirements-dev.txt
    python -m pytest tests/ -q

TestClient drives the app in-process, so no server needs to be running.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_clear_positive():
    response = client.post(
        "/predict", json={"text": "An absolute masterpiece, I loved every minute."}
    )
    assert response.status_code == 200
    assert response.json() == {"sentiment": "positive"}


def test_predict_clear_negative():
    response = client.post(
        "/predict", json={"text": "A boring, painful waste of two hours."}
    )
    assert response.status_code == 200
    assert response.json() == {"sentiment": "negative"}


def test_predict_proba_returns_sentiment_and_probability():
    response = client.post("/predict_proba", json={"text": "A wonderful, moving film."})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"sentiment", "probability"}
    assert body["sentiment"] in {"positive", "negative"}
    assert 0.0 <= body["probability"] <= 1.0


def test_predict_rejects_missing_field():
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_rejects_blank_text():
    response = client.post("/predict", json={"text": "   "})
    assert response.status_code == 422


def test_predict_rejects_extra_field():
    response = client.post("/predict", json={"text": "great film", "junk": "x"})
    assert response.status_code == 422


def test_predict_rejects_oversized_text():
    # Over MAX_TEXT_LENGTH: rejected by Pydantic before the model does any work.
    response = client.post("/predict", json={"text": "a" * (main.MAX_TEXT_LENGTH + 1)})
    assert response.status_code == 422


def test_example_returns_a_review():
    response = client.get("/example")
    assert response.status_code == 200
    review = response.json()["review"]
    assert isinstance(review, str) and review


def test_example_review_has_no_br_tags():
    # /example must serve a clean review; <br> markup is stripped to spaces.
    for _ in range(25):  # sample several random draws
        review = client.get("/example").json()["review"]
        assert "<br" not in review
        assert review == review.strip()


def test_example_loads_from_full_dataset():
    # After the switch, the loaded corpus is the full dataset, not a 200-row sample.
    assert len(main.EXAMPLE_REVIEWS) > 1000


def test_bad_example_source_degrades_instead_of_crashing(tmp_path, monkeypatch):
    # A misconfigured EXAMPLE_DATA_PATH must degrade to an empty list, not raise, so the
    # rest of the API stays up and only /example answers 503.
    bad_csv = tmp_path / "no_review_column.csv"
    bad_csv.write_text("wrong,header\n1,2\n", encoding="utf-8")
    monkeypatch.setenv("EXAMPLE_DATA_PATH", str(bad_csv))
    assert main.load_example_reviews() == []

    monkeypatch.setenv("EXAMPLE_DATA_PATH", str(tmp_path))  # a directory, not a file
    assert main.load_example_reviews() == []

    missing = tmp_path / "does_not_exist.csv"
    monkeypatch.setenv("EXAMPLE_DATA_PATH", str(missing))
    assert main.load_example_reviews() == []


def test_load_reviews_reads_review_column(tmp_path):
    csv_path = tmp_path / "reviews.csv"
    csv_path.write_text(
        'review,sentiment\n"Great, loved it",positive\n"Awful",negative\n',
        encoding="utf-8",
    )
    reviews = main.load_reviews(Path(csv_path))
    assert reviews == ["Great, loved it", "Awful"]


@pytest.mark.parametrize("literal", [b"NaN", b"Infinity", b"-Infinity", b"1e400"])
def test_predict_rejects_nonfinite_numbers_with_422_not_500(literal):
    # These JSON literals parse to nan/inf server-side; the response must be a clean 422.
    body = b'{"text": ' + literal + b"}"
    response = client.post("/predict", content=body, headers={"content-type": "application/json"})
    assert response.status_code == 422


def test_normal_validation_errors_still_return_422_detail():
    # The custom handler must not regress ordinary validation failures.
    for bad in ({}, {"text": "   "}, {"text": "ok", "junk": "x"}):
        response = client.post("/predict", json=bad)
        assert response.status_code == 422
        assert isinstance(response.json()["detail"], list)
