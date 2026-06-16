"""
train_model.py - Train and serialize the sentiment-analysis model for Assignment 1.

Course:  COMP 4450 MLOps
Owner:   Rock Lambros <rock@rockcyber.com>
Version: 1.0.0

Loads the IMDB 50K movie-review dataset, fits a TF-IDF + Multinomial Naive Bayes
pipeline on the full corpus, and serializes it to sentiment_model.pkl with joblib.
Run once to (re)generate the model file:

    python train_model.py

The dataset is not committed to the repository. Download it first from
https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
and place 'IMDB Dataset.csv' next to this script.
"""

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Resolve paths relative to this file so the script runs from any working directory.
HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "IMDB Dataset.csv"
MODEL_PATH = HERE / "sentiment_model.pkl"


def load_data(path: Path) -> pd.DataFrame:
    """Load the IMDB CSV and validate its shape before training."""
    if not path.exists():
        sys.exit(
            f"ERROR: dataset not found at '{path}'.\n"
            "Download it from https://www.kaggle.com/datasets/"
            "lakshmi25npathi/imdb-dataset-of-50k-movie-reviews and place "
            "'IMDB Dataset.csv' next to this script."
        )
    df = pd.read_csv(path)
    expected = {"review", "sentiment"}
    if not expected.issubset(df.columns):
        sys.exit(f"ERROR: expected columns {expected}, found {set(df.columns)}.")
    return df.dropna(subset=["review", "sentiment"])


def build_pipeline() -> Pipeline:
    """TF-IDF + Multinomial Naive Bayes: a strong, fast baseline for text sentiment."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    # Unigrams + bigrams so a negation like "not good" survives as one
                    # feature. We deliberately do NOT strip English stop words: sklearn's
                    # stop list drops "no", "not", "never", which carry the sentiment.
                    ngram_range=(1, 2),
                    min_df=5,            # drop ultra-rare terms (noise / overfit)
                    max_features=20000,  # cap vocab to keep the committed .pkl small
                    sublinear_tf=True,   # log-scaled term frequency, standard for text
                ),
            ),
            ("clf", MultinomialNB()),
        ]
    )


def main() -> None:
    df = load_data(DATA_PATH)
    X, y = df["review"], df["sentiment"]
    print(f"Loaded {len(df):,} reviews ({y.value_counts().to_dict()}).")

    pipeline = build_pipeline()
    print("Training TF-IDF + MultinomialNB on the full corpus ...")
    pipeline.fit(X, y)

    # Resubstitution accuracy is optimistic (scored on the training data, per the
    # assignment's no-split instruction) but confirms training produced a usable model.
    print(f"Training-set accuracy (optimistic): {pipeline.score(X, y):.3f}")

    # Sanity check on two sentences the model never saw during training.
    for text in (
        "An absolute masterpiece, I loved every minute.",
        "A boring, painful waste of two hours.",
    ):
        pred = pipeline.predict([text])[0]
        proba = pipeline.predict_proba([text]).max()
        print(f"  '{text[:38]}...' -> {pred} ({proba:.1%})")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH.name} ({MODEL_PATH.stat().st_size / 1e6:.1f} MB).")


if __name__ == "__main__":
    main()
