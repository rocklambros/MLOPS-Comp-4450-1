# Dockerfile - FastAPI sentiment prediction + logging service (Assignment 5, hw7).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image: the course baseline is python:3.9-slim, but the pinned stack
# (scikit-learn 1.9, numpy 2.4) needs Python 3.10+ and the model was pickled under
# 3.13, so 3.13-slim matches the build and loads the model cleanly. Documented
# deviation carried forward from Assignments 2 and 3 (see README).
#
# Digest-pinned, not tag-pinned: `python:3.13-slim` is a moving target, so a rebuild
# months from now would silently pull a different base than the one that was tested.
# Digest resolved 2026-08-01. Re-resolve with:
#   docker buildx imagetools inspect python:3.13-slim
FROM python:3.13-slim@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91

# Non-root user with a home directory: least privilege for the serving process.
# /logs is pre-created and owned by appuser so the empty named volume initializes
# writable for the non-root process on first mount.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app /logs \
    && chown appuser:appuser /app /logs

WORKDIR /app

# Requirements first so the dependency layer caches across app changes. Hashes in the
# lockfile make pip verify every artifact before install. --root-user-action=ignore
# silences pip's "don't run as root" notice: installing into the image as root and then
# dropping to appuser for the runtime is the intended pattern here, so the warning is
# noise that would otherwise hide a real one.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# App and model, owned by the non-root user. The full IMDB dataset is never copied
# (large, gitignored); the dashboard, not the API, holds the reference sample.
COPY --chown=appuser:appuser main.py sentiment_model.pkl ./

USER appuser

EXPOSE 8000

# Bind to 0.0.0.0 so the published port is reachable from the host.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
