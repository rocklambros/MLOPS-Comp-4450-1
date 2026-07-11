"""main.py - FastAPI backend serving a trained IMDB movie-review sentiment model.

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Wraps a pre-trained sentiment classifier (a scikit-learn Pipeline of TfidfVectorizer +
Multinomial Naive Bayes, bundled as sentiment_model.pkl) in four REST endpoints:

    GET  /health         liveness check
    POST /predict        text -> {"sentiment": ...}
    POST /predict_proba  text -> {"sentiment": ..., "probability": ...}
    GET  /example        a random review from the full IMDB dataset

Run locally with:

    uvicorn main:app --reload

or inside the container on port 8000 (see the Dockerfile and Makefile).
"""

import csv
import logging
import math
import os
import random
import re
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger("sentiment_api")

# /example returns raw dataset reviews, which carry literal <br /> HTML line breaks.
# Strip them to spaces so the endpoint returns readable text. The model never sees
# /example output, so this display cleanup has no effect on predictions.
_BR_TAG = re.compile(r"<br\s*/?>", re.IGNORECASE)

# Cap request text length. TfidfVectorizer.transform cost scales with input size, so an
# unbounded string is a CPU amplification vector at validation. This field cap bounds
# model work; it does not bound the raw bytes buffered off the wire before validation
# runs — that is BodySizeLimitMiddleware's job (see MAX_BODY_BYTES below). 20k
# characters comfortably fits a long movie review; anything larger is rejected with 422
# before any work happens.
MAX_TEXT_LENGTH = 20_000

# Cap the raw request body. Pydantic's max_length above caps model work, but the full
# body is buffered before validation runs, so an unbounded body is a memory-amplification
# vector regardless of what the field validator eventually rejects. BodySizeLimitMiddleware
# enforces this ceiling on actual bytes read, ahead of validation.
MAX_BODY_BYTES = 1024 * 1024  # 1 MiB ceiling on the raw request body.

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "sentiment_model.pkl"

# /example data source, resolved at startup. The full IMDB dataset is committed next to
# main.py and is /example's only source. An explicit EXAMPLE_DATA_PATH env var wins over
# it, keeping the path configurable without a code change. Config in the environment,
# not hardcoded.
FULL_DATASET_PATH = HERE / "IMDB Dataset.csv"


def load_model():
    """Return the trained sentiment Pipeline, or None if it cannot be loaded.

    A missing or unreadable model is a degraded mode, not a crash: /health still reports
    the API is up, and the prediction endpoints answer 503 so the failure is explicit to
    the caller instead of taking the whole process down at startup.
    """
    if not MODEL_PATH.exists():
        logger.warning("model file %s not found; prediction endpoints will 503", MODEL_PATH)
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as exc:  # noqa: BLE001 - degrade on any unpickling/version error
        logger.warning("failed to load model %s: %s; endpoints will 503", MODEL_PATH, exc)
        return None


def resolve_example_source() -> Path | None:
    """Pick the CSV that /example draws from: env override, then the full dataset."""
    override = os.getenv("EXAMPLE_DATA_PATH")
    if override:
        path = Path(override)
        return path if path.exists() else None
    if FULL_DATASET_PATH.exists():
        return FULL_DATASET_PATH
    return None


def load_reviews(path: Path) -> list[str]:
    """Read the 'review' column from an IMDB-format CSV into memory once at startup.

    csv.DictReader handles the quoted fields in IMDB reviews (embedded commas, quotes,
    and newlines) correctly, so no extra parsing is needed.
    """
    csv.field_size_limit(10 * 1024 * 1024)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "review" not in reader.fieldnames:
            raise ValueError(f"{path.name} is missing a 'review' column")
        return [row["review"] for row in reader if row.get("review")]


def load_example_reviews() -> list[str]:
    """Resolve and read the example reviews, degrading to an empty list on any failure.

    A misconfigured EXAMPLE_DATA_PATH (missing 'review' column, a directory, an
    unreadable file) must not take the API down. It degrades to an empty list so only
    /example answers 503 while the rest of the API keeps serving.
    """
    source = resolve_example_source()
    if source is None:
        logger.warning("no example data source found; /example will 503")
        return []
    try:
        return load_reviews(source)
    except (OSError, ValueError) as exc:
        logger.warning("could not read example data %s: %s; /example will 503", source, exc)
        return []


model = load_model()
EXAMPLE_REVIEWS = load_example_reviews()


class ReviewRequest(BaseModel):
    """Request body for /predict and /predict_proba: a single review string.

    extra='forbid' enforces the single-key contract: a body carrying any field other
    than `text` is rejected with 422 rather than silently ignored. min_length and
    max_length bound the input so blank and oversized payloads fail before the model.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TEXT_LENGTH,
        description="Movie review text to classify.",
    )

    @field_validator("text")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty or whitespace")
        return value


class HealthResponse(BaseModel):
    status: str


class PredictResponse(BaseModel):
    sentiment: str


class PredictProbaResponse(BaseModel):
    sentiment: str
    probability: float


class ExampleResponse(BaseModel):
    review: str


class _BodyTooLarge(BaseException):
    """Raised inside the receive wrapper when the streamed body exceeds the ceiling.

    Deliberately a BaseException, not Exception (same reasoning as asyncio.CancelledError
    and GeneratorExit). FastAPI's routing.py wraps `await request.body()` in a bare
    `except Exception` that converts ANY exception into a generic HTTPException(400,
    "There was an error parsing the body") and lets Starlette's ExceptionMiddleware send
    that response from inside the app -- before this exception could ever reach the outer
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
    Body-less requests (GET /health, /example) stream no bytes and pass through.
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
    title="Movie Review Sentiment API",
    description=(
        "Serves a TF-IDF + Multinomial Naive Bayes IMDB sentiment model over a REST API."
    ),
    version="1.0.0",
)
app.add_middleware(BodySizeLimitMiddleware)


def _json_safe(value):
    """Recursively coerce non-JSON-compliant floats (nan, inf, -inf) to strings.

    FastAPI's default validation handler echoes the offending input back in the
    error detail. A body like {"text": NaN} is accepted by the stdlib JSON parser,
    so the echoed input is a non-finite float; Starlette then renders the 422 with
    allow_nan=False and raises, turning the 422 into a 500. Coercing here keeps it 422.
    """
    if isinstance(value, float):
        return str(value) if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    # jsonable_encoder flattens non-serializable ctx objects (e.g. the ValueError a
    # custom validator raises); _json_safe then neutralizes any non-finite float the
    # encoder leaves as-is. Both are required: the encoder alone 500s on NaN, and
    # float-coercion alone 500s on the blank-text ctx error.
    return JSONResponse(
        status_code=422,
        content={"detail": _json_safe(jsonable_encoder(exc.errors()))},
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check: confirms the API process is up and serving."""
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictResponse)
def predict(request: ReviewRequest) -> PredictResponse:
    """Classify a review as 'positive' or 'negative'."""
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    sentiment = str(model.predict([request.text])[0])
    return PredictResponse(sentiment=sentiment)


@app.post("/predict_proba", response_model=PredictProbaResponse)
def predict_proba(request: ReviewRequest) -> PredictProbaResponse:
    """Classify a review and return the confidence of the predicted class."""
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    sentiment = str(model.predict([request.text])[0])
    # predict_proba returns probabilities in model.classes_ order. Pair each class with
    # its probability and look the predicted label up by name, so the confidence stays
    # correct regardless of the class ordering.
    probabilities = dict(zip(model.classes_, model.predict_proba([request.text])[0]))
    return PredictProbaResponse(
        sentiment=sentiment,
        probability=round(float(probabilities[sentiment]), 4),
    )


@app.get("/example", response_model=ExampleResponse)
def example() -> ExampleResponse:
    """Return a random review from the IMDB dataset, HTML-stripped, for testing the predictors."""
    if not EXAMPLE_REVIEWS:
        raise HTTPException(status_code=503, detail="no example reviews available")
    review = _BR_TAG.sub(" ", random.choice(EXAMPLE_REVIEWS)).strip()
    return ExampleResponse(review=review)


if __name__ == "__main__":
    import uvicorn

    # Bind to 0.0.0.0 so the published container port is reachable from the host.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
