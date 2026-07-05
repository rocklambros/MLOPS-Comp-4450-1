# Sentiment Analysis FastAPI Backend

A FastAPI REST service that wraps a trained IMDB movie-review sentiment model
(TF-IDF + Multinomial Naive Bayes, bundled as `sentiment_model.pkl`), validates requests
with Pydantic, and ships as a Docker container. Four endpoints serve health, prediction,
prediction-with-confidence, and a sample review for testing.

- Course: COMP 4450 MLOps, Assignment 3
- Topic: FastAPI backend for model serving
- Due: per the course schedule on Canvas

## Objective

Serve the trained sentiment model over a FastAPI application exposing four endpoints,
validate request bodies with Pydantic, then containerize the service with Docker and
push it to a GitHub repository.

## API

| Method | Path | Request body | Response |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok"}` |
| POST | `/predict` | `{"text": "..."}` | `{"sentiment": "positive"}` |
| POST | `/predict_proba` | `{"text": "..."}` | `{"sentiment": "positive", "probability": 0.95}` |
| GET | `/example` | none | `{"review": "..."}` |

Interactive docs are auto-generated at `/docs` (Swagger UI) and `/redoc` once the server
is running.

## Files

- `main.py` - the FastAPI app and the four endpoints
- `requirements.txt` - pinned runtime dependencies (reproducible build)
- `requirements-dev.txt` - test and lint tools, kept out of the image
- `sentiment_model.pkl` - the trained sentiment pipeline the API serves
- `examples.csv` - 200 real IMDB reviews (100 positive, 100 negative) that back `/example`
- `make_examples.py` - regenerates `examples.csv` deterministically from the full dataset
- `Dockerfile`, `.dockerignore` - container build
- `Makefile` - `build`, `run`, `clean`, plus `test` and `smoke`
- `tests/test_api.py` - endpoint and validation checks (verification aid, beyond the spec)

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload          # serves on http://127.0.0.1:8000
```

Call the endpoints with curl (or import them into Postman):

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}

curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "This movie was a masterpiece!"}'
# {"sentiment":"positive"}

curl -X POST http://127.0.0.1:8000/predict_proba \
  -H 'Content-Type: application/json' \
  -d '{"text": "One of the best films I have seen in years. Every scene earns its place, the pacing never drags, and the lead performance is unforgettable."}'
# {"sentiment":"positive","probability":0.7697}

curl http://127.0.0.1:8000/example
# {"review":"..."}
```

A request with no `text` field, with blank or whitespace text, with any field beyond
`text`, or with text longer than 20,000 characters returns HTTP 422. Pydantic rejects the
body before it reaches the model.

Confidence tracks how much text the model sees: a short phrase reads lower, a full review
reads higher. `/predict_proba` reports the model's calibrated probability for the
predicted class, not a hard 0 or 1, so a moderate number on a short input is expected.

## Run it in Docker

```bash
make build        # docker build -t sentiment-api .
make run          # docker run --rm -p 8000:8000 sentiment-api
```

The API is then reachable on `http://localhost:8000` exactly as above. Stop with Ctrl-C,
remove the image with `make clean`. Raw Docker equivalents:

```bash
docker build -t sentiment-api .
docker run --rm -p 8000:8000 sentiment-api
```

## Tests

```bash
pip install -r requirements-dev.txt
make test         # pytest: the four endpoints, the 422 validation paths, degraded modes
make smoke        # builds, runs the container, confirms it serves /health
ruff check main.py tests/   # lint, zero errors
```

## Notes

- **Base image.** Built on `python:3.13-slim`, not the `python:3.9-slim` example in the
  spec. The pinned scikit-learn stack requires Python 3.10+, and the model was serialized
  under Python 3.13, so a 3.9 image cannot install the dependencies or load the model.
  This is the one deliberate deviation from the spec.
- **Port 8000.** FastAPI serves on 8000, fixed and consistent across the Dockerfile
  `EXPOSE`, the `docker run` port mapping, and the Makefile.
- **`/example` data source.** The endpoint prefers the full `IMDB Dataset.csv` when it is
  present next to `main.py` (set `EXAMPLE_DATA_PATH` to point elsewhere), and otherwise
  falls back to the committed `examples.csv`. The full dataset (~63 MB) is gitignored and
  is not baked into the image, so inside the container and from a fresh clone the sample
  is what serves. `examples.csv` is 200 real IMDB reviews, balanced 100 positive / 100
  negative; `make_examples.py` regenerates it deterministically (fixed seed 4450) from the
  full dataset, so the sample is reproducible rather than an opaque blob.
- **Degraded modes.** A missing or unreadable model, or a misconfigured `EXAMPLE_DATA_PATH`,
  does not crash the process: `/health` stays up and the affected endpoint answers 503, so
  a configuration problem is explicit to the caller instead of a dead server.
- **Sync endpoints on purpose.** Model inference is CPU-bound and fast, so the path
  operations are plain `def`, which FastAPI runs in a worker thread off the event loop.
  No `async` is needed here.

## Repository and submission

This folder is self-contained: clone the repository, `cd` into it, and build and run as
shown above. Everything the container needs (`main.py`, `sentiment_model.pkl`,
`examples.csv`, `requirements.txt`, `Dockerfile`) is committed, so `make build` works from
a fresh clone with no extra downloads.
