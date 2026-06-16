# Makefile - build, run, test, and smoke-check the sentiment-app image (Assignment 2).
IMAGE := sentiment-app
PORT := 8501

.PHONY: build run clean test smoke

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm -p $(PORT):8501 $(IMAGE)

clean:
	-docker rmi $(IMAGE)

# Unit check: model prediction path. Install dev deps first: pip install -r requirements-dev.txt
test:
	python -m pytest tests/ -q

# Integration check: the container actually serves Streamlit's health endpoint.
smoke: build
	-docker rm -f $(IMAGE)-smoke 2>/dev/null
	docker run -d --rm --name $(IMAGE)-smoke -p $(PORT):8501 $(IMAGE)
	curl --retry 30 --retry-delay 1 --retry-all-errors -fsS http://localhost:$(PORT)/_stcore/health && echo " smoke: ok" || (docker logs $(IMAGE)-smoke; docker stop $(IMAGE)-smoke; exit 1)
	docker stop $(IMAGE)-smoke
