# Dockerfile - Streamlit model-monitoring dashboard (Assignment 5, hw7).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image: 3.13-slim to match the rest of the stack (pandas 3.0, numpy 2.4) and the
# API container. Documented deviation from the course's 3.9 baseline (see README).
FROM python:3.13-slim

# Non-root user with a home directory. Streamlit writes config and cache under $HOME.
# /logs is pre-created and owned by appuser (same uid as the API) so the shared volume
# ownership is consistent whichever container mounts it first.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app /logs \
    && chown appuser:appuser /app /logs

WORKDIR /app

# Requirements first so the dependency layer caches across app changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dashboard, the full IMDB dataset (the data-drift and target-drift reference), and the
# small fallback sample, owned by the non-root user. The exec-form COPY handles the
# space in the dataset filename. The sample serves only if the dataset is ever absent.
COPY --chown=appuser:appuser ["dashboard.py", "imdb_sample.csv", "IMDB Dataset.csv", "./"]

USER appuser

EXPOSE 8501

# Headless and stats-off so the container neither prompts nor sends telemetry.
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
