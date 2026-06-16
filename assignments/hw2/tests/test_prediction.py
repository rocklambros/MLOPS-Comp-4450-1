"""Unit tests for the sentiment model's prediction path (Assignment 2).

The unit under test is the prediction path the container serves: load the model,
classify clear examples, and confirm predict_proba returns a probability. Run with:

    python -m pytest tests/ -q
"""
from pathlib import Path

import joblib
import pytest

MODEL_PATH = Path(__file__).resolve().parent.parent / "sentiment_model.pkl"


@pytest.fixture(scope="module")
def model():
    assert MODEL_PATH.exists(), f"model not found at {MODEL_PATH}; build hw1 first"
    return joblib.load(MODEL_PATH)


def test_classifies_clear_positive(model):
    assert model.predict(["An absolute masterpiece, I loved every minute."])[0] == "positive"


def test_classifies_clear_negative(model):
    assert model.predict(["A boring, painful waste of two hours."])[0] == "negative"


def test_predict_proba_is_a_probability(model):
    proba = model.predict_proba(["A wonderful, moving film."])[0]
    assert len(proba) == 2
    assert all(0.0 <= p <= 1.0 for p in proba)
    assert abs(sum(proba) - 1.0) < 1e-9
