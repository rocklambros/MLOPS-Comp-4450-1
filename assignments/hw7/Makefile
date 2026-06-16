# Makefile - build, run, seed, and tear down the hw7 monitoring stack (Assignment 5).
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>   Version: 1.0.0
COMPOSE := docker compose
API_URL := http://localhost:8000

.PHONY: build up down logs seed clean

# Build both images.
build:
	$(COMPOSE) build

# Start both services detached on the shared volume and network.
up:
	$(COMPOSE) up -d --build

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

# Stop everything, remove the shared volume (wipes the logs), and drop both images.
clean:
	-$(COMPOSE) down -v
	-docker rmi sentiment-monitor-api sentiment-monitor-dashboard 2>/dev/null
