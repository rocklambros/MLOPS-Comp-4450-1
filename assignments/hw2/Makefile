# Makefile - build, run, test, and smoke-check the sentiment-app image (Assignment 2).
IMAGE := sentiment-app
PORT := 8501

.PHONY: build run clean test smoke

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm -p $(PORT):8501 $(IMAGE)

# Delete the image. Force-remove any container still running from it first, so the
# rmi does not silently fail on an in-use image (the leading - keeps clean idempotent
# when the container or image is already gone).
clean:
	-docker rm -f $$(docker ps -aq --filter ancestor=$(IMAGE)) 2>/dev/null
	-docker rmi $(IMAGE)

# Unit check: model prediction path. Install dev deps first: pip install -r requirements-dev.txt
test:
	python3 -m pytest tests/ -q

# Integration check: the container actually serves Streamlit's health endpoint.
smoke: build
	-docker rm -f $(IMAGE)-smoke 2>/dev/null
	docker run -d --rm --name $(IMAGE)-smoke -p $(PORT):8501 $(IMAGE)
	curl --retry 30 --retry-delay 1 --retry-all-errors -fsS http://localhost:$(PORT)/_stcore/health && echo " smoke: ok" || (docker logs $(IMAGE)-smoke; docker stop $(IMAGE)-smoke; exit 1)
	docker stop $(IMAGE)-smoke
