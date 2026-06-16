# Model Monitoring (Assignment 5)

A two-container monitoring system for the COMP 4450 sentiment service. A FastAPI
prediction service logs every request to a shared Docker volume, and a Streamlit
dashboard reads that log to watch for data drift, target drift, and accuracy decay.
Same model as Assignments 1 and 3 (`sentiment_model.pkl`, TF-IDF + Multinomial Naive
Bayes); the request logging and the monitoring dashboard are new this week.

- Week: 7
- Topic: model monitoring (data drift, target drift, live accuracy)
- Partner: solo
- Due: defer to Canvas. The scraped spec disagrees with itself (header `8/11/2026`,
  body `11/05/2025`), so neither is trustworthy. See Notes.

## Objective

Build a FastAPI service that serves `POST /predict` and logs every call to
`/logs/prediction_logs.json` (one JSON object per line) with the timestamp, request
text, predicted sentiment, and a user-supplied true sentiment. Run it next to a
Streamlit dashboard that reads the same log from a shared named volume and plots data
drift, target drift, and live accuracy. The two services run as separate containers on
a shared network. All prediction traffic comes from Postman or curl, no frontend.

## Architecture

```
  Postman / curl
        |  POST /predict  {"text": "...", "true_sentiment": "positive"}
        v
  +------------------+      append one JSON line       +-------------------+
  |  api (FastAPI)   | ------------------------------> |  prediction-logs  |
  |  port 8000       |   /logs/prediction_logs.json    |  (named volume)   |
  +------------------+                                  +-------------------+
        ^                                                        |
        |  GET /health (service name "api")            read log  |
        |                                                        v
  +-----------------------------------------------------------------------+
  |  dashboard (Streamlit), port 8501                                     |
  |  data drift  |  target drift  |  accuracy + feedback                  |
  +-----------------------------------------------------------------------+

  network: sentiment-net (user-defined bridge, name resolution by service)
  volume:  prediction-logs (mounted at /logs in both containers)
```

The dashboard reads predictions through the shared **volume**, not over the network.
The shared **network** carries the dashboard's best-effort `GET http://api:8000/health`
call, which drives the API status badge and proves the two services resolve each other
by name.

## Files

```
api/
  main.py            FastAPI app: POST /predict (logs) + GET /health
  requirements.txt   pinned serving stack (same as hw3)
  Dockerfile         python:3.13-slim, non-root, pre-creates /logs
  .dockerignore
  sentiment_model.pkl  the Assignment 1 model (unchanged)
monitoring/
  dashboard.py       Streamlit monitoring dashboard
  requirements.txt   pinned streamlit + pandas + matplotlib + requests
  Dockerfile         python:3.13-slim, non-root, pre-creates /logs
  .dockerignore
  IMDB Dataset.csv   full 50k-row IMDB set, the drift and target-drift reference
  imdb_sample.csv    200-row balanced fallback if the dataset is ever absent
docker-compose.yml   wires the two services, the volume, and the network
Makefile             build, up, down, logs, seed, clean
```

## Quick start (Docker Compose)

```bash
make up        # build both images, create the volume + network, run detached
make seed      # send a handful of labeled predictions so the charts have data
```

Then open the dashboard at <http://localhost:8501> and the API docs at
<http://localhost:8000/docs>. Tear down with:

```bash
make down      # stop containers, keep the volume (logs persist)
make clean     # stop, remove the volume (wipes logs), drop both images
```

`make up` wraps `docker compose up -d --build`. The dashboard `depends_on` the API so
the API container claims the empty volume first; both images pre-create `/logs` owned
by the same non-root uid, so the named volume initializes writable either way.

## The manual Docker path (what Compose does, for hw8)

hw8 runs these by hand on an EC2 host, so here is the equivalent without Compose:

```bash
docker network create sentiment-net
docker volume create prediction-logs

docker build -t sentiment-monitor-api ./api
docker build -t sentiment-monitor-dashboard ./monitoring

docker run -d --name sentiment-monitor-api \
  --network sentiment-net -p 8000:8000 \
  -v prediction-logs:/logs sentiment-monitor-api

docker run -d --name sentiment-monitor-dashboard \
  --network sentiment-net -p 8501:8501 \
  -v prediction-logs:/logs -e API_URL=http://sentiment-monitor-api:8000 \
  sentiment-monitor-dashboard
```

With raw `docker run` the service DNS name is the `--name`, so the dashboard points at
`http://sentiment-monitor-api:8000`. Under Compose it is the service name, `http://api:8000`.

## Driving it from Postman or curl

`POST /predict` takes the review text and an optional ground-truth label:

```bash
# With feedback (drives the accuracy chart)
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "One of the best films I have seen in years.", "true_sentiment": "positive"}'
# {"timestamp":"2026-...","predicted_sentiment":"positive","true_sentiment":"positive","logged":true}

# Without feedback (still logged; just not counted in accuracy)
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "It was fine, nothing special."}'
```

Each call appends one line to `/logs/prediction_logs.json`:

```json
{"timestamp":"2026-06-16T18:04:11.482103+00:00","request_text":"One of the best films I have seen in years.","predicted_sentiment":"positive","true_sentiment":"positive"}
```

A blank `text`, a missing `text`, an unknown `true_sentiment` value, or any extra
field returns HTTP 422. Pydantic rejects the body before it reaches the model.

## What the dashboard shows

- **Data drift** - overlaid histograms of review length in words, training data vs
  the logged live requests. A live distribution that drifts away from training is the
  leading indicator that inputs have changed.
- **Target drift** - grouped bar chart of the predicted-sentiment mix in the logs
  against the trained label balance (IMDB is near 50/50). A heavy live skew flags that
  the model's outputs are shifting.
- **Accuracy and feedback** - live accuracy, per-class accuracy, and a predicted-vs-true
  count table, computed only over the requests that carried a `true_sentiment`. Also
  reports feedback coverage (what share of requests included a label).

## Local dev without Docker

```bash
# API
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
LOG_PATH=../logs/prediction_logs.json uvicorn main:app --reload   # :8000

# Dashboard (second shell)
cd monitoring
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
LOG_PATH=../logs/prediction_logs.json API_URL=http://localhost:8000 \
  streamlit run dashboard.py                                      # :8501
```

`LOG_PATH` points both processes at the same file in place of the shared volume. The
dashboard's drift reference is the full `IMDB Dataset.csv` committed under `monitoring/`.
Set `REFERENCE_DATA_PATH` to point at a different reference file if you need one.

## Notes

- **Ports.** FastAPI on 8000, Streamlit on 8501, consistent with hw3 and lined up for
  the hw8 EC2 security group.
- **`true_sentiment` is optional, but always logged.** Real feedback is sporadic, so a
  `/predict` call without it still succeeds and logs the field as `null`. The key is
  present in every log line, never absent, so each entry carries it as the spec asks.
  Accuracy is computed over the labeled subset. Including the field (Postman does)
  always works, so this is the more permissive choice against an automated check.
- **"Sentence length" = word count.** The spec says "sentence lengths" without a unit.
  Word count is the standard text-length feature; the chart axis is labeled "words" so
  the choice is explicit.
- **Volume permissions.** Both images run as a non-root user (uid 1000) and pre-create
  `/logs` owned by that user. An empty named volume inherits the mount point's ownership
  on first mount, so the non-root API can write. This is the one real Docker gotcha here.
- **Names.** Images `sentiment-monitor-api` / `sentiment-monitor-dashboard`, volume
  `prediction-logs`, network `sentiment-net`. The spec does not pin these, so they are
  local choices, flagged here and kept consistent across the compose file, the Makefile,
  and this README.
- **Reference data.** The drift and target-drift references come from the full
  `monitoring/IMDB Dataset.csv` (50k rows), which ships in the dashboard image so the
  charts reflect the real training distribution from a fresh clone with no setup. This is
  a deliberate deviation from the earlier weeks' "dataset stays out of git and out of the
  image" convention, recorded in `COURSE_STATE.md`, and it adds 63 MB to git history.
  `imdb_sample.csv` (200 balanced rows, seed 4450) is the fallback used only if the
  dataset is absent. Nothing is fabricated.
- **Base image `python:3.13-slim`.** Same documented deviation as Assignments 2 and 3:
  the pinned stack needs Python 3.10+ and the model was pickled under 3.13, so a 3.9
  image cannot install the dependencies or load the model.

## Flagged spec conflicts (defer to Canvas)

- **Due date.** The spec header reads `8/11/2026`, the body reads `11/05/2025`. Both are
  scraped from a PDF and untrustworthy. Canvas is authoritative.
- **Points.** This spec shows 15 points; the syllabus lists seven homeworks at 10 each.
  Defer to Canvas for the real weight.

## Note to the instructor

This runs on `python:3.13-slim` rather than the `python:3.9-slim` example in the spec,
for the same reason as Assignments 2 and 3: the pinned stack (pandas 3.0.3,
scikit-learn 1.9.0) requires Python 3.10 or newer, and the Assignment 1 model was
serialized under Python 3.13, so a 3.9 image cannot install the dependencies or load the
model. If a 3.9 base is a hard requirement, I will re-pin the stack to 3.9-compatible
versions and retrain the model to match.
