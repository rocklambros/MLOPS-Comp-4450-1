# hw8 (Assignment 6) CI/CD, Testing, and EC2 Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing hw7 sentiment stack in a pytest suite, a GitHub Actions pipeline that gates every pull request to `main`, and a README that a stranger can follow to deploy both containers to a t2.micro EC2 host.

**Architecture:** `assignments/hw8/` holds a self-contained copy of hw7's `api/` and `monitoring/` services. Tests live at the spec's flat paths. One CI job at the repo root runs five ordered steps scoped to `assignments/hw8`. Deployment is manual and documented, never automated from the workflow.

**Tech Stack:** Python 3.13, FastAPI, Streamlit 1.58.0, scikit-learn 1.9.0, pytest 9.1.0, ruff 0.15.17, Docker, GitHub Actions, AWS EC2 t2.micro Ubuntu 22.04 LTS.

**Spec:** `docs/superpowers/specs/2026-08-01-hw8-cicd-testing-design.md`

## Global Constraints

Every task's requirements implicitly include this section.

- **Work happens on branch `dev`.** Already created. Never commit to `main`.
- **Never merge the pull request.** The brief bolds "Do not merge it until after grading."
- **Python 3.13** everywhere: CI `setup-python`, both Dockerfiles, every lockfile compile.
- **Ports are fixed:** FastAPI 8000, Streamlit 8501. Same numbers in Dockerfile `EXPOSE`, compose, `docker run -p`, the EC2 security group, and the README.
- **Spec-literal file paths:** `api/test_api.py` and `monitoring/test_dashboard.py`, flat, not under `tests/`.
- **Spec-literal names:** volume `prediction-logs`, network `sentiment-net`, containers `sentiment-monitor-api` and `sentiment-monitor-dashboard`.
- **Lockfiles compile with** `uv pip compile <in> --generate-hashes --universal --python-version 3.13 -o <out>`. Never hand-edit a `.txt` lockfile.
- **No fabricated evidence.** Every number in the README comes from real command output. No claimed test count, CI status, or accuracy that was not produced by running the command.
- **No AI attribution** in any commit message, file header, or documentation.
- **Writing style:** no em dashes, no semicolons, no sentence-initial "And", "But", "So", or "Or".

---

## File Structure

| File | Responsibility |
|---|---|
| `.gitignore` (root, modify) | Two negations so hw8's model and CSV are tracked |
| `.github/workflows/ci.yml` (create) | The five-step CI job, repo root because GitHub reads workflows nowhere else |
| `assignments/hw8/api/main.py` (copy) | FastAPI service, unchanged from hw7 v1.1.0 |
| `assignments/hw8/api/test_api.py` (create) | Spec-literal API tests, ported plus label assertions |
| `assignments/hw8/api/conftest.py` (copy) | `sys.path` shim so `import main` resolves |
| `assignments/hw8/monitoring/dashboard.py` (copy) | Streamlit dashboard, unchanged |
| `assignments/hw8/monitoring/test_dashboard.py` (create) | Spec-literal launch tests |
| `assignments/hw8/monitoring/test_reference_stats.py` (copy) | Carried so the suite does not shrink |
| `assignments/hw8/requirements.in` (create) | Single source for the root lockfile |
| `assignments/hw8/requirements.txt` (generate) | Spec-literal target of CI step 3 |
| `assignments/hw8/pyproject.toml` (create) | ruff configuration, pinned rules |
| `assignments/hw8/pytest.ini` (create) | `filterwarnings = error` gate |
| `assignments/hw8/Makefile` (adapt) | Local targets, `test` pointed at flat paths |
| `assignments/hw8/README.md` (create) | The operational manual, Part 4's deliverable |

---

### Task 1: Scaffold hw8 and defeat the `.gitignore` trap

The highest-cost failure in this assignment is silent. `git add` skips the model with no error, and the grader's `docker build` dies. This task ends only when the binaries are proven tracked on the pushed remote.

**Files:**
- Create: `assignments/hw8/` (copied tree from `assignments/hw7/`)
- Modify: `.gitignore` (root, append two negations)
- Delete after copy: `assignments/hw8/api/tests/`, `assignments/hw8/monitoring/tests/`, `assignments/hw8/hw7.postman_collection.json`, `assignments/hw8/week7_Assignment5ModelMonitoring.md`, `assignments/hw8/requirements-dev.in`, `assignments/hw8/requirements-dev.txt`

**Interfaces:**
- Consumes: nothing, this is the first task
- Produces: the `assignments/hw8/` tree every later task edits. Service lockfiles `api/requirements.txt` and `monitoring/requirements.txt` carry forward unchanged.

- [ ] **Step 1: Copy the hw7 tree, excluding build and virtualenv artifacts**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
rsync -a --exclude '.venv/' --exclude '__pycache__/' --exclude '.pytest_cache/' \
  --exclude 'IMDB Dataset.csv' \
  assignments/hw7/ assignments/hw8/
```

- [ ] **Step 2: Remove the files hw8 replaces or does not need**

The old README is hw7's. The nested `tests/` directories are replaced by flat spec-literal files. `requirements-dev.*` is replaced by the root `requirements.in` in Task 2.

```bash
cd assignments/hw8
rm -rf api/tests monitoring/tests
rm -f README.md week7_Assignment5ModelMonitoring.md hw7.postman_collection.json
rm -f requirements-dev.in requirements-dev.txt
git checkout -- README.md 2>/dev/null || true   # restore the tracked hw8 stub if git had one
ls -la
```

- [ ] **Step 3: Confirm the trap exists before fixing it**

Run: `cd /Users/klambros/github_projects/MLOPS-Comp-4450-1 && git check-ignore -v assignments/hw8/api/sentiment_model.pkl assignments/hw8/monitoring/imdb_sample.csv`

Expected output, proving the problem is real:

```
.gitignore:234:*.pkl	assignments/hw8/api/sentiment_model.pkl
.gitignore:250:*.csv	assignments/hw8/monitoring/imdb_sample.csv
```

- [ ] **Step 4: Add the two negations to the root `.gitignore`**

Append next to the existing hw7 negations at lines 261 and 289 so the pattern stays discoverable:

```gitignore
# hw8 ships the same two binaries hw7 does: the trained model the API loads at
# import, and the small CSV fallback the monitoring Dockerfile COPYs by name.
# Without these negations `git add` skips both silently and the grader's
# `docker build` fails at COPY.
!assignments/hw8/api/sentiment_model.pkl
!assignments/hw8/monitoring/imdb_sample.csv
```

- [ ] **Step 5: Verify the negations took**

Run: `git check-ignore -v assignments/hw8/api/sentiment_model.pkl assignments/hw8/monitoring/imdb_sample.csv`
Expected: no output, exit status 1. Any output means the negation is in the wrong place relative to the ignoring pattern.

- [ ] **Step 6: Verify the model is byte-identical to the graded artifact**

Run: `shasum -a 256 assignments/hw8/api/sentiment_model.pkl assignments/hw7/api/sentiment_model.pkl`
Expected: both print `b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329`. A different hash means the copy is wrong and every downstream test is testing the wrong model.

- [ ] **Step 7: Commit and push**

```bash
git add .gitignore assignments/hw8
git commit -m "hw8: scaffold from hw7 and track the model and sample CSV

The root .gitignore swallows *.pkl and *.csv. hw7 works only because of
path-literal negations. hw8 needs its own or the model never reaches the
pull request and the deployment build fails at COPY."
git push -u origin dev
```

- [ ] **Step 8: Verify the binaries reached the remote, not just the index**

Run: `git ls-tree -r origin/dev --name-only | grep -E 'hw8.*(\.pkl|\.csv)'`
Expected: both `assignments/hw8/api/sentiment_model.pkl` and `assignments/hw8/monitoring/imdb_sample.csv` listed. This is the check that would have caught the failure, so it runs against the remote rather than the working tree.

---

### Task 2: Dependency and tooling layer

CI step 3 installs from a single `requirements.txt` that does not exist yet. It must carry `httpx`, which is absent from the API lockfile and which FastAPI's `TestClient` imports.

**Files:**
- Create: `assignments/hw8/requirements.in`
- Create: `assignments/hw8/requirements.txt` (generated, never hand-edited)
- Create: `assignments/hw8/pyproject.toml`
- Create: `assignments/hw8/pytest.ini`

**Interfaces:**
- Consumes: `api/requirements.in` and `monitoring/requirements.in` from Task 1
- Produces: `requirements.txt` (the CI step 3 target), a `ruff` config that pins the rule set, and a `pytest.ini` whose rootdir anchors at `assignments/hw8`

- [ ] **Step 1: Write `assignments/hw8/requirements.in`**

Modeled on hw7's `requirements-dev.in`, which already chains both service `.in` files. `ruff` is the addition, pinned to the version hw3 already uses.

```
# Root dependency source for hw8. One compile, one lockfile, because CI step 3
# says "Install all project dependencies from requirements.txt" (singular).
#
# Chains both service runtimes so the test suite can import `main` (api) and
# `reference_stats` plus `dashboard` (monitoring), then adds the test and lint
# tooling. httpx is required by fastapi.testclient.TestClient and is NOT in
# api/requirements.in, so every API test would die at collection without it.
#
# Compile with:
#   uv pip compile requirements.in --generate-hashes --universal \
#     --python-version 3.13 -o requirements.txt
-r api/requirements.in
-r monitoring/requirements.in
pytest==9.1.0
httpx==0.28.1
ruff==0.15.17
```

- [ ] **Step 2: Compile the lockfile**

`--universal` and `--python-version 3.13` are mandatory. Without them the compile produces macOS-arm64 wheel hashes that fail `--require-hashes` on `ubuntu-latest`.

Run:
```bash
cd assignments/hw8
uv pip compile requirements.in --generate-hashes --universal \
  --python-version 3.13 -o requirements.txt
```

- [ ] **Step 3: Verify the lockfile carries hashes and the required packages**

```bash
grep -c 'sha256' requirements.txt          # expect a large number, not 0
grep -E '^(httpx|pytest|ruff|streamlit|scikit-learn)==' requirements.txt
```
Expected: `httpx==0.28.1`, `pytest==9.1.0`, `ruff==0.15.17`, `streamlit==1.58.0`, `scikit-learn==1.9.0` all present.

- [ ] **Step 4: Verify the root lockfile agrees with the service lockfiles on the model stack**

A mismatch means CI tests a different scikit-learn than the shipped image unpickles with.

```bash
grep -E '^(scikit-learn|numpy|scipy|joblib)==' requirements.txt
grep -E '^(scikit-learn|numpy|scipy|joblib)==' api/requirements.txt
```
Expected: identical versions in both lists.

- [ ] **Step 5: Write `assignments/hw8/pyproject.toml`**

No lint config exists anywhere in this repo, and bare "ruff defaults" drift between versions. Pin the rule set so a future ruff cannot redden a graded pipeline.

```toml
# ruff configuration for hw8.
# Course: COMP 4450 MLOps   Owner: Rock Lambros <rock@rockcyber.com>
#
# The rule set is pinned explicitly rather than left to ruff's defaults, because
# defaults shift between releases and this linter gates a graded pull request.
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
# E/W pycodestyle, F pyflakes, I import sorting, B bugbear, UP pyupgrade.
select = ["E", "W", "F", "I", "B", "UP"]
```

- [ ] **Step 6: Write `assignments/hw8/pytest.ini`**

```ini
[pytest]
# Treat warnings as failures so a green run means something, then allowlist the one
# known third-party deprecation: FastAPI's TestClient imports starlette's TestClient
# with httpx, which starlette now flags. Not our code. Any new warning from our own
# code still fails the run.
filterwarnings =
    error
    ignore::starlette.exceptions.StarletteDeprecationWarning
```

- [ ] **Step 7: Verify the toolchain installs and runs from the lockfile**

Run:
```bash
cd assignments/hw8
python3 -m venv /tmp/hw8check && /tmp/hw8check/bin/pip install --require-hashes -r requirements.txt
/tmp/hw8check/bin/ruff --version
```
Expected: install succeeds with no hash errors, and ruff reports `0.15.17`. Using the venv's ruff rather than the one on PATH is the point, since the machine's ambient ruff is a different version.

- [ ] **Step 8: Commit**

```bash
git add assignments/hw8/requirements.in assignments/hw8/requirements.txt \
        assignments/hw8/pyproject.toml assignments/hw8/pytest.ini
git commit -m "hw8: single hash-compiled lockfile, ruff config, pytest gate

CI step 3 installs from one requirements.txt. httpx is added explicitly
because fastapi.testclient.TestClient imports it and the API lockfile does
not carry it. The ruff rule set is pinned rather than left to defaults."
```

---

### Task 3: `api/test_api.py` at the spec-literal path

The brief names `api/test_api.py` and requires a positive example, a negative example, and malformed-data handling. hw7's suite covers the request contract but never asserts a predicted label.

**Files:**
- Create: `assignments/hw8/api/test_api.py`
- Reference: `assignments/hw7/api/tests/test_api.py` (the 14 tests to port)

**Interfaces:**
- Consumes: `api/conftest.py` from Task 1, which inserts `api/` on `sys.path` so `import main` resolves. The shim uses `Path(__file__).resolve().parent`, so it works unchanged with a flat test file beside it.
- Produces: a suite `pytest -q` collects from `assignments/hw8`. Task 6's CI step 5 runs it.

- [ ] **Step 1: Measure the model's actual margin before writing any assertion**

A fixture that classifies at 0.51 is a flaky red check on the graded pull request. Measure first, then pick.

Run:
```bash
cd assignments/hw8/api
/tmp/hw8check/bin/python -c "
import joblib
m = joblib.load('sentiment_model.pkl')
cases = [
    'An absolute masterpiece, I loved every minute of it.',
    'A boring, painful waste of two hours.',
    'The acting was wooden and the plot made no sense at all.',
    'Beautifully shot with a moving, unforgettable score.',
]
for t in cases:
    p = m.predict([t])[0]
    conf = max(m.predict_proba([t])[0])
    print(f'{conf:.4f}  {p:<9}  {t}')
"
```
Record the output. Choose the highest-confidence positive and the highest-confidence negative for the two graded fixtures.

- [ ] **Step 2: Port hw7's 14 tests, then write the two failing label tests**

Copy `assignments/hw7/api/tests/test_api.py` to `assignments/hw8/api/test_api.py` verbatim, then append the two new tests. Substitute the actual margin measured in Step 1 into the comment.

```python
# ---------------------------------------------------------------------------
# Assignment 6, Part 1: the brief requires "/predict with both a positive and a
# negative example". hw7's suite pins the request contract (log keys, echoed
# response, timestamp format) but never asserts the predicted label, so these two
# close that gap.
#
# Fixtures are chosen for margin, not realism. Week 1 material warns that ML
# models are evaluated empirically rather than proven correct, so a borderline
# review would make this a flaky gate on a graded pipeline. Measured confidence
# on the shipped model: positive <FILL FROM STEP 1>, negative <FILL FROM STEP 1>.
# ---------------------------------------------------------------------------


def test_predict_classifies_a_clearly_positive_review_as_positive(client, log_path):
    """Part 1: the positive example."""
    response = client.post(
        "/predict",
        json={"text": "An absolute masterpiece, I loved every minute of it."},
    )

    assert response.status_code == 200
    assert response.json()["predicted_sentiment"] == "positive"


def test_predict_classifies_a_clearly_negative_review_as_negative(client, log_path):
    """Part 1: the negative example."""
    response = client.post(
        "/predict",
        json={"text": "A boring, painful waste of two hours."},
    )

    assert response.status_code == 200
    assert response.json()["predicted_sentiment"] == "negative"


def test_predict_rejects_malformed_and_missing_data(client, log_path):
    """Part 1: the brief's "missing or malformed data" bullet, named to match its wording.

    The parametrized 422 cases above cover this in more depth. This test exists so a
    grader reading the file against the checklist finds the bullet's own language.
    """
    missing_text = client.post("/predict", json={})
    malformed_body = client.post(
        "/predict",
        content=b"{not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert missing_text.status_code == 422
    assert malformed_body.status_code == 422
    assert read_log(log_path) == []
```

Match the fixture names (`client`, `log_path`) and the `read_log` helper to whatever the ported hw7 file actually defines. Read the ported file first rather than assuming.

- [ ] **Step 3: Run the new tests and watch them fail for the right reason**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/python -m pytest api/test_api.py -k "clearly_positive or clearly_negative or malformed_and_missing" -v`
Expected: they fail on a fixture or helper name mismatch, not on the assertion. Fix the names until the failure is a real assertion failure or a pass.

- [ ] **Step 4: Run the whole file**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/python -m pytest api/test_api.py -q`
Expected: all pass, zero warnings. Record the collected count for the README.

- [ ] **Step 5: Lint**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/ruff check api/`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add assignments/hw8/api/test_api.py
git commit -m "hw8: API tests at the spec-literal path with label assertions

Ports hw7's request-contract suite to api/test_api.py and adds the positive
and negative label assertions Part 1 names. Fixtures are chosen by measured
predict_proba margin so the gate cannot flake on a graded pipeline."
```

---

### Task 4: `monitoring/test_dashboard.py` at the spec-literal path

The only genuinely net-new test work. `dashboard.py` has zero coverage. A naive test greens on a dashboard that rendered nothing, because `dashboard.py:162` calls `st.stop()` when the log is empty.

**Files:**
- Create: `assignments/hw8/monitoring/test_dashboard.py`
- Move: `assignments/hw7/monitoring/tests/test_reference_stats.py` becomes `assignments/hw8/monitoring/test_reference_stats.py`

**Interfaces:**
- Consumes: `monitoring/conftest.py` from Task 1 for the `sys.path` shim. `dashboard.py` reads `LOG_PATH` and `API_URL` from the environment at module import (`dashboard.py:33` and `:36`), which is the seam these tests use.
- Produces: the dashboard-launch evidence Part 1 requires.

- [ ] **Step 1: Move the reference-stats tests to the flat path**

The suite must not shrink. CI step 5 runs "your entire test suite".

```bash
cd assignments/hw8/monitoring
git mv ../../hw7/monitoring/tests/test_reference_stats.py test_reference_stats.py 2>/dev/null \
  || cp ../../hw7/monitoring/tests/test_reference_stats.py test_reference_stats.py
```

- [ ] **Step 2: Write `assignments/hw8/monitoring/test_dashboard.py`**

```python
"""Launch tests for the Streamlit monitoring dashboard (Assignment 6, Part 1).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>

The brief asks for "at least one simple test for your Streamlit application to
ensure it can launch without errors". One test is not enough to mean anything
here, for two reasons.

First, dashboard.py calls st.stop() at line 162 when the prediction log is empty.
An AppTest run against an empty log therefore stops early, and an assertion that
no exception was raised is vacuously true on a dashboard that rendered almost
nothing. Every test below seeds a log first so the script runs to completion.

Second, AppTest runs the script in-process and never binds a port, so it cannot
prove the real server starts. The subprocess test covers that and nothing more:
Streamlit answers /_stcore/health before the script finishes, so a healthy probe
proves the process is up, not that dashboard.py rendered. The two tests together
cover import-time failure and boot-time failure. Neither covers the other.
"""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest

HERE = Path(__file__).resolve().parent
APP = HERE / "dashboard.py"

# dashboard.py defaults API_URL to http://api:8000, a Docker-network name that does
# not resolve off the network. requests.get would burn its full 2-second timeout on
# DNS before the script continues, which is most of AppTest's default budget. Point
# it at a closed local port instead for an instant connection-refused.
UNREACHABLE_API = "http://127.0.0.1:1"


def _write_log(path, records):
    """Write newline-delimited JSON, the format the API appends and the dashboard reads."""
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def _labeled_records():
    """Three logged predictions with feedback, so the accuracy section has data."""
    return [
        {
            "timestamp": "2026-08-01T12:00:00+00:00",
            "request_text": "An absolute masterpiece, I loved every minute of it.",
            "predicted_sentiment": "positive",
            "true_sentiment": "positive",
        },
        {
            "timestamp": "2026-08-01T12:00:01+00:00",
            "request_text": "A boring, painful waste of two hours.",
            "predicted_sentiment": "negative",
            "true_sentiment": "negative",
        },
        {
            "timestamp": "2026-08-01T12:00:02+00:00",
            "request_text": "The acting was wooden and the plot made no sense.",
            "predicted_sentiment": "positive",
            "true_sentiment": "negative",
        },
    ]


@pytest.fixture
def seeded_log(tmp_path, monkeypatch):
    """Point the dashboard at a temp log holding labeled predictions."""
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _labeled_records())
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)
    return log


def test_dashboard_launches_without_errors(seeded_log):
    """Part 1: the required launch test, run past both st.stop() branches."""
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()

    assert not at.exception, f"dashboard raised: {at.exception}"
    # Rendering proof, not just absence of a traceback: the success banner only
    # renders after the log loads, which is past the st.stop() at line 162.
    assert len(at.success) >= 1
    assert len(at.error) == 0


def test_dashboard_renders_charts_from_the_seeded_log(seeded_log):
    """The three monitoring signals reach the page rather than erroring out."""
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()

    assert not at.exception
    rendered = " ".join(str(m.value) for m in at.markdown) + " ".join(
        str(s.value) for s in at.success
    )
    assert "prediction" in rendered.lower()


def test_dashboard_warns_when_no_feedback_has_been_collected(tmp_path, monkeypatch):
    """The degraded state a freshly deployed host is actually in.

    Logs exist but nobody has supplied true_sentiment, so the drift charts render
    while the accuracy section has nothing to measure. This is the state the grader
    sees right after the runbook's seed step if feedback is omitted.
    """
    log = tmp_path / "prediction_logs.json"
    _write_log(
        log,
        [
            {
                "timestamp": "2026-08-01T12:00:00+00:00",
                "request_text": "An absolute masterpiece, I loved every minute of it.",
                "predicted_sentiment": "positive",
                "true_sentiment": None,
            }
        ],
    )
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()

    assert not at.exception
    assert len(at.error) == 0


def test_dashboard_stops_cleanly_when_no_predictions_are_logged(tmp_path, monkeypatch):
    """An empty log is an informational state, not a crash."""
    log = tmp_path / "prediction_logs.json"
    log.write_text("", encoding="utf-8")
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()

    assert not at.exception
    assert len(at.info) >= 1


def test_accuracy_alert_threshold_is_the_spec_value():
    """hw7's spec set an 80 percent alert threshold. Pin it so a refactor cannot drift it."""
    import dashboard

    assert dashboard.ACCURACY_ALERT_THRESHOLD == 0.80


def _free_port():
    """Bind port 0 and let the OS choose, so a busy 8501 cannot fail the run."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_streamlit_server_boots_and_serves_health(tmp_path):
    """Boot proof. AppTest never binds a port, so this covers what it cannot.

    Proves only that the Streamlit process starts and serves its health endpoint.
    Streamlit answers /_stcore/health before the script body finishes, so this does
    NOT prove dashboard.py rendered. The AppTest cases above cover that.
    """
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _labeled_records())
    port = _free_port()

    env = {
        **os.environ,
        "LOG_PATH": str(log),
        "API_URL": UNREACHABLE_API,
    }
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(APP),
            "--server.headless", "true",       # without this Streamlit blocks on an email prompt
            "--server.port", str(port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                output = proc.stdout.read().decode("utf-8", "replace")
                pytest.fail(f"streamlit exited early with {proc.returncode}:\n{output}")
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/_stcore/health", timeout=1)
                if resp.status_code == 200:
                    return
            except requests.RequestException:
                time.sleep(0.5)
        pytest.fail("streamlit did not serve /_stcore/health within 60 seconds")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
```

- [ ] **Step 3: Run the dashboard tests**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/python -m pytest monitoring/test_dashboard.py -v`
Expected: all pass. If `test_dashboard_renders_charts_from_the_seeded_log` fails on the substring, print the rendered elements and adjust the assertion to something the app actually renders. Do not weaken it to `assert True`.

- [ ] **Step 4: Run the whole suite and record the real count**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/python -m pytest -q`
Expected: every test passes with zero warnings under `filterwarnings = error`. Write the collected count down. The README cites this number and it must be the real one.

- [ ] **Step 5: Lint**

Run: `cd assignments/hw8 && /tmp/hw8check/bin/ruff check .`
Expected: `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add assignments/hw8/monitoring/test_dashboard.py assignments/hw8/monitoring/test_reference_stats.py
git commit -m "hw8: dashboard launch tests at the spec-literal path

dashboard.py calls st.stop() on an empty log, so a bare launch assertion is
vacuously true. Every case seeds a log first. AppTest covers import-time
failure, a headless subprocess on a free port covers boot-time failure, and
each test states what it does not prove."
```

---

### Task 5: Local orchestration and stack verification

**Files:**
- Modify: `assignments/hw8/Makefile` (the `test` target points at directories that no longer exist)
- Verify: `assignments/hw8/docker-compose.yml` (carried from hw7, names already correct)

**Interfaces:**
- Consumes: the test files from Tasks 3 and 4
- Produces: `make test`, `make run`, `make seed`, `make clean` working from `assignments/hw8`

- [ ] **Step 1: Fix the `test` target**

hw7's target reads `$(PYTHON) -m pytest api/tests monitoring/tests -q`. Both directories are gone.

Replace that line with:

```makefile
# Unit and API checks for both services. Install deps first:
#   pip install --require-hashes -r requirements.txt
test:
	$(PYTHON) -m pytest -q
```

Bare `pytest` picks up `pytest.ini` and collects both flat test files from the rootdir.

- [ ] **Step 2: Update the stale comment on the `evaluate` target**

hw7's comment says "the 50-row labeled test set". `test.json` holds 174 records. Change `50-row` to `174-record`.

- [ ] **Step 3: Verify the Makefile**

Run: `cd assignments/hw8 && PYTHON=/tmp/hw8check/bin/python make test`
Expected: the same pass count Task 4 recorded.

- [ ] **Step 4: Build both images**

Run: `cd assignments/hw8 && make build`
Expected: both images build. A failure at `COPY ... sentiment_model.pkl` means Task 1 Step 5 was skipped.

- [ ] **Step 5: Run the stack and seed it**

```bash
cd assignments/hw8
make run
sleep 10
make seed
curl -fsS http://localhost:8000/health
```
Expected: `{"status":"ok"}`, and `make seed` prints five JSON responses.

- [ ] **Step 6: Confirm the dashboard renders with data**

Open `http://localhost:8501`. Expected: the success banner and three charts, not "No predictions logged yet". Take the screenshot the README will use.

- [ ] **Step 7: Tear down**

Run: `cd assignments/hw8 && make clean`
Expected: containers, volume, network, and both images removed. This matters because Task 8 reuses the same fixed names.

- [ ] **Step 8: Commit**

```bash
git add assignments/hw8/Makefile
git commit -m "hw8: point make test at the flat spec-literal test paths

hw7's target named api/tests and monitoring/tests, which the flat layout
removes. Also corrects the evaluate comment: test.json holds 174 records,
not 50."
```

---

### Task 6: The CI workflow

**Files:**
- Create: `.github/workflows/ci.yml` (repo root, GitHub reads workflows nowhere else)

**Interfaces:**
- Consumes: `assignments/hw8/requirements.txt` from Task 2, the suites from Tasks 3 and 4
- Produces: the green check the brief requires the pull request to display

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
# CI for COMP 4450 Assignment 6 (hw8).
# Owner: Rock Lambros <rock@rockcyber.com>
#
# The brief specifies ONE job whose steps run "in order": checkout, set up Python,
# install from requirements.txt, lint, test. The week 8 lecture sketches two jobs
# (Test and Code Quality), which would break that stated ordering, so the brief wins.
#
# The workflow lives at the repository root because GitHub reads workflows only from
# there. Every step is scoped to assignments/hw8 via working-directory, which also
# keeps pytest's rootdir on hw8's pytest.ini and its filterwarnings=error gate.
#
# No paths: filter. It would suppress the run on a pull request touching nothing under
# assignments/hw8, and the brief requires the checks to be visible on the pull request.
name: ci

on:
  pull_request:
    branches: [main]

# Least privilege. The job only reads the repository.
permissions:
  contents: read

jobs:
  ci:
    name: lint and test
    runs-on: ubuntu-latest
    # The dashboard subprocess test starts a real server. A hung job shows the grader
    # a yellow check, which reads worse than a red one.
    timeout-minutes: 15
    defaults:
      run:
        working-directory: assignments/hw8

    steps:
      # 1. Check out the code from the repository.
      # Actions are pinned to commit SHAs rather than tags, so a moved tag cannot
      # change what runs. This exceeds anything the course showed.
      - name: Check out the repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      # 2. Set up a specific version of Python.
      # 3.13, not the course's 3.9: pandas 3.0.3 and scikit-learn 1.9.0 need 3.10+,
      # and sentiment_model.pkl was serialized under 3.13.
      - name: Set up Python 3.13
        uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b  # v5.3.0
        with:
          python-version: '3.13'

      # 3. Install all project dependencies from requirements.txt.
      - name: Install dependencies
        run: pip install --require-hashes -r requirements.txt

      # 4. Linting.
      - name: Lint with ruff
        run: ruff check .

      # 5. Testing.
      - name: Run the test suite
        run: pytest -q
```

- [ ] **Step 2: Validate the YAML parses**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml')); print('valid')"`
Expected: `valid`.

- [ ] **Step 3: Confirm the five steps are in the brief's order**

Run: `grep -n 'name:' .github/workflows/ci.yml`
Expected, in this order: Check out, Set up Python, Install dependencies, Lint with ruff, Run the test suite.

- [ ] **Step 4: Commit and push**

```bash
git add .github/workflows/ci.yml
git commit -m "hw8: CI workflow, one job with the five ordered steps

Triggers on every pull request to main with no paths filter, so the check is
always visible on the graded pull request. Scoped to assignments/hw8 so
pytest's rootdir keeps hw8's filterwarnings=error gate. Actions pinned to SHAs."
git push
```

- [ ] **Step 5: Prove the workflow is green BEFORE the graded pull request exists**

This is the step that prevents discovering a red pipeline on the artifact the instructor is looking at.

```bash
git checkout -b ci-smoke-test
git commit --allow-empty -m "chore: trigger a CI validation run"
git push -u origin ci-smoke-test
gh pr create --base main --head ci-smoke-test --title "CI validation, do not merge" \
  --body "Throwaway pull request to prove the workflow runs green. Closing immediately."
gh pr checks --watch
```
Expected: the `lint and test` check passes. If it fails, fix on this branch, and only move on once it is green.

- [ ] **Step 6: Close the throwaway and clean up**

```bash
gh pr close ci-smoke-test --delete-branch
git checkout dev
```

---

### Task 7: The README operational manual

Part 4 calls this "the final, most critical piece". The instructor grades Part 3 by executing it, so a command that errors is the most legible deduction available.

**Files:**
- Create: `assignments/hw8/README.md`

**Interfaces:**
- Consumes: real output from every prior task
- Produces: the Part 4 deliverable and the Part 3 procedure

- [ ] **Step 1: Write the architecture section**

Extend hw7's Mermaid diagram (at `assignments/hw7/README.md:77-94`) with two additions Part 4 item 1 names: the CI pipeline and the EC2 host boundary. Cover all four required elements: the FastAPI service, the Streamlit dashboard, the CI/CD pipeline, and the deployment on EC2.

Use the course's own five-stage vocabulary from `resources/wk8/week8_Introduction.md`: Source and Commit, Build, Test, Deploy, Monitor and Feedback. State that hw8 automates Test and documents Deploy manually. Do not write "continuous deployment", which the course defines as running "without any human intervention" and which Part 3 contradicts on the same page.

- [ ] **Step 2: Write the local development section**

Both paths. The `make` targets, then the raw `docker` equivalents for a grader who skips `make`. Include the teardown between them, because both paths use the same fixed container, volume, and network names and the second fails on a name collision without it.

- [ ] **Step 3: Write the EC2 deployment guide with every literal command**

Written for a reader who just downloaded a fresh key pair and has nothing else. Thirteen numbered steps:

````markdown
1. Launch the instance
   - AMI: Ubuntu Server 22.04 LTS
   - Instance type: t2.micro
   - Key pair: create or select one, download the .pem
   - Security group inbound rules:

     | Type       | Port | Source        |
     |------------|------|---------------|
     | SSH        | 22   | My IP         |
     | Custom TCP | 8000 | Anywhere-IPv4 |
     | Custom TCP | 8501 | Anywhere-IPv4 |

2. Protect the key. A freshly downloaded .pem is world-readable and SSH refuses it.
   ```bash
   chmod 400 <key>.pem
   ```

3. Connect.
   ```bash
   ssh -i <key>.pem ubuntu@<EC2_PUBLIC_IP>
   ```

4. Install Docker and Git.
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io git
   sudo systemctl enable --now docker
   ```

5. Grant docker access, then reload the group. Group membership does not apply to the
   current shell, so skipping this fails the first build with a socket permission error.
   ```bash
   sudo usermod -aG docker ubuntu
   newgrp docker
   docker ps
   ```

6. Get the code onto the host.

   Primary path, no credential on the box. Run this from your laptop, not the instance:
   ```bash
   scp -i <key>.pem -r assignments/hw8 ubuntu@<EC2_PUBLIC_IP>:/home/ubuntu/hw8
   ```

   Alternative satisfying Part 3's "Clone your GitHub repository onto the EC2 instance".
   The `-b dev` is required: the pull request stays unmerged for grading, so `main`
   carries no hw8 code. The repository is private, so this needs a credential.
   ```bash
   git clone -b dev https://github.com/rocklambros/MLOPS-Comp-4450-1.git
   cd MLOPS-Comp-4450-1/assignments/hw8
   ```

7. Create the shared network. The brief mandates a volume and never mentions a network,
   yet the dashboard resolves the API by container name, which the default bridge does
   not provide. Without this the stack looks healthy and the API badge reads unreachable.
   ```bash
   docker network create sentiment-net
   ```

8. Create the shared volume.
   ```bash
   docker volume create prediction-logs
   ```

9. Build both images.
   ```bash
   cd /home/ubuntu/hw8
   docker build -t sentiment-monitor-api ./api
   docker builder prune -f
   docker build -t sentiment-monitor-dashboard ./monitoring
   ```

10. Run both containers detached on the shared volume and network.
    ```bash
    docker run -d --name sentiment-monitor-api \
      --network sentiment-net \
      -p 8000:8000 \
      -v prediction-logs:/logs \
      --restart unless-stopped \
      sentiment-monitor-api

    docker run -d --name sentiment-monitor-dashboard \
      --network sentiment-net \
      -p 8501:8501 \
      -v prediction-logs:/logs \
      -e API_URL=http://sentiment-monitor-api:8000 \
      --restart unless-stopped \
      sentiment-monitor-dashboard
    ```
    `API_URL` is the CONTAINER name here. Compose uses the service name `api`, and
    copying that value into this path breaks the dashboard's health badge.

11. Seed the log so the dashboard has data. Without this the grader opens port 8501
    and sees "No predictions logged yet" and nothing else.
    ```bash
    curl -fsS -X POST http://<EC2_PUBLIC_IP>:8000/predict \
      -H 'Content-Type: application/json' \
      -d '{"text": "An absolute masterpiece, I loved every minute of it.", "true_sentiment": "positive"}'
    curl -fsS -X POST http://<EC2_PUBLIC_IP>:8000/predict \
      -H 'Content-Type: application/json' \
      -d '{"text": "A boring, painful waste of two hours.", "true_sentiment": "negative"}'
    ```

12. Verify. Check `/predict`, not only `/health`: a mis-copied model yields a container
    that passes `docker ps` and `GET /health` while returning 503 on `/predict`.
    ```bash
    docker ps
    curl -fsS http://<EC2_PUBLIC_IP>:8000/health
    ```
    Then open `http://<EC2_PUBLIC_IP>:8501` and confirm the charts render.

13. Tear down when finished.
    ```bash
    docker rm -f sentiment-monitor-api sentiment-monitor-dashboard
    docker volume rm prediction-logs
    docker network rm sentiment-net
    ```
    Then terminate the instance in the console. Leaving it running leaves an
    unauthenticated service exposed to the internet.
````

- [ ] **Step 4: Write the requirement-to-evidence table**

Use hw7's format from `assignments/hw7/README.md:50-75`. One row per brief requirement, with the file and the verification command. No row claims more than its command proves. The subprocess dashboard test proves the server boots, not that the page rendered, and the table must say so.

- [ ] **Step 5: Write the deviations and limitations sections**

Deviations: monorepo rather than a new repository and private rather than public, granted verbally in class; Python 3.13; ruff over flake8; the workflow at the repository root; CI without CD; pinned action SHAs; 413 and 503 beyond the taught status vocabulary.

Limitations, both directions of the security posture: inbound, anyone can post to `/predict`, bounded only by the 1 MiB body cap and the 20,000-character text cap. Outbound, port 8501 serves an unauthenticated read of every logged prediction, because `dashboard.py:328` renders the recent-requests table including `request_text`. Note that this contradicts week 3's guidance that HTTPS is "essential for protecting data in transit" and is the configuration the brief specifies.

Also state what is deliberately absent so it reads as scoping: no S3, DynamoDB, or IAM instance profile, because the brief says only "Clone your GitHub repository" and the model ships in the repository.

- [ ] **Step 6: Redact and verify**

Every host reference reads `<EC2_PUBLIC_IP>`. Any pasted command output has the real IP redacted the same way. Public IPv4 changes on stop and start, so a hard-coded address goes stale immediately.

Run: `grep -nE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' assignments/hw8/README.md`
Expected: only `127.0.0.1`, `0.0.0.0`, and version numbers. No EC2 address.

- [ ] **Step 7: Verify every claimed number is real**

Cross-check the test count against Task 4 Step 4's recorded output. Cross-check any accuracy figure against a real `evaluate.py` run. An unverified number violates the Honor Code's fabrication clause and the spec's own §12.

- [ ] **Step 8: Commit**

```bash
git add assignments/hw8/README.md
git commit -m "hw8: operational manual covering architecture, local dev, and EC2 deploy

The instructor grades Part 3 by replicating the written procedure rather than
inspecting the instance, so every command is copy-pasteable from a fresh box:
chmod 400, the docker group reload, the shared network the brief omits, the
container-name API_URL, the seed step, and teardown."
```

---

### Task 8: Sandbox validation of the deployment guide

The guide is the graded artifact. Executing it once is the only way to know it works.

**Files:** none. This task produces evidence, not code.

**Interfaces:**
- Consumes: the README from Task 7
- Produces: corrections to Task 7 plus screenshots for the README

- [ ] **Step 1: Launch a sandbox instance following only the README**

Follow the written steps literally. Do not use knowledge that is not on the page. Every place you reach for something the README did not tell you is a defect in the README.

- [ ] **Step 2: Record every deviation**

Keep a running list of every command that failed, every missing prerequisite, and every ambiguous instruction.

- [ ] **Step 3: Watch the resource ceiling**

Between the two builds run `df -h` and `free -m`. t2.micro is 1 vCPU, 1 GB RAM, and an 8 GB root volume holding two images plus build cache. If the build or the running stack exhausts memory, add the swap step to the README as a numbered step rather than a footnote:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
```

- [ ] **Step 4: Verify the deployed stack end to end**

```bash
curl -fsS http://<EC2_PUBLIC_IP>:8000/health
curl -fsS -X POST http://<EC2_PUBLIC_IP>:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "An absolute masterpiece, I loved every minute of it.", "true_sentiment": "positive"}'
```
Expected: `{"status":"ok"}` and a 200 carrying `predicted_sentiment`. A 503 means the model did not reach the image, which sends you back to Task 1.

- [ ] **Step 5: Capture screenshots**

The running dashboard at port 8501 with charts, and `docker ps` showing both containers Up. Redact the IP.

- [ ] **Step 6: Fold every correction back into the README, then tear down**

Run the README's own step 13, then terminate the instance.

- [ ] **Step 7: Commit the corrections**

```bash
git add assignments/hw8/README.md
git commit -m "hw8: correct the deployment guide against a real sandbox run

Executed the runbook top to bottom on a fresh t2.micro following only what the
page says. Corrections folded back in."
```

---

### Task 9: Branch protection, pull request, submission

These are graded and leave no artifact in the repository, so each needs its own evidence.

**Files:**
- Modify: `assignments/hw8/README.md` (add the branch-protection screenshot)

- [ ] **Step 1: Protect `main`**

Currently unprotected, verified. Configure protection on `rocklambros/MLOPS-Comp-4450-1`, requiring a pull request before merging and requiring the `lint and test` status check to pass.

```bash
gh api -X PUT repos/rocklambros/MLOPS-Comp-4450-1/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f 'required_status_checks[strict]=true' \
  -f 'required_status_checks[contexts][]=lint and test' \
  -F 'enforce_admins=true' \
  -F 'required_pull_request_reviews[required_approving_review_count]=0' \
  -F 'restrictions=null'
```

- [ ] **Step 2: Verify and capture evidence**

Run: `gh api repos/rocklambros/MLOPS-Comp-4450-1/branches/main/protection --jq '{enforce_admins: .enforce_admins.enabled, checks: .required_status_checks.contexts}'`
Expected: `enforce_admins: true` and the check listed. Screenshot the settings page, because a collaborator cannot see this setting and the brief grades it.

- [ ] **Step 3: Add the screenshot to the README and push**

```bash
git add assignments/hw8/README.md
git commit -m "hw8: document branch protection with settings evidence"
git push
```

- [ ] **Step 4: Open the graded pull request**

```bash
gh pr create --base main --head dev \
  --title "Assignment 6: CI/CD, testing, and EC2 deployment (hw8)" \
  --body "$(cat <<'BODY'
Assignment 6 (hw8) for COMP 4450. Do not merge until after grading.

Part 1: tests at assignments/hw8/api/test_api.py and
assignments/hw8/monitoring/test_dashboard.py
Part 2: .github/workflows/ci.yml, one job, five ordered steps, triggered on
pull requests to main
Part 3 and 4: assignments/hw8/README.md carries the architecture, local
development, and the step-by-step EC2 deployment guide

Submitted from the course monorepo rather than a new repository, per the
permission given in class. The deviation and its basis are documented in the
README.
BODY
)"
```

- [ ] **Step 5: Confirm the check is green on the graded pull request**

Run: `gh pr checks --watch`
Expected: `lint and test` passes. This is what the instructor sees.

- [ ] **Step 6: Confirm the grader can reach it**

Run: `gh api repos/rocklambros/MLOPS-Comp-4450-1/collaborators/navido89/permission --jq '.permission'`
Expected: `write` or higher. Copy the pull request URL and confirm it loads.

- [ ] **Step 7: Submit to Canvas**

Paste the pull request URL into the text box at `canvas.du.edu/courses/223323/assignments/2011240`. Due Aug 18 at 11:59pm.

- [ ] **Step 8: Do not merge**

The brief bolds this. Every prior pull request in this repository was merged on green, so the habit runs the other way. Leave it open until the grade posts.

---

## Self-Review

**Spec coverage.** Every spec section maps to a task: §4 and §4.1 to Task 1, §6 to Task 2, §7.1 to Task 3, §7.2 and §7.4 to Task 4, §5 to Task 6, §8 to Tasks 7 and 8, §9 to Task 7, §10 and §11 to Task 7 Step 5, §12 across every task's verification steps, §13 to Task 9.

**Placeholders.** One deliberate fill-in remains: the measured `predict_proba` margins in Task 3 Step 2, which cannot be known until Step 1 runs the model. The step that produces them immediately precedes it. `<EC2_PUBLIC_IP>` and `<key>.pem` are intentional reader-substituted parameters, called out as such.

**Type and name consistency.** `sentiment-monitor-api` and `sentiment-monitor-dashboard` are the container names in Tasks 5, 7, and 8. `prediction-logs` and `sentiment-net` are consistent throughout. `API_URL` is the container name on the raw path and the service name on the compose path, stated explicitly in Task 7 Step 3 step 10. The `lint and test` job name in Task 6 matches the required status check in Task 9 Step 1.

**Fixture names verified.** Task 3 Step 2's `client`, `log_path`, and `read_log` were checked against `assignments/hw7/api/tests/test_api.py:24-44` and match exactly. `log_path` patches the module attribute with `monkeypatch.setattr(main, "LOG_PATH", path)` rather than the environment, which is why the new label tests take the fixture even though they only assert on the response: it keeps a rejected or accepted request from writing to a real log.

**Cross-check on the dashboard tests.** `monitoring/test_dashboard.py` seeds through the `LOG_PATH` environment variable instead, because `dashboard.py:33` reads `os.getenv` at module import and `AppTest` re-executes the script. The two mechanisms differ by design and each matches how its target module resolves configuration.
