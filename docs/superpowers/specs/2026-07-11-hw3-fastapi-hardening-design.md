# hw3 FastAPI Backend: Spec-Compliance and Hardening Design (Option B, premortem-revised)

- Status: revised after adversarial premortem #2; approved scope = Option B (maximal hardening)
- Date: 2026-07-11
- Owner: Rock Lambros <rock@rockcyber.com>
- Scope: `assignments/hw3` only. The graded folder must stay self-contained and must not reference hw1 or hw2.
- Source of requirements: the corrected `week3_Assignment3FastAPI.md` spec, plus two adversarial premortems (on the code at `1732c71`, and on this design at `2d5f535`).

## Goal

Take hw3 from "already builds and runs clean" to full marks with **no residual risk left open**. The owner chose Option B: close every residual, and implement each fix exactly as premortem #2's scratch-verified recipes specify, so the fixes do not reproduce or introduce the bugs they target.

Two classes of work:
1. Close the spec-compliance gaps the corrected spec revealed (project structure, the `IMDB Dataset.csv` data source, Postman grading, self-containment).
2. Fix every premortem finding and residual risk, using the safe implementation recipes below.

## Settled decisions

- **Submission stays the private monorepo.** Instructor `navido89` is a confirmed active write collaborator; he confirmed a private repo he can access is acceptable. This supersedes the spec's literal "public repository" line and root-level structure diagram. Add a one-line Canvas submission note recording that access is granted to `navido89`.
- **Commit the real dataset.** Ship the real `IMDB Dataset.csv` (66,212,309 bytes = 63.1 MiB, over GitHub's 50 MiB warn, under the 100 MiB block) inside `assignments/hw3/`, serve `/example` from it in repo and container, and remove `examples.csv` + `make_examples.py`. Plain commit, no Git LFS (LFS burns a metered quota; a plain 63 MiB file only warns).
- **Option B accepted both flagged decisions:** keep the body-size guard (as a real byte bound, not a comment-only fix) and keep the Postman collection.

## Premortem #2 must-fix defects (verified, would have zeroed the grade)

These are new relative to the first design and are the highest-priority work.

### D1 (Critical) — the 63 MiB commit would silently no-op

`git check-ignore -v "assignments/hw3/IMDB Dataset.csv"` resolves to `assignments/hw3/.gitignore:16` (`IMDB Dataset.csv`). A root-level re-include cannot override a deeper `.gitignore`; the deeper file wins. So `git add` silently skips the file (no `-f`), the local `docker build` still passes (it reads the working tree, not git), and only the grader's fresh clone breaks (`/example` 503 or a `COPY` build failure). The plan's own acceptance checks, all run "on the local platform," go green on a broken commit.

**Fix:** change `assignments/hw3/.gitignore:16` from `IMDB Dataset.csv` to `!IMDB Dataset.csv` (a deep-level negation overrides the parent `*.csv` and the local ignore; no root edit needed). Update the adjacent comment (lines 14-15) to say the dataset now ships. Then **verify** with `git check-ignore -v "assignments/hw3/IMDB Dataset.csv"` (must print nothing) and **stage explicitly** with `git add "assignments/hw3/IMDB Dataset.csv"` (errors loudly if still ignored, instead of silently skipping). Remove the now-obsolete `!assignments/hw3/examples.csv` re-include from the root `.gitignore`.

### D2 (High) — Dockerfile `COPY` of a filename with a space breaks the build

Shell-form `COPY ... IMDB Dataset.csv ./` splits on the space into two missing sources; quoting in shell form is a syntax error. Only JSON/exec form works.

**Fix:** rewrite the COPY as `COPY --chown=appuser:appuser ["main.py", "sentiment_model.pkl", "IMDB Dataset.csv", "./"]` (the `--chown` flag stays before the array). Verified to build clean. Keep the spaced filename (the spec structure diagram lists it verbatim).

## Fixes, with the safe recipe for each (Option B)

| Item | Source | Safe implementation (verified in premortem #2) |
|---|---|---|
| Dataset switch | S1, F8 | Copy `assignments/hw1/IMDB Dataset.csv` → `assignments/hw3/`; serve `/example` from it; delete `examples.csv` + `make_examples.py`; remove the `SAMPLE_PATH` tier and sample-era comments from `main.py` |
| `/example` HTML cleanup | F9, M7 | `re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)` — br-only, replace with a space. NOT a broad `<[^>]+>` empty-replace (word-jams 58% of draws, deletes text around stray `<`). Data has zero entity-encoded markup, so this is complete |
| NaN/Infinity 500 | F5, M4 | `RequestValidationError` handler returning 422 with `content={"detail": _json_safe(jsonable_encoder(exc.errors()))}`, where `_json_safe` **recursively** coerces any `float` that is `math.isnan` or `math.isinf` to `str`. `jsonable_encoder` alone leaves `nan` (still 500s); float-coerce alone 500s on blank-text's `ctx` `ValueError`. Both are required. Covers `NaN`, `Infinity`, `-Infinity`, and `1e400` (parses to `inf`) |
| Raw-body size limit | F6, M3 | Pure-ASGI middleware that bounds **actual bytes buffered**: reject with 413 if `Content-Length` (read via `.get()`, `int()` in try/except) exceeds the ceiling, AND accumulate body bytes across `http.request` messages and 413 when they exceed it (closes the chunked-encoding bypass). Must be a no-op for body-less GET (`/health`, `/example`). Ceiling 1 MiB |
| Test-suite pin fragility | F3, M8 | Keep the category filter `ignore::starlette.exceptions.StarletteDeprecationWarning`; correct the justification comment (it suppresses message rewording, not a class rename) |
| Dependency reproducibility | R, M5 | Hash-pin via `uv pip compile --generate-hashes --universal` for BOTH runtime and dev closures (all nine dev packages, not just six). Header comment: "generated, never hand-edit; regenerate with uv." Dockerfile: `pip install --require-hashes`. Document Python 3.13 as a hard prerequisite for the local install path |
| Base-image drift | R, M6 | Digest-pin the **multi-arch index** digest: `FROM python:3.13-slim@sha256:eb43ff125d8d58d7449dcba7d336c23bcac412f526d861db493b9994d8010280` (from `docker buildx imagetools inspect`, NOT a per-arch sub-digest from `docker manifest inspect`). Verify it builds on both arches. Document the drift/CVE trade in the design notes |
| Model provenance | R | Publish the model SHA-256 with a `shasum -a 256` verify command in the README |
| `0.7697` claim | F4 | Qualify as "under the pinned environment" |
| Port 8000 collision | F7 | README note: remap with `-p 8001:8000` if 8000 is busy |
| Postman grading | S2 | README Postman section + importable `hw3.postman_collection.json` (four requests vs `http://localhost:8000`); add `*.json` to `.dockerignore` so it stays out of the image |
| README required sections | S3 | Confirm API+endpoints description, Makefile build/run steps, `/docs` link; add the FastAPI `deployment/docker` reference the spec cites |
| CSV robustness | DS #6 | Bump `csv.field_size_limit` in `load_reviews` to future-proof against a longer review (today's max is 13,704 chars) |

## Architecture

Single-module FastAPI service (`main.py`), four endpoints, no framework change. Additions are surgical: one exception handler, one ASGI middleware, one serve-time string cleanup, one data-source change.

### `main.py`
- Data source resolves env override → committed `IMDB Dataset.csv` (next to `main.py`) → 503. No `examples.csv` tier. Full 50k loads once at import (measured 0.38-0.54s, ~68 MB, well inside the 10s healthcheck start-period). `csv.field_size_limit` bumped.
- `/example` strips `<br>` to a space at serve time (model is not involved, so no meaningful train/serve concern; the immaterial "br" token shift is noted honestly rather than claimed absent).
- NaN handler and body-size middleware per the recipes above. Degraded modes preserved (model→503 on predict endpoints; data→503 on `/example`; `/health` always up).

### Packaging
- `Dockerfile`: index-digest base, JSON-form COPY including the dataset, `pip install --require-hashes`, non-root user, stdlib-urllib healthcheck, `EXPOSE 8000`, uvicorn CMD.
- `requirements.txt` / `requirements-dev.txt`: `uv`-generated `--universal --generate-hashes` closures (~395 / ~454 lines), regenerate-only header.
- `.dockerignore`: stop excluding the dataset; add `*.json`; keep excluding tests, dev reqs, caches, `*.md`.
- `.gitignore` (both files): the D1 fix.

### Docs and grader ergonomics
- `README.md`: dataset + Files sections updated; Postman section; qualified `0.7697`; port note; model SHA-256; `/docs` link; FastAPI docker reference; 3.13 local-install prerequisite.
- `hw3.postman_collection.json`: four requests vs localhost:8000.

### Removed
- `examples.csv`, `make_examples.py`, and their references in `README.md`, `Dockerfile`, `.dockerignore`, root `.gitignore`, and `main.py`. A `grep -rn "examples.csv\|make_examples" assignments/hw3` gate must return clean before commit.

## Error handling
- `NaN`/`Infinity`/`-Infinity`/`1e400` in the body → 422 (not 500), via the recursive sanitizer.
- Oversized raw body (declared or chunked) → 413.
- Blank/missing/extra-field/oversized-field/wrong-type body → 422, unchanged default shape.
- Model or data source not loadable → 503 on the affected endpoint.

## Testing

Keep the 11 existing checks. Add:
- Malformed numbers as **raw bytes** (`content=b'{"text": NaN}'` with explicit `content-type: application/json`, NOT `json=float("nan")` which raises client-side in httpx) → assert 422 for `NaN`, `Infinity`, `-Infinity`, `1e400`.
- Normal 422 paths (blank, missing, extra-field) → assert 422 AND the default detail shape still renders (guards the handler against regression).
- `GET /health` and `GET /example` → assert 200 (guards the body-size middleware against the GET-500 regression).
- Oversized declared body and oversized chunked body → assert 413.
- `/example` → assert the review contains no `<br` and is not word-jammed at former tag sites.
- Dataset load path → non-empty list from the committed dataset.

Target: pytest green (≈19 checks), `ruff` clean, under the pinned `.venv`.

## Acceptance criteria
1. Cold `docker build --no-cache` succeeds with `--require-hashes` and the index-digest base, and the container reports `healthy`.
2. **Fresh-clone check (new, closes D1):** clone the repo to a throwaway dir, `docker build` and run there, and confirm all four endpoints serve — including `/example` returning a real HTML-stripped review. This is the only check that catches a silently-dropped dataset.
3. All four endpoints return the exact spec JSON shapes when driven by Postman against the running container.
4. pytest green (≈19), `ruff` clean, under the pinned env.
5. Every premortem finding (both rounds) and residual risk has a landed, correctly-implemented change.
6. `assignments/hw3` builds and runs with no reference to hw1 or hw2.
7. `grep -rn "examples.csv\|make_examples"` over hw3 is clean.

## Design notes / accepted trades (Option B)
- **Digest pin freezes CVEs.** Pinning the index digest trades "base drifts under me" for "base never patches." Correct for a short grading window; noted so it is not mistaken for defense-in-depth on a long-lived repo.
- **Hashed requirements are ~395/454 lines and 3.13-coupled.** Never hand-edit; regenerate with `uv`. Local installs require Python 3.13; the container path is unaffected.
- **Explicit content in `/example`** (~3.3%/draw) is inherent to the spec-mandated random draw from the original dataset and is deliberately not filtered.

## Out of scope (YAGNI)
- Git LFS; content filtering of `/example`; auth, rate limiting, multi-worker concurrency, load testing; any change outside `assignments/hw3`.
