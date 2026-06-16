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

## Service conventions

- **hw7 monitoring reference data.** hw7 (week 7) deviates from the earlier weeks' rule
  that the full IMDB dataset stays gitignored and out of the image. The Streamlit
  monitoring dashboard ships the full `IMDB Dataset.csv` (50k rows, 63 MB) committed under
  `assignments/hw7/monitoring/` and copied into its image, so the data-drift and
  target-drift charts compare against the real training distribution from a fresh clone
  with no setup. Decision made explicitly on 2026-06-16 with the 63 MB git-history cost
  accepted. `imdb_sample.csv` stays as the fallback. The root `.gitignore` re-includes
  this one dataset copy through a negation, and every other dataset copy stays ignored.
