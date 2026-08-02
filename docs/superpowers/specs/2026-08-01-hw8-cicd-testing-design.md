# hw8 (Assignment 6): CI/CD, Testing, and EC2 Deployment

Design spec. COMP 4450 MLOps, University of Denver.
Owner: Rock Lambros <rock@rockcyber.com>
Date: 2026-08-01
Status: approved, pending adversarial premortem

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
executing the README on a fresh box. The instance is never inspected.

Canvas header, authoritative: Points 17, Due Aug 18 by 11:59pm. Submission is a text entry box
or website URL at `canvas.du.edu/courses/223323/assignments/2011240`. The document body's
"Due Date: 18 August 2025" is stale and confirmed superseded.

## 3. Decisions locked

| Decision | Choice | Basis |
|---|---|---|
| Repository | Monorepo, `assignments/hw8/`, stays private | Instructor `navido89` verified as collaborator with push access |
| Layout | Self-contained copy of `api/` and `monitoring/` | Matches how hw3 and hw7 were each built |
| Branch | `dev` | Spec literal, overrides the repo's `hw8`-style convention |
| Dashboard launch test | `AppTest` plus a subprocess health poll | No course or repo precedent exists. Both together prove import-time and boot-time health |
| Linter | ruff with an explicit config | Spec permits flake8 or ruff. The repo already pins `ruff==0.15.17` |
| Python | 3.13 | Matches the hash-pinned lockfiles and the pickled model |
| Jobs | One job, five ordered steps | Spec says "Define a job" and "steps in order" |

## 4. Directory layout

```
assignments/hw8/
  api/
    main.py                 copied from hw7 v1.1.0
    test_api.py             SPEC LITERAL, flat
    conftest.py
    Dockerfile
    .dockerignore           must exclude the flat test file
    requirements.txt
    sentiment_model.pkl
  monitoring/
    dashboard.py            copied from hw7
    test_dashboard.py       SPEC LITERAL, flat
    reference_stats.py
    reference_stats.json
    conftest.py
    Dockerfile
    .dockerignore           must exclude the flat test file
    requirements.txt
  requirements.in           single source for the root lockfile
  requirements.txt          SPEC LITERAL for CI step 3
  pyproject.toml            ruff configuration
  pytest.ini
  docker-compose.yml
  Makefile
  README.md                 the operational manual
.github/workflows/ci.yml    repo root, GitHub reads workflows nowhere else
```

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
    defaults:
      run:
        working-directory: assignments/hw8
    steps:
      - uses: actions/checkout@<pinned-sha>
      - uses: actions/setup-python@<pinned-sha>
        with:
          python-version: '3.13'
      - run: pip install --require-hashes -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

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
(production) server", so the course model is `git pull` on the box. Part 3 calls the deployment
manual. The README will describe continuous integration plus a documented manual deploy and
will not claim continuous deployment, which the course defines as running "without any human
intervention."

## 6. Dependencies

One `requirements.in` listing every direct dependency for both services plus `pytest` and
`ruff`, compiled once with `uv pip compile --generate-hashes` into
`assignments/hw8/requirements.txt`. CI step 3 then satisfies the spec's singular
`requirements.txt` with one install.

This must be a single compile rather than an aggregator chaining the three existing lockfiles.
pip switches the entire install into hash-checking mode as soon as any requirement carries a
hash, so appending a package at the command line fails with "Hashes are required in
--require-hashes mode." The linter and the test runner have to be inside the compiled lockfile.

The two service Dockerfiles keep their own narrower lockfiles so the shipped images stay lean
and do not carry pytest or ruff.

## 7. Tests

### 7.1 `api/test_api.py`

Ports hw7's 14 test functions (21 collected cases) and closes one gap. hw7 asserts the request
contract: the four log keys, the echoed response, the ISO-8601 UTC timestamp, six parametrized
422 cases, three non-finite-float cases, a 413 over the body cap, and a 503 degraded-model case.
It does not assert the predicted label.

The spec asks for "The `/predict` endpoint with both a positive and a negative example." Add two
named tests asserting the label on unambiguous fixtures. Week 1 material warns that "ML models
are evaluated empirically, not proven correct", which is the reason to pick clearly-signed
inputs and to say so in a comment rather than to assert on borderline text.

### 7.2 `monitoring/test_dashboard.py`

Net-new. No dashboard test exists anywhere in the repo and `dashboard.py` has zero coverage.

A bare `import dashboard` cannot serve as the launch proof, because the module calls
`st.set_page_config` at import time and `st.stop()` in two branches. Two complementary tests:

1. `streamlit.testing.v1.AppTest` running the script headless in-process, asserting no
   exception. Fast, deterministic, catches import-time and render-time failures.
2. A subprocess `streamlit run` polling `/_stcore/health`, the same probe hw2's Dockerfile
   HEALTHCHECK already uses. Proves the real server boots and binds.

Cover the degraded state a freshly deployed host is actually in: log present, zero
`true_sentiment` values, drift charts render, accuracy section warns.

### 7.3 Packaging consequence

Flat test paths force a `.dockerignore` change in the same commit. Both service `.dockerignore`
files currently exclude `tests/`, which does not match a flat `test_api.py`. Without the change
the test files ship inside the production images.

## 8. EC2 deployment guide

The graded deliverable for Part 3 and Part 4 item 3, since the instructor replicates rather
than inspects. Every command must be copy-pasteable, correct in order, and free of implicit
local state.

Mirror the week 6 exercise wording so the grader recognizes the steps: Ubuntu Server 22.04 LTS,
t2.micro, key pair, security group rules stated as Type, Port, Source. Login user `ubuntu`.

Security group: port 22 from your IP, port 8000 from anywhere, port 8501 from anywhere.

Sequence: launch, SSH, install Docker and Git, clone, `cd assignments/hw8`, create the network,
create the volume, build both images, run both containers detached on the shared volume and
network, verify.

### 8.1 The three traps the guide must close

**Shared volume without a shared network.** Part 3 mandates a volume and never mentions a
network. `dashboard.py` resolves the API by name, which requires a user-defined network. Docker
provides no name resolution on the default bridge. Following the spec literally yields two
containers that look healthy in `docker ps` and a dashboard whose API badge reads unreachable.
The guide includes `docker network create sentiment-net` and passes `--network` and `--name` to
both containers.

**`API_URL` differs between the compose path and the raw path.** Compose sets
`http://api:8000`, the service name. Raw `docker run` needs `http://sentiment-monitor-api:8000`,
the container name. Copying the compose value into the runbook breaks the health badge.

**t2.micro is 1 vCPU and 1 GB** building scikit-learn, pandas, matplotlib, and streamlit wheels,
then running both containers. The build can exhaust memory. Document a swap-file step as the
named fallback. Do not silently upsize past the spec's `t2.micro`.

### 8.2 Parameterization

Public IPv4 changes on stop and start, and neither week 5 nor week 6 covers Elastic IPs. Every
host reference is `<EC2_PUBLIC_IP>` with an instruction to substitute. No hard-coded IP goes in
the README or the Postman collection.

Post-deploy verification hits `/predict`, not only `/health`. A mis-copied `sentiment_model.pkl`
produces a container that passes `docker ps` and `GET /health` while returning 503 on
`/predict`. `evaluate.py --api-url http://<EC2_PUBLIC_IP>:8000` exercises the real path and
exits 2 when unreachable, 1 when any record fails.

## 9. README structure

1. Project architecture, extending hw7's Mermaid diagram with the CI pipeline and the EC2 host
   boundary. Covers the FastAPI service, the Streamlit dashboard, the pipeline, and the
   deployment, which are Part 4 item 1's four named elements.
2. Local development with Docker, both the compose path and the raw `docker` equivalents.
3. The manual deployment guide from section 8.
4. Requirement-to-evidence table in hw7's format, mapping each spec line to a file and a
   verification command.
5. Deviations, stated plainly.

## 10. Deviations to document

| Deviation | Reason |
|---|---|
| Monorepo rather than a new repository, private rather than public | Verbal instructor grant, `navido89` has push access. Get it in writing and screenshot it into the README. |
| Python 3.13 rather than the course's 3.9 | `COURSE_STATE.md`: pandas 3.0.3 and scikit-learn 1.9.0 need 3.10+, and the model was pickled under 3.13 |
| ruff rather than flake8 | Spec permits either. Only flake8 was taught. The repo already pins ruff |
| Workflow at the repo root, not `assignments/hw8/.github/` | GitHub reads workflows only from the repository root |
| CI without CD | Part 3 calls the deploy manual. The course defines continuous deployment as having no human intervention |
| 413 and 503 status codes | Beyond the course's taught vocabulary of 200, 404, 422, 500. Deliberate hardening carried from hw7. |

## 11. Out of scope

No S3, DynamoDB, or IAM instance profile. The week 6 exercise uses all three and this spec says
only "Clone your GitHub repository." The model ships in the repo. State the absence in the
README so it reads as scoping rather than omission.

No Elastic IP, no TLS, no reverse proxy, no systemd unit, no log rotation. Ports 8000 and 8501
open to `0.0.0.0/0` over plain HTTP with no authentication is the graded configuration, and it
contradicts the course's own week 3 guidance that HTTPS is "essential for protecting data in
transit." Follow the spec and name the gap in a README limitations section. The abuse controls
that do exist are the 1 MiB body cap and the 20,000-character text cap carried from hw7.

No changes to the model, the endpoints, or the log record shape. hw7's suite asserts exact-set
equality on the four log keys, so adding an observability field is a breaking change.

## 12. Verification plan

| Claim | Command |
|---|---|
| Lint clean | `ruff check .` from `assignments/hw8` |
| Suite green | `pytest -q` from `assignments/hw8`, zero warnings |
| Images build | `docker compose build` |
| Stack runs | `make up`, then `make seed` |
| Raw path works | The literal `docker run` commands from the README, on a clean Docker state |
| Pipeline green | A real Actions run visible on the open pull request |
| Deploy guide correct | Execute it top to bottom on a fresh sandbox instance |

Nothing is reported as passing without the command output to back it. The Honor Code's
fabrication clause covers falsified resources, which includes a claimed CI status or a test
count that was never produced.

## 13. Known risks

| Risk | Mitigation |
|---|---|
| Repo deviation costs points, and the hw7 brief penalized reusing prior repos | Get the grant in writing before submitting |
| `main` is currently unprotected on the monorepo | Configure protection. The account already runs it on a private repo |
| Merging the PR before grading | Spec bolds "Do not merge it until after grading". Every prior PR here was merged on green |
| t2.micro build exhausts memory | Documented swap-file fallback |
| Grade weight unresolved, brief says 17 and syllabus says 10 | Not resolvable from documents. Ask the instructor |
| No AI-use policy found in the repo | Check the Canvas syllabus page directly |

## 14. Open items requiring the instructor

1. Written confirmation of the monorepo and private-visibility grant.
2. Reconciliation of 17 points on the brief against 10 points per homework in the syllabus.
3. Whether a Canvas-hosted AI-use policy exists that never reached the PDF extractions in this
   repo. The course outline's own bullet says "Check Syllabus section in the canvas."
