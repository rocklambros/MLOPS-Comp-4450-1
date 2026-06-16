# Dockerfile - FastAPI sentiment prediction + logging service (Assignment 5, hw7).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image: the course baseline is python:3.9-slim, but the pinned stack
# (scikit-learn 1.9, numpy 2.4) needs Python 3.10+ and the model was pickled under
# 3.13, so 3.13-slim matches the build and loads the model cleanly. Documented
# deviation carried forward from Assignments 2 and 3 (see README).
FROM python:3.13-slim

# Non-root user with a home directory: least privilege for the serving process.
# /logs is pre-created and owned by appuser so the empty named volume initializes
# writable for the non-root process on first mount.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app /logs \
    && chown appuser:appuser /app /logs

WORKDIR /app

# Requirements first so the dependency layer caches across app changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App and model, owned by the non-root user. The full IMDB dataset is never copied
# (large, gitignored); the dashboard, not the API, holds the reference sample.
COPY --chown=appuser:appuser main.py sentiment_model.pkl ./

USER appuser

EXPOSE 8000

# Bind to 0.0.0.0 so the published port is reachable from the host.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
