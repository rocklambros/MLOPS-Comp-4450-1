# Assignment 3: FastAPI Sentiment Backend

A FastAPI REST service that serves a trained movie-review sentiment model over four
endpoints, validates every request with Pydantic, and ships as a Docker container. This
folder is self-contained: the trained model and the full IMDB dataset are committed, so
it builds and runs from a fresh clone with no other assignment present.

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

The build needs no downloads: the model (`sentiment_model.pkl`) and the full dataset
(`IMDB Dataset.csv`) are committed and copied into the image. A healthcheck is baked in,
so `docker ps` reports the container as `healthy` once it is serving. Stop the container
with Ctrl-C, and remove the image with `make clean`.

If host port 8000 is already taken, remap the published port instead of the container
port: `docker run --rm -p 8001:8000 sentiment-api`. The API still listens on 8000 inside
the container. Only the host-side mapping changes.

## Exercise every endpoint

With the container running (or `uvicorn main:app` locally), each endpoint responds as
below. The `/predict_proba` value is deterministic, so the number reproduces exactly
under the pinned environment (0.7697). Different scikit-learn or NumPy versions can
shift the floating-point result.

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
# {"review":"..."}   a random review from the full IMDB dataset, <br> tags stripped
```

Pydantic rejects a bad body with HTTP 422 before it reaches the model. A request with no
`text` field, with blank or whitespace text, with any field other than `text`, or with
text longer than 20,000 characters returns 422.

## Test with Postman

Postman Desktop is the stated grading tool, so a ready-to-import collection is committed
at `hw3.postman_collection.json`.

1. Start the container: `make build && make run`.
2. In Postman, **Import** → select `hw3.postman_collection.json` from this folder.
3. Run each of the four requests in the "HW3 Sentiment API" collection:

| Request | Status | Expected response |
|---|---|---|
| `health` | `200` | `{"status":"ok"}` |
| `predict` | `200` | `{"sentiment":"positive"}` |
| `predict_proba` | `200` | `{"sentiment":"positive","probability":<float>}` |
| `example` | `200` | `{"review":"..."}`, a random dataset review |

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

The hashed requirements were resolved for Python 3.13, so a local `pip install` needs a
3.13 interpreter to match the pinned hashes. The container path is unaffected: the image
always builds on `python:3.13-slim` regardless of the host's Python version.

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
- `IMDB Dataset.csv` - the full IMDB dataset backing `/example`
- `hw3.postman_collection.json` - importable Postman requests for all four endpoints
- `requirements.txt` - pinned runtime dependencies (reproducible build)
- `requirements-dev.txt` - test and lint tools, kept out of the image
- `Dockerfile`, `.dockerignore` - container build
- `Makefile` - `build`, `run`, `clean`, `test`, `smoke`
- `tests/test_api.py` - endpoint, validation, and degraded-mode checks

## Model integrity

`sentiment_model.pkl` is committed, not downloaded, so its hash should match this build:

```
b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329
```

Verify with:

```bash
shasum -a 256 sentiment_model.pkl
```

A mismatch means the file was regenerated, corrupted in transit, or tampered with, and
the `0.7697` reproducibility claim above no longer applies to that copy.

## Design notes

- **Python base image.** Built on `python:3.13-slim`, the same base used in Assignment 2.
  The spec lists `python:3.9-slim` as an example, but the pinned scikit-learn stack needs
  Python 3.10 or newer and the model was serialized under 3.13, so a 3.9 image cannot
  install the dependencies or load the model.
- **Port 8000.** Fixed and consistent across the Dockerfile `EXPOSE`, the `docker run`
  mapping, and the Makefile. Assignment 2's Streamlit app stays on 8501, so both run at once.
- **`/example` data source.** The endpoint reads from the full `IMDB Dataset.csv`
  committed next to `main.py` (point `EXAMPLE_DATA_PATH` elsewhere to override). The
  dataset carries literal `<br />` line breaks from the source HTML. `/example` strips
  them before returning the review. The file is committed (not gitignored), so it is
  present in the image at `COPY` time and on a fresh clone.
- **Degraded modes, not crashes.** A missing or unreadable model, or a misconfigured
  `EXAMPLE_DATA_PATH`, does not take the process down. `/health` stays up and the affected
  endpoint answers 503, so a configuration problem is explicit to the caller.
- **Docker packaging.** The Dockerfile follows FastAPI's own deployment guidance
  (https://fastapi.tiangolo.com/deployment/docker/): a slim Python base, dependencies
  installed before the app is copied in for layer caching, and `uvicorn` run directly as
  the container's entrypoint rather than behind a process manager.

## Assignment metadata

- Course: COMP 4450 MLOps, Assignment 3
- Points: 10
- Due: July 14, 2026, 11:59 PM (per the assignment spec header)
