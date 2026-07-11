# hw3 FastAPI Backend: Spec-Compliance and Hardening Design

- Status: draft, pending user review
- Date: 2026-07-11
- Owner: Rock Lambros <rock@rockcyber.com>
- Scope: `assignments/hw3` only. The graded folder must stay self-contained and must not reference hw1 or hw2.
- Source of requirements: the corrected `week3_Assignment3FastAPI.md` spec, plus the adversarial premortem run on commit `1732c71`.

## Goal

Take hw3 from "already builds and runs clean" to "earns full marks with no residual risk I am unwilling to accept." Two classes of work:

1. **Close the spec-compliance gaps** the corrected spec revealed (project structure, the `IMDB Dataset.csv` data source, Postman as the grading tool, explicit self-containment).
2. **Fix every premortem finding and every residual risk**, including the ones the first premortem parked as acceptable, because the owner does not accept them.

Success is defined by the acceptance criteria at the end of this doc. It is not "the code looks better." It is "a grader following the spec with Postman awards 10/10, and a supply-chain or reproducibility failure cannot silently zero the build later."

## Settled decisions

Two forks were resolved with the owner before this design:

- **Submission stays the private monorepo.** The instructor (`navido89`) is a confirmed active write collaborator on `MLOPS-Comp-4450-1`, and the instructor has confirmed a private repo he can access is acceptable. This supersedes the spec's literal "public repository" line and its root-level structure diagram. No new repo, no public flip. The monorepo-plus-PR model holds.
- **Commit the real dataset.** Ship a 63 MB copy of `IMDB Dataset.csv` inside `assignments/hw3/`, serve `/example` from it in both local and container runs, and remove the `examples.csv` sample and `make_examples.py`. Rationale: the grader tests the running container with Postman, so the container's `/example` must return a review from "the original IMDB training dataset" the spec names, not a 200-row sample. A plain 63 MB commit is well inside GitHub's limits (100 MB per-file hard cap; Git LFS would be the thing that burns a metered quota, so it is deliberately avoided).

## What changes, and why

Every row below traces to a premortem finding (F#), a residual risk (R#), or a newly revealed spec requirement (S#). Nothing here is speculative feature work.

| Item | Source | Change | Files |
|---|---|---|---|
| Dataset switch | S1, F8 | Serve `/example` from committed `IMDB Dataset.csv`; drop the sample machinery | `main.py`, `Dockerfile`, `.dockerignore`, `.gitignore`, remove `examples.csv` + `make_examples.py` |
| `/example` HTML cleanup | F9 | Strip `<br />` and other HTML tags from the returned review at serve time | `main.py`, test |
| NaN/Infinity 500 | F5 | Custom `RequestValidationError` handler returns a clean 422, never a 500 | `main.py`, test |
| Raw-body size limit | F6 | Middleware rejects oversized raw bodies with 413 before buffering; comment corrected to match | `main.py`, test |
| Test-suite pin fragility | F3 | Replace the message-prefix warning ignore with a category filter | `pytest.ini` |
| Dependency yank/re-upload | R (PyPI yank) | Hash-pin the full runtime and dev closures with `--require-hashes` | `requirements.txt`, `requirements-dev.txt`, `Dockerfile` |
| Base-image drift | R (base image) | Digest-pin `python:3.13-slim@sha256:...` | `Dockerfile` |
| Dev deps unpinned | R (dev deps) | Pin and hash the six dev transitives | `requirements-dev.txt` |
| Model provenance unverifiable | R (pkl hash) | Publish the model's SHA-256 with a verify command | `README.md` |
| `0.7697` exactness claim | F4 | Qualify the claim as "under the pinned environment" | `README.md` |
| Port 8000 collision | F7 | Document remapping if 8000 is busy | `README.md` |
| Postman grading | S2 | Add a Postman testing section and a ready-to-import collection | `README.md`, new `hw3.postman_collection.json` |
| README required sections | S3 | Confirm API+endpoints description, Makefile build/run steps, `/docs` link are present and correct | `README.md` |
| Public-repo line | S4 | Document that instructor access to the private repo satisfies this; no code change | `README.md` (design note) |

## Architecture

The app stays a single-module FastAPI service (`main.py`) with four endpoints. No new modules, no framework changes. The changes are surgical additions to the existing structure.

### `main.py`

- **Data source resolution.** Keep the `EXAMPLE_DATA_PATH` env override, then resolve to the committed `IMDB Dataset.csv` next to `main.py`. Remove the `examples.csv` fallback tier (the file is gone). If no source resolves, `/example` degrades to 503 as today. The full dataset (~50k reviews) loads once at import into memory, which is fine for a single-worker container. Startup parse cost is a few seconds, comfortably inside the healthcheck's 10s start-period.
- **HTML stripping in `/example`.** A small helper strips `<br />` and other HTML tags from the review string at serve time (one operation per call, not 50k at load). The model is not involved in `/example`, so there is no train/serve text mismatch concern. Explicit content is inherent to a random draw from the dataset the spec mandates and is deliberately not filtered, because filtering would break "a random review from the original dataset." This is documented, not hidden.
- **NaN/Infinity handler.** Register a `RequestValidationError` exception handler that returns a 422 whose body is JSON-safe (non-standard floats coerced to strings before serialization). This closes the one reproducible 500 path, where FastAPI's default parser accepts `NaN`, Pydantic rejects it, and rendering the raw float in the 422 detail throws. The endpoints themselves are unchanged.
- **Raw-body size guard.** A Starlette middleware rejects requests whose `Content-Length` exceeds a generous ceiling (1 MB; a 20k-char review is well under 100 KB) with 413 before the body is buffered. This makes the existing `MAX_TEXT_LENGTH` comment's amplification-vector claim actually true; the comment is corrected to state that the field cap bounds model work while the middleware bounds bytes buffered.
- **Degraded modes preserved.** Missing model → prediction endpoints 503. Missing/unreadable data source → `/example` 503. `/health` always up. Unchanged philosophy.

### Packaging

- **`Dockerfile`.** Digest-pin the base image. Add `IMDB Dataset.csv` to the `COPY` set (owned by `appuser`). Switch the install to `pip install --require-hashes -r requirements.txt`. Keep the non-root user, the stdlib-urllib healthcheck, `EXPOSE 8000`, and the uvicorn `CMD`.
- **`requirements.txt` / `requirements-dev.txt`.** Regenerate with `--generate-hashes` so every pin carries wheel hashes for both `linux/amd64` and `linux/arm64`. Pin and hash the six dev transitives (`certifi`, `httpcore`, `iniconfig`, `packaging`, `pluggy`, `pygments`). The runtime closure is the verified 19-package set; the dev file layers pytest, httpx, ruff, and their closure on top.
- **`.dockerignore`.** Stop excluding `IMDB Dataset.csv` so it enters the image. Continue excluding tests, dev requirements, caches, and docs.
- **`.gitignore`.** Re-include `assignments/hw3/IMDB Dataset.csv` past the repo-wide `*.csv` / dataset ignores. Drop the now-obsolete `examples.csv` re-include.

### Docs and grader ergonomics

- **`README.md`.** Update the data-source and Files sections for the dataset switch. Add a Postman testing section (the stated grading tool) walking each of the four endpoints. Qualify the `0.7697` claim. Add the port-remap note. Publish the model SHA-256 with a `shasum -a 256` verify command. Confirm the three spec-required README elements are present: an API-and-endpoints description, Makefile build/run instructions, and a link to the auto-generated `/docs`.
- **`hw3.postman_collection.json`.** A minimal, importable collection with the four requests against `http://localhost:8000`, so the grader's Postman workflow is one import away. It is an extra beyond the structure diagram; the instructor's acceptance of a deviating layout makes extra helper files safe, and it directly reduces grading friction.

### Files removed

- `examples.csv` (replaced by the full dataset)
- `make_examples.py` (sample generator, now vestigial)

Their references in `README.md`, `Dockerfile`, `.dockerignore`, `.gitignore`, and any test are removed in the same pass.

## Data flow

- `GET /health` → `{"status":"ok"}`. Unchanged.
- `POST /predict` → body passes the size middleware, then Pydantic validation, then the model. Unchanged output contract.
- `POST /predict_proba` → same path, returns sentiment plus 4-dp probability. Unchanged.
- `GET /example` → random review from the loaded full dataset, HTML-stripped, returned as `{"review": "..."}`.

## Error handling

- Malformed numeric JSON (`NaN`, `Infinity`, `-Infinity`) → 422 (was 500).
- Oversized raw body → 413 (was 200 after full buffering).
- Missing/blank/extra-field/oversized-field body → 422. Unchanged.
- Model not loadable → 503 on prediction endpoints. Data source not loadable → 503 on `/example`. Unchanged.

## Testing

Keep the existing 11 checks. Add:

- `POST /predict` with `{"text": NaN}` (raw JSON literal) → asserts 422, not 500.
- An oversized raw body → asserts 413.
- `/example` returns a review with no `<br` substring, asserting HTML stripping.
- Dataset load path returns a non-empty list from the committed dataset.

The suite must pass under the pinned `.venv`, and must not error at collection under a plausible starlette version bump (the category-based warning filter is what buys this).

## Acceptance criteria

1. Cold `docker build --no-cache` succeeds with `--require-hashes` and a digest-pinned base, on the local platform, and the container reports `healthy`.
2. All four endpoints return the exact spec JSON shapes when driven by Postman against the running container, and `/example` returns a clean (HTML-stripped) real dataset review.
3. `pytest` passes 15/15 (11 existing plus 4 new) under the pinned env.
4. `ruff check` is clean.
5. Every premortem finding (F3–F9) and every residual risk (yank, base image, dev deps, model hash) has a landed change or a documented, defensible resolution.
6. `assignments/hw3` builds and runs with no reference to hw1 or hw2 (self-containment holds after the dataset copy).
7. The corrected spec's Part 2/Part 3 elements are each satisfied or explicitly reconciled (public-repo line reconciled via instructor access).

## Out of scope (YAGNI)

- Git LFS for the dataset (burns a metered quota; plain commit is within limits).
- Digest-pinning transitive dependencies beyond the base image (hashes already bind them).
- Filtering explicit content from `/example` (would break "random from the dataset"; inherent to the mandated source).
- Auth, rate limiting, multi-worker concurrency, load testing (no spec requirement; single-worker container is how it is graded).
- Any change outside `assignments/hw3`.

## Risks introduced by these changes

- **Repo and image grow by 63 MB.** Accepted: within GitHub limits, trivial for grading, closes the compliance gap.
- **Hashed requirements need regeneration when a pin moves.** Accepted: pins are stable for the grading window; the reproducibility gain outweighs the maintenance cost.
- **Larger startup memory/time** from loading the full dataset. Accepted: a few seconds and ~150 MB, inside the healthcheck window and a container's normal footprint.

## Open decisions for the reviewer

Two judgment calls are flagged so they can be vetoed rather than discovered later:

- The raw-body **413 middleware** goes beyond "correct the misleading comment." It is included because the owner rejects residuals and it is a legitimate control, but the minimal alternative is a comment-only fix.
- The **Postman collection file** is an extra beyond the spec's structure diagram. Included for grader ergonomics; can be dropped to README instructions only.
