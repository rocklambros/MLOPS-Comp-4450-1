"""dashboard.py - Streamlit model-monitoring dashboard (Assignment 5, hw7).

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Reads the prediction log the FastAPI service writes to the shared Docker volume
(/logs/prediction_logs.json) and visualizes three monitoring signals:

  1. Data drift   - review-length distribution, training data vs live requests.
  2. Target drift - predicted-sentiment mix vs the trained label mix.
  3. Accuracy     - live accuracy and feedback from the logged true_sentiment.

Run inside the container on port 8501, or locally with:

    LOG_PATH=./logs/prediction_logs.json streamlit run dashboard.py
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

import reference_stats
from reference_stats import resolve_reference_path, text_length

HERE = Path(__file__).resolve().parent
LOG_PATH = Path(os.getenv("LOG_PATH", "/logs/prediction_logs.json"))

# The API is reachable by service name on the shared Docker network.
API_URL = os.getenv("API_URL", "http://api:8000")

# Fixed class order so every chart and table lines the two labels up the same way.
SENTIMENTS = ["negative", "positive"]

LOG_COLUMNS = ["timestamp", "request_text", "predicted_sentiment", "true_sentiment"]


@st.cache_data
def load_reference(path_str: str) -> pd.DataFrame:
    """Cached load of the reference distribution (precomputed JSON or raw CSV).

    Cached on the path so the source is read and reconstructed once per session.
    Source resolution and the JSON/CSV dispatch live in reference_stats; both paths
    return the length and sentiment columns the charts below consume.
    """
    return reference_stats.load_reference(path_str)


def load_logs(path: Path) -> pd.DataFrame:
    """Parse the newline-delimited prediction log into a DataFrame.

    Tolerates a missing file (nothing logged yet) and skips any malformed line, so a
    single bad row never blanks the whole dashboard. Read fresh every run so the
    dashboard reflects new predictions on refresh.
    """
    if not path.exists():
        return pd.DataFrame(columns=[*LOG_COLUMNS, "length"])
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=[*LOG_COLUMNS, "length"])
    # Guarantee the expected columns exist so a foreign or partial log degrades to
    # empty cells instead of raising KeyError in the charts below.
    for column in LOG_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    frame["length"] = frame["request_text"].map(text_length)
    return frame


def api_status() -> str:
    """Best-effort health check over the shared network. Never raises."""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        if resp.ok and resp.json().get("status") == "ok":
            return "online"
        return "degraded"
    except requests.RequestException:
        return "unreachable"


st.set_page_config(page_title="Sentiment Model Monitoring", layout="wide")
st.title("Sentiment Model Monitoring")

status = api_status()
badge = {
    "online": "🟢 online",
    "degraded": "🟡 degraded",
    "unreachable": "🔴 unreachable",
}[status]
header_left, header_right = st.columns([3, 1])
header_left.caption(f"Reading predictions from `{LOG_PATH}`")
header_right.metric("Prediction API", badge)

if st.button("Refresh"):
    st.cache_data.clear()
    st.rerun()

reference_path = resolve_reference_path(HERE)
if reference_path is None:
    st.error(
        "No reference distribution found. Expected reference_stats.json next to this app."
    )
    st.stop()
reference = load_reference(str(reference_path))

logs = load_logs(LOG_PATH)
if logs.empty:
    st.info(
        "No predictions logged yet. Send reviews to the API (`POST /predict`) from "
        "Postman or curl, then refresh to populate the charts."
    )
    st.stop()

st.success(
    f"Loaded {len(logs):,} logged prediction(s). "
    f"Reference: {reference_path.name} ({len(reference):,} reviews)."
)

# 1. Data drift ----------------------------------------------------------------
st.header("1. Data drift: review length")
st.caption(
    "Distribution of review length in words, training data vs live requests. A live "
    "distribution that pulls away from training means the model is seeing different "
    "inputs than it learned on, the leading indicator of performance decay."
)
length_left, length_right = st.columns(2)
length_left.metric("Mean length, training", f"{reference['length'].mean():.0f} words")
length_right.metric("Mean length, live", f"{logs['length'].mean():.0f} words")

# Trim the shared x-range to the 99th percentile of the combined lengths so a handful
# of very long reviews do not flatten the histogram, while keeping both series visible.
upper = float(pd.concat([reference["length"], logs["length"]]).quantile(0.99))
fig_drift, ax_drift = plt.subplots(figsize=(8, 4))
ax_drift.hist(
    reference["length"].clip(upper=upper),
    bins=40,
    density=True,
    alpha=0.5,
    label=f"training ({len(reference):,})",
)
ax_drift.hist(
    logs["length"].clip(upper=upper),
    bins=40,
    density=True,
    alpha=0.5,
    label=f"live requests ({len(logs):,})",
)
ax_drift.set_xlabel("review length (words)")
ax_drift.set_ylabel("density")
ax_drift.legend()
st.pyplot(fig_drift)
plt.close(fig_drift)

# 2. Target drift --------------------------------------------------------------
st.header("2. Target drift: predicted sentiment mix")
st.caption(
    "Share of predictions by class, live vs the trained label balance. The IMDB "
    "training set is balanced near 50/50, so a heavy live skew is worth a look."
)
trained_mix = (
    reference["sentiment"]
    .value_counts(normalize=True)
    .reindex(SENTIMENTS, fill_value=0.0)
)
live_mix = (
    logs["predicted_sentiment"]
    .value_counts(normalize=True)
    .reindex(SENTIMENTS, fill_value=0.0)
)
positions = range(len(SENTIMENTS))
width = 0.35
fig_target, ax_target = plt.subplots(figsize=(6, 4))
ax_target.bar(
    [p - width / 2 for p in positions], trained_mix.to_numpy(), width, label="trained"
)
ax_target.bar(
    [p + width / 2 for p in positions],
    live_mix.to_numpy(),
    width,
    label="live predicted",
)
ax_target.set_xticks(list(positions))
ax_target.set_xticklabels(SENTIMENTS)
ax_target.set_ylabel("proportion")
ax_target.set_ylim(0, 1)
ax_target.legend()
st.pyplot(fig_target)
plt.close(fig_target)

# 3. Accuracy and user feedback ------------------------------------------------
st.header("3. Model accuracy and user feedback")
st.caption(
    "Computed only over requests that carried a true_sentiment (the user feedback). "
    "This is live accuracy on real inputs, not the optimistic training score."
)
labeled = logs[logs["true_sentiment"].notna()].copy()
coverage = len(labeled) / len(logs)
if labeled.empty:
    st.warning(
        "No feedback yet. Include a `true_sentiment` field in the /predict request "
        "to measure live accuracy."
    )
else:
    labeled["correct"] = labeled["predicted_sentiment"] == labeled["true_sentiment"]
    acc_col, count_col, cover_col = st.columns(3)
    acc_col.metric("Live accuracy", f"{labeled['correct'].mean():.1%}")
    count_col.metric("Feedback count", f"{len(labeled):,}")
    cover_col.metric("Feedback coverage", f"{coverage:.1%}")

    per_class = (
        labeled.groupby("true_sentiment")["correct"]
        .agg(accuracy="mean", n="count")
        .reindex(SENTIMENTS)
    )
    st.subheader("Per-class accuracy")
    st.dataframe(per_class.style.format({"accuracy": "{:.1%}", "n": "{:.0f}"}))

    st.subheader("Predicted vs true (counts)")
    confusion = pd.crosstab(labeled["true_sentiment"], labeled["predicted_sentiment"])
    confusion = confusion.reindex(index=SENTIMENTS, columns=SENTIMENTS, fill_value=0)
    st.dataframe(confusion)

# Recent activity --------------------------------------------------------------
st.header("Recent predictions")
recent = logs.tail(20)[["timestamp", "predicted_sentiment", "true_sentiment", "length"]]
st.dataframe(recent.iloc[::-1], width="stretch")
