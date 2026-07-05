# Dockerfile - containerizes the Movie Review Sentiment Analyzer (Assignment 2).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image: the spec lists python:3.9-slim as an example, but the pinned stack
# (pandas 3.0, scikit-learn 1.9) needs Python 3.10+ and the model was pickled under
# 3.13, so 3.13-slim matches the build and loads the model cleanly.
FROM python:3.13-slim

# Non-root user with a home directory. Streamlit writes its config and cache under
# $HOME, so the user needs one to run without permission errors.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app \
    && chown appuser:appuser /app

WORKDIR /app

# Requirements first so the dependency layer caches across app changes.
# --root-user-action=ignore silences pip's root warning (installing system-wide as root
# then running as appuser is the intended container pattern); --disable-pip-version-check
# drops the upgrade notice, keeping the build output clean.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check \
    -r requirements.txt

# App and model, owned by the non-root user. model.pkl is the filename the
# Assignment 2 spec tree names, and the one app.py loads.
COPY --chown=appuser:appuser app.py model.pkl ./

USER appuser

EXPOSE 8501

# Liveness probe: Streamlit serves /_stcore/health. Baking it in surfaces container
# health in `docker ps` and lets an orchestrator restart a hung-but-running process.
# Uses stdlib urllib (slim has no curl) and the container's own port.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status == 200 else 1)"

# Bind to 0.0.0.0 so the published port is reachable from the host; headless and
# stats-off stop the container from prompting or writing telemetry.
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
