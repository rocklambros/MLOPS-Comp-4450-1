# Movie Review Sentiment Analyzer, Containerized (Assignment 2)

The Assignment 1 Streamlit app packaged as a Docker image, so it runs the same way on any
machine with Docker. Same TF-IDF + Multinomial Naive Bayes model, now built into a
reproducible container with a Makefile front end.

## Files

- `Dockerfile` - builds the image (python:3.13-slim base, non-root user)
- `Makefile` - `build`, `run`, `clean`, plus `test` and `smoke`
- `requirements.txt` - fully pinned dependency set for a reproducible build
- `app.py`, `model.pkl` - the Assignment 1 app and its trained model
- `tests/test_prediction.py` - unit check for the model's prediction path
- `.gitignore`, `.dockerignore`, `requirements-dev.txt`

## Prerequisites

Docker installed and running.

## Build and run

```bash
make build            # docker build -t sentiment-app .
make run              # runs the container, maps port 8501 to the host
make run PORT=8502    # same, but publish on host port 8502 if 8501 is busy
```

Open http://localhost:8501 and analyze a review. Stop with Ctrl-C. Remove the image with `make clean`.

Raw Docker equivalents:

```bash
docker build -t sentiment-app .
docker run --rm -p 8501:8501 sentiment-app
```

## Tests

```bash
pip install -r requirements-dev.txt   # installs pytest plus the runtime deps it needs
make test         # pytest: the model loads and classifies a clear positive and negative
make smoke        # builds, runs, and confirms the container serves /_stcore/health
```

## Notes

- Base image. The spec lists `python:3.9-slim` as an example. The pinned stack (pandas 3.0,
  scikit-learn 1.9) needs Python 3.10+, and the model was pickled under 3.13, so this uses
  `python:3.13-slim`. A documented deviation, flagged to the instructor.
- Model file. `model.pkl` is the trained sentiment Pipeline, named to match the Assignment 2
  spec tree. It is loaded by `app.py`, exercised by the tests, and copied into the image. It is
  a snapshot of the Assignment 1 model, carried over so this assignment builds from this
  directory alone.
- Provenance. `app.py` is the Assignment 1 Streamlit app, carried over so the assignment is
  self-contained. It adds one hardening over the Assignment 1 version: input with no words the
  model recognizes returns a 0.5/0.5 tie, so the app reports "not enough recognizable words"
  instead of a confident-looking wrong verdict.

## Note to the instructor

This assignment uses `python:3.13-slim` rather than the `python:3.9-slim` shown as the example
in the spec ("e.g., python:3.9-slim"). The reason is concrete: the pinned stack (pandas 3.0.3,
scikit-learn 1.9.0) requires Python 3.10 or newer, so a 3.9 image cannot even install the
dependencies; the Assignment 1 model was additionally serialized under Python 3.13. The
container builds, runs, and serves on 3.13-slim. If a 3.9 base image is a hard requirement,
please let me know and I will re-pin the stack to 3.9-compatible versions (scikit-learn 1.6.x,
pandas 2.2.x) and retrain the model to match.
