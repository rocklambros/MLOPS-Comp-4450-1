# Makefile - build, run, test, and smoke-check the FastAPI sentiment image (Assignment 3).
IMAGE := sentiment-api
PORT := 8000

.PHONY: build run clean test smoke

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm -p $(PORT):8000 $(IMAGE)

clean:
	-docker rmi $(IMAGE)

# Unit/API checks against the four endpoints. Install dev deps first:
#   pip install -r requirements-dev.txt
test:
	python -m pytest tests/ -q

# Integration check: the container actually serves the /health endpoint.
smoke: build
	-docker rm -f $(IMAGE)-smoke 2>/dev/null
	docker run -d --rm --name $(IMAGE)-smoke -p $(PORT):8000 $(IMAGE)
	curl --retry 30 --retry-delay 1 --retry-all-errors -fsS http://localhost:$(PORT)/health && echo " smoke: ok" || (docker logs $(IMAGE)-smoke; docker stop $(IMAGE)-smoke; exit 1)
	docker stop $(IMAGE)-smoke
