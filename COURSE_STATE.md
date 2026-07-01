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

- **hw7 monitoring reference data.** The Streamlit monitoring dashboard compares live
  traffic against a *reference distribution*: the review-length histogram (data drift) and
  the sentiment class mix (target drift). Both are aggregates. The dashboard ships
  `reference_stats.json` (11 KB), a precomputed length-count and sentiment-count map built
  from the full 50k-row IMDB set by `reference_stats.py`. It is proven identical to reading
  the raw CSV for every signal the charts consume (row count, mean length, 99th-percentile
  clip, class mix, and the full length multiset), so no chart moves. `imdb_sample.csv` stays
  as the CSV fallback. Regenerate the artifact when the reference data changes:
  `python reference_stats.py "IMDB Dataset.csv" reference_stats.json`.

  This reverses the 2026-06-16 decision to commit the full 63 MB `IMDB Dataset.csv`. That
  copy shipped a permanent blob in git history to carry two aggregates, 300x more data than
  the charts read. On 2026-06-30 the CSV was replaced by the precomputed artifact and purged
  from the `feat/hw7-monitoring` history through a single-commit rewrite and force-push, so a
  fresh clone of the branch no longer pulls the 63 MB blob.
