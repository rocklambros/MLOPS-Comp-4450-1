# Assignment 2: Package the Sentiment App with Docker

Course: COMP 4450 MLOps. Owner: Rock Lambros.

This directory packages the Assignment 1 movie-review sentiment app into a Docker image, so it
runs the same way on any machine that has Docker. The app is a Streamlit web page: paste a movie
review, click Analyze, and it predicts positive or negative with a confidence score. The model
is a TF-IDF plus Multinomial Naive Bayes pipeline trained on the IMDB 50K dataset. Assignment 1
built the app and the model. Assignment 2 wraps them in a reproducible container with a Makefile
front end.

## Run it in two commands

Prerequisite: Docker installed and running. `docker version` should print a "Server" section.
All commands run from inside this `assignments/hw2/` directory.

```bash
make build     # builds the image and tags it sentiment-app
make run       # starts the container, maps container port 8501 to host port 8501
```

Open http://localhost:8501 in a browser. Type a review such as `An absolute masterpiece, I loved
every minute.` and click Analyze. The page shows "Predicted Sentiment: Positive" with a
confidence percentage. Type `A boring, painful waste of two hours.` to see a Negative result.

Stop the container with Ctrl-C. Delete the image afterward with `make clean`.

If host port 8501 is already taken, publish on a different port with `make run PORT=8502`, then
open http://localhost:8502.

Raw Docker equivalents, for a grader who prefers not to use make:

```bash
docker build -t sentiment-app .
docker run --rm -p 8501:8501 sentiment-app
```

## How this meets the assignment

Every required deliverable and where to find it:

| Requirement from the spec | Where it is satisfied |
|---|---|
| `.gitignore` ignores `__pycache__/`, `.pyc`, and `*.env` | `.gitignore` |
| Dockerfile starts from an official Python base image | `Dockerfile`: `FROM python:3.13-slim` (see the base-image note below) |
| Dockerfile sets a working directory | `Dockerfile`: `WORKDIR /app` |
| Dockerfile copies `requirements.txt`, then installs dependencies | `Dockerfile`: `COPY requirements.txt .` then `RUN pip install ...` |
| Dockerfile copies the application | `Dockerfile`: `COPY ... app.py model.pkl ./` |
| Dockerfile exposes the Streamlit port | `Dockerfile`: `EXPOSE 8501` |
| Dockerfile defines the run command | `Dockerfile`: `CMD ["streamlit", "run", "app.py", ...]` |
| Makefile `build` target builds and names the image | `Makefile`: `build:` runs `docker build -t sentiment-app .` |
| Makefile `run` target maps the port to the host | `Makefile`: `run:` runs `docker run --rm -p 8501:8501 sentiment-app` |
| Makefile `clean` target deletes the image | `Makefile`: `clean:` runs `docker rmi sentiment-app` |

## Optional checks

Two extra targets go beyond the assignment requirements and prove the container works end to end:

```bash
pip install -r requirements-dev.txt   # pytest, plus the runtime deps the tests need
make test    # three unit tests: the model loads and classifies a clear positive and negative
make smoke   # builds, runs the container, and confirms it serves Streamlit's health endpoint
```

`make test` exercises the model's prediction path on the host. `make smoke` builds the image,
starts the container, and confirms it answers on `/_stcore/health`, then stops it.

## Files in this directory

- `Dockerfile` builds the image: `python:3.13-slim` base, a non-root user, and a health check.
- `Makefile` provides `build`, `run`, and `clean` (the three required targets), plus `test` and `smoke`.
- `requirements.txt` is the fully pinned dependency set, so the build is reproducible.
- `app.py` is the Streamlit front end (the Assignment 1 app).
- `model.pkl` is the trained TF-IDF plus Naive Bayes pipeline the app loads.
- `tests/test_prediction.py` holds the unit tests for the model's prediction path.
- `requirements-dev.txt` adds pytest and pulls in the runtime deps for `make test`.
- `.gitignore` and `.dockerignore` hold the ignore rules for git and the Docker build context.

## Base-image note for the instructor

The spec lists `python:3.9-slim` as an example ("e.g., python:3.9-slim"). This image uses
`python:3.13-slim` instead. The pinned stack (pandas 3.0.3, scikit-learn 1.9.0) requires Python
3.10 or newer, so a 3.9 base cannot even install the dependencies, and the Assignment 1 model
was serialized under Python 3.13. The container builds, runs, and serves on 3.13-slim, verified
on both arm64 and amd64. If a 3.9 base image is a hard requirement, tell me and I will re-pin the
stack to 3.9-compatible versions (scikit-learn 1.6.x, pandas 2.2.x) and retrain the model to match.

## Two smaller notes

- `model.pkl` is named to match the file tree shown in the spec. It is the Assignment 1 model,
  copied into this directory so the image builds from here alone.
- `app.py` carries one change over the Assignment 1 version. Input with no words the model
  recognizes (punctuation only, for example) produces a 0.5/0.5 tie, so the app reports "not
  enough recognizable words" rather than a confident but meaningless verdict.
