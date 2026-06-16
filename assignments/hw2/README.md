# Movie Review Sentiment Analyzer, Containerized (Assignment 2)

The Assignment 1 Streamlit app packaged as a Docker image, so it runs the same way on any
machine with Docker. Same TF-IDF + Multinomial Naive Bayes model, now built into a
reproducible container with a Makefile front end.

## Files

- `Dockerfile` - builds the image (python:3.13-slim base, non-root user)
- `Makefile` - `build`, `run`, `clean`, plus `test` and `smoke`
- `requirements.txt` - fully pinned dependency set for a reproducible build
- `app.py`, `sentiment_model.pkl` - snapshot of the Assignment 1 app and model
- `tests/test_prediction.py` - unit check for the model's prediction path
- `.gitignore`, `.dockerignore`, `requirements-dev.txt`

## Prerequisites

Docker installed and running.

## Build and run

```bash
make build        # docker build -t sentiment-app .
make run          # runs the container, maps port 8501 to the host
```

Open http://localhost:8501 and analyze a review. Stop with Ctrl-C. Remove the image with `make clean`.

Raw Docker equivalents:

```bash
docker build -t sentiment-app .
docker run --rm -p 8501:8501 sentiment-app
```

## Tests

```bash
pip install -r requirements-dev.txt
make test         # pytest: the model loads and classifies a clear positive and negative
make smoke        # builds, runs, and confirms the container serves /_stcore/health
```

## Notes

- Base image. The spec lists `python:3.9-slim` as an example. The pinned stack (pandas 3.0,
  scikit-learn 1.9) needs Python 3.10+, and the model was pickled under 3.13, so this uses
  `python:3.13-slim`. A documented deviation, flagged to the instructor.
- Model filename. `sentiment_model.pkl` is the canonical model, loaded by `app.py` and copied
  into the image. `model.pkl` is a byte-identical copy of it, present only to match the
  filename shown in the Assignment 2 spec tree. The `model.pkl`-vs-`sentiment_model.pkl` mismatch is flagged, not
  silently resolved.
- Provenance. `app.py` and `sentiment_model.pkl` are a snapshot of the Assignment 1 deliverable
  as of this commit, copied rather than referenced so the assignment is self-contained and the
  image builds from this directory alone.

## Note to the instructor

This assignment uses `python:3.13-slim` rather than the `python:3.9-slim` shown as the example
in the spec ("e.g., python:3.9-slim"). The reason is concrete: the pinned stack (pandas 3.0.3,
scikit-learn 1.9.0) requires Python 3.10 or newer, and the Assignment 1 model was serialized
under Python 3.13, so a 3.9 image cannot install the dependencies or load the model. The
container builds, runs, and serves on 3.13-slim. If a 3.9 base image is a hard requirement,
please let me know and I will re-pin the stack to 3.9-compatible versions (scikit-learn 1.6.x,
pandas 2.2.x) and retrain the model to match.
