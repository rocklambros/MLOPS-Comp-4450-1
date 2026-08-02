# hw8 (Assignment 6): CI/CD, Testing, and EC2 Deployment

Design spec. COMP 4450 MLOps, University of Denver.
Owner: Rock Lambros <rock@rockcyber.com>
Date: 2026-08-01
Status: approved, amended after a six-perspective adversarial premortem (53 findings)

## 1. Goal

Add three layers to the existing sentiment-analysis system: a pytest suite at the paths the
spec names, a GitHub Actions pipeline that gates every pull request to `main`, and a README
that works as an operational manual for deploying both containers to a t2.micro EC2 host.

The model, the FastAPI service, and the Streamlit dashboard already exist and are graded. This
assignment wraps them. Nothing gets retrained and no endpoint changes.

## 2. Authoritative sources

Work from `assignments/hw8/week8_Assignment6CICDTesting.pdf`, the Canvas print, not from
`week8_Assignment6CICDTesting.md`. The docling extraction is lossy: it carries mojibake bullet
glyphs, collapses Part 3 into one unreadable block, clips the System Architecture bullet
mid-sentence, truncates the submission bullet at "see both your code", and drops an entire
graded instruction.

The dropped instruction, verbatim from page 4:

> Use the AWS sandbox for this assignment. I will not check your EC2 instance since it will not
> persist once you close it, instead I will replicate the steps you mentioned and clone it on my
> end to grade your work

This is the single most scope-shaping line in the assignment. Part 3 is graded by a human
executing the README on a fresh box. The instance is never inspected. Every command in the
runbook has to work for a reader with no local state.

Canvas header, authoritative: Points 17, Due Aug 18 by 11:59pm. Submission is a text entry box
or website URL at `canvas.du.edu/courses/223323/assignments/2011240`. The document body's
"Due Date: 18 August 2025" is stale and confirmed superseded.

## 3. Decisions locked

| Decision | Choice | Basis |
|---|---|---|
| Repository | Monorepo, `assignments/hw8/`, stays private | Instructor `navido89` verified as collaborator with push access |
| Layout | Self-contained copy of `api/` and `monitoring/` | Matches how hw3 and hw7 were each built |
| Branch | `dev` | Spec literal, overrides the repo's `hw8`-style convention |
| Dashboard launch test | `AppTest` plus a subprocess health poll | No course or repo precedent exists. Each proves a different failure class, per §7.2 |
| Linter | ruff with an explicit config | Spec permits flake8 or ruff. The repo already pins `ruff==0.15.17` |
| Python | 3.13 | Matches the hash-pinned lockfiles and the pickled model |
| Jobs | One job, five ordered steps | Spec says "Define a job" and "steps in order" |
| EC2 code transfer | `scp` primary, `git clone -b dev` documented alongside | `scp` needs no credential on the host. The clone is kept because Part 3 says "Clone your GitHub repository onto the EC2 instance" |

## 4. Directory layout

```
assignments/hw8/
  api/
    main.py                 copied from hw7 v1.1.0
    test_api.py             SPEC LITERAL, flat
    conftest.py             sys.path shim, must still resolve with a flat test file
    Dockerfile
    .dockerignore
    requirements.txt        service lockfile, unchanged from hw7
    sentiment_model.pkl     REQUIRES a .gitignore negation, see 4.1
  monitoring/
    dashboard.py            copied from hw7
    test_dashboard.py       SPEC LITERAL, flat
    test_reference_stats.py carried forward so the suite does not shrink
    reference_stats.py
    reference_stats.json
    imdb_sample.csv         COPYed by name in the Dockerfile. REQUIRES a negation, see 4.1
    conftest.py
    Dockerfile
    .dockerignore
    requirements.txt        service lockfile, unchanged from hw7
  evaluate.py               post-deploy scoring, referenced by 8.3
  test.json                 174 labeled records, input to evaluate.py
  requirements.in           single source for the root lockfile
  requirements.txt          SPEC LITERAL for CI step 3
  pyproject.toml            ruff configuration
  pytest.ini
  docker-compose.yml
  Makefile                  test target must point at the flat paths, not api/tests
  README.md                 the operational manual
.github/workflows/ci.yml    repo root, GitHub reads workflows nowhere else
```

### 4.1 The `.gitignore` trap, verified

`git check-ignore -v` confirms the root `.gitignore` silently swallows two files hw8 cannot
build without:

```
.gitignore:234:*.pkl   assignments/hw8/api/sentiment_model.pkl
.gitignore:250:*.csv   assignments/hw8/monitoring/imdb_sample.csv
```

hw7 works only because of two hand-written path-literal negations at `.gitignore:261` and
`.gitignore:289`. There is no hw8 equivalent.

The failure is silent and reaches the grader. `git add assignments/hw8/` skips both files with
no error, the commit and the push succeed, the pull request opens, and the instructor's
`docker build ./api` dies at `api/Dockerfile:34`, which is
`COPY --chown=appuser:appuser main.py sentiment_model.pkl ./`. The monitoring build fails the
same way on `imdb_sample.csv`, which `monitoring/Dockerfile:34` names explicitly.

Two negations land in the same commit as the copied binaries:

```
!assignments/hw8/api/sentiment_model.pkl
!assignments/hw8/monitoring/imdb_sample.csv
```

Verification runs against the pushed remote, not the working tree. See §12.

## 5. CI pipeline

### 5.1 Shape

```yaml
name: ci
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
jobs:
  ci:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: assignments/hw8
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683      # v4.2.2
      - uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b  # v5.3.0
        with:
          python-version: '3.13'
      - run: pip install --require-hashes -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

The action SHAs are real and already proven in the owner's own CI. No placeholder ships in a
graded artifact.

`timeout-minutes: 15` bounds the job. The subprocess dashboard test can hang, and an unbounded
yellow check on the submitted pull request reads worse than a red one.

### 5.2 Rationale for each non-obvious choice

**No `paths:` filter.** A filter is tidier and can suppress the run on a pull request that
touches nothing under `assignments/hw8`, leaving the pull request with no visible check. The
spec requires the trigger on every pull request to `main` and requires the checks to be visible
to the grader.

**`working-directory` is load-bearing.** It keeps pytest's rootdir at `assignments/hw8` so
hw8's `pytest.ini` and its `filterwarnings = error` gate apply. Running pytest from the repo
root also hits a hard collection error, because `assignments/hw3/tests/test_api.py` and
`assignments/hw7/api/tests/test_api.py` share a basename with no `__init__.py`. hw8 adds a
third.

**One job.** The week 8 lecture shows two jobs, a Test Job and a Code Quality Job. The spec
says "Define a job" and "The job must perform the following steps in order" with lint as step 4
and pytest as step 5. Two jobs breaks the stated ordering. One job satisfies both readings.

**Pinned action SHAs.** Exceeds anything the course showed. Justified in one README line
against the repo's existing supply-chain standard.

### 5.3 What the pipeline does not do

No SSH or deploy job. The week 8 demo build order ends at "Pull from repo for deployment on EC2
(production) server", so the course model is a manual pull on the box. Part 3 calls the
deployment manual. The README will describe continuous integration plus a documented manual
deploy and will not claim continuous deployment, which the course defines as running "without
any human intervention."

## 6. Dependencies

One `requirements.in` compiled once into `assignments/hw8/requirements.txt`:

```
uv pip compile requirements.in --generate-hashes --universal \
  --python-version 3.13 -o requirements.txt
```

`--universal` and `--python-version 3.13` are mandatory, not stylistic. Compiling on an arm64
Mac without them produces a macOS-specific lockfile whose wheel hashes do not match what pip
resolves on `ubuntu-latest`, and CI step 3 fails on the graded pull request. hw7's lockfile
header records the same invocation.

`requirements.in` must list, at minimum, the direct dependencies of both services plus:

- `pytest`, the test runner
- `ruff`, the linter
- `httpx`, which is **not** in `api/requirements.txt` (verified: `grep -c '^httpx'` returns 0).
  FastAPI's `TestClient` imports it. Without it every API test dies at collection.

The single compile matters. pip switches the entire install into hash-checking mode as soon as
any requirement carries a hash, so appending a package at the command line fails with "Hashes
are required in --require-hashes mode." Every tool has to be inside the compiled lockfile.

The two service Dockerfiles keep their own narrower lockfiles so the shipped images stay lean
and do not carry pytest, ruff, or httpx. The root lockfile and the service lockfiles must
resolve the same `scikit-learn` and `numpy` versions, or CI tests a different stack than the
image loads the pickle with. Verify, do not assume.

## 7. Tests

### 7.1 `api/test_api.py`

Ports hw7's 14 test functions (21 collected cases) and closes one gap. hw7 asserts the request
contract: the four log keys, the echoed response, the ISO-8601 UTC timestamp, six parametrized
422 cases, three non-finite-float cases, a 413 over the body cap, and a 503 degraded-model case.
It does not assert the predicted label.

The spec asks for "The `/predict` endpoint with both a positive and a negative example." Add two
named tests asserting the label, using the sentences already canonical in `hw7/Makefile:43-46`:

- positive: "An absolute masterpiece, I loved every minute of it."
- negative: the Makefile's paired negative sentence

Record the model's actual `predict_proba` margin on both fixtures in a comment when the tests
are written. A fixture that classifies at 0.51 is a flaky red check on the graded pull request.
Week 1 material warns that "ML models are evaluated empirically, not proven correct", which is
the reason to pick wide-margin inputs and to say so rather than to assert on borderline text.

Name at least one test so its name maps to the brief's wording, for a grader reading the file
against the checklist rather than running it.

### 7.2 `monitoring/test_dashboard.py`

Net-new. No dashboard test exists anywhere in the repo and `dashboard.py` has zero coverage.

A bare `import dashboard` cannot serve as the launch proof, because the module calls
`st.set_page_config` at import time and `st.stop()` in two branches.

**The vacuous-assertion trap.** `dashboard.py:156-162` calls `st.stop()` when the log file is
empty. An `AppTest` run with no log therefore stops early and "no exception raised" is trivially
true on a dashboard that rendered almost nothing. The test must:

1. Seed a temporary log with at least one record, including a `true_sentiment` value, so the
   script runs past both `st.stop()` branches.
2. Assert `not at.exception`.
3. Assert on rendered content, not only absence of error. At minimum that the success banner
   is present and that no `st.error` element rendered.
4. Cover the degraded state separately as its own case: log present, zero `true_sentiment`
   values, asserting the accuracy section warns while the drift charts still render.

**The subprocess test** proves the real server boots and binds, which `AppTest` does not. It
must pass `--server.headless true` or Streamlit blocks on the email prompt and hangs the CI job.
It also needs a bound wait with a timeout, a free-port strategy rather than a hardcoded 8501,
and a `finally` block that terminates the process. Poll `/_stcore/health`, the probe hw2's
Dockerfile HEALTHCHECK already uses.

State plainly what each test proves. The health poll proves the server process starts. It does
not prove `dashboard.py` rendered, because Streamlit serves the health endpoint before the
script finishes. The README's evidence table must not overclaim it.

### 7.3 Packaging note, corrected

An earlier draft of this spec claimed flat test files would ship inside the production images
without a `.dockerignore` change. That is wrong, and the correction is recorded rather than
quietly dropped. Both Dockerfiles use an explicit COPY allowlist:

- `api/Dockerfile:34` copies `main.py sentiment_model.pkl` and nothing else
- `monitoring/Dockerfile:34` copies a named list of five files

No unlisted file can reach either image. Updating `.dockerignore` for the flat test paths is
build-context hygiene that keeps builds fast, not a correctness requirement.

### 7.4 Suite scope

`monitoring/test_reference_stats.py` carries forward. Dropping it would shrink the suite that
CI step 5 is told to run "in full" from 28 collected cases to fewer, for no gain.

`Makefile`'s `test` target currently reads `pytest api/tests monitoring/tests`. Flat test files
break it. Update it in the same commit that moves the files.

## 8. EC2 deployment guide

The graded deliverable for Part 3 and Part 4 item 3, since the instructor replicates rather
than inspects. Every command must be copy-pasteable, correct in order, and free of implicit
local state. The runbook is written for a reader who has just downloaded a fresh key pair and
has nothing else.

Mirror the week 6 exercise wording so the grader recognizes the steps: Ubuntu Server 22.04 LTS,
t2.micro, key pair, security group rules stated as Type, Port, Source. Login user `ubuntu`.

Security group: port 22 from your IP, port 8000 from anywhere, port 8501 from anywhere.

### 8.1 Ordered steps, each with its literal command

1. Launch the instance and configure the security group.
2. `chmod 400 <key>.pem` before the first SSH. A freshly downloaded key is world-readable and
   SSH refuses it outright. No `chmod 400` appears anywhere in this repo today.
3. SSH in as `ubuntu`.
4. Install Docker and Git.
5. Add `ubuntu` to the `docker` group, then re-login or `newgrp docker`. Without this the first
   `docker build` fails with permission denied on the socket. Group membership does not apply
   to the current shell.
6. Get the code onto the host. Primary path, needing no credential on the box:
   `scp -i <key>.pem -r assignments/hw8 ubuntu@<EC2_PUBLIC_IP>:/home/ubuntu/`
   Documented alternative, satisfying Part 3's "Clone your GitHub repository onto the EC2
   instance": `git clone -b dev <url>`, with a note that the repository is private and needs a
   credential, and that `-b dev` is required because the pull request stays unmerged so `main`
   carries no hw8 code. Verified: `git ls-tree -r main` under `assignments/hw8` returns only the
   stub README and the brief.
7. `docker network create sentiment-net`
8. `docker volume create prediction-logs`
9. Build both images with explicit tags.
10. Run both containers detached, each with `--network sentiment-net`, `--name`,
    `-v prediction-logs:/logs`, `-p`, and `--restart unless-stopped`. The dashboard also needs
    `-e API_URL=http://sentiment-monitor-api:8000`.
11. Seed the log so the dashboard is not empty, reusing the two `curl` calls from
    `hw7/Makefile:43-46`.
12. Verify.
13. Tear down.

### 8.2 The traps the guide must close

**Shared volume without a shared network.** Part 3 mandates a volume and never mentions a
network. `dashboard.py` resolves the API by name, which requires a user-defined network. Docker
provides no name resolution on the default bridge. Following the spec literally yields two
containers that look healthy in `docker ps` and a dashboard whose API badge reads unreachable.

**`API_URL` differs between the compose path and the raw path.** Compose sets
`http://api:8000`, the service name. Raw `docker run` needs `http://sentiment-monitor-api:8000`,
the container name. Copying the compose value into the runbook breaks the health badge.

**The empty dashboard.** `dashboard.py:156-162` calls `st.stop()` when no predictions are
logged. A grader who follows the runbook and opens port 8501 sees "No predictions logged yet"
and nothing else. Step 11 exists to prevent the deployment reading as broken.

**Name collisions between the two documented paths.** Compose and raw `docker run` both use
fixed container, volume, and network names. Running one after the other without a teardown
fails on a name already in use. The README states this and gives the teardown.

**No restart policy.** Without `--restart unless-stopped` the containers do not survive the
instance stop and start that §8.3 already anticipates.

**Resource reality, corrected.** An earlier draft blamed wheel compilation for build failures on
t2.micro. That diagnosis was wrong: the lockfiles are wheel-based and nothing compiles from
source. The real pressure is two containers co-resident in 1 GB at runtime, plus an 8 GB root
volume holding two images and the build cache. Mitigations that match the actual cause: prune
build cache between the two builds, add a swap file for runtime headroom rather than build
headroom, and check `df -h` before building. Do not silently upsize past the spec's `t2.micro`.

### 8.3 Verification and parameterization

Public IPv4 changes on stop and start, and neither week 5 nor week 6 covers Elastic IPs. Every
host reference is `<EC2_PUBLIC_IP>` with an instruction to substitute. No hard-coded IP goes in
the README or the Postman collection. Pasted command output in the README has the IP redacted
the same way.

Post-deploy verification hits `/predict`, not only `/health`. A mis-copied `sentiment_model.pkl`
produces a container that passes `docker ps` and `GET /health` while returning 503 on
`/predict`. Two levels:

- Dependency-free, always available on the host:
  `curl -fsS -X POST http://<EC2_PUBLIC_IP>:8000/predict -H 'Content-Type: application/json'
  -d '{"text":"An absolute masterpiece, I loved every minute of it.","true_sentiment":"positive"}'`
  asserting HTTP 200 and a `predicted_sentiment` field.
- Optional and fuller: `evaluate.py --api-url http://<EC2_PUBLIC_IP>:8000`, which needs
  `evaluate.py`, `test.json`, and `requests` present. All three are now in the §4 layout, and
  the runbook states the `pip install requests` prerequisite.

## 9. README structure

1. Project architecture, extending hw7's Mermaid diagram with the CI pipeline and the EC2 host
   boundary. Covers the FastAPI service, the Streamlit dashboard, the pipeline, and the
   deployment, which are Part 4 item 1's four named elements.
2. Local development with Docker, both the compose path and the raw `docker` equivalents, with
   the teardown that lets a reader switch between them.
3. The manual deployment guide from §8, including teardown.
4. Requirement-to-evidence table in hw7's format, mapping each spec line to a file and a
   verification command. No row claims more than the command proves.
5. Deviations, stated plainly.
6. Limitations, including the security posture in §11.

## 10. Deviations to document

| Deviation | Reason |
|---|---|
| Monorepo rather than a new repository, private rather than public | Verbal instructor grant, `navido89` has push access. Get it in writing and screenshot it into the README. |
| Python 3.13 rather than the course's 3.9 | `COURSE_STATE.md`: pandas 3.0.3 and scikit-learn 1.9.0 need 3.10+, and the model was pickled under 3.13 |
| ruff rather than flake8 | Spec permits either. Only flake8 was taught. The repo already pins ruff |
| Workflow at the repo root, not `assignments/hw8/.github/` | GitHub reads workflows only from the repository root |
| CI without CD | Part 3 calls the deploy manual. The course defines continuous deployment as having no human intervention |
| 413 and 503 status codes | Beyond the course's taught vocabulary of 200, 404, 422, 500. Deliberate hardening carried from hw7. |
| `scp` as the primary host transfer | The repository is private. `git clone -b dev` is documented alongside to satisfy Part 3's wording. |

## 11. Out of scope

No S3, DynamoDB, or IAM instance profile. The week 6 exercise uses all three and this spec says
only "Clone your GitHub repository." The model ships in the repo. State the absence in the
README so it reads as scoping rather than omission.

No Elastic IP, no TLS, no reverse proxy, no systemd unit, no log rotation. Ports 8000 and 8501
open to `0.0.0.0/0` over plain HTTP with no authentication is the graded configuration, and it
contradicts the course's own week 3 guidance that HTTPS is "essential for protecting data in
transit."

The limitations section names both directions of that exposure. Inbound: anyone can post to
`/predict`, bounded only by the 1 MiB body cap and the 20,000-character text cap carried from
hw7. Outbound: port 8501 serves an unauthenticated read of every logged prediction, because
`dashboard.py:328` renders the recent-requests table including `request_text`.

No changes to the model, the endpoints, or the log record shape. hw7's suite asserts exact-set
equality on the four log keys, so adding an observability field is a breaking change.

## 12. Verification plan

Nothing is reported as passing without the command output behind it. The Honor Code's
fabrication clause covers falsified resources, which includes a claimed CI status or a test
count that was never produced.

| Claim | Command |
|---|---|
| Binaries are actually tracked | `git ls-tree -r origin/dev --name-only \| grep -E 'hw8.*(\.pkl\|\.csv)'` lists both, run against the pushed remote |
| Nothing is silently ignored | `git check-ignore -v assignments/hw8/api/sentiment_model.pkl assignments/hw8/monitoring/imdb_sample.csv` prints nothing |
| Lint clean, at the CI version | `ruff check .` using the ruff from the compiled lockfile, not whatever is on PATH |
| Suite green | `pytest -q` from `assignments/hw8`, zero warnings under `filterwarnings = error` |
| Lockfile installs on Linux | `pip install --require-hashes -r requirements.txt` on a linux/amd64 container, not only on the Mac |
| Workflow is valid before the graded PR | Open a throwaway pull request into `main` from a scratch branch and confirm the run goes green, then close it |
| Images build | `docker compose build` |
| Stack runs | `make up`, then `make seed`, then both ports respond |
| Raw path works | The literal `docker run` commands from the README, from a clean Docker state |
| Fresh-clone integrity | Clone into a scratch directory and build there, proving no untracked local file is load-bearing |
| Deploy guide correct | Execute it top to bottom on a fresh sandbox instance, including teardown |
| Pipeline green | A real Actions run visible on the open pull request |
| Grader can see it | Confirm the pull request URL resolves for `navido89`, not only for the owner |

## 13. Deliverables that are settings, not files

These are graded and leave no artifact in the repository, so each needs its own evidence.

| Item | Action | Evidence |
|---|---|---|
| `main` protected | Configure branch protection on the monorepo, currently absent | Screenshot in the README, since a collaborator cannot see the setting |
| Pull request open, unmerged | Open `dev` into `main`, leave it | The brief bolds "Do not merge it until after grading." Every prior pull request in this repo was merged on green, so this breaks a 14-for-14 habit deliberately |
| Canvas submission | Paste the pull request URL into the Canvas text box | Confirm the URL loads |

## 14. Known risks

| Risk | Mitigation |
|---|---|
| Repo deviation costs points, and the hw7 brief penalized reusing prior repos | Get the grant in writing before submitting |
| Merging the PR before grading | §13 makes it an explicit deliverable with a check |
| Label fixtures flip and redden the pipeline | Record the `predict_proba` margin, pick wide-margin sentences |
| `filterwarnings = error` catches a new streamlit or pandas deprecation | Run the suite before opening the graded pull request, allowlist by category if needed |
| Grade weight unresolved, brief says 17 and syllabus says 10 | Not resolvable from documents. Ask the instructor |
| No AI-use policy found in the repo | Check the Canvas syllabus page directly |

## 15. Open items requiring the instructor

1. Written confirmation of the monorepo and private-visibility grant.
2. Reconciliation of 17 points on the brief against 10 points per homework in the syllabus.
3. Whether a Canvas-hosted AI-use policy exists that never reached the PDF extractions in this
   repo. The course outline's own bullet says "Check Syllabus section in the canvas."
