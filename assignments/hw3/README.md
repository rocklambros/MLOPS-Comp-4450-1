# Assignment 3: FastAPI Sentiment Backend

This is a REST API that classifies movie-review text as positive or negative. It wraps the
sentiment model from Assignment 1 (a scikit-learn `TfidfVectorizer` + `MultinomialNB`
pipeline) in a FastAPI app with four endpoints, validates every request with Pydantic, and
ships as a Docker container. The folder is self-contained: the model and the IMDB dataset
are committed here, so it builds and runs from a fresh clone with nothing else present.

## Grade it in three commands

Run from inside `assignments/hw3`. Docker is the intended way to run and grade this.

```bash
make build     # docker build -t sentiment-api .
make run       # docker run --rm -p 8000:8000 sentiment-api
curl http://localhost:8000/health
# {"status":"ok"}
```

That is the whole setup. The build downloads nothing else: the model
(`sentiment_model.pkl`) and the dataset (`IMDB Dataset.csv`) are committed and copied into
the image. A healthcheck is baked in, so `docker ps` shows the container as `healthy` once
it is serving. Stop it with Ctrl-C. Remove the image afterward with `make clean`.

If host port 8000 is already in use, remap only the host side: `docker run --rm -p
8001:8000 sentiment-api`. The API still listens on 8000 inside the container, so point your
requests at `http://localhost:8001` instead.

## The four endpoints

Each returns the exact JSON shape the assignment asks for.

| Method | Path | Request body | Response |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok"}` |
| POST | `/predict` | `{"text": "..."}` | `{"sentiment": "positive"}` |
| POST | `/predict_proba` | `{"text": "..."}` | `{"sentiment": "positive", "probability": 0.95}` |
| GET | `/example` | none | `{"review": "..."}` |

Interactive API docs generate automatically at `http://localhost:8000/docs` (Swagger UI)
and `/redoc` once the server is running. You can send every request from the `/docs` page
in the browser without any other tool.

## Test every endpoint with Postman

Postman Desktop is the stated grading tool, so a ready-to-import collection is committed at
`hw3.postman_collection.json`.

1. Start the container: `make build && make run`.
2. In Postman, choose **Import** and select `hw3.postman_collection.json` from this folder.
3. Open the **HW3 Sentiment API** collection and send each of its four requests.

| Request | Method | Expected status | Expected response |
|---|---|---|---|
| `health` | GET | `200` | `{"status":"ok"}` |
| `predict` | POST | `200` | `{"sentiment":"positive"}` |
| `predict_proba` | POST | `200` | `{"sentiment":"positive","probability":0.7697}` |
| `example` | GET | `200` | `{"review":"..."}`, a random IMDB review |

The `predict_proba` request uses a fixed review, and the result is deterministic under the
pinned dependencies, so its probability reproduces exactly as `0.7697`. The `example`
request returns a different random review each time you send it.

## ...or test with curl

If you would rather not open Postman, the same four checks run from a terminal against the
running container.

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "This movie was a masterpiece!"}'
# {"sentiment":"positive"}

curl -X POST http://localhost:8000/predict_proba \
  -H 'Content-Type: application/json' \
  -d '{"text": "One of the best films I have seen in years. Every scene earns its place, the pacing never drags, and the lead performance is unforgettable."}'
# {"sentiment":"positive","probability":0.7697}

curl http://localhost:8000/example
# {"review":"..."}   a random IMDB review, HTML line-break tags stripped
```

Pydantic rejects a malformed body with HTTP 422 before it reaches the model. A request with
no `text` field, with blank or whitespace-only text, with any field other than `text`, or
with text longer than 20,000 characters returns 422.

## Rubric coverage

Every requirement in the spec, and how to confirm it.

| Spec requirement | Where it lives | How to verify |
|---|---|---|
| `main.py` serves the model | `main.py` | `make run`, then send any request |
| `GET /health` returns `{"status":"ok"}` | `main.py` `health()` | `health` request above |
| `POST /predict` returns `{"sentiment":...}` | `main.py` `predict()` | `predict` request above |
| `POST /predict_proba` returns sentiment and probability | `main.py` `predict_proba()` | `predict_proba` request above |
| `GET /example` returns a random dataset review | `main.py` `example()` | `example` request above |
| Pydantic request validation | `main.py` `ReviewRequest` | send a bad body, get 422 |
| Containerize with Docker | `Dockerfile`, `.dockerignore` | `make build` |
| README with API, run steps, and `/docs` link | this file | you are reading it |
| Self-contained project | model and dataset committed here | builds from a fresh clone |
| Pushed to a GitHub repository | committed and pushed | the submitted repository URL |

## Run the automated tests (optional)

The tests are not required by the assignment. They check all four endpoints, the 422
validation paths, the 413 body-size limit, and the degraded-mode fallbacks, so the API can
be verified without a running server.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make test                  # pytest, in-process via TestClient
make smoke                 # builds the image, runs it, confirms /health
ruff check main.py tests/  # lint, zero errors
```

To run the API directly instead of in Docker:

```bash
pip install -r requirements.txt
uvicorn main:app --reload  # serves on http://127.0.0.1:8000
```

The pinned requirements carry dependency hashes resolved for Python 3.13, so a local `pip
install` needs a 3.13 interpreter. The container path is unaffected, since the image always
builds on `python:3.13-slim` regardless of the host's Python version.

## Files

- `main.py` - the FastAPI app and the four endpoints
- `sentiment_model.pkl` - the trained sentiment pipeline the API serves
- `IMDB Dataset.csv` - the IMDB dataset backing `/example`
- `hw3.postman_collection.json` - importable Postman requests for all four endpoints
- `Dockerfile`, `.dockerignore` - the container build
- `Makefile` - `build`, `run`, `clean`, `test`, `smoke`
- `requirements.txt` - runtime dependencies, hash-pinned for a reproducible build
- `requirements-dev.txt` - test and lint tools, kept out of the image
- `requirements.in`, `requirements-dev.in` - the human-readable pins the hashed files compile from
- `tests/test_api.py` - endpoint, validation, and degraded-mode checks

## Background

This is the third step in one continuous project. It reuses the earlier work rather than
starting over.

| Assignment | Deliverable | Serving interface |
|---|---|---|
| 1 | Train the sentiment model (`sentiment_model.pkl`) and build a Streamlit app | Streamlit UI |
| 2 | Containerize the Streamlit app with Docker | Streamlit UI in a container |
| 3 (this one) | Serve the same model as a REST API and containerize it | FastAPI backend |

The model here is byte-for-byte the one trained in Assignment 1. Assignment 2 wrapped it in
a Streamlit UI on port 8501. Assignment 3 wraps the identical model in a FastAPI API on
port 8000, so the two serving interfaces run side by side without colliding.

## Design notes

- **Python base image.** Built on `python:3.13-slim`. The spec lists `python:3.9-slim` as
  an example, but the pinned scikit-learn stack needs Python 3.10 or newer and the model
  was serialized under 3.13, so a 3.9 image cannot install the dependencies or load the
  model. The base is digest-pinned so the exact image is reproducible.
- **`/example` data source.** The endpoint reads a random review from the committed `IMDB
  Dataset.csv` next to `main.py`. Those reviews carry literal `<br />` line breaks from the
  source HTML, so `/example` strips them before returning the text. Point `EXAMPLE_DATA_PATH`
  at another CSV to override the source.
- **Degraded modes, not crashes.** A missing or unreadable model, or a misconfigured
  `EXAMPLE_DATA_PATH`, does not take the process down. `/health` stays up and the affected
  endpoint answers 503, so a configuration problem is explicit to the caller.
- **Input limits.** The `text` field is capped at 20,000 characters (422 above that), and a
  middleware caps the whole request body at 1 MiB (413 above that), so an oversized payload
  is rejected before it reaches the model.
- **Reproducible build.** Runtime dependencies are hash-pinned, and the Dockerfile installs
  them with `--require-hashes`, so the image resolves the same bytes every time. Packaging
  follows FastAPI's deployment guidance (https://fastapi.tiangolo.com/deployment/docker/).

## Model integrity

`sentiment_model.pkl` is committed, not downloaded. Its SHA-256 is:

```
b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329
```

Verify with `shasum -a 256 sentiment_model.pkl`. A mismatch means the file was regenerated,
corrupted, or altered, and the `0.7697` probability above no longer applies to that copy.

## Assignment metadata

- Course: COMP 4450 MLOps, Assignment 3
- Points: 10
- Due: July 14, 2026, 11:59 PM (per the assignment spec header)
