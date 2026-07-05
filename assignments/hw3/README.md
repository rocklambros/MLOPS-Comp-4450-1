# Assignment 3: FastAPI Sentiment Backend

A FastAPI REST service that serves a trained movie-review sentiment model over four
endpoints, validates every request with Pydantic, and ships as a Docker container. This
folder is self-contained: the trained model and a sample of reviews are committed, so it
builds and runs from a fresh clone with no other assignment present.

## Where this sits in the course

This is the third step in one continuous project, and it reuses the earlier work rather
than starting over.

| Assignment | Deliverable | Serving interface |
|---|---|---|
| 1 | Train the sentiment model (`sentiment_model.pkl`) and build a Streamlit app | Streamlit UI |
| 2 | Containerize the Streamlit app with Docker | Streamlit UI in a container |
| 3 (this one) | Serve the **same** model as a REST API and containerize it | FastAPI backend |

The model here is byte-for-byte the one trained in Assignment 1 (a scikit-learn Pipeline
of `TfidfVectorizer` + `MultinomialNB`). Assignment 2 wrapped that model in a Streamlit
UI on port 8501. Assignment 3 wraps the identical model in a FastAPI API on port 8000, so
the two serving interfaces run side by side without colliding. The Docker approach,
Makefile, dependency pinning, non-root user, healthcheck, and Python base image all follow
the conventions established in Assignment 2.

## What it does

Four endpoints, each returning the exact JSON shape the spec asks for.

| Method | Path | Request body | Response |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok"}` |
| POST | `/predict` | `{"text": "..."}` | `{"sentiment": "positive"}` |
| POST | `/predict_proba` | `{"text": "..."}` | `{"sentiment": "positive", "probability": 0.95}` |
| GET | `/example` | none | `{"review": "..."}` |

Interactive API docs generate automatically at `/docs` (Swagger UI) and `/redoc` once the
server is running.

## Grade it in three commands (Docker)

The container is the intended way to run and grade this. From inside `assignments/hw3`:

```bash
make build                 # docker build -t sentiment-api .
make run                   # docker run --rm -p 8000:8000 sentiment-api
curl http://localhost:8000/health
# {"status":"ok"}
```

The build needs no downloads: the model (`sentiment_model.pkl`) and the review sample
(`examples.csv`) are committed and copied into the image. A healthcheck is baked in, so
`docker ps` reports the container as `healthy` once it is serving. Stop the container with
Ctrl-C, and remove the image with `make clean`.

## Exercise every endpoint

With the container running (or `uvicorn main:app` locally), each endpoint responds as
below. The `/predict_proba` value is deterministic, so the number reproduces exactly.

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "This movie was a masterpiece!"}'
# {"sentiment":"positive"}

curl -X POST http://localhost:8000/predict_proba \
  -H 'Content-Type: application/json' \
  -d '{"text": "One of the best films I have seen in years. Every scene earns its place, the pacing never drags, and the lead performance is unforgettable."}'
# {"sentiment":"positive","probability":0.7697}

curl http://localhost:8000/example
# {"review":"..."}   a random review from the sample data
```

Pydantic rejects a bad body with HTTP 422 before it reaches the model. A request with no
`text` field, with blank or whitespace text, with any field other than `text`, or with
text longer than 20,000 characters returns 422.

## Run the tests

The tests are not required by the spec. They check all four endpoints, the 422 validation
paths, and the degraded-mode fallbacks, so the API can be verified without a running
server.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make test                  # pytest, 11 checks, in-process via TestClient
make smoke                 # builds the image, runs it, confirms /health
ruff check main.py tests/  # lint, zero errors
```

To run the API directly instead of in Docker:

```bash
pip install -r requirements.txt
uvicorn main:app --reload  # serves on http://127.0.0.1:8000
```

## Rubric coverage

Every requirement in the spec, and where to check it.

| Spec requirement | Where it lives | How to verify |
|---|---|---|
| `main.py` serves the model | `main.py` | `make run`, then curl the endpoints |
| `GET /health` returns `{"status":"ok"}` | `main.py` `health()` | `curl /health` |
| `POST /predict` returns `{"sentiment":...}` | `main.py` `predict()` | curl example above |
| `POST /predict_proba` returns sentiment + probability | `main.py` `predict_proba()` | curl example above |
| `GET /example` returns a random review | `main.py` `example()` | `curl /example` |
| Pydantic request validation | `main.py` `ReviewRequest` | send a bad body, get 422 |
| Containerize with Docker | `Dockerfile`, `.dockerignore` | `make build` |
| Documentation | this `README.md` | you are reading it |
| Push to a GitHub repository | committed and pushed | the repository URL for this submission |

## Files

- `main.py` - the FastAPI app and the four endpoints
- `sentiment_model.pkl` - the trained sentiment pipeline the API serves
- `examples.csv` - 200 real IMDB reviews (100 positive, 100 negative) backing `/example`
- `make_examples.py` - regenerates `examples.csv` deterministically from the full dataset
- `requirements.txt` - pinned runtime dependencies (reproducible build)
- `requirements-dev.txt` - test and lint tools, kept out of the image
- `Dockerfile`, `.dockerignore` - container build
- `Makefile` - `build`, `run`, `clean`, `test`, `smoke`
- `tests/test_api.py` - endpoint, validation, and degraded-mode checks

## Design notes

- **Python base image.** Built on `python:3.13-slim`, the same base used in Assignment 2.
  The spec lists `python:3.9-slim` as an example, but the pinned scikit-learn stack needs
  Python 3.10 or newer and the model was serialized under 3.13, so a 3.9 image cannot
  install the dependencies or load the model.
- **Port 8000.** Fixed and consistent across the Dockerfile `EXPOSE`, the `docker run`
  mapping, and the Makefile. Assignment 2's Streamlit app stays on 8501, so both run at once.
- **`/example` data source.** The endpoint prefers the full `IMDB Dataset.csv` when it is
  present next to `main.py` (point `EXAMPLE_DATA_PATH` elsewhere to override), and otherwise
  falls back to the committed `examples.csv`. The full dataset (about 63 MB) is gitignored
  and never enters the image, so the sample serves inside the container and from a fresh
  clone. `make_examples.py` regenerates that sample deterministically (fixed seed 4450), so
  it is reproducible rather than an opaque file.
- **Degraded modes, not crashes.** A missing or unreadable model, or a misconfigured
  `EXAMPLE_DATA_PATH`, does not take the process down. `/health` stays up and the affected
  endpoint answers 503, so a configuration problem is explicit to the caller.

## Assignment metadata

- Course: COMP 4450 MLOps, Assignment 3
- Points: 10
- Due: July 14, 2026, 11:59 PM (per the assignment spec header)
