"""main.py - FastAPI prediction service with request logging (Assignment 5, hw7).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Serves the Assignment 1 sentiment model (TF-IDF + Multinomial Naive Bayes,
sentiment_model.pkl) over POST /predict and appends one JSON record per call to
/logs/prediction_logs.json on a shared Docker volume. The companion Streamlit
dashboard reads that log to monitor drift and accuracy. Run locally with:

    LOG_PATH=./logs/prediction_logs.json uvicorn main:app --reload

or inside the container on port 8000 (see the Dockerfile and docker-compose.yml).
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "sentiment_model.pkl"

# Newline-delimited JSON log on the shared volume. The path is configurable so the
# service runs both in the container (the spec's /logs/prediction_logs.json) and in
# local dev (point LOG_PATH at a writable directory). Config in the environment.
LOG_PATH = Path(os.getenv("LOG_PATH", "/logs/prediction_logs.json"))

# The two labels the model emits and the only accepted feedback values.
VALID_SENTIMENTS = {"positive", "negative"}

# One process appends from a thread pool (sync path operations run off the event
# loop), so serialize writes to keep each JSON line intact under concurrency.
_log_lock = threading.Lock()


def load_model():
    """Return the trained sentiment Pipeline, or None if the model file is missing.

    A missing model is a degraded mode, not a crash: /health still reports up, and
    /predict answers 503 so the failure is explicit to the caller.
    """
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


model = load_model()


class PredictRequest(BaseModel):
    """Request body for /predict.

    `text` is the review to classify. `true_sentiment` is optional user feedback
    (the real label), supplied through the request since this exercise has no
    frontend feedback form. extra='forbid' rejects unexpected fields with 422.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, description="Movie review text to classify.")
    true_sentiment: str | None = Field(
        None, description="Optional ground-truth label: 'positive' or 'negative'."
    )

    @field_validator("text")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty or whitespace")
        return value

    @field_validator("true_sentiment")
    @classmethod
    def normalize_feedback(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in VALID_SENTIMENTS:
            raise ValueError("true_sentiment must be 'positive' or 'negative'")
        return normalized


class PredictResponse(BaseModel):
    timestamp: str
    predicted_sentiment: str
    true_sentiment: str | None
    logged: bool


class HealthResponse(BaseModel):
    status: str


app = FastAPI(
    title="Sentiment Monitoring API",
    description=(
        "Serves the COMP 4450 IMDB sentiment model and logs every prediction to a "
        "shared volume for the monitoring dashboard."
    ),
    version="1.0.0",
)


def append_log(record: dict) -> None:
    """Append one record as a JSON line to the shared log file.

    Creates the parent directory if needed (local dev); inside the container the
    named volume already provides /logs. Compact separators keep one object per line.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, separators=(",", ":"))
    with _log_lock, LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check: confirms the API process is up and serving."""
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    """Classify a review, log the prediction to the shared volume, echo the record."""
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    predicted = str(model.predict([request.text])[0])
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_text": request.text,
        "predicted_sentiment": predicted,
        "true_sentiment": request.true_sentiment,
    }
    try:
        append_log(record)
    except OSError as exc:
        # Logging is this service's contract, so a write failure is surfaced to the
        # caller rather than silently dropped.
        raise HTTPException(
            status_code=500, detail=f"failed to write log: {exc}"
        ) from exc

    return PredictResponse(
        timestamp=record["timestamp"],
        predicted_sentiment=predicted,
        true_sentiment=request.true_sentiment,
        logged=True,
    )


if __name__ == "__main__":
    import uvicorn

    # Bind to 0.0.0.0 so the published container port is reachable from the host.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
