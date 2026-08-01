"""main.py - FastAPI prediction service with request logging (Assignment 5, hw7).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.1.0

Serves the Assignment 1 sentiment model (TF-IDF + Multinomial Naive Bayes,
sentiment_model.pkl) over POST /predict and appends one JSON record per call to
/logs/prediction_logs.json on a shared Docker volume. The companion Streamlit
dashboard reads that log to monitor drift and accuracy. Run locally with:

    LOG_PATH=./logs/prediction_logs.json uvicorn main:app --reload

or inside the container on port 8000 (see the Dockerfile and docker-compose.yml).
"""

import json
import logging
import math
import os
import threading
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.requests import Request

logger = logging.getLogger("sentiment_monitor_api")

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "sentiment_model.pkl"

# Newline-delimited JSON log on the shared volume. The path is configurable so the
# service runs both in the container (the spec's /logs/prediction_logs.json) and in
# local dev (point LOG_PATH at a writable directory). Config in the environment.
LOG_PATH = Path(os.getenv("LOG_PATH", "/logs/prediction_logs.json"))

# The two labels the model emits and the only accepted feedback values.
VALID_SENTIMENTS = {"positive", "negative"}

# Cap request text length. TfidfVectorizer.transform cost scales with input size, so an
# unbounded string is a CPU amplification vector at validation. This field cap bounds
# model work; it does not bound the raw bytes buffered off the wire before validation
# runs, which is BodySizeLimitMiddleware's job (see MAX_BODY_BYTES below). It also bounds
# what reaches the log, so one oversized request cannot distort the dashboard's live
# length distribution. 20k characters comfortably fits a long movie review.
MAX_TEXT_LENGTH = 20_000

# Cap the raw request body. Pydantic's max_length above caps model work, but the full
# body is buffered before validation runs, so an unbounded body is a memory-amplification
# vector regardless of what the field validator eventually rejects.
MAX_BODY_BYTES = 1024 * 1024  # 1 MiB ceiling on the raw request body.

# One process appends from a thread pool (sync path operations run off the event
# loop), so serialize writes to keep each JSON line intact under concurrency.
_log_lock = threading.Lock()


def load_model():
    """Return the trained sentiment Pipeline, or None if it cannot be loaded.

    A missing or unreadable model is a degraded mode, not a crash: /health still reports
    up, and /predict answers 503 so the failure is explicit to the caller instead of
    taking the whole process down at startup.
    """
    if not MODEL_PATH.exists():
        logger.warning("model file %s not found; /predict will 503", MODEL_PATH)
        return None
    try:
        with warnings.catch_warnings():
            # Unpickling a scikit-learn Pipeline surfaces third-party deprecations as
            # the numpy/scipy versions drift away from the ones the model was saved
            # under (numpy 2.5, for one, deprecates in-place shape assignment). Those
            # are advisory. Under escalated warnings (pytest -W error, or
            # PYTHONWARNINGS=error) they would raise, get caught below, and take the
            # whole service to 503 over a message that changes nothing about the
            # model. Pin the filter back to default here so only a genuine load
            # failure degrades the service.
            warnings.simplefilter("default")
            return joblib.load(MODEL_PATH)
    except Exception as exc:  # noqa: BLE001 - degrade on any unpickling/version error
        logger.warning("failed to load model %s: %s; /predict will 503", MODEL_PATH, exc)
        return None


model = load_model()


class PredictRequest(BaseModel):
    """Request body for /predict.

    `text` is the review to classify. `true_sentiment` is optional user feedback
    (the real label), supplied through the request since this exercise has no
    frontend feedback form. extra='forbid' rejects unexpected fields with 422.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TEXT_LENGTH,
        description="Movie review text to classify.",
    )
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


class _BodyTooLarge(BaseException):
    """Raised inside the receive wrapper when the streamed body exceeds the ceiling.

    Deliberately a BaseException, not Exception (same reasoning as asyncio.CancelledError
    and GeneratorExit). FastAPI's routing.py wraps `await request.body()` in a bare
    `except Exception` that converts ANY exception into a generic HTTPException(400,
    "There was an error parsing the body") and lets Starlette's ExceptionMiddleware send
    that response from inside the app, before this exception could ever reach the outer
    middleware's own handler. Subclassing BaseException lets the reject-mid-stream signal
    skip every `except Exception` in FastAPI/Starlette's internals and actually surface at
    BodySizeLimitMiddleware, which converts it to the intended 413.
    """


class BodySizeLimitMiddleware:
    """Pure-ASGI middleware bounding the raw request body to max_body_bytes.

    Pydantic's max_length caps model work, but the full body is buffered before
    validation runs, so an unbounded body is a memory-amplification vector. This
    bounds actual bytes read: it rejects a declared-oversize Content-Length up front,
    and counts streamed bytes so a chunked body (no Content-Length) cannot slip past.
    Body-less requests (GET /health) stream no bytes and pass through.
    """

    def __init__(self, app, max_body_bytes: int = MAX_BODY_BYTES):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    if int(value) > self.max_body_bytes:
                        await self._reject(send)
                        return
                except ValueError:
                    pass  # Unparseable header: fall through to byte counting.
                break
        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    raise _BodyTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await self._reject(send)

    async def _reject(self, send):
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({"type": "http.response.body", "body": b'{"detail":"request body too large"}'})


app = FastAPI(
    title="Sentiment Monitoring API",
    description=(
        "Serves the COMP 4450 IMDB sentiment model and logs every prediction to a "
        "shared volume for the monitoring dashboard."
    ),
    version="1.1.0",
)
app.add_middleware(BodySizeLimitMiddleware)


def _json_safe(value):
    """Recursively coerce non-JSON-compliant floats (nan, inf, -inf) to strings.

    FastAPI's default validation handler echoes the offending input back in the
    error detail. A body like {"true_sentiment": NaN} is accepted by the stdlib JSON
    parser, so the echoed input is a non-finite float; Starlette then renders the 422
    with allow_nan=False and raises, turning the 422 into a 500. Coercing here keeps
    it 422.
    """
    if isinstance(value, float):
        return str(value) if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # jsonable_encoder flattens non-serializable ctx objects (e.g. the ValueError a
    # custom validator raises); _json_safe then neutralizes any non-finite float the
    # encoder leaves as-is. Both are required: the encoder alone 500s on NaN, and
    # float-coercion alone 500s on the blank-text ctx error.
    return JSONResponse(
        status_code=422,
        content={"detail": _json_safe(jsonable_encoder(exc.errors()))},
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
