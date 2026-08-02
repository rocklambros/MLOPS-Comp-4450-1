#!/usr/bin/env python3
"""evaluate.py - batch-evaluate the running FastAPI service (Assignment 5, hw7).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Reads the instructor's test.json (or test_data.json, same contents), sends every item
to the running service's POST /predict, and prints a final accuracy score. The service
must already be up:

    make run           # start both containers
    python evaluate.py # score the API over the instructor's test set

Requires only the `requests` library:

    pip install -r requirements-dev.txt

Every request also carries its ground-truth label as `true_sentiment`, so an
evaluation run doubles as feedback traffic and the monitoring dashboard's accuracy
panel populates from it. The label never reaches the model: /predict classifies
`text` alone and logs `true_sentiment` untouched. Pass --no-feedback to send the
text only.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30

# The brief names the test file two different ways: the body says `test_data.json`, the
# link at the end of the PDF says `test.json`. Both ship here with identical contents
# (the instructor's file), and either name resolves, so a grader following either
# reference gets the same run.
TEST_DATA_CANDIDATES = ("test.json", "test_data.json")

# The two labels the model emits. Anything else in the test file is a data error, not
# a model error, so it is reported separately rather than counted as a wrong answer.
VALID_LABELS = {"positive", "negative"}


def default_test_data() -> Path:
    """First of the spec's two filenames that exists next to this script."""
    for name in TEST_DATA_CANDIDATES:
        candidate = HERE / name
        if candidate.exists():
            return candidate
    return HERE / TEST_DATA_CANDIDATES[0]


def load_test_data(path: Path) -> list[dict]:
    """Read and validate the test file.

    The spec's schema is [{"text": ..., "true_label": ...}, ...]. Validating up front
    turns a malformed file into one clear message instead of a flood of confusing
    request failures.
    """
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"error: test data not found at {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON: {exc}") from exc

    if not isinstance(records, list) or not records:
        raise SystemExit(f"error: {path} must be a non-empty JSON array")

    for index, record in enumerate(records):
        if not isinstance(record, dict) or "text" not in record or "true_label" not in record:
            raise SystemExit(
                f"error: {path}[{index}] must be an object with 'text' and 'true_label'"
            )
    return records


def score_one(
    session: requests.Session, api_url: str, record: dict, timeout: int, send_feedback: bool
) -> tuple[str | None, str | None]:
    """Send one record to /predict. Returns (predicted_label, error_message).

    A per-item failure never aborts the run: the caller tallies errors and reports them
    alongside the score, so one bad row does not hide the rest of the results.
    """
    payload = {"text": record["text"]}
    if send_feedback and record["true_label"] in VALID_LABELS:
        payload["true_sentiment"] = record["true_label"]
    try:
        response = session.post(f"{api_url}/predict", json=payload, timeout=timeout)
    except requests.RequestException as exc:
        return None, f"request failed: {exc}"
    if response.status_code != 200:
        return None, f"HTTP {response.status_code}: {response.text[:120]}"
    try:
        return str(response.json()["predicted_sentiment"]), None
    except (ValueError, KeyError) as exc:
        return None, f"unexpected response body: {exc}"


def precision_for(pairs: list[tuple[str, str]], label: str) -> float | None:
    """Precision for one class over (true, predicted) pairs. None if never predicted."""
    predicted_as = [p for _, p in pairs if p == label]
    if not predicted_as:
        return None
    hits = sum(1 for t, p in pairs if p == label and t == label)
    return hits / len(predicted_as)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the running sentiment API against a labeled test file."
    )
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help=f"default: {DEFAULT_API_URL}")
    parser.add_argument(
        "--test-data",
        type=Path,
        default=None,
        help="default: ./test.json, falling back to ./test_data.json",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="per-request seconds")
    parser.add_argument(
        "--no-feedback",
        action="store_true",
        help="send text only, without the ground-truth label (skips dashboard feedback)",
    )
    args = parser.parse_args(argv[1:])

    api_url = args.api_url.rstrip("/")
    test_data_path = args.test_data or default_test_data()
    records = load_test_data(test_data_path)

    # Fail fast with an actionable message rather than N identical connection errors.
    try:
        health = requests.get(f"{api_url}/health", timeout=5)
        health.raise_for_status()
    except requests.RequestException as exc:
        print(f"error: cannot reach the API at {api_url} ({exc})", file=sys.stderr)
        print("hint: start the stack with `make run`, then re-run.", file=sys.stderr)
        return 2

    print(f"Evaluating {len(records)} records against {api_url}/predict")
    print(f"Test data: {test_data_path.name} ({len(records)} records)")
    print()

    pairs: list[tuple[str, str]] = []
    errors: list[str] = []
    skipped = 0

    with requests.Session() as session:
        for index, record in enumerate(records, start=1):
            true_label = record["true_label"]
            if true_label not in VALID_LABELS:
                skipped += 1
                errors.append(f"[{index}] unknown true_label {true_label!r}, skipped")
                continue
            predicted, error = score_one(
                session, api_url, record, args.timeout, not args.no_feedback
            )
            if error is not None:
                errors.append(f"[{index}] {error}")
                continue
            pairs.append((true_label, predicted))
            mark = "ok " if predicted == true_label else "MISS"
            print(f"  {index:>3}/{len(records)} {mark} true={true_label:<8} pred={predicted}")

    print()
    if not pairs:
        print("No records were scored successfully.", file=sys.stderr)
        for line in errors:
            print(f"  {line}", file=sys.stderr)
        return 1

    correct = sum(1 for true, predicted in pairs if true == predicted)
    accuracy = correct / len(pairs)

    print("=" * 52)
    print(f"Scored          : {len(pairs)} of {len(records)}")
    print(f"Correct         : {correct}")
    print(f"ACCURACY        : {accuracy:.2%}")
    for label in sorted(VALID_LABELS):
        precision = precision_for(pairs, label)
        shown = "n/a (never predicted)" if precision is None else f"{precision:.2%}"
        print(f"Precision ({label[:3]}) : {shown}")
    predicted_mix = Counter(p for _, p in pairs)
    print(f"Predicted mix   : {dict(predicted_mix)}")
    print("=" * 52)

    if skipped:
        print(f"\nSkipped {skipped} record(s) with an unrecognized true_label.")
    if errors:
        print(f"\n{len(errors)} record(s) did not score:", file=sys.stderr)
        for line in errors:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
