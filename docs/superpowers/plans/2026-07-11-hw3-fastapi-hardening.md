# hw3 FastAPI Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `assignments/hw3` to full spec compliance and close every residual risk from two adversarial premortems, using verified-safe implementations.

**Architecture:** A single-module FastAPI app (`main.py`) serving four endpoints. Changes are surgical: switch `/example` to the committed full IMDB dataset, add a validation-error sanitizer and a body-size ASGI middleware, harden packaging (hash-pinned deps, digest-pinned base), and update docs. No framework or structural change.

**Tech Stack:** Python 3.13, FastAPI 0.137.1, scikit-learn 1.9.0, Docker, pytest, uv (for hash generation).

## Global Constraints

- Work only inside `assignments/hw3/` (plus the two `.gitignore` files and the repo-root as noted). No changes to hw1/hw2. Self-containment is a spec requirement.
- All dependency versions stay exactly as currently pinned; hashing must not change any version.
- Base image: `python:3.13-slim@sha256:eb43ff125d8d58d7449dcba7d336c23bcac412f526d861db493b9994d8010280` (multi-arch index digest).
- Dataset filename is verbatim `IMDB Dataset.csv` (with the space), per the spec structure diagram.
- Run all commands from `assignments/hw3/` unless stated. The pinned venv is at `assignments/hw3/.venv`.
- Attribution: git author/committer stay the human; no AI attribution anywhere.

## File Structure

- `main.py` — data source, `/example` HTML cleanup, NaN handler, body-size middleware (Tasks 2-4)
- `tests/test_api.py` — new tests alongside the existing 11 (Tasks 2-4)
- `IMDB Dataset.csv` — the committed 63.1 MiB dataset (Task 1)
- `assignments/hw3/.gitignore`, repo-root `.gitignore` — D1 fix (Task 1)
- `requirements.in`, `requirements.txt`, `requirements-dev.in`, `requirements-dev.txt` — hashed closures (Task 5)
- `Dockerfile`, `.dockerignore`, `pytest.ini` — packaging + config (Task 5)
- `README.md`, `hw3.postman_collection.json` — docs + grader ergonomics (Task 6)
- Deleted: `examples.csv`, `make_examples.py` (Task 2)

---

### Task 1: Commit the full dataset (premortem D1 — the invisible-failure fix)

**Files:**
- Create: `assignments/hw3/IMDB Dataset.csv` (copied from hw1)
- Modify: `assignments/hw3/.gitignore` (line 16), repo-root `.gitignore` (remove the examples.csv re-include)

**Interfaces:**
- Produces: a git-tracked `IMDB Dataset.csv` next to `main.py`, which Task 2's `/example` and Task 5's Dockerfile depend on.

This task has no unit test; its verification is git state. The failure mode it closes is silent, so the verification is mandatory, not optional.

- [ ] **Step 1: Copy the dataset into hw3**

Run (from repo root):
```bash
cp "assignments/hw1/IMDB Dataset.csv" "assignments/hw3/IMDB Dataset.csv"
ls -l "assignments/hw3/IMDB Dataset.csv"
```
Expected: a 66,212,309-byte file listed.

- [ ] **Step 2: Confirm it is currently ignored (proves the bug is real)**

Run (from repo root):
```bash
git check-ignore -v "assignments/hw3/IMDB Dataset.csv"
```
Expected: prints `assignments/hw3/.gitignore:16:IMDB Dataset.csv	assignments/hw3/IMDB Dataset.csv` (the deeper file is the blocker).

- [ ] **Step 3: Negate the ignore in the hw3-local .gitignore**

In `assignments/hw3/.gitignore`, replace line 16 `IMDB Dataset.csv` with `!IMDB Dataset.csv`, and update the comment on lines 14-15 to:
```
# The full IMDB dataset ships with this assignment so /example serves a real
# training review and the folder is self-contained. Re-included past the root *.csv rule.
!IMDB Dataset.csv
```

- [ ] **Step 4: Remove the obsolete examples.csv re-include from the repo-root .gitignore**

In the repo-root `.gitignore`, delete the line `!assignments/hw3/examples.csv` (the sample is being removed). Leave the rest untouched.

- [ ] **Step 5: Verify it is no longer ignored**

Run (from repo root):
```bash
git check-ignore -v "assignments/hw3/IMDB Dataset.csv"; echo "exit=$?"
```
Expected: no path line printed, `exit=1` (not ignored).

- [ ] **Step 6: Stage explicitly so a still-ignored state errors loudly**

Run (from repo root):
```bash
git add "assignments/hw3/IMDB Dataset.csv" "assignments/hw3/.gitignore" ".gitignore"
git status --short | grep "IMDB Dataset.csv"
```
Expected: `A  assignments/hw3/IMDB Dataset.csv` appears. If `git add` prints "The following paths are ignored", STOP — Step 3 was not applied correctly.

- [ ] **Step 7: Commit**

Run (from repo root):
```bash
git commit -m "hw3: commit full IMDB Dataset.csv so /example serves a real training review"
```

---

### Task 2: Switch /example to the full dataset and strip HTML (premortem M7, F8)

**Files:**
- Modify: `assignments/hw3/main.py`
- Modify: `assignments/hw3/tests/test_api.py`
- Delete: `assignments/hw3/examples.csv`, `assignments/hw3/make_examples.py`

**Interfaces:**
- Consumes: the committed `IMDB Dataset.csv` from Task 1.
- Produces: `/example` returns `{"review": "..."}` with `<br>` tags replaced by spaces, sourced from the full dataset. `resolve_example_source()` no longer references a sample.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py`:
```python
def test_example_review_has_no_br_tags():
    # /example must serve a clean review; <br> markup is stripped to spaces.
    for _ in range(25):  # sample several random draws
        review = client.get("/example").json()["review"]
        assert "<br" not in review
        assert review == review.strip()


def test_example_loads_from_full_dataset():
    # After the switch, the loaded corpus is the full dataset, not a 200-row sample.
    assert len(main.EXAMPLE_REVIEWS) > 1000
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_api.py::test_example_review_has_no_br_tags tests/test_api.py::test_example_loads_from_full_dataset -v`
Expected: FAIL (`<br` present, and/or fewer than 1000 reviews from the sample).

- [ ] **Step 3: Update main.py data source and add HTML stripping**

In `main.py`:

a) Add `import re` near the top imports, and after the imports add:
```python
# /example returns raw dataset reviews, which carry literal <br /> HTML line breaks.
# Strip them to spaces so the endpoint returns readable text. The model never sees
# /example output, so this display cleanup has no effect on predictions.
_BR_TAG = re.compile(r"<br\s*/?>", re.IGNORECASE)
```

b) Remove the sample fallback tier. Delete the `SAMPLE_PATH = HERE / "examples.csv"` line and change `resolve_example_source()` to:
```python
def resolve_example_source() -> Path | None:
    """Pick the CSV that /example draws from: env override, then the full dataset."""
    override = os.getenv("EXAMPLE_DATA_PATH")
    if override:
        path = Path(override)
        return path if path.exists() else None
    if FULL_DATASET_PATH.exists():
        return FULL_DATASET_PATH
    return None
```

c) Raise the CSV field-size limit so a future longer review cannot raise `_csv.Error` (today's max is 13,704 chars). At the top of `load_reviews`, before opening the file:
```python
    csv.field_size_limit(10 * 1024 * 1024)
```

d) In the `example()` endpoint, strip tags before returning:
```python
@app.get("/example", response_model=ExampleResponse)
def example() -> ExampleResponse:
    """Return a random review from the IMDB dataset, HTML-stripped, for testing the predictors."""
    if not EXAMPLE_REVIEWS:
        raise HTTPException(status_code=503, detail="no example reviews available")
    review = _BR_TAG.sub(" ", random.choice(EXAMPLE_REVIEWS)).strip()
    return ExampleResponse(review=review)
```

e) Update the module docstring and the `FULL_DATASET_PATH`/`SAMPLE_PATH` comment block (lines ~13, ~43-50) to describe the full dataset as the source and drop all "sample" wording.

- [ ] **Step 4: Delete the sample files**

Run:
```bash
git rm examples.csv make_examples.py
```

- [ ] **Step 5: Run the tests**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass (existing 11 plus the 2 new). `test_bad_example_source_degrades_instead_of_crashing` still passes (env-override path unchanged).

- [ ] **Step 6: Commit**

Run:
```bash
git add main.py tests/test_api.py
git commit -m "hw3: serve /example from the full dataset, strip <br> tags, drop the sample"
```

---

### Task 3: NaN/Infinity validation handler (premortem M4, F5)

**Files:**
- Modify: `assignments/hw3/main.py`
- Modify: `assignments/hw3/tests/test_api.py`

**Interfaces:**
- Consumes: the `app` object from `main.py`.
- Produces: a `RequestValidationError` handler that returns a clean 422 for every malformed body, including non-finite-float inputs.

The tests MUST use raw bytes: `client.post("/predict", json={"text": float("nan")})` raises inside httpx before the request is sent, so it would error instead of testing the server.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py`:
```python
import pytest


@pytest.mark.parametrize("literal", [b"NaN", b"Infinity", b"-Infinity", b"1e400"])
def test_predict_rejects_nonfinite_numbers_with_422_not_500(literal):
    # These JSON literals parse to nan/inf server-side; the response must be a clean 422.
    body = b'{"text": ' + literal + b"}"
    response = client.post("/predict", content=body, headers={"content-type": "application/json"})
    assert response.status_code == 422


def test_normal_validation_errors_still_return_422_detail():
    # The custom handler must not regress ordinary validation failures.
    for bad in ({}, {"text": "   "}, {"text": "ok", "junk": "x"}):
        response = client.post("/predict", json=bad)
        assert response.status_code == 422
        assert isinstance(response.json()["detail"], list)
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_api.py -k "nonfinite or normal_validation" -v`
Expected: the non-finite tests FAIL with 500 (the current behavior); the normal test may pass.

- [ ] **Step 3: Add the handler to main.py**

Add imports near the top:
```python
import math

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
```

After `app = FastAPI(...)` is defined, add:
```python
def _json_safe(value):
    """Recursively coerce non-JSON-compliant floats (nan, inf, -inf) to strings.

    FastAPI's default validation handler echoes the offending input back in the
    error detail. A body like {"text": NaN} is accepted by the stdlib JSON parser,
    so the echoed input is a non-finite float; Starlette then renders the 422 with
    allow_nan=False and raises, turning the 422 into a 500. Coercing here keeps it 422.
    """
    if isinstance(value, float):
        return str(value) if (math.isnan(value) or math.isinf(value)) else value
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    # jsonable_encoder flattens non-serializable ctx objects (e.g. the ValueError a
    # custom validator raises); _json_safe then neutralizes any non-finite float the
    # encoder leaves as-is. Both are required: the encoder alone 500s on NaN, and
    # float-coercion alone 500s on the blank-text ctx error.
    return JSONResponse(
        status_code=422,
        content={"detail": _json_safe(jsonable_encoder(exc.errors()))},
    )
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass, including the four non-finite cases and the normal-validation case.

- [ ] **Step 5: Commit**

Run:
```bash
git add main.py tests/test_api.py
git commit -m "hw3: return 422 (not 500) for non-finite-float request bodies"
```

---

### Task 4: Body-size limit middleware (premortem M3, F6)

**Files:**
- Modify: `assignments/hw3/main.py`
- Modify: `assignments/hw3/tests/test_api.py`

**Interfaces:**
- Consumes: the `app` object.
- Produces: raw request bodies over 1 MiB rejected with 413; body-less GET requests unaffected.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py`:
```python
def test_get_endpoints_unaffected_by_body_middleware():
    # The middleware must be a no-op for body-less GET (regression guard).
    assert client.get("/health").status_code == 200
    assert client.get("/example").status_code == 200


def test_oversized_declared_body_rejected_413():
    body = b'{"text": "' + b"a" * (1024 * 1024 + 100) + b'"}'
    response = client.post("/predict", content=body, headers={"content-type": "application/json"})
    assert response.status_code == 413


def test_oversized_chunked_body_rejected():
    # No Content-Length (streamed) must still be bounded by counting bytes.
    def gen():
        for _ in range(24):
            yield b"a" * (100 * 1024)  # ~2.4 MiB total
    response = client.post("/predict", content=gen(), headers={"content-type": "application/json"})
    assert response.status_code == 413
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_api.py -k "body_middleware or oversized" -v`
Expected: the oversized tests FAIL (currently return 200 or 422, not 413).

- [ ] **Step 3: Add the middleware to main.py**

Add near the top-level constants:
```python
MAX_BODY_BYTES = 1024 * 1024  # 1 MiB ceiling on the raw request body.
```

Add the middleware class (before `app` is created, or after — it is registered below):
```python
class _BodyTooLarge(Exception):
    """Raised inside the receive wrapper when the streamed body exceeds the ceiling."""


class BodySizeLimitMiddleware:
    """Pure-ASGI middleware bounding the raw request body to max_body_bytes.

    Pydantic's max_length caps model work, but the full body is buffered before
    validation runs, so an unbounded body is a memory-amplification vector. This
    bounds actual bytes read: it rejects a declared-oversize Content-Length up front,
    and counts streamed bytes so a chunked body (no Content-Length) cannot slip past.
    Body-less requests (GET /health, /example) stream no bytes and pass through.
    """

    def __init__(self, app, max_body_bytes: int = MAX_BODY_BYTES):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    if int(value) > self.max_body_bytes:
                        await self._reject(send)
                        return
                except ValueError:
                    pass  # Unparseable header: fall through to byte counting.
                break
        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    raise _BodyTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await self._reject(send)

    async def _reject(self, send):
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({"type": "http.response.body", "body": b'{"detail":"request body too large"}'})
```

After `app = FastAPI(...)`, register it:
```python
app.add_middleware(BodySizeLimitMiddleware)
```

Correct the `MAX_TEXT_LENGTH` comment (lines ~34-37) to state accurately: the field cap bounds model work at validation, and `BodySizeLimitMiddleware` bounds the raw bytes buffered.

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass. If the chunked test errors instead of returning 413, the mid-stream reject needs the `_BodyTooLarge` path to fire before the app sends a response; confirm the app reads the body during validation (it does for a Pydantic body).

- [ ] **Step 5: Commit**

Run:
```bash
git add main.py tests/test_api.py
git commit -m "hw3: bound raw request body to 1 MiB (413), safe for body-less GET"
```

---

### Task 5: Reproducible packaging — hashed deps, digest base, config (premortem M5, M6, M8, D2)

**Files:**
- Create: `requirements.in`, `requirements-dev.in`
- Modify: `requirements.txt`, `requirements-dev.txt` (regenerated with hashes), `Dockerfile`, `.dockerignore`, `pytest.ini`

**Interfaces:**
- Produces: a `docker build` that installs with `--require-hashes` from a digest-pinned base and copies the space-named dataset.

- [ ] **Step 1: Capture the human-readable pins as .in files**

Create `requirements.in` with the current 19 runtime pins (copy the package lines from the existing `requirements.txt`, dropping its comment header):
```
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.14.0
click==8.4.1
fastapi==0.137.1
h11==0.16.0
idna==3.18
joblib==1.5.3
narwhals==2.22.1
numpy==2.4.6
pydantic==2.13.4
pydantic_core==2.46.4
scikit-learn==1.9.0
scipy==1.17.1
starlette==1.3.1
threadpoolctl==3.6.0
typing-inspection==0.4.2
typing_extensions==4.15.0
uvicorn==0.49.0
```
Create `requirements-dev.in`:
```
-r requirements.in
pytest==9.1.0
httpx==0.28.1
ruff==0.15.17
```

- [ ] **Step 2: Generate hashed, multi-arch closures with uv**

Run:
```bash
uv pip compile requirements.in --generate-hashes --universal --python-version 3.13 -o requirements.txt
uv pip compile requirements-dev.in --generate-hashes --universal --python-version 3.13 -o requirements-dev.txt
```
Expected: `requirements.txt` grows to ~395 lines, `requirements-dev.txt` ~454 lines, each pin followed by `--hash=sha256:...` lines. If `uv` is unavailable, `pip install pip-tools==7.* && pip-compile --generate-hashes --allow-unsafe` is the fallback.

Prepend a header comment to both generated files:
```
# GENERATED by uv pip compile --generate-hashes --universal. Do NOT hand-edit.
# Regenerate from the .in file. Hashes resolved for Python 3.13.
```

- [ ] **Step 3: Verify the hashed runtime install works**

Run:
```bash
python3.13 -m venv /tmp/hashcheck && /tmp/hashcheck/bin/pip install --require-hashes -r requirements.txt && /tmp/hashcheck/bin/python -c "import sklearn, fastapi; print('ok', sklearn.__version__)"
rm -rf /tmp/hashcheck
```
Expected: installs with no "hashes are required" error and prints `ok 1.9.0`.

- [ ] **Step 4: Update the Dockerfile**

- Change the base line to: `FROM python:3.13-slim@sha256:eb43ff125d8d58d7449dcba7d336c23bcac412f526d861db493b9994d8010280`
- Change the pip install to: `RUN pip install --no-cache-dir --require-hashes --root-user-action=ignore --disable-pip-version-check -r requirements.txt`
- Replace the shell-form COPY of app files with exec form including the dataset:
  `COPY --chown=appuser:appuser ["main.py", "sentiment_model.pkl", "IMDB Dataset.csv", "./"]`
- Update the comment that says the dataset is not copied — it now ships.

- [ ] **Step 5: Update .dockerignore and pytest.ini**

- In `.dockerignore`: delete the `IMDB Dataset.csv` line (it must enter the image); delete the `make_examples.py` line; add a `*.json` line (keep the Postman collection out of the image).
- In `pytest.ini`: replace the message-prefix ignore with a category filter and correct the comment:
```
filterwarnings =
    error
    # Suppress starlette's TestClient httpx-deprecation by category, robust to message
    # rewording (a class rename would still surface, which is acceptable under pinned deps).
    ignore::starlette.exceptions.StarletteDeprecationWarning
```

- [ ] **Step 6: Verify tests still pass under the new config**

Run: `.venv/bin/python -m pytest tests/ -q && ruff check main.py tests/`
Expected: all tests pass, ruff clean.

- [ ] **Step 7: Commit**

Run:
```bash
git add requirements.in requirements-dev.in requirements.txt requirements-dev.txt Dockerfile .dockerignore pytest.ini
git commit -m "hw3: hash-pin deps (uv --universal), digest-pin base, JSON-form dataset COPY"
```

---

### Task 6: README, Postman collection, model hash (premortem S2, S3, F4, F7, R)

**Files:**
- Modify: `assignments/hw3/README.md`
- Create: `assignments/hw3/hw3.postman_collection.json`

**Interfaces:**
- Consumes: nothing from code; documents the finished behavior.

- [ ] **Step 1: Create the Postman collection**

Create `hw3.postman_collection.json`:
```json
{
  "info": {
    "name": "HW3 Sentiment API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "health",
      "request": { "method": "GET", "url": "http://localhost:8000/health" }
    },
    {
      "name": "predict",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": { "mode": "raw", "raw": "{\"text\": \"This movie was a masterpiece!\"}" },
        "url": "http://localhost:8000/predict"
      }
    },
    {
      "name": "predict_proba",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": { "mode": "raw", "raw": "{\"text\": \"This movie was a masterpiece!\"}" },
        "url": "http://localhost:8000/predict_proba"
      }
    },
    {
      "name": "example",
      "request": { "method": "GET", "url": "http://localhost:8000/example" }
    }
  ]
}
```
Validate it: `.venv/bin/python -c "import json; json.load(open('hw3.postman_collection.json'))"` (no error).

- [ ] **Step 2: Compute the model hash**

Run: `shasum -a 256 sentiment_model.pkl`
Record the hex digest for Step 3.

- [ ] **Step 3: Update README.md**

Make these edits (keep the existing structure, matching its tone):
- **Files section:** remove `examples.csv` and `make_examples.py`; add `IMDB Dataset.csv - the full IMDB dataset backing /example` and `hw3.postman_collection.json - importable Postman requests`.
- **/example description and design note:** it now serves a random review from the full committed dataset with `<br>` tags stripped.
- **Add a "Test with Postman" section** (Postman is the stated grading tool): import `hw3.postman_collection.json`, start the container, and hit the four requests; note the expected JSON for each.
- **Qualify the probability claim:** change "reproduces exactly" to "reproduces exactly under the pinned environment (0.7697)".
- **Add a port note:** if host port 8000 is busy, remap with `-p 8001:8000`.
- **Add model integrity:** the `sentiment_model.pkl` SHA-256 is `<digest from Step 2>`; verify with `shasum -a 256 sentiment_model.pkl`.
- **Add the FastAPI Docker reference** the spec cites: packaging follows FastAPI's `https://fastapi.tiangolo.com/deployment/docker/` guidance.
- **Add a local-install prerequisite note:** the hashed requirements are resolved for Python 3.13; local `pip install` requires Python 3.13 (the container path is unaffected).
- **Confirm present:** an API-and-endpoints description, Makefile build/run instructions, and the `/docs` link (all already exist; verify wording).

- [ ] **Step 4: Verify no stale references remain**

Run: `grep -rn "examples.csv\|make_examples" . --include="*.py" --include="*.md" --include="Dockerfile" --include=".dockerignore" --include=".gitignore"`
Expected: no output (clean). Fix any hit.

- [ ] **Step 5: Commit**

Run:
```bash
git add README.md hw3.postman_collection.json
git commit -m "hw3: README Postman section, model SHA-256, dataset docs, /docs + docker refs"
```

---

### Task 7: Full verification and fresh-clone acceptance (premortem D1 acceptance gate)

**Files:** none modified; this task proves the whole plan landed.

- [ ] **Step 1: Full test + lint**

Run: `.venv/bin/python -m pytest tests/ -q && ruff check main.py tests/`
Expected: all tests pass (~19), ruff clean.

- [ ] **Step 2: Cold container build and health**

Run:
```bash
docker build --no-cache -t sentiment-api-hw3 .
docker run -d --rm --name hw3check -p 8000:8000 sentiment-api-hw3
sleep 8
curl -fsS http://localhost:8000/health && echo
curl -fsS http://localhost:8000/example && echo
docker inspect --format '{{.State.Health.Status}}' hw3check
docker stop hw3check
```
Expected: `/health` returns `{"status":"ok"}`, `/example` returns a clean review (no `<br`), health status `healthy`.

- [ ] **Step 3: Fresh-clone check (the only test that catches a silently-dropped dataset)**

Run (from repo root):
```bash
tmp=$(mktemp -d)
git clone --depth 1 "file://$(pwd)/.git" "$tmp/clone"
ls -l "$tmp/clone/assignments/hw3/IMDB Dataset.csv"   # MUST exist and be ~66MB
cd "$tmp/clone/assignments/hw3"
docker build --no-cache -t hw3-freshclone .
docker run -d --rm --name hw3fresh -p 8000:8000 hw3-freshclone
sleep 8
curl -fsS http://localhost:8000/health && echo
curl -fsS http://localhost:8000/predict -H 'Content-Type: application/json' -d '{"text":"a masterpiece"}' && echo
curl -fsS http://localhost:8000/example && echo
docker stop hw3fresh
cd - && rm -rf "$tmp"
```
Expected: the dataset file exists in the clone, the image builds, and all endpoints serve. If `IMDB Dataset.csv` is missing from the clone, Task 1 failed — return to it.

- [ ] **Step 4: Confirm self-containment and no stale refs**

Run (from repo root):
```bash
grep -rn "hw1\|hw2\|\.\./" assignments/hw3/main.py assignments/hw3/Dockerfile assignments/hw3/Makefile || echo "no cross-assignment refs"
grep -rn "examples.csv\|make_examples" assignments/hw3 --include="*.py" --include="*.md" --include="Dockerfile" || echo "no stale sample refs"
```
Expected: both print the "no ..." message.

- [ ] **Step 5: Final commit if any fixups were needed**

Run:
```bash
git add -A
git commit -m "hw3: verification fixups" --allow-empty
```

---

## Self-Review

**Spec coverage** (design doc → task):
- D1 gitignore → Task 1. D2 COPY-space → Task 5 Step 4. Dataset switch/S1/F8 → Tasks 1-2. HTML strip F9/M7 → Task 2. NaN F5/M4 → Task 3. Body-size F6/M3 → Task 4. Hash-pin R/M5 → Task 5. Digest R/M6 → Task 5. Warning filter F3/M8 → Task 5 Step 5. Model hash R → Task 6. 0.7697 F4 → Task 6. Port F7 → Task 6. Postman S2 → Task 6. README trio S3 → Task 6. field_size_limit → Task 2. Fresh-clone acceptance → Task 7. Self-containment → Task 7. All covered.

**Placeholder scan:** the only runtime value left to fill is the model SHA-256 (Task 6 Step 2 computes it before Step 3 uses it) and the two hashed requirements files (generated by tool in Task 5, not hand-written). No TODO/TBD.

**Type consistency:** `_json_safe`, `BodySizeLimitMiddleware`, `_BodyTooLarge`, `MAX_BODY_BYTES`, `_BR_TAG`, `EXAMPLE_REVIEWS`, `FULL_DATASET_PATH`, `resolve_example_source()` are used consistently across Tasks 2-4 and match `main.py`'s existing names.

## Execution Handoff

Ordering is strict: Task 1 first (unblocks `/example` tests), then 2→3→4 (main.py TDD), then 5 (packaging), 6 (docs), 7 (acceptance).
