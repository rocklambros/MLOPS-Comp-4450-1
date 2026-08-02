"""reference_stats.py - precomputed drift-reference distribution (Assignment 5, hw7).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

The monitoring dashboard needs a *reference distribution* to compare live traffic
against: the review-length histogram (data drift) and the sentiment class mix
(target drift). Both are aggregates. Shipping the full 63 MB IMDB CSV to carry two
aggregates is 300x more data than the charts consume, and it lands permanently in
git history.

This module precomputes those aggregates into a small JSON artifact
(reference_stats.json, tens of KB) and reconstructs a DataFrame from it that is
behaviorally identical to reading the raw CSV for the length and sentiment columns.
Framework-free (no Streamlit) so it stays unit-testable and importable from both the
dashboard and the regeneration CLI.

Regenerate the artifact after the reference data changes:

    python reference_stats.py "IMDB Dataset.csv" reference_stats.json
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd

SCHEMA_VERSION = 1

# Canonical artifact and fallback filenames, resolved next to this module.
STATS_FILENAME = "reference_stats.json"
FULL_DATASET_FILENAME = "IMDB Dataset.csv"
SAMPLE_FILENAME = "imdb_sample.csv"


def text_length(text: str) -> int:
    """Length feature for drift: word count. Simple, robust, and unit-labeled."""
    return len(str(text).split())


def build_reference_stats(csv_path: str) -> dict:
    """Reduce an IMDB reference CSV to length-count and sentiment-count maps.

    Applies the same dropna the dashboard applies so the artifact reflects exactly
    the rows the raw path would have kept. Counts, not raw rows, so the artifact
    stays tiny while preserving the exact multiset the charts consume.
    """
    frame = pd.read_csv(csv_path).dropna(subset=["review", "sentiment"])
    lengths = frame["review"].map(text_length)
    length_counts = lengths.value_counts().sort_index()
    sentiment_counts = frame["sentiment"].value_counts()
    return {
        "schema_version": SCHEMA_VERSION,
        "source": Path(csv_path).name,
        "reference_rows": int(len(frame)),
        # JSON coerces dict keys to strings; reconstruction casts back to int.
        "length_counts": {int(k): int(v) for k, v in length_counts.items()},
        "sentiment_counts": {str(k): int(v) for k, v in sentiment_counts.items()},
    }


def reference_frame_from_stats(stats: dict) -> pd.DataFrame:
    """Rebuild a length/sentiment DataFrame from the precomputed count maps.

    Expands each count map back into a flat column. Both maps derive from the same
    post-dropna frame, so both expand to reference_rows entries and align into one
    frame. The dashboard never joins length and sentiment per row on the reference,
    so row order carries no meaning here.
    """
    lengths: list[int] = []
    for value, count in stats["length_counts"].items():
        lengths.extend([int(value)] * int(count))
    sentiments: list[str] = []
    for label, count in stats["sentiment_counts"].items():
        sentiments.extend([str(label)] * int(count))
    return pd.DataFrame({"length": lengths, "sentiment": sentiments})


def load_stats(path: str | Path) -> dict:
    """Read a reference_stats.json artifact."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_reference(path_str: str) -> pd.DataFrame:
    """Load a reference distribution, dispatching on file type.

    A .json path is a precomputed stats artifact; anything else is a raw CSV read
    the legacy way. Both return a frame carrying the length and sentiment columns
    the dashboard consumes, so the caller does not care which source was used.
    """
    path = Path(path_str)
    if path.suffix == ".json":
        return reference_frame_from_stats(load_stats(path))
    frame = pd.read_csv(path).dropna(subset=["review", "sentiment"])
    frame["length"] = frame["review"].map(text_length)
    return frame


def resolve_reference_path(here: Path) -> Path | None:
    """Pick the reference source, preferring the precomputed artifact.

    Order: explicit env override, then the committed stats JSON (the fresh-clone
    default), then a full CSV if a copy is present for local dev, then the small
    sample. Returns None when nothing is available so the caller can degrade.
    """
    override = os.getenv("REFERENCE_DATA_PATH")
    if override:
        path = Path(override)
        return path if path.exists() else None
    for candidate in (STATS_FILENAME, FULL_DATASET_FILENAME, SAMPLE_FILENAME):
        path = here / candidate
        if path.exists():
            return path
    return None


def _main(argv: list[str]) -> int:
    """CLI: build_reference_stats(csv) -> JSON. Regenerates the shipped artifact."""
    if len(argv) != 3:
        print(f"usage: {Path(argv[0]).name} <input.csv> <output.json>", file=sys.stderr)
        return 2
    _, csv_path, out_path = argv
    stats = build_reference_stats(csv_path)
    Path(out_path).write_text(json.dumps(stats), encoding="utf-8")
    print(
        f"wrote {out_path}: {stats['reference_rows']:,} rows, "
        f"{len(stats['length_counts'])} distinct lengths"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
