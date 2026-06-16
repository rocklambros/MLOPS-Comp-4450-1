# Movie Review Sentiment Analyzer (Assignment 1)

An end-to-end ML app: a TF-IDF + Multinomial Naive Bayes model trained on the IMDB
50K movie-review dataset, served through an interactive Streamlit web app. Paste in a
review and the app predicts **positive** or **negative** with a confidence score.

## Files

- `train_model.py` - trains the model and writes `sentiment_model.pkl`
- `app.py` - the Streamlit web app
- `sentiment_model.pkl` - the trained model (committed, so the app runs without retraining)
- `requirements.txt` - pinned dependencies

The dataset (`IMDB Dataset.csv`, ~66 MB) is **not** committed. You only need it to retrain.

## Run it locally

- Clone the repo and enter this folder:
  - `git clone https://github.com/rocklambros/MLOPS-Comp-4450-1.git`
  - `cd MLOPS-Comp-4450-1/assignments/hw1`
- Create and activate a virtual environment:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
- Install dependencies:
  - `pip install -r requirements.txt`
- Launch the app (uses the committed model, no training needed):
  - `streamlit run app.py`
- Open the URL Streamlit prints (default http://localhost:8501) and analyze a review.

## Retrain the model (optional)

- Download *IMDB Dataset of 50K Movie Reviews* from Kaggle:
  https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
- Place `IMDB Dataset.csv` in this folder.
- Run: `python train_model.py`
