"""make_examples.py - regenerate the examples.csv sample that backs /example.

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

The full IMDB dataset (IMDB Dataset.csv, ~63 MB) is too large to commit, so /example
ships a small balanced sample instead. This script produces that sample deterministically:
a fixed seed and per-class balancing mean the same seed yields the same rows, so the
committed examples.csv is reproducible provenance rather than an opaque blob.

Usage (needs the full IMDB Dataset.csv next to this script, or pass --source):

    python make_examples.py                 # 100 positive + 100 negative, seed 4450
    python make_examples.py --per-class 250 --seed 7

Uses only the standard library, matching the CSV handling in main.py.
"""

import argparse
import csv
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE / "IMDB Dataset.csv"
DEFAULT_OUTPUT = HERE / "examples.csv"
DEFAULT_SEED = 4450
DEFAULT_PER_CLASS = 100


def build_sample(source: Path, per_class: int, seed: int) -> list[dict[str, str]]:
    """Return a class-balanced, seed-deterministic sample of rows from the source CSV."""
    by_class: dict[str, list[dict[str, str]]] = {"positive": [], "negative": []}
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or {"review", "sentiment"} - set(reader.fieldnames):
            raise ValueError("source CSV must have 'review' and 'sentiment' columns")
        for row in reader:
            label = row.get("sentiment", "").strip().lower()
            if label in by_class and row.get("review"):
                by_class[label].append({"review": row["review"], "sentiment": label})

    rng = random.Random(seed)
    sample: list[dict[str, str]] = []
    for label, rows in by_class.items():
        if len(rows) < per_class:
            raise ValueError(f"only {len(rows)} '{label}' rows available, need {per_class}")
        sample.extend(rng.sample(rows, per_class))
    rng.shuffle(sample)
    return sample


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-class", type=int, default=DEFAULT_PER_CLASS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    if not args.source.exists():
        print(f"error: source dataset not found at {args.source}", file=sys.stderr)
        print("download IMDB Dataset.csv and place it next to this script.", file=sys.stderr)
        return 1

    rows = build_sample(args.source, args.per_class, args.seed)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["review", "sentiment"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output} (seed={args.seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
