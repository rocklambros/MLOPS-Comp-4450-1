"""
app.py - Streamlit front end for the IMDB sentiment-analysis model.

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Run locally with:

    streamlit run app.py

Requires model.pkl (the trained sentiment Pipeline) in the same directory.
"""

from pathlib import Path

import joblib
import streamlit as st

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "model.pkl"


# Cache the model so it loads once and is reused across Streamlit reruns (every widget
# interaction reruns this whole script top to bottom). The assignment (Part 2, Step 3)
# requires @st.cache_data, so that is what we use. Tradeoff worth remembering a year from
# now: @st.cache_data caches by pickling the return value and hands each rerun a fresh
# copy, whereas @st.cache_resource would share one instance with no copy. This Pipeline is
# small (~1.4 MB) and picklable, so the copy cost is negligible and either decorator works.
@st.cache_data
def load_model():
    """Return the trained sentiment Pipeline, or None if the model file is missing."""
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


st.title("Movie Review Sentiment Analyzer")
st.write(
    "Enter a movie review and the model predicts whether it reads as **positive** "
    "or **negative**, with its confidence. The model is a TF-IDF + Multinomial Naive "
    "Bayes pipeline trained on the IMDB 50K dataset."
)

model = load_model()
if model is None:
    st.error(
        "Model file 'model.pkl' not found. "
        "It ships with the container; if running locally, place the trained model here."
    )
    st.stop()

review = st.text_area("Enter a movie review to analyze:", height=160)

if st.button("Analyze"):
    text = review.strip()
    if not text:
        st.warning("Please enter a review before analyzing.")
    else:
        # predict_proba returns probabilities in model.classes_ order (alphabetical:
        # ['negative', 'positive']), not a fixed positive-then-negative order. Pair each
        # class with its probability and look the predicted label up by name, so the
        # confidence stays correct even if the class ordering ever changes.
        probs = dict(zip(model.classes_, model.predict_proba([text])[0]))
        sentiment = model.predict([text])[0]
        confidence = probs[sentiment]

        # Input that tokenizes to nothing the model has seen (punctuation or unknown
        # words only) yields a 0.5/0.5 tie, which argmax would report as a confident
        # "negative". Treat a near-tie as "no signal" rather than a decisive verdict.
        if abs(probs["positive"] - probs["negative"]) < 0.02:
            st.warning(
                "Not enough recognizable words to judge sentiment. "
                "Try a longer review with clearer wording."
            )
        elif sentiment == "positive":
            st.subheader("Predicted Sentiment: Positive \U0001F44D")
            st.success(f"Confidence: {confidence:.1%}")
            st.progress(float(confidence))
        else:
            st.subheader("Predicted Sentiment: Negative \U0001F44E")
            st.error(f"Confidence: {confidence:.1%}")
            st.progress(float(confidence))

st.caption("COMP 4450 - Assignment 1 - TF-IDF + Naive Bayes baseline")
