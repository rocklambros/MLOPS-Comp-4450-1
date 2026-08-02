"""Launch tests for the Streamlit monitoring dashboard (Assignment 6, Part 1).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>

The brief asks for "at least one simple test for your Streamlit application to
ensure it can launch without errors". One assertion is not enough to mean
anything here, for three reasons found by reading dashboard.py.

1. dashboard.py:161 calls st.stop() when the prediction log is empty, so an
   AppTest run against an empty log stops early and "no exception" is vacuously
   true on a page that rendered almost nothing. Every launch test seeds a log.
2. dashboard.py:265 renders an st.error accuracy alert whenever live accuracy is
   below ACCURACY_ALERT_THRESHOLD. The healthy fixture is therefore 100 percent
   correct, and the alert gets its own test rather than poisoning the launch one.
3. Importing dashboard at module scope would execute the whole Streamlit script
   outside a runtime. The threshold constant is read by parsing the source.

AppTest runs the script in-process and never binds a port, so it cannot prove the
real server starts. The subprocess test covers exactly that and nothing more:
Streamlit answers /_stcore/health before the script finishes, so a healthy probe
proves the process is up, not that dashboard.py rendered.
"""

import ast
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest

HERE = Path(__file__).resolve().parent
APP = HERE / "dashboard.py"

# dashboard.py defaults API_URL to http://api:8000, a Docker-network name that does
# not resolve off the network. requests.get would burn its full 2-second timeout on
# DNS before the script continues. A closed local port fails instantly instead.
UNREACHABLE_API = "http://127.0.0.1:1"

# Generous because a cold CI runner imports pandas, matplotlib, and streamlit.
LAUNCH_TIMEOUT = 60


def _write_log(path, records):
    """Write newline-delimited JSON, the format the API appends and the dashboard reads."""
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def _record(text, predicted, true_sentiment, second):
    return {
        "timestamp": f"2026-08-01T12:00:{second:02d}+00:00",
        "request_text": text,
        "predicted_sentiment": predicted,
        "true_sentiment": true_sentiment,
    }


def _all_correct_records():
    """Every prediction correct, so accuracy is 100 percent and no alert fires."""
    return [
        _record("An absolute masterpiece, I loved every minute of it.", "positive", "positive", 0),
        _record("A boring, painful waste of two hours.", "negative", "negative", 1),
        _record("Beautifully shot with a moving, unforgettable score.", "positive", "positive", 2),
    ]


def _mostly_wrong_records():
    """One of three correct, so accuracy is well below the 80 percent threshold."""
    return [
        _record("An absolute masterpiece, I loved every minute of it.", "positive", "positive", 0),
        _record("A boring, painful waste of two hours.", "positive", "negative", 1),
        _record("The acting was wooden and the plot made no sense.", "positive", "negative", 2),
    ]


@pytest.fixture
def healthy_log(tmp_path, monkeypatch):
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _all_correct_records())
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)
    return log


def _run_app():
    at = AppTest.from_file(str(APP), default_timeout=LAUNCH_TIMEOUT)
    at.run()
    return at


def test_dashboard_launches_without_errors(healthy_log):
    """Part 1: the required launch test, run past both st.stop() branches."""
    at = _run_app()

    assert not at.exception, f"dashboard raised: {at.exception}"
    # Rendering proof rather than mere absence of a traceback. The success banner
    # only renders after the log loads, which is past the st.stop() at line 161.
    assert len(at.success) >= 1
    assert len(at.error) == 0


def test_dashboard_renders_the_accuracy_alert_when_accuracy_is_low(tmp_path, monkeypatch):
    """The alert path, which is a graded hw7 behavior and the reason the healthy
    fixture above is 100 percent correct."""
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _mostly_wrong_records())
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = _run_app()

    assert not at.exception
    assert len(at.error) >= 1
    assert "accuracy" in " ".join(str(e.value) for e in at.error).lower()


def test_dashboard_handles_logs_with_no_feedback(tmp_path, monkeypatch):
    """The degraded state a freshly deployed host is in: predictions logged, no
    true_sentiment supplied, so the drift charts render and accuracy has nothing
    to measure."""
    log = tmp_path / "prediction_logs.json"
    _write_log(
        log,
        [
            {
                "timestamp": "2026-08-01T12:00:00+00:00",
                "request_text": "An absolute masterpiece, I loved every minute of it.",
                "predicted_sentiment": "positive",
                "true_sentiment": None,
            }
        ],
    )
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = _run_app()

    assert not at.exception


def test_dashboard_stops_cleanly_when_no_predictions_are_logged(tmp_path, monkeypatch):
    """An empty log is an informational state, not a crash."""
    log = tmp_path / "prediction_logs.json"
    log.write_text("", encoding="utf-8")
    monkeypatch.setenv("LOG_PATH", str(log))
    monkeypatch.setenv("API_URL", UNREACHABLE_API)

    at = _run_app()

    assert not at.exception
    assert len(at.info) >= 1


def test_accuracy_alert_threshold_is_the_spec_value():
    """hw7's spec set an 80 percent alert threshold. Pin it so a refactor cannot drift it.

    Read by parsing the source rather than importing: `import dashboard` would execute
    the whole Streamlit script outside a runtime.
    """
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    threshold = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ACCURACY_ALERT_THRESHOLD":
                    threshold = ast.literal_eval(node.value)

    assert threshold == 0.80


def _free_port():
    """Bind port 0 and let the OS choose, so a busy 8501 cannot fail the run."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_streamlit_server_boots_and_serves_health(tmp_path):
    """Boot proof. AppTest never binds a port, so this covers what it cannot.

    Proves only that the Streamlit process starts and serves its health endpoint.
    Streamlit answers /_stcore/health before the script body finishes, so this does
    NOT prove dashboard.py rendered. The AppTest cases above cover that.
    """
    log = tmp_path / "prediction_logs.json"
    _write_log(log, _all_correct_records())
    port = _free_port()

    env = {**os.environ, "LOG_PATH": str(log), "API_URL": UNREACHABLE_API}
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(APP),
            # Without headless, Streamlit blocks on an interactive email prompt and
            # the CI job hangs until its timeout.
            "--server.headless", "true",
            "--server.port", str(port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + LAUNCH_TIMEOUT
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                output = proc.stdout.read().decode("utf-8", "replace")
                pytest.fail(f"streamlit exited early with {proc.returncode}:\n{output}")
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/_stcore/health", timeout=1)
                if resp.status_code == 200:
                    return
            except requests.RequestException:
                time.sleep(0.5)
        pytest.fail(f"streamlit did not serve /_stcore/health within {LAUNCH_TIMEOUT} seconds")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        # Close the pipe explicitly. Leaving it to the garbage collector raises a
        # ResourceWarning, which pytest.ini's filterwarnings=error turns into a failure.
        if proc.stdout is not None:
            proc.stdout.close()
