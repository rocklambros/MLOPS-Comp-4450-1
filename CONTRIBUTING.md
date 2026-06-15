# Contributing

This is a coursework repository for COMP 4450. Contributors are the repository owner and, on assignments done in pairs, a partner. This file covers how to set up, how to organize an assignment, the branch and commit flow, and the rules for secrets and large files.

## Setup

```bash
git clone https://github.com/rocklambros/MLOPS-Comp-4450-1.git
cd MLOPS-Comp-4450-1
python3 -m venv .venv
source .venv/bin/activate
```

Dependencies are pinned per assignment, not globally. When you start an assignment, install its `requirements.txt` from inside the assignment directory so versions stay reproducible for whoever grades or reruns the work.

```bash
cd assignments/hw3
pip install -r requirements.txt
```

## One branch per assignment

Work on a branch named for the assignment, never directly on `main`.

```bash
git checkout -b hw3
```

Keep all of an assignment's files inside its own directory, for example `assignments/hw3/`. Fill in that directory's stub `README.md` first: the week, the topic, the partner if any, the objective, and how to run the solution. Commit in small steps with messages that say what changed, for example `hw3: add input validation to the predict endpoint` rather than `update`.

## Working in pairs

Assignments may be done in pairs. When you pair up:

1. Record the partner in the assignment's `README.md`.
2. Both partners commit under their own GitHub identity so the work is attributable. Do not commit on a partner's behalf.
3. Open a pull request from the assignment branch into `main` and have the partner review before merge.

If you work solo, you can merge your own branch without a review, but still use a branch so `main` always reflects submitted work.

## Secrets and credentials

The later labs and the final project use AWS and other cloud services. Credentials never get committed.

- Keep secrets in a local `.env` file or your shell environment. `.env` is ignored by `.gitignore`.
- Never paste an access key, token, or password into source, a notebook, or a commit message.
- If a credential is committed by accident, rotate it immediately. Removing it in a later commit does not erase it from history.

## Large files

Trained models, datasets, and checkpoints do not belong in git. The `.gitignore` already excludes common model and data extensions. Reference data by its source or a download script instead of committing the bytes. If a graded artifact must be shared, link to external storage from the assignment `README.md`.

## Before you push

- Run the assignment's tests and linters if it has them.
- Confirm no secrets or large binaries are staged: `git status` and `git diff --cached`.
- Confirm the assignment `README.md` explains how to run the solution from a clean clone.
