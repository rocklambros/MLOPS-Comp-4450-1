# Dockerfile - Streamlit model-monitoring dashboard (Assignment 5, hw7).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image: 3.13-slim to match the rest of the stack (pandas 3.0, numpy 2.4) and the
# API container. Documented deviation from the course's 3.9 baseline (see README).
#
# Digest-pinned, not tag-pinned: `python:3.13-slim` is a moving target, so a rebuild
# months from now would silently pull a different base than the one that was tested.
# Digest resolved 2026-08-01. Re-resolve with:
#   docker buildx imagetools inspect python:3.13-slim
FROM python:3.13-slim@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91

# Non-root user with a home directory. Streamlit writes config and cache under $HOME.
# /logs is pre-created and owned by appuser (same uid as the API) so the shared volume
# ownership is consistent whichever container mounts it first.
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

# Dashboard, its reference-stats module, the precomputed reference distribution (the
# 11 KB data-drift and target-drift reference, provably identical to the raw 50k-row
# CSV for the length multiset and sentiment mix), and the small CSV fallback, all owned
# by the non-root user. The sample serves only if the precomputed artifact is absent.
COPY --chown=appuser:appuser \
     ["dashboard.py", "reference_stats.py", "reference_stats.json", "imdb_sample.csv", "./"]

USER appuser

EXPOSE 8501

# Headless and stats-off so the container neither prompts nor sends telemetry.
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
