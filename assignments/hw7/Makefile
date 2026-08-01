# Makefile - build, run, evaluate, test, and tear down the hw7 monitoring stack.
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.1.0
#
# Spec-required targets: build, run, clean. The rest are conveniences.
# ?= so the environment can override without editing this file, e.g. when the host's
# `requests` lives in a virtualenv:  PYTHON=.venv/bin/python make evaluate
COMPOSE ?= docker compose
API_URL ?= http://localhost:8000
PYTHON  ?= python3

.PHONY: build run up down logs seed evaluate test clean

# Build both images.
build:
	$(COMPOSE) build

# Start both services detached on the shared volume and network, building first.
# This is the spec's `run` target and the one the README points the grader at.
run:
	$(COMPOSE) up -d --build
	@echo
	@echo "  API       http://localhost:8000/docs"
	@echo "  Dashboard http://localhost:8501"
	@echo
	@echo "  Next: make seed   (a few labeled predictions)"
	@echo "        make evaluate (score the API over test_data.json)"

# Alias kept so older README/runbook references keep working.
up: run

# Stop and remove the containers and the network (keeps the volume and its logs).
down:
	$(COMPOSE) down

# Follow both services' logs.
logs:
	$(COMPOSE) logs -f

# Send a few labeled predictions so the dashboard has data to plot. Real IMDB-style
# inputs with their true labels; safe to run repeatedly since the log appends. The
# last call omits true_sentiment to exercise the optional-feedback path.
seed:
	@curl -fsS -X POST $(API_URL)/predict -H 'Content-Type: application/json' \
	  -d '{"text": "An absolute masterpiece, I loved every minute of it.", "true_sentiment": "positive"}'; echo
	@curl -fsS -X POST $(API_URL)/predict -H 'Content-Type: application/json' \
	  -d '{"text": "A boring, painful waste of two hours.", "true_sentiment": "negative"}'; echo
	@curl -fsS -X POST $(API_URL)/predict -H 'Content-Type: application/json' \
	  -d '{"text": "The acting was wooden and the plot made no sense at all.", "true_sentiment": "negative"}'; echo
	@curl -fsS -X POST $(API_URL)/predict -H 'Content-Type: application/json' \
	  -d '{"text": "Beautifully shot with a moving, unforgettable score.", "true_sentiment": "positive"}'; echo
	@curl -fsS -X POST $(API_URL)/predict -H 'Content-Type: application/json' \
	  -d '{"text": "I expected more but it fell flat in the second half."}'; echo

# Score the running API over the 50-row labeled test set and print a final accuracy.
# Needs the `requests` library: pip install -r requirements-dev.txt
evaluate:
	$(PYTHON) evaluate.py --api-url $(API_URL)

# Unit and API checks for both services. Install dev deps first:
#   pip install -r requirements-dev.txt
test:
	$(PYTHON) -m pytest api/tests monitoring/tests -q

# Stop everything, remove the shared volume and the network (wipes the logs), and
# drop both images. This is the spec's `clean`.
clean:
	-$(COMPOSE) down -v
	-docker rmi sentiment-monitor-api sentiment-monitor-dashboard 2>/dev/null
