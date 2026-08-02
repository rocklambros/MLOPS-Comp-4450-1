"""Tests for reference_stats - the precomputed drift-reference distribution.

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>

The precomputed reference must be behaviorally identical to reading the raw IMDB
CSV for the only two signals the dashboard consumes: the review-length multiset
(data-drift histogram) and the sentiment proportions (target-drift bars). If those
match, no chart moves, so these tests pin that equivalence rather than internals.
"""

import json
from pathlib import Path

import pandas as pd
from reference_stats import (
    build_reference_stats,
    load_reference,
    reference_frame_from_stats,
    resolve_reference_path,
    text_length,
)

MINI_CSV = (
    "review,sentiment\n"
    '"a b c",positive\n'
    '"one two three four five",negative\n'
    '"single",positive\n'
    '"two words",negative\n'
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _raw_reference(csv_path: Path) -> pd.DataFrame:
    """The exact frame dashboard.py builds today from the raw CSV."""
    frame = pd.read_csv(csv_path).dropna(subset=["review", "sentiment"])
    frame["length"] = frame["review"].map(text_length)
    return frame


def test_reconstructed_reference_matches_raw_csv(tmp_path):
    csv = _write(tmp_path / "mini.csv", MINI_CSV)
    raw = _raw_reference(csv)

    stats = build_reference_stats(str(csv))
    recon = reference_frame_from_stats(stats)

    # Identical length multiset => identical mean, quantile, and histogram.
    assert sorted(recon["length"].tolist()) == sorted(raw["length"].tolist())
    # Identical sentiment proportions => identical target-drift bars.
    pd.testing.assert_series_equal(
        recon["sentiment"].value_counts(normalize=True).sort_index(),
        raw["sentiment"].value_counts(normalize=True).sort_index(),
    )
    assert len(recon) == len(raw)


def test_stats_counts_sum_to_reference_rows(tmp_path):
    csv = _write(tmp_path / "mini.csv", MINI_CSV)
    stats = build_reference_stats(str(csv))

    assert stats["reference_rows"] == 4
    assert sum(stats["length_counts"].values()) == stats["reference_rows"]
    assert sum(stats["sentiment_counts"].values()) == stats["reference_rows"]


def test_missing_sentiment_rows_dropped(tmp_path):
    # Trailing empty field -> NaN sentiment -> must be dropped, matching raw dropna.
    csv = _write(tmp_path / "mini.csv", MINI_CSV + '"no label here",\n')
    raw = _raw_reference(csv)
    stats = build_reference_stats(str(csv))

    assert stats["reference_rows"] == len(raw) == 4


def test_resolve_prefers_stats_json_over_csv(tmp_path, monkeypatch):
    monkeypatch.delenv("REFERENCE_DATA_PATH", raising=False)
    _write(tmp_path / "reference_stats.json", "{}")
    _write(tmp_path / "IMDB Dataset.csv", MINI_CSV)
    _write(tmp_path / "imdb_sample.csv", MINI_CSV)

    chosen = resolve_reference_path(tmp_path)

    assert chosen == tmp_path / "reference_stats.json"


def test_resolve_env_override_wins(tmp_path, monkeypatch):
    override = _write(tmp_path / "custom.json", "{}")
    _write(tmp_path / "reference_stats.json", "{}")
    monkeypatch.setenv("REFERENCE_DATA_PATH", str(override))

    assert resolve_reference_path(tmp_path) == override


def test_resolve_falls_back_to_sample(tmp_path, monkeypatch):
    monkeypatch.delenv("REFERENCE_DATA_PATH", raising=False)
    sample = _write(tmp_path / "imdb_sample.csv", MINI_CSV)

    assert resolve_reference_path(tmp_path) == sample


def test_load_reference_dispatches_on_suffix(tmp_path):
    csv = _write(tmp_path / "mini.csv", MINI_CSV)
    stats = build_reference_stats(str(csv))
    stats_path = tmp_path / "reference_stats.json"
    stats_path.write_text(json.dumps(stats), encoding="utf-8")

    from_json = load_reference(str(stats_path))
    from_csv = load_reference(str(csv))

    assert "length" in from_json.columns and "sentiment" in from_json.columns
    assert sorted(from_json["length"].tolist()) == sorted(from_csv["length"].tolist())
