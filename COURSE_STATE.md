# Course state

A running ledger of cross-assignment decisions for COMP 4450, so later weeks stay
consistent with the earlier ones.

## Stack decisions

- **Python baseline: 3.13.** Set in hw2 (week 2). The Assignment 1 model is pinned to
  pandas 3.0.3 and scikit-learn 1.9.0, which require Python 3.10 or newer, and the model
  was serialized under Python 3.13. Every containerized assignment from hw2 forward uses
  `python:3.13-slim` so the dependencies install and the model loads. This deviates from
  the course's stated 3.9 baseline. The reasoning and an offer to re-pin are in the note to
  the instructor in `assignments/hw2/README.md`. Downgrading later would mean re-pinning the
  stack to 3.9-compatible versions (scikit-learn 1.6.x, pandas 2.2.x) and retraining the model.
