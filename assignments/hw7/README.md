# Model Monitoring (Assignment 5)

A two-container monitoring system for the COMP 4450 sentiment service. A FastAPI
prediction service logs every request to a shared Docker volume, and a Streamlit
dashboard reads that log to watch for data drift, target drift, and accuracy decay.
Same model as Assignments 1 and 3 (`sentiment_model.pkl`, TF-IDF + Multinomial Naive
Bayes). The request logging, the monitoring dashboard, and the evaluation script are
new this week.

- Week: 7
- Topic: model monitoring (data drift, target drift, live accuracy and precision)
- Partner: solo
- Points: 15 per the assignment brief
- Due: `8/11/2026 11:59 PM` per the brief header. See "Flagged spec conflicts" below.

---

## For the grader: evaluate this in four commands

```bash
cd assignments/hw7
make run          # builds both images, creates the volume + network, starts both containers
make evaluate     # scores the API over the 50-row labeled test set, prints a final accuracy
open http://localhost:8501     # the monitoring dashboard
make clean        # stops containers, removes the volume and network, drops both images
```

`make evaluate` needs the `requests` library on the host: `pip install -r requirements-dev.txt`.
If those deps live in a virtualenv, point the Makefile at it:
`PYTHON=.venv/bin/python make evaluate`. Everything else runs in Docker.

Expected output from `make evaluate` on a clean stack:

```
====================================================
Scored          : 50 of 50
Correct         : 40
ACCURACY        : 80.00%
Precision (neg) : 82.61%
Precision (pos) : 77.78%
Predicted mix   : {'negative': 23, 'positive': 27}
====================================================
```

Those 50 calls also populate the dashboard, so after `make evaluate` the accuracy panel
and all three plots have real data. No separate seeding step is required.

## Requirement-to-evidence map

Every line of the assignment brief, where it is implemented, and how to check it.

| # | Requirement (from the brief) | Where | How to verify |
|---|---|---|---|
| 1 | FastAPI app with `POST /predict` | `api/main.py:260` | `curl -X POST localhost:8000/predict -H 'Content-Type: application/json' -d '{"text":"great"}'` |
| 2 | Every request logs a JSON object to `prediction_logs.json` in a `/logs` directory | `api/main.py:242` (`append_log`) | `docker compose exec dashboard cat /logs/prediction_logs.json` |
| 3 | Each log entry is a new line | `api/main.py:251` (one `json.dumps` + `\n` per call) | `test_each_request_appends_one_new_line` |
| 4 | Log carries `timestamp`, `request_text`, `predicted_sentiment`, `true_sentiment` | `api/main.py:267-271` | `test_predict_logs_exactly_the_four_required_fields` (exact-set equality) |
| 5 | Streamlit app reads and parses the log from the shared `/logs` | `monitoring/dashboard.py:63` (`load_logs`) | Dashboard header reads "Loaded N logged prediction(s)" |
| 6 | Data drift: histogram of sentence lengths, `IMDB Dataset.csv` vs logged requests | `monitoring/dashboard.py:169-202` | Dashboard section 1. Reference provenance is proven below. |
| 7 | Target drift: bar chart, predicted sentiments vs trained sentiments | `monitoring/dashboard.py:204-238` | Dashboard section 2 |
| 8 | Accuracy **and precision** from all collected feedback | `monitoring/dashboard.py:240-323` | Dashboard section 3: live accuracy, precision (positive), precision (macro), per-class precision/recall |
| 9 | **Alerting**: accuracy below 80% shows a prominent banner via `st.error()` | `monitoring/dashboard.py:266` | Drive accuracy under 80% and the red banner renders at the top of the page, above every chart |
| 10 | `evaluate.py` in the project root | `evaluate.py` | `make evaluate` |
| 11 | Reads `test_data.json` of `[{"text": ..., "true_label": ...}]` | `evaluate.py:44` (`load_test_data`) | `head -c 200 test_data.json` |
| 12 | Loops each item, POSTs to `/predict`, prints a final accuracy score | `evaluate.py:138-174` | The `ACCURACY` line in the output above |
| 13 | Two Dockerfiles: `api/Dockerfile` and `monitoring/Dockerfile` | both present | `make build` |
| 14 | Makefile handles `build`, `run`, `clean` | `Makefile` | `make build`, `make run`, `make clean` |
| 15 | README explains the architecture, Makefile steps, curl examples, evaluate.py instructions | this file | The sections below |

## System architecture

```
  Postman / curl / evaluate.py
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
  |  accuracy alert banner (top)                                          |
  |  data drift  |  target drift  |  accuracy + precision + feedback       |
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
evaluate.py          batch-scores the running API over test_data.json, prints accuracy
test_data.json       50 labeled IMDB reviews (25 positive / 25 negative), seed 4450
Makefile             build, run, seed, evaluate, test, clean
docker-compose.yml   wires the two services, the volume, and the network
pytest.ini           warnings-as-errors for the whole suite
requirements-dev.in/.txt   host-side test + eval deps, hash-pinned
hw7.postman_collection.json   7 requests, each asserting its own expected status
api/
  main.py            FastAPI app: POST /predict (logs) + GET /health
  requirements.in/.txt  pinned serving stack, hash-pinned
  Dockerfile         python:3.13-slim (digest-pinned), non-root, pre-creates /logs
  sentiment_model.pkl   the Assignment 1 model (unchanged)
  conftest.py, tests/test_api.py   21 tests on the graded logging contract
monitoring/
  dashboard.py       Streamlit monitoring dashboard
  reference_stats.py precomputed drift reference: build, load, resolve
  reference_stats.json  the 11 KB drift reference that ships in the image
  imdb_sample.csv    200-row balanced fallback if the artifact is ever absent
  requirements.in/.txt  pinned streamlit + pandas + matplotlib + requests, hash-pinned
  Dockerfile         python:3.13-slim (digest-pinned), non-root, pre-creates /logs
  conftest.py, tests/test_reference_stats.py   7 tests on reference equivalence
```

## Using the Makefile, step by step

| Command | What it does |
|---|---|
| `make build` | Builds `sentiment-monitor-api` and `sentiment-monitor-dashboard`. |
| `make run` | Builds if needed, creates the `prediction-logs` volume and `sentiment-net` network, starts both containers detached, prints the two URLs. |
| `make seed` | Sends five labeled predictions so the charts have data without running the full evaluation. |
| `make evaluate` | Runs `evaluate.py` against `http://localhost:8000` over all 50 rows of `test_data.json` and prints the final accuracy. |
| `make test` | Runs all 28 tests (21 API + 7 reference). Needs `pip install -r requirements-dev.txt`. |
| `make logs` | Follows both containers' logs. |
| `make down` | Stops the containers, keeps the volume so logs persist. |
| `make clean` | Stops containers, removes the volume **and** the network, drops both images. |

`up` is kept as an alias for `run` so older references keep working.

## Driving the API from curl

`POST /predict` takes the review text and an optional ground-truth label:

```bash
# With feedback (drives the accuracy and precision panel)
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "One of the best films I have seen in years.", "true_sentiment": "positive"}'
# {"timestamp":"2026-...","predicted_sentiment":"positive","true_sentiment":"positive","logged":true}

# Without feedback (still logged, not counted in accuracy)
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "It was fine, nothing special."}'

# Liveness
curl http://localhost:8000/health
# {"status":"ok"}
```

Each call appends one line to `/logs/prediction_logs.json`:

```json
{"timestamp":"2026-08-01T14:59:22.876856+00:00","request_text":"One of the best films I have seen in years.","predicted_sentiment":"positive","true_sentiment":"positive"}
```

Interactive docs are at <http://localhost:8000/docs>. A Postman collection covering all
seven cases below ships as `hw7.postman_collection.json`; import it and choose Run
Collection, and every request asserts its own expected status.

### Validation behavior

| Request | Response |
|---|---|
| Valid text, with or without `true_sentiment` | 200 |
| `true_sentiment` in any case or with surrounding spaces | 200, normalized to lowercase |
| Blank text, whitespace-only text, missing `text`, non-string `text` | 422 |
| Unknown `true_sentiment` value | 422 |
| Any extra field (`extra="forbid"`) | 422 |
| Non-finite JSON float (`NaN`, `Infinity`) | 422 |
| `text` longer than 20,000 characters | 422 |
| Raw body larger than 1 MiB | 413 |
| Model file missing or unreadable | 503 from `/predict`, `/health` stays 200 |

Rejected requests never reach the log, so the dashboard only ever plots real traffic.

## Using evaluate.py

The script reads a labeled JSON file, sends each `text` to the running service, and
prints a final accuracy score along with per-class precision.

```bash
pip install -r requirements-dev.txt   # only needs `requests`
make run                              # the API must be up first
make evaluate                         # or: python evaluate.py
```

Options:

```bash
python evaluate.py --api-url http://localhost:8000   # point at a different host
python evaluate.py --test-data other_data.json       # use a different labeled file
python evaluate.py --no-feedback                     # send text only, skip dashboard feedback
python evaluate.py --timeout 60                      # per-request timeout in seconds
```

By default each request also carries its ground-truth label as `true_sentiment`, so an
evaluation run doubles as feedback traffic and the dashboard's accuracy panel fills from
it. The label never reaches the model: `/predict` classifies `text` alone and logs
`true_sentiment` untouched, so there is no leakage into the prediction. Pass
`--no-feedback` to send the text only.

The script exits 0 on a clean run, 1 if any record failed to score, and 2 if the API is
unreachable. A single failed request is reported and does not abort the run.

### About `test_data.json`

The brief links an instructor-provided `test.json` at the end of the PDF. That link was
not retrievable from the assignment file, so `test_data.json` here is a stand-in built
from the genuine IMDB dataset: 50 rows, 25 positive and 25 negative, sampled with seed
4450 from the same `IMDB Dataset.csv` the model was trained on. It uses the exact schema
the brief specifies, `[{"text": ..., "true_label": ...}]`. **To grade against the
instructor's file, drop it in and run `python evaluate.py --test-data <file>`.** No code
change is needed as long as it matches that schema.

Note that these 50 rows come from the training corpus, so 80% is a generous read of true
generalization. The number is a smoke test of the serving path, not a held-out estimate.

## What the dashboard shows

- **Accuracy alert banner.** Rendered at the very top of the page, above every chart,
  whenever live accuracy falls below 80%. Implemented with `st.error()` as the brief
  requires, using a slot reserved before the charts so the banner appears at the top even
  though accuracy is computed further down. When accuracy is at or above 80% the same
  slot shows a green confirmation instead of staying blank.
- **Data drift.** Overlaid density histograms of review length in words, training data vs
  logged live requests, with the shared x-range clipped at the 99th percentile so a few
  long reviews do not flatten the chart.
- **Target drift.** Grouped bar chart of the predicted-sentiment mix in the logs against
  the trained label balance (IMDB is 25,000 / 25,000).
- **Accuracy, precision, and feedback.** Live accuracy, precision for the positive class,
  macro precision, feedback coverage, a per-class precision/recall/accuracy table, and a
  predicted-versus-true count table. All computed over the labeled subset only.

Precision for a class the model never predicted is reported as `n/a`, not `0%`. An empty
denominator makes precision undefined, and printing zero would claim the model got every
such prediction wrong when it made none at all.

## Drift-reference provenance

The dashboard's drift reference is `monitoring/reference_stats.json` (11 KB), a
precomputed length-count and sentiment-count map. The raw 63 MB `IMDB Dataset.csv` is
**not** committed in this folder, because shipping 63 MB to carry two aggregates puts a
permanent blob in git history for 300x more data than the charts read.

The substitution is verifiable, not asserted:

```bash
# The artifact reproduces exactly from the real dataset.
shasum -a 256 "../hw3/IMDB Dataset.csv"
# dfc447764f82be365fa9c2beef4e8df89d3919e3da95f5088004797d79695aa2

cd monitoring
python reference_stats.py "../../hw3/IMDB Dataset.csv" /tmp/check.json
python -c "import json; a=json.load(open('reference_stats.json')); b=json.load(open('/tmp/check.json')); print('identical:', a==b)"
# identical: True
```

`reference_stats.json` records `reference_rows: 50000` and `sentiment_counts:
{positive: 25000, negative: 25000}`. The seven tests in
`monitoring/tests/test_reference_stats.py` pin that the reconstructed frame has the same
length multiset and the same sentiment proportions as reading the CSV directly, so no
chart moves. `imdb_sample.csv` (200 balanced rows, seed 4450) is the fallback used only
if the artifact is absent. Nothing is fabricated.

This reverses an earlier decision to commit the full CSV. The reversal is recorded in
`../../COURSE_STATE.md`.

## Running the tests

```bash
pip install -r requirements-dev.txt
make test
# 28 passed
```

`pytest.ini` treats warnings as errors, with one allowlisted third-party deprecation
(starlette's TestClient httpx warning). The 21 API tests pin the graded logging contract
field by field, the newline-delimited format, every 422 path, the 413 ceiling, and the
503 degraded mode. The 7 monitoring tests pin the reference-artifact equivalence.

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

`LOG_PATH` points both processes at the same file in place of the shared volume. Set
`REFERENCE_DATA_PATH` to point the dashboard at a different reference file.

## Design decisions

- **Ports.** FastAPI on 8000, Streamlit on 8501, consistent with hw3 and lined up for the
  hw8 EC2 security group.
- **`true_sentiment` is optional, but always logged.** Real feedback is sporadic, so a
  `/predict` call without it still succeeds and logs the field as `null`. The key is
  present in every log line, never absent, so each entry carries it as the brief asks.
  Accuracy and precision are computed over the labeled subset. Including the field
  (Postman does) always works, so this is the more permissive choice against an automated
  check.
- **"Sentence length" = word count.** The brief says "sentence lengths" without a unit.
  Word count is the standard text-length feature; the chart axis is labeled "words" so the
  choice is explicit.
- **Precision without a qualifier means the positive class.** That is the binary
  convention. Macro precision and both per-class values are shown alongside it so nothing
  is hidden behind the single headline number.
- **Alert threshold is a named constant.** `ACCURACY_ALERT_THRESHOLD = 0.80` in
  `dashboard.py`, so the banner, the caption, and the docs cannot drift apart. The
  comparison is strict (`accuracy < 0.80`), matching "drops below 80%": exactly 80% does
  not alert.
- **Request bounds.** `text` is capped at 20,000 characters and the raw body at 1 MiB.
  Beyond the resource argument, the cap protects the monitoring signal itself: without it
  a single 400,000-word request moves the dashboard's "mean length, live" metric from 231
  words to 40,005 while the histogram still looks normal, which is a wrong number next to
  a plausible chart.
- **Non-finite floats return 422.** FastAPI echoes the offending input into the 422 body
  and Starlette renders JSON with `allow_nan=False`, so an uncoerced `NaN` turned the 422
  into a 500. `_json_safe` coerces it. Carried over from Assignment 3.
- **Volume permissions.** Both images run as a non-root user (uid 1000) and pre-create
  `/logs` owned by that user. An empty named volume inherits the mount point's ownership
  on first mount, so the non-root API can write. This is the one real Docker gotcha here.
- **Supply chain.** Both runtime stacks and the dev stack are hash-pinned with
  `uv pip compile --generate-hashes --universal`, and both base images are digest-pinned
  to `python:3.13-slim@sha256:6771159c...` (resolved 2026-08-01). A tag is a moving
  target; a rebuild months from now would otherwise pull a different base than the one
  tested. Regenerate a lockfile from its `.in` file, never by hand.
- **Names.** Images `sentiment-monitor-api` / `sentiment-monitor-dashboard`, volume
  `prediction-logs`, network `sentiment-net`. The brief does not pin these, so they are
  local choices, flagged here and kept consistent across the compose file, the Makefile,
  and this README.
- **Base image `python:3.13-slim`.** Same documented deviation as Assignments 2 and 3: the
  pinned stack needs Python 3.10+ and the model was pickled under 3.13, so a 3.9 image
  cannot install the dependencies or load the model.

## Flagged spec conflicts (defer to Canvas)

- **Truncated brief.** The scraped `week7_Assignment5ModelMonitoring.md` in this folder
  originally ended mid-sentence and silently dropped three graded sections: the
  accuracy/precision and alerting requirements, the entire Evaluation Script section, and
  the Packaging, Documentation, and Submission sections. It has been re-transcribed from
  the source PDF and carries an extraction note. If the transcription differs from the
  official text anywhere, the official text governs.
- **Due date.** The brief header reads `8/11/2026`, the body reads `11/05/2025`. Canvas is
  authoritative.
- **Points.** This brief shows 15 points; the syllabus lists seven homeworks at 10 each.
  Defer to Canvas for the real weight.
- **Submission repository.** The brief asks for a **new public GitHub repository**, and
  says not to reuse a repository from a previous assignment. This assignment currently
  lives in the course monorepo alongside the earlier weeks. Confirm the intended
  submission channel before the deadline. Nothing in this folder can satisfy that
  requirement by itself.

## Note to the instructor

This runs on `python:3.13-slim` rather than the `python:3.9-slim` example in the brief,
for the same reason as Assignments 2 and 3: the pinned stack (pandas 3.0.3,
scikit-learn 1.9.0) requires Python 3.10 or newer, and the Assignment 1 model was
serialized under Python 3.13, so a 3.9 image cannot install the dependencies or load the
model. If a 3.9 base is a hard requirement, I will re-pin the stack to 3.9-compatible
versions and retrain the model to match.
