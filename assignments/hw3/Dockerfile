# Dockerfile - containerizes the FastAPI sentiment backend.
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
#
# Base image python:3.13-slim (not the spec's python:3.9-slim example): the pinned
# scikit-learn stack needs Python 3.10+, and the model was serialized under 3.13, so a
# 3.9 base cannot install the dependencies or load the model. See README for detail.
FROM python:3.13-slim

# Non-root user with a home directory: least privilege for the serving process.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app \
    && chown appuser:appuser /app

WORKDIR /app

# Requirements first so the dependency layer caches across app changes.
# --root-user-action=ignore and --disable-pip-version-check keep the build output clean:
# installing system-wide as root, then running as appuser, is the intended pattern.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check \
    -r requirements.txt

# App, model, and the example sample, owned by the non-root user. The full IMDB
# dataset is intentionally not copied (it is gitignored and large); /example uses the
# committed examples.csv inside the container.
COPY --chown=appuser:appuser main.py sentiment_model.pkl examples.csv ./

USER appuser

EXPOSE 8000

# Liveness probe: the app serves /health. Baking it in surfaces container health in
# `docker ps` and lets an orchestrator restart a hung-but-running process. Uses stdlib
# urllib (the slim image has no curl) against the container's own port.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status == 200 else 1)"

# Bind to 0.0.0.0 so the published port is reachable from the host.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
