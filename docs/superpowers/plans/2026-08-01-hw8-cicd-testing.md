# hw8 (Assignment 6) CI/CD, Testing, and EC2 Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing hw7 sentiment stack in a pytest suite, a GitHub Actions pipeline that gates every pull request to `main`, and a README that a stranger can follow to deploy both containers to a t2.micro EC2 host.

**Architecture:** `assignments/hw8/` holds a self-contained copy of hw7's `api/` and `monitoring/` services. Tests live at the spec's flat paths. One CI job at the repo root runs five ordered steps scoped to `assignments/hw8`. Deployment is manual and documented, never automated from the workflow.

**Tech Stack:** Python 3.13, FastAPI, Streamlit 1.58.0, scikit-learn 1.9.0, pytest 9.1.0, ruff 0.15.17, Docker, GitHub Actions, AWS EC2 t2.micro Ubuntu 22.04 LTS.

**Spec:** `docs/superpowers/specs/2026-08-01-hw8-cicd-testing-design.md`

**Revision:** amended after a six-perspective adversarial premortem on the plan itself (50 findings). Every command below was verified against the real repository.

## Global Constraints

Every task's requirements implicitly include this section.

- **NEVER modify, move, rename, or delete anything under `assignments/hw7/`.** It is graded and merged. Copy out of it with `cp` only. Never `git mv`, never `mv`, never `rm`. After any task that reads from hw7, `git status --porcelain assignments/hw7` must print nothing.
- **Work happens on branch `dev`.** Already created. Never commit to `main`.
- **Never merge the pull request.** The brief bolds "Do not merge it until after grading."
- **All paths are absolute or explicitly `cd`-anchored.** A fresh subagent does not inherit a working directory. Every command block starts by `cd`-ing to a known absolute path. `REPO` below means `/Users/klambros/github_projects/MLOPS-Comp-4450-1`.
- **The virtualenv is `$REPO/assignments/hw8/.venv`**, not `/tmp`. It is covered by the existing `.venv/` ignore rule. Every task that uses it first runs the guard in Task 2 Step 8.
- **Python 3.13** everywhere: CI `setup-python`, both Dockerfiles, every lockfile compile.
- **Ports are fixed:** FastAPI 8000, Streamlit 8501.
- **Spec-literal paths:** `api/test_api.py`, `monitoring/test_dashboard.py`, flat.
- **Spec-literal names:** volume `prediction-logs`, network `sentiment-net`, containers `sentiment-monitor-api` and `sentiment-monitor-dashboard`.
- **Lockfiles compile with** `uv pip compile <in> --generate-hashes --universal --python-version 3.13 -o <out>`. `uv` is installed at 0.8.14. Never hand-edit a `.txt` lockfile.
- **The ambient `ruff` on this machine is 0.6.9 and is the wrong version.** Always invoke `.venv/bin/ruff`, never bare `ruff`.
- **No fabricated evidence.** Every number in the README comes from real command output.
- **No AI attribution** in any commit message, file header, or documentation.
- **Writing style:** no em dashes, no semicolons, no sentence-initial "And", "But", "So", or "Or".

---

## File Structure

| File | Responsibility |
|---|---|
| `.gitignore` (root, modify) | Two negations so hw8's model and CSV are tracked |
| `.github/workflows/ci.yml` (create) | The five-step CI job, repo root because GitHub reads workflows nowhere else |
| `assignments/README.md` (modify) | Status table row for hw8 |
| `assignments/hw8/api/main.py` (copy, lint-fix) | FastAPI service |
| `assignments/hw8/api/test_api.py` (create) | Spec-literal API tests |
| `assignments/hw8/api/conftest.py` (copy) | `sys.path` shim so `import main` resolves |
| `assignments/hw8/api/.dockerignore` (modify) | Exclude the flat test file from build context |
| `assignments/hw8/monitoring/dashboard.py` (copy, lint-fix) | Streamlit dashboard |
| `assignments/hw8/monitoring/test_dashboard.py` (create) | Spec-literal launch tests |
| `assignments/hw8/monitoring/test_reference_stats.py` (copy) | Carried so the suite does not shrink |
| `assignments/hw8/monitoring/.dockerignore` (modify) | Exclude the flat test files |
| `assignments/hw8/evaluate.py` (copy, lint-fix) | Post-deploy scoring |
| `assignments/hw8/requirements.in` (create) | Single source for the root lockfile |
| `assignments/hw8/requirements.txt` (generate) | Spec-literal target of CI step 3 |
| `assignments/hw8/pyproject.toml` (create) | ruff configuration |
| `assignments/hw8/pytest.ini` (create) | `filterwarnings = error` gate |
| `assignments/hw8/Makefile` (adapt) | `test` target pointed at flat paths |
| `assignments/hw8/README.md` (overwrite) | The operational manual |
| `assignments/hw8/docs/` (create) | Screenshots that are evidence for graded settings |

---

### Task 1: Scaffold hw8 and defeat the `.gitignore` trap

The highest-cost failure in this assignment is silent. `git add` skips the model with no error, and the grader's `docker build` dies. This task ends only when the binaries are proven tracked on the pushed remote.

**Files:**
- Create: `assignments/hw8/` (copied from `assignments/hw7/`)
- Modify: `.gitignore` (root)

**Interfaces:**
- Consumes: nothing, this is the first task
- Produces: the `assignments/hw8/` tree every later task edits

- [ ] **Step 1: Copy the hw7 tree, excluding build artifacts**

`rsync` reads hw7 and never writes to it. The trailing slash on the source is required.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
rsync -a --exclude '.venv/' --exclude '__pycache__/' --exclude '.pytest_cache/' \
  --exclude 'IMDB Dataset.csv' \
  assignments/hw7/ assignments/hw8/
```

- [ ] **Step 2: Confirm hw7 is untouched**

Run: `git status --porcelain assignments/hw7`
Expected: no output. Any output means hw7 was modified, which is a stop-everything condition.

- [ ] **Step 3: Remove what hw8 does not need**

`rm` here operates only inside `assignments/hw8`. The nested `tests/` directories are replaced by flat spec-literal files in Tasks 3 and 4. hw7's README and brief are replaced by hw8's own in Task 7.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
rm -rf api/tests monitoring/tests
rm -f week7_Assignment5ModelMonitoring.md hw7.postman_collection.json
rm -f requirements-dev.in requirements-dev.txt
ls -la
```

`README.md` is deliberately left in place. It currently holds hw7's copy, and Task 7 overwrites it wholesale. Do not run `git checkout` on it: the tracked version is the stale "# Homework 4" stub, and restoring it helps nothing.

- [ ] **Step 4: Confirm the trap exists before fixing it**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git check-ignore -v assignments/hw8/api/sentiment_model.pkl assignments/hw8/monitoring/imdb_sample.csv
```
Expected output, proving the problem is real:

```
.gitignore:234:*.pkl	assignments/hw8/api/sentiment_model.pkl
.gitignore:250:*.csv	assignments/hw8/monitoring/imdb_sample.csv
```

- [ ] **Step 5: Add the two negations to the root `.gitignore`**

Append these next to the existing hw7 negations at lines 261 and 289 so the pattern stays discoverable:

```gitignore
# hw8 ships the same two binaries hw7 does: the trained model the API loads at
# import, and the small CSV fallback the monitoring Dockerfile COPYs by name.
# Without these negations `git add` skips both silently and the grader's
# `docker build` fails at COPY.
!assignments/hw8/api/sentiment_model.pkl
!assignments/hw8/monitoring/imdb_sample.csv
```

- [ ] **Step 6: Verify the negations took**

Run: `git check-ignore -v assignments/hw8/api/sentiment_model.pkl assignments/hw8/monitoring/imdb_sample.csv`
Expected: no output, exit status 1.

- [ ] **Step 7: Verify the model is byte-identical to the graded artifact**

```bash
shasum -a 256 assignments/hw8/api/sentiment_model.pkl assignments/hw7/api/sentiment_model.pkl
```
Expected: both print `b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329`.

- [ ] **Step 8: Commit and push**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git add .gitignore assignments/hw8
git commit -m "hw8: scaffold from hw7 and track the model and sample CSV

The root .gitignore swallows *.pkl and *.csv. hw7 works only because of
path-literal negations. hw8 needs its own or the model never reaches the
pull request and the deployment build fails at COPY."
git push -u origin dev
```

- [ ] **Step 9: Verify the binaries reached the remote, and that hw7 is still whole**

```bash
git ls-tree -r origin/dev --name-only | grep -E 'hw8.*(\.pkl|\.csv)'
git ls-tree -r origin/dev --name-only | grep -c 'assignments/hw7/'
```
Expected: both hw8 binaries listed, and the hw7 file count unchanged from `git ls-tree -r main --name-only | grep -c 'assignments/hw7/'`.

---

### Task 2: Dependency and tooling layer, and bring the copied code under lint

CI step 3 installs from a single `requirements.txt` that does not exist yet. It must carry `httpx`, absent from the API lockfile, which FastAPI's `TestClient` imports.

The copied hw7 code has never been linted. Under the rule set below it produces seven errors, so this task fixes them before any later step claims `All checks passed!`.

**Files:**
- Create: `assignments/hw8/requirements.in`, `requirements.txt`, `pyproject.toml`, `pytest.ini`
- Modify (lint fixes, hw8 copies only): `assignments/hw8/api/main.py`, `monitoring/dashboard.py`, `monitoring/test_reference_stats.py`, `evaluate.py`

**Interfaces:**
- Consumes: `api/requirements.in` and `monitoring/requirements.in` from Task 1
- Produces: `requirements.txt` (the CI step 3 target), `.venv/` (used by every later task), and a lint-clean tree

- [ ] **Step 1: Write `assignments/hw8/requirements.in`**

Modeled on hw7's `requirements-dev.in`, which already chains both service `.in` files. `ruff` is the addition.

```
# Root dependency source for hw8. One compile, one lockfile, because CI step 3
# says "Install all project dependencies from requirements.txt" (singular).
#
# Chains both service runtimes so the suite can import `main` (api) and
# `reference_stats` plus `dashboard` (monitoring), then adds test and lint tooling.
# httpx is required by fastapi.testclient.TestClient and is NOT in
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

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
uv pip compile requirements.in --generate-hashes --universal \
  --python-version 3.13 -o requirements.txt
```

- [ ] **Step 3: Verify the lockfile**

```bash
grep -c 'sha256' requirements.txt
grep -E '^(httpx|pytest|ruff|streamlit|scikit-learn)==' requirements.txt
grep -E '^(scikit-learn|numpy|scipy|joblib)==' requirements.txt api/requirements.txt
```
Expected: a large hash count, all five packages present at the pinned versions, and identical model-stack versions between the root and service lockfiles. A mismatch means CI tests a different scikit-learn than the image unpickles with.

- [ ] **Step 4: Write `assignments/hw8/pyproject.toml`**

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

- [ ] **Step 5: Write `assignments/hw8/pytest.ini`**

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

- [ ] **Step 6: Create the virtualenv and install from the lockfile**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.txt
.venv/bin/ruff --version
```
Expected: the install succeeds with no hash errors, and ruff reports `0.15.17`. The ambient ruff on this machine is 0.6.9, which is why every later step calls `.venv/bin/ruff` explicitly.

- [ ] **Step 7: Bring the copied hw7 code under the pinned rule set**

The copied code has never been linted. Auto-fix what is safe, then hand-fix the rest.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
.venv/bin/ruff check . --output-format=concise    # see the full list first
.venv/bin/ruff check . --fix                      # fixes import sorting (I001) and UP017
.venv/bin/ruff check . --output-format=concise    # what remains needs hands
```

Hand-fix the remainder. The known set, verified against the current hw7 sources:

- `evaluate.py`, two `raise` statements inside an `except` block (B904): append `from exc` to each, binding the exception with `as exc` if it is not already bound.
- `api/main.py` (UP038): rewrite `isinstance(value, (list, tuple))` as `isinstance(value, list | tuple)`.
- `api/test_api.py` line 41 is 103 characters (E501, limit 100). It is the `read_log` list comprehension. Wrap it:

```python
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
```

Ruff versions differ on which rules fire. Treat the list from the first command as authoritative rather than this one, and fix whatever it reports.

- [ ] **Step 8: Verify lint is clean and hw7 is still untouched**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
.venv/bin/ruff check .
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git status --porcelain assignments/hw7
```
Expected: `All checks passed!` and no output from the hw7 check. Every lint edit belongs to the hw8 copies only.

This is the venv guard every later task depends on. If `.venv/bin/ruff` is missing when a later task runs, re-run Step 6.

- [ ] **Step 9: Commit**

```bash
git add assignments/hw8
git commit -m "hw8: single hash-compiled lockfile, ruff config, pytest gate

CI step 3 installs from one requirements.txt. httpx is added explicitly because
fastapi.testclient.TestClient imports it and the API lockfile does not carry it.
The ruff rule set is pinned rather than left to defaults, and the copied sources
are brought under it so the pipeline can go green."
```

---

### Task 3: `api/test_api.py` at the spec-literal path

**Files:**
- Create: `assignments/hw8/api/test_api.py`
- Modify: `assignments/hw8/api/.dockerignore`
- Read only: `assignments/hw7/api/tests/test_api.py`

**Interfaces:**
- Consumes: `api/conftest.py` from Task 1, which inserts `api/` on `sys.path` via `Path(__file__).resolve().parent`, so it works unchanged beside a flat test file. The ported file defines fixtures `client` and `log_path` and a helper `read_log`, verified at `assignments/hw7/api/tests/test_api.py:24-44`. `log_path` patches the module attribute with `monkeypatch.setattr(main, "LOG_PATH", path)`.
- Produces: the API half of the suite CI step 5 runs

- [ ] **Step 1: Measure the model's actual margins before writing any assertion**

A fixture that classifies at 0.51 is a flaky red check on a graded pipeline. Measure, then choose.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8/api
../.venv/bin/python -c "
import joblib
m = joblib.load('sentiment_model.pkl')
cases = [
    'An absolute masterpiece, I loved every minute of it.',
    'Beautifully shot with a moving, unforgettable score.',
    'A boring, painful waste of two hours.',
    'The acting was wooden and the plot made no sense at all.',
]
for t in cases:
    p = m.predict([t])[0]
    conf = max(m.predict_proba([t])[0])
    print(f'{conf:.4f}  {p:<9}  {t}')
"
```

Record the output. Pick the highest-confidence sentence that predicts `positive` and the highest-confidence sentence that predicts `negative`. Those two are the fixtures. Substitute them into Step 2 in place of the defaults shown there, and put the measured confidences in the comment.

- [ ] **Step 2: Copy the ported suite, then append the three new tests**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8/api
cp ../../hw7/api/tests/test_api.py test_api.py
```

Read the copied file first and match the fixture names it actually defines. Then append:

```python
# ---------------------------------------------------------------------------
# Assignment 6, Part 1: the brief requires "/predict with both a positive and a
# negative example" and that the endpoint "correctly handles requests with
# missing or malformed data".
#
# hw7's suite above pins the request contract (log keys, echoed response,
# timestamp format) but never asserts the predicted label, which is the gap
# these close.
#
# Fixtures are chosen for margin, not realism. Week 1 material warns that ML
# models are evaluated empirically rather than proven correct, so a borderline
# review would make this a flaky gate. Measured confidence on the shipped model:
# positive <FILL FROM STEP 1>, negative <FILL FROM STEP 1>.
# ---------------------------------------------------------------------------


def test_predict_classifies_a_clearly_positive_review_as_positive(client, log_path):
    """Part 1: the positive example."""
    response = client.post(
        "/predict",
        json={"text": "<HIGHEST-CONFIDENCE POSITIVE FROM STEP 1>"},
    )

    assert response.status_code == 200
    assert response.json()["predicted_sentiment"] == "positive"


def test_predict_classifies_a_clearly_negative_review_as_negative(client, log_path):
    """Part 1: the negative example."""
    response = client.post(
        "/predict",
        json={"text": "<HIGHEST-CONFIDENCE NEGATIVE FROM STEP 1>"},
    )

    assert response.status_code == 200
    assert response.json()["predicted_sentiment"] == "negative"


def test_predict_handles_missing_or_malformed_data(client, log_path):
    """Part 1: named to match the brief's own wording.

    The parametrized 422 cases above cover this in more depth. This test exists so a
    grader reading the file against the checklist finds the bullet's language, and it
    also pins that a rejected request never reaches the log.
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

- [ ] **Step 3: Run the new tests**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
.venv/bin/python -m pytest api/test_api.py -k "clearly_positive or clearly_negative or missing_or_malformed" -v
```
Expected: three pass. A fixture-name error means the copied file uses different names, so read it and adjust.

- [ ] **Step 4: Run the whole file and lint it**

```bash
.venv/bin/python -m pytest api/test_api.py -q
.venv/bin/ruff check api/
```
Expected: all pass with zero warnings, and `All checks passed!`. Record the collected count for the README. If E501 fires on the appended code, wrap the long line rather than raising the limit.

- [ ] **Step 5: Keep the flat test out of the build context**

`api/.dockerignore` excludes `tests/`, which no longer matches. The image uses an explicit COPY allowlist so no test could ship regardless, and this keeps the build context small. Add below the existing `tests/` line:

```
# The flat spec-literal test path Assignment 6 requires.
test_api.py
```

- [ ] **Step 6: Commit**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git add assignments/hw8/api
git commit -m "hw8: API tests at the spec-literal path with label assertions

Ports hw7's request-contract suite to api/test_api.py and adds the positive and
negative label assertions Part 1 names. Fixtures are chosen by measured
predict_proba margin so the gate cannot flake on a graded pipeline."
```

---

### Task 4: `monitoring/test_dashboard.py` at the spec-literal path

The only genuinely net-new test work. Three traps here, all verified against `dashboard.py`:

1. `dashboard.py:162` calls `st.stop()` on an empty log, so a launch assertion against an empty log is vacuously true.
2. `dashboard.py:265` calls `alert_slot.error(...)` whenever accuracy is below `ACCURACY_ALERT_THRESHOLD = 0.80`. Seed data that is less than 80 percent correct makes `assert len(at.error) == 0` fail. The seeded records below are deliberately 100 percent correct, and the alert gets its own dedicated test.
3. `import dashboard` at module scope executes the whole Streamlit script outside a Streamlit runtime. The threshold constant is read by parsing the source instead.

**Files:**
- Create: `assignments/hw8/monitoring/test_dashboard.py`
- Create: `assignments/hw8/monitoring/test_reference_stats.py` (copied, never moved)
- Modify: `assignments/hw8/monitoring/.dockerignore`

**Interfaces:**
- Consumes: `monitoring/conftest.py` from Task 1. `dashboard.py:33` reads `LOG_PATH` and `:36` reads `API_URL` from the environment at module import, which is the seam these tests use.
- Produces: the dashboard-launch evidence Part 1 requires

- [ ] **Step 1: Copy the reference-stats tests. Never move them.**

`assignments/hw7/monitoring/tests/test_reference_stats.py` is tracked and graded. `git mv` would succeed, delete it from hw7, and stage that deletion into the graded pull request.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8/monitoring
cp ../../hw7/monitoring/tests/test_reference_stats.py test_reference_stats.py
test -f test_reference_stats.py || { echo "copy failed"; exit 1; }

cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git status --porcelain assignments/hw7
test -f assignments/hw7/monitoring/tests/test_reference_stats.py || { echo "hw7 DAMAGED"; exit 1; }
```
Expected: no output from `git status`, and the hw7 file still present.

- [ ] **Step 2: Write `assignments/hw8/monitoring/test_dashboard.py`**

```python
"""Launch tests for the Streamlit monitoring dashboard (Assignment 6, Part 1).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>

The brief asks for "at least one simple test for your Streamlit application to
ensure it can launch without errors". One assertion is not enough to mean
anything here, for three reasons found by reading dashboard.py.

1. dashboard.py:162 calls st.stop() when the prediction log is empty, so an
   AppTest run against an empty log stops early and "no exception" is vacuously
   true on a page that rendered almost nothing. Every launch test seeds a log.
2. dashboard.py:265 renders an st.error accuracy alert whenever live accuracy is
   below ACCURACY_ALERT_THRESHOLD. The healthy fixture is therefore 100 percent
   correct, and the alert gets its own test rather than poisoning the launch one.
3. Importing dashboard at module scope would execute the whole Streamlit script
   outside a runtime. The threshold constant is read by parsing the source.

AppTest runs the script in-process and never binds a port, so it cannot prove the
real server starts. The subprocess test covers exactly that and nothing more:
Streamlit answers /_stcore/health before the script finishes, so a healthy probe
proves the process is up, not that dashboard.py rendered.
"""

import ast
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
# DNS before the script continues. A closed local port fails instantly instead.
UNREACHABLE_API = "http://127.0.0.1:1"

# Generous because a cold CI runner imports pandas, matplotlib, and streamlit.
LAUNCH_TIMEOUT = 60


def _write_log(path, records):
    """Write newline-delimited JSON, the format the API appends and the dashboard reads."""
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def _record(text, predicted, true_sentiment, second):
    return {
        "timestamp": f"2026-08-01T12:00:{second:02d}+00:00",
        "request_text": text,
        "predicted_sentiment": predicted,
        "true_sentiment": true_sentiment,
    }


def _all_correct_records():
    """Every prediction correct, so accuracy is 100 percent and no alert fires."""
    return [
        _record("An absolute masterpiece, I loved every minute of it.", "positive", "positive", 0),
        _record("A boring, painful waste of two hours.", "negative", "negative", 1),
        _record("Beautifully shot with a moving, unforgettable score.", "positive", "positive", 2),
    ]


def _mostly_wrong_records():
    """One of three correct, so accuracy is well below the 80 percent threshold."""
    return [
        _record("An absolute masterpiece, I loved every minute of it.", "positive", "positive", 0),
        _record("A boring, painful waste of two hours.", "positive", "negative", 1),
        _record("The acting was wooden and the plot made no sense.", "positive", "negative", 2),
    ]


@pytest.fixture
def healthy_log(tmp_path, monkeypatch):
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _all_correct_records())
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)
    return log


def _run_app():
    at = AppTest.from_file(str(APP), default_timeout=LAUNCH_TIMEOUT)
    at.run()
    return at


def test_dashboard_launches_without_errors(healthy_log):
    """Part 1: the required launch test, run past both st.stop() branches."""
    at = _run_app()

    assert not at.exception, f"dashboard raised: {at.exception}"
    # Rendering proof rather than mere absence of a traceback. The success banner
    # only renders after the log loads, which is past the st.stop() at line 162.
    assert len(at.success) >= 1
    assert len(at.error) == 0


def test_dashboard_renders_the_accuracy_alert_when_accuracy_is_low(tmp_path, monkeypatch):
    """The alert path, which is a graded hw7 behavior and the reason the healthy
    fixture above is 100 percent correct."""
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _mostly_wrong_records())
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = _run_app()

    assert not at.exception
    assert len(at.error) >= 1
    assert "accuracy" in " ".join(str(e.value) for e in at.error).lower()


def test_dashboard_handles_logs_with_no_feedback(tmp_path, monkeypatch):
    """The degraded state a freshly deployed host is in: predictions logged, no
    true_sentiment supplied, so the drift charts render and accuracy has nothing
    to measure."""
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

    at = _run_app()

    assert not at.exception


def test_dashboard_stops_cleanly_when_no_predictions_are_logged(tmp_path, monkeypatch):
    """An empty log is an informational state, not a crash."""
    log = tmp_path / "prediction_logs.json"
    log.write_text("", encoding="utf-8")
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = _run_app()

    assert not at.exception
    assert len(at.info) >= 1


def test_accuracy_alert_threshold_is_the_spec_value():
    """hw7's spec set an 80 percent alert threshold. Pin it so a refactor cannot drift it.

    Read by parsing the source rather than importing: `import dashboard` would execute
    the whole Streamlit script outside a runtime.
    """
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    threshold = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ACCURACY_ALERT_THRESHOLD":
                    threshold = ast.literal_eval(node.value)

    assert threshold == 0.80


def _free_port():
    """Bind port 0 and let the OS choose, so a busy 8501 cannot fail the run."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_streamlit_server_boots_and_serves_health(tmp_path):
    """Boot proof. AppTest never binds a port, so this covers what it cannot.

    Proves only that the Streamlit process starts and serves its health endpoint.
    Streamlit answers /_stcore/health before the script body finishes, so this does
    NOT prove dashboard.py rendered. The AppTest cases above cover that.
    """
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _all_correct_records())
    port = _free_port()

    env = {**os.environ, "LOG_PATH": str(log), "API_URL": UNREACHABLE_API}
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(APP),
            # Without headless, Streamlit blocks on an interactive email prompt and
            # the CI job hangs until its timeout.
            "--server.headless", "true",
            "--server.port", str(port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + LAUNCH_TIMEOUT
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
        pytest.fail(f"streamlit did not serve /_stcore/health within {LAUNCH_TIMEOUT} seconds")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        # Close the pipe explicitly. Leaving it to the garbage collector raises a
        # ResourceWarning, which pytest.ini's filterwarnings=error turns into a failure.
        if proc.stdout is not None:
            proc.stdout.close()
```

- [ ] **Step 3: Run the dashboard tests**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
.venv/bin/python -m pytest monitoring/test_dashboard.py -v
```
Expected: six pass. If an AppTest attribute (`at.success`, `at.error`, `at.info`) does not exist on streamlit 1.58.0, print `dir(at)` and use the real accessor. Do not weaken an assertion to make it pass.

- [ ] **Step 4: Run the whole suite and record the real count**

```bash
.venv/bin/python -m pytest -q
```
Expected: everything passes with zero warnings under `filterwarnings = error`. Write the collected count down. The README cites this number and it must be real.

- [ ] **Step 5: Lint, and confirm hw7 is untouched**

```bash
.venv/bin/ruff check .
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1 && git status --porcelain assignments/hw7
```
Expected: `All checks passed!` and no hw7 output.

- [ ] **Step 6: Keep the flat tests out of the build context**

Append to `assignments/hw8/monitoring/.dockerignore`, below the existing `tests/` line:

```
# The flat spec-literal test paths Assignment 6 requires.
test_dashboard.py
test_reference_stats.py
```

- [ ] **Step 7: Commit**

```bash
git add assignments/hw8/monitoring
git commit -m "hw8: dashboard launch tests at the spec-literal path

dashboard.py calls st.stop() on an empty log, so a bare launch assertion is
vacuously true. Every case seeds a log first. The healthy fixture is 100 percent
correct because dashboard.py renders an st.error accuracy alert below the 80
percent threshold, and the alert gets its own test. The threshold constant is
read by parsing the source, since importing the module would execute the whole
Streamlit script outside a runtime."
```

---

### Task 5: Local orchestration and stack verification

**Files:**
- Modify: `assignments/hw8/Makefile`

**Interfaces:**
- Consumes: the test files from Tasks 3 and 4
- Produces: `make test`, `make run`, `make seed`, `make clean` working from `assignments/hw8`

- [ ] **Step 1: Fix the `test` target**

hw7's target reads `$(PYTHON) -m pytest api/tests monitoring/tests -q`. Both directories are gone. Replace with:

```makefile
# Unit and API checks for both services. Install deps first:
#   python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.txt
test:
	$(PYTHON) -m pytest -q
```

Also change the `PYTHON ?= python3` default to `PYTHON ?= .venv/bin/python` so the target uses the pinned toolchain by default, and update the stale `evaluate` comment from "50-row" to "174-record".

- [ ] **Step 2: Verify the Makefile**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1/assignments/hw8
make test
```
Expected: the same pass count Task 4 Step 4 recorded.

- [ ] **Step 3: Free the fixed Docker names before building**

hw7's compose file uses the same container, volume, and network names hw8 does. If an hw7 stack is running, the hw8 run collides.

```bash
docker rm -f sentiment-monitor-api sentiment-monitor-dashboard 2>/dev/null || true
docker network rm sentiment-net 2>/dev/null || true
docker ps -a --filter name=sentiment-monitor
```
Expected: no sentiment-monitor containers listed.

- [ ] **Step 4: Build both images**

```bash
make build
```
Expected: both build. A failure at `COPY ... sentiment_model.pkl` means Task 1 Step 6 was skipped.

- [ ] **Step 5: Run the stack, seed it, and verify `/predict`**

```bash
make run
sleep 15
make seed
curl -fsS http://localhost:8000/health
curl -fsS -X POST http://localhost:8000/predict -H 'Content-Type: application/json' \
  -d '{"text":"An absolute masterpiece, I loved every minute of it.","true_sentiment":"positive"}'
```
Expected: `{"status":"ok"}` and a 200 carrying `predicted_sentiment`. A 503 means the model is not in the image.

- [ ] **Step 6: Capture the dashboard screenshot**

Open `http://localhost:8501`. Expected: the success banner and the charts, not "No predictions logged yet". Save the screenshot to `assignments/hw8/docs/dashboard-local.png`. Create the directory first:

```bash
mkdir -p assignments/hw8/docs
```

- [ ] **Step 7: Tear down**

```bash
make clean
```
Expected: containers, volume, network, and both images removed. Task 8 reuses the same fixed names.

- [ ] **Step 8: Commit**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git add assignments/hw8/Makefile assignments/hw8/docs
git commit -m "hw8: point make test at the flat spec-literal paths

hw7's target named api/tests and monitoring/tests, which the flat layout
removes. Defaults PYTHON at the pinned venv and corrects the evaluate comment:
test.json holds 174 records, not 50."
```

---

### Task 6: The CI workflow

**Files:**
- Create: `.github/workflows/ci.yml` (repo root)

**Interfaces:**
- Consumes: `assignments/hw8/requirements.txt` from Task 2, the suites from Tasks 3 and 4
- Produces: the green check the brief requires the pull request to display. The job's `name` is `lint and test`, which is the status-check context Task 9 requires.

- [ ] **Step 1: Create the directory and write the workflow**

The directory does not exist anywhere in this repository yet.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
mkdir -p .github/workflows
```

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
      # change what runs. persist-credentials: false keeps the job token out of the
      # runner's .git/config, since no step needs to push.
      - name: Check out the repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
        with:
          persist-credentials: false

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

- [ ] **Step 2: Confirm the five steps are in the brief's order**

PyYAML is not installed on this machine, so a local parse is not available. Verify the ordering by inspection, and let Step 5's real run be the parse test.

```bash
grep -n '      - name:' .github/workflows/ci.yml
```
Expected, in this order: Check out the repository, Set up Python 3.13, Install dependencies, Lint with ruff, Run the test suite.

- [ ] **Step 3: Commit and push**

```bash
git add .github/workflows/ci.yml
git commit -m "hw8: CI workflow, one job with the five ordered steps

Triggers on every pull request to main with no paths filter, so the check is
always visible on the graded pull request. Scoped to assignments/hw8 so pytest's
rootdir keeps hw8's filterwarnings=error gate. Actions pinned to SHAs."
git push
```

- [ ] **Step 4: Prove the workflow is green BEFORE the graded pull request exists**

This prevents discovering a red pipeline on the artifact the instructor is looking at.

```bash
git checkout -b ci-smoke-test
git commit --allow-empty -m "chore: trigger a CI validation run"
git push -u origin ci-smoke-test
gh pr create --base main --head ci-smoke-test --title "CI validation, do not merge" \
  --body "Throwaway pull request to prove the workflow runs green. Closing immediately."
gh pr checks ci-smoke-test --watch
```
Expected: `lint and test` passes. If it fails, fix on this branch and cherry-pick or re-apply to `dev`. Do not proceed until it is green.

- [ ] **Step 5: Return to `dev` first, then close the throwaway**

Order matters. Deleting the branch you are standing on leaves the repository in a detached state.

```bash
git checkout dev
git cherry-pick ..ci-smoke-test 2>/dev/null || true   # only if fixes were made on the smoke branch
gh pr close ci-smoke-test --delete-branch
git branch --show-current
```
Expected: `dev`. If fixes were made on `ci-smoke-test`, make sure they reached `dev` before closing, and re-push.

---

### Task 7: The README operational manual

Part 4 calls this "the final, most critical piece". The instructor grades Part 3 by executing it, so a command that errors is the most legible deduction available.

**Files:**
- Overwrite: `assignments/hw8/README.md` (currently holds hw7's copy from Task 1)
- Modify: `assignments/README.md` (status table row)

**Interfaces:**
- Consumes: real output from every prior task
- Produces: the Part 4 deliverable and the Part 3 procedure

- [ ] **Step 1: Write the architecture section**

Extend hw7's Mermaid diagram (`assignments/hw7/README.md:77-94`) with the two additions Part 4 item 1 names: the CI pipeline and the EC2 host boundary. Cover all four required elements: the FastAPI service, the Streamlit dashboard, the CI/CD pipeline, and the deployment on EC2.

Use the course's own five-stage vocabulary from `resources/wk8/week8_Introduction.md`: Source and Commit, Build, Test, Deploy, Monitor and Feedback. State that hw8 automates Test and documents Deploy manually. Do not write "continuous deployment", which the course defines as running "without any human intervention" and which Part 3 contradicts on the same page.

- [ ] **Step 2: Write the local development section**

Both paths: the `make` targets, then the raw `docker` equivalents for a grader who skips `make`. Include the teardown between them, because both paths use the same fixed names and the second fails on a collision without it.

- [ ] **Step 3: Write the EC2 deployment guide**

Written for a reader who just downloaded a fresh key pair and has nothing else. A single `APP_DIR` variable resolves the two transfer paths to one location, so every later step works regardless of which path was taken.

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

6. Get the code onto the host. Pick ONE path, then set APP_DIR to match.

   Path A, scp. No credential ever lands on the box. Run this on your laptop:
   ```bash
   scp -i <key>.pem -r assignments/hw8 ubuntu@<EC2_PUBLIC_IP>:/home/ubuntu/hw8
   ```
   Then on the instance:
   ```bash
   export APP_DIR=/home/ubuntu/hw8
   ```

   Path B, clone. This is what Part 3's "Clone your GitHub repository onto the EC2
   instance" describes. `-b dev` is required: the pull request stays unmerged for
   grading, so `main` carries no hw8 code. The repository is private, so this prompts
   for a GitHub username and a personal access token as the password.
   ```bash
   git clone -b dev https://github.com/rocklambros/MLOPS-Comp-4450-1.git
   export APP_DIR=/home/ubuntu/MLOPS-Comp-4450-1/assignments/hw8
   ```
   If you use Path B, revoke the token when finished. A token typed on a shared
   sandbox host outlives the instance.

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
   cd "$APP_DIR"
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

11. Seed the log so the dashboard has data. Without this the grader opens port 8501 and
    sees "No predictions logged yet" and nothing else.
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
    curl -fsS -X POST http://<EC2_PUBLIC_IP>:8000/predict \
      -H 'Content-Type: application/json' \
      -d '{"text": "A boring, painful waste of two hours.", "true_sentiment": "negative"}'
    ```
    Expected: `{"status":"ok"}` from the second, and a 200 carrying `predicted_sentiment`
    from the third. Then open `http://<EC2_PUBLIC_IP>:8501` and confirm the charts render.

    Optional fuller check, scoring the API over the 174-record labeled set:
    ```bash
    sudo apt-get install -y python3-pip && pip3 install requests
    python3 evaluate.py --api-url http://<EC2_PUBLIC_IP>:8000
    ```

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

Use hw7's format from `assignments/hw7/README.md:50-75`. One row per brief requirement with the file and the verification command. No row claims more than its command proves. The subprocess dashboard test proves the server boots, not that the page rendered, and the table says so.

- [ ] **Step 5: Write the deviations and limitations sections**

Deviations: monorepo rather than a new repository and private rather than public, granted verbally in class; Python 3.13; ruff over flake8; the workflow at the repository root; CI without CD; pinned action SHAs; 413 and 503 beyond the taught status vocabulary.

Limitations, stated accurately. Inbound: anyone can post to `/predict`, bounded only by the 1 MiB body cap and the 20,000-character text cap. Outbound: port 8501 serves an unauthenticated read of the monitoring surface. Scope it correctly. `dashboard.py:328` renders `["timestamp", "predicted_sentiment", "true_sentiment", "length"]`, so the review text is **not** displayed. What leaks is volume, timing, label mix, and per-request length. Do not claim `request_text` is exposed.

Note that this contradicts week 3's guidance that HTTPS is "essential for protecting data in transit" and is the configuration the brief specifies.

State what is deliberately absent so it reads as scoping: no S3, DynamoDB, or IAM instance profile, because the brief says only "Clone your GitHub repository" and the model ships in the repository.

- [ ] **Step 6: Redact and verify**

```bash
grep -nE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' assignments/hw8/README.md
```
Expected: only `127.0.0.1`, `0.0.0.0`, and version numbers. No EC2 address, no token.

- [ ] **Step 7: Verify every claimed number is real**

Cross-check the test count against Task 4 Step 4's recorded output. If the README cites an accuracy figure, it must come from a real `evaluate.py` run performed in Task 5 or Task 8, not from hw7's README. An unverified number violates the Honor Code's fabrication clause.

- [ ] **Step 8: Update the assignments index**

`assignments/README.md:16` currently reads `| [`hw8`](hw8/) | 8 | 6 | CI/CD and testing | spec only |`. Change the status to reflect the built state.

- [ ] **Step 9: Commit**

```bash
git add assignments/hw8/README.md assignments/README.md
git commit -m "hw8: operational manual covering architecture, local dev, and EC2 deploy

The instructor grades Part 3 by replicating the written procedure rather than
inspecting the instance, so every command is copy-pasteable from a fresh box:
chmod 400, the docker group reload, an APP_DIR that resolves both transfer
paths, the shared network the brief omits, the container-name API_URL, the seed
step, a /predict verification, and teardown."
```

---

### Task 8: Sandbox validation of the deployment guide

The guide is the graded artifact. Executing it once is the only way to know it works. This task needs a human to launch the AWS Academy sandbox.

**Files:** `assignments/hw8/README.md` (corrections), `assignments/hw8/docs/` (screenshots)

- [ ] **Step 1: Launch a sandbox instance following only the README**

Follow the written steps literally. Do not use knowledge that is not on the page. Every place you reach for something the README did not say is a defect in the README.

- [ ] **Step 2: Record every deviation**

Keep a running list of every command that failed, every missing prerequisite, every ambiguous instruction.

- [ ] **Step 3: Watch the resource ceiling**

Between the two builds run `df -h` and `free -m`. t2.micro is 1 vCPU, 1 GB RAM, and an 8 GB root volume holding two images plus build cache. If the build or the running stack exhausts memory, add the swap step to the README as a numbered step:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
```

- [ ] **Step 4: Verify the deployed stack end to end**

Run the README's own step 12 verbatim. Expected: `{"status":"ok"}` and a 200 with `predicted_sentiment`. A 503 means the model did not reach the image, which sends you back to Task 1.

- [ ] **Step 5: Capture screenshots**

Save to `assignments/hw8/docs/`: `ec2-dashboard.png` (the running dashboard on 8501) and `ec2-docker-ps.png` (both containers Up). Redact the IP in both.

- [ ] **Step 6: Fold every correction back into the README, then tear down**

Run the README's step 13, then terminate the instance.

- [ ] **Step 7: Commit, staging the screenshots explicitly**

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
git add assignments/hw8/README.md assignments/hw8/docs/
git status --short assignments/hw8/docs/    # confirm the images are staged, not ignored
git commit -m "hw8: correct the deployment guide against a real sandbox run

Executed the runbook top to bottom on a fresh t2.micro following only what the
page says. Corrections folded back in, with screenshots as evidence."
```

If `git status` shows the images unstaged, an ignore rule is catching them. Add a negation the same way Task 1 did for the binaries.

---

### Task 9: Branch protection, pull request, submission

These are graded and leave no artifact in the repository, so each needs its own evidence.

- [ ] **Step 1: Protect `main`**

`gh api -f` sends every value as a JSON string, and this endpoint requires real booleans and nested objects, so a `-f`-built call returns 422. Use a JSON body on stdin.

`enforce_admins` is set to `false` deliberately. With `true`, plus a required status check that has never run on `main`, the repository owner cannot merge or push to `main` at all, which is an unnecessary lockout on a solo repository. The brief asks that `main` be protected, which requiring a pull request accomplishes.

```bash
cd /Users/klambros/github_projects/MLOPS-Comp-4450-1
cat > /tmp/hw8-protection.json <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint and test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "restrictions": null
}
JSON
gh api -X PUT repos/rocklambros/MLOPS-Comp-4450-1/branches/main/protection \
  -H "Accept: application/vnd.github+json" --input /tmp/hw8-protection.json
rm -f /tmp/hw8-protection.json
```

- [ ] **Step 2: Verify and capture evidence**

```bash
gh api repos/rocklambros/MLOPS-Comp-4450-1/branches/main/protection \
  --jq '{checks: .required_status_checks.contexts, prs: .required_pull_request_reviews != null}'
```
Expected: `lint and test` listed and `prs: true`. Screenshot the settings page to `assignments/hw8/docs/branch-protection.png`, because a collaborator cannot see this setting and the brief grades it.

To undo if it ever blocks you: `gh api -X DELETE repos/rocklambros/MLOPS-Comp-4450-1/branches/main/protection`.

- [ ] **Step 3: Add the screenshot and push**

```bash
git add assignments/hw8/README.md assignments/hw8/docs/branch-protection.png
git status --short assignments/hw8/docs/
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

```bash
gh pr checks --watch
```
Expected: `lint and test` passes. This is what the instructor sees.

- [ ] **Step 6: Confirm the grader can reach it, and that hw7 survived**

```bash
gh api repos/rocklambros/MLOPS-Comp-4450-1/collaborators/navido89/permission --jq '.permission'
gh pr diff --name-only | grep '^assignments/hw7/' && echo ">>> STOP: the PR touches hw7" || echo "hw7 untouched"
gh pr view --json url --jq '.url'
```
Expected: `write` or higher, `hw7 untouched`, and a URL that loads.

- [ ] **Step 7: Submit to Canvas**

Paste the pull request URL into the text box at `canvas.du.edu/courses/223323/assignments/2011240`. Due Aug 18 at 11:59pm.

- [ ] **Step 8: Do not merge**

The brief bolds this. Every prior pull request in this repository was merged on green, so the habit runs the other way. Branch protection requires a pull request but does not prevent you from merging your own, so this is a discipline gate, not a technical one. Leave it open until the grade posts.

---

## Self-Review

**Spec coverage.** Spec §4 and §4.1 to Task 1. §6 to Task 2. §7.1 to Task 3. §7.2 and §7.4 to Task 4. §7.3 to Task 3 Step 5 and Task 4 Step 6. §5 to Task 6. §8 to Tasks 7 and 8. §9 to Task 7. §10 and §11 to Task 7 Step 5. §12 across every task's verification steps, including the fresh-clone and Linux-install rows now covered by Task 6 Step 4's real CI run on `ubuntu-latest` from a clean checkout. §13 to Task 9.

**Premortem fixes applied.** `git mv` replaced with `cp` plus an hw7-integrity assertion, and a global constraint forbidding any write under hw7. A lint-fix step added before any `All checks passed!` expectation. The dashboard launch fixture made 100 percent accurate so it cannot trip the `st.error` accuracy alert, with the alert given its own test. `import dashboard` replaced with `ast` parsing. `proc.stdout` closed explicitly. Branch protection switched to a JSON body with `enforce_admins: false`. The PyYAML parse removed. `APP_DIR` introduced so the runbook works on both transfer paths. Screenshots given a directory and staged explicitly. The venv moved into the repo and given a guard. `.github/workflows/` creation made explicit. Branch checkout ordered before deletion. `assignments/README.md` and both `.dockerignore` files added. The false `request_text` claim corrected.

**Placeholders.** Two deliberate fill-ins, each immediately preceded by the step that produces the value: the measured margins and chosen fixtures in Task 3 Step 2, and the recorded test count cited in Task 7. `<EC2_PUBLIC_IP>` and `<key>.pem` are reader-substituted parameters.

**Name consistency.** `sentiment-monitor-api` and `sentiment-monitor-dashboard` across Tasks 5, 7, and 8. `prediction-logs` and `sentiment-net` throughout. The job `name: lint and test` in Task 6 matches the required status-check context in Task 9 Step 1. `.venv/bin/` used in every Python and ruff invocation after Task 2 Step 6.
