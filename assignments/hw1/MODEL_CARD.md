# Model card: imdb-sentiment-nb v1.0.0

A binary sentiment classifier for English movie reviews, built for COMP 4450 Assignment 1.
This card follows Mitchell et al. 2019 *Model Cards for Model Reporting* plus an AIBOM
addendum for supply-chain traceability.

**Deployment context:** local, single-user educational demo (a Streamlit app run on a
developer's machine). Not production, not customer-facing, no automated or consequential
decisions. Harms analysis is sized to that low-stakes context; the card states explicitly
what would have to change before any wider use.

## 1. Model details

- **Name / version:** `imdb-sentiment-nb` v1.0.0
- **Architecture:** scikit-learn `Pipeline` = `TfidfVectorizer(ngram_range=(1,2), min_df=5, max_features=20000, sublinear_tf=True, stop_words=None)` -> `MultinomialNB(alpha=1.0)`
- **Task:** binary text classification (`positive` / `negative`)
- **Trained:** 2026-06-15 on the IMDB 50K Movie Reviews dataset
- **Maintainer:** Rock Lambros <rock@rockcyber.com>
- **Repository:** https://github.com/rocklambros/MLOPS-Comp-4450-1 (`assignments/hw1`)
- **Serialized artifact:** `sentiment_model.pkl`, SHA-256 `b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329`
- **License:** MIT (model + code)

## 2. Intended use and out-of-scope use

**In-scope:**
- Classify a single English-language movie review as positive or negative.
- Short-to-medium English review prose, interactively, in a local demo.

**Out-of-scope (explicitly excluded):**
- Non-English text, or domains other than movie reviews (product, medical, legal, financial, social media).
- Any consequential or automated decision about a person (moderation, hiring, eligibility, scoring).
- Treating the confidence score as a calibrated probability (see Section 4).
- Batch or production serving without the evaluation gaps in Sections 4 and 7 first being closed.

## 3. Factors / subgroups

Performance-affecting factors that the available data lets us measure:

- **Input length** (review character count) — measured and reported in Section 7.

Factors we **cannot** measure, because the IMDB corpus carries no such labels:
- Demographic (author age, gender, race), geographic, or temporal subgroups. No fairness
  disaggregation across protected attributes is possible with this dataset. This is a
  documented gap, not an assertion of fairness.

## 4. Metrics + 95% confidence intervals

Two numbers matter and they differ:

| Metric | Value | 95% CI | Basis |
|---|---|---|---|
| **Held-out accuracy** | **0.8796** | **[0.8729, 0.8863]** | stratified 80/20 split, seed 42, n_test = 10,000; same pipeline config |
| Macro F1 (held-out) | 0.8796 | — | same split |
| Resubstitution accuracy | 0.888 | — | shipped artifact, fit on full 50K, no split (optimistic) |

Per-class (held-out):

| Class | Precision | Recall | F1 |
|---|---|---|---|
| negative | 0.8858 | 0.8716 | 0.8786 |
| positive | 0.8736 | 0.8876 | 0.8806 |

- **CIs are bootstrap** (2,000 resamples of the held-out predictions).
- **Important distinction:** the *shipped* `sentiment_model.pkl` was fit on the full 50K with
  no held-out split (per the assignment), so its only direct metric is resubstitution accuracy
  (0.888), which is optimistic. The 0.8796 [0.8729, 0.8863] above is an honest generalization
  estimate of the *same configuration* trained on an 80% split. They are close, as expected for
  a high-bias/low-variance Naive Bayes model.
- **Decision rule:** argmax of class posteriors (effective 0.5 threshold).
- **Calibration:** uncalibrated. Naive Bayes' feature-independence assumption makes
  `predict_proba` overconfident; treat the displayed confidence as a relative score, not a probability.

## 5. Evaluation data

- **Source:** IMDB Dataset of 50K Movie Reviews (Kaggle: `lakshmi25npathi/imdb-dataset-of-50k-movie-reviews`), SHA-256 `dfc447764f82be365fa9c2beef4e8df89d3919e3da95f5088004797d79695aa2`.
- **Evaluation split:** 20% stratified hold-out (10,000 reviews, 5,000 / 5,000) from the same corpus, seed 42.
- **Collection window / license:** the redistributed Kaggle dataset does not state a precise
  collection window; reviews predate the 2011 IMDB dataset publication. License per the Kaggle source.
- **Known biases:** evaluation and training come from the *same* corpus, so the hold-out
  estimate does not measure distribution shift to other review styles, platforms, or time periods.

## 6. Training data

- **Source:** same IMDB 50K corpus (SHA-256 above).
- **n_samples:** 50,000 labeled reviews, balanced 25,000 positive / 25,000 negative.
- **Preprocessing:** drop null `review`/`sentiment`; TF-IDF over unigrams+bigrams; `min_df=5`;
  vocabulary capped at 20,000 features; English stop words deliberately **retained** to preserve
  negation cues ("not good").
- **Known biases:** movie-review domain only; English only; reviewer self-selection bias;
  topic and sentiment-expression conventions specific to IMDB. Not representative of general text.

## 7. Quantitative analyses (disaggregated)

Held-out accuracy by review-length tertile (character count; q33 = 768, q67 = 1,291):

| Length band | n | Accuracy | 95% CI |
|---|---|---|---|
| short (<= 768 chars) | 3,340 | 0.8871 | [0.8769, 0.8976] |
| medium | 3,327 | 0.8834 | [0.8723, 0.8945] |
| long (> 1,291 chars) | 3,333 | 0.8683 | [0.8566, 0.8794] |

**Finding:** a mild, real degradation on long reviews (~1.9 points below short; CIs barely
overlap). Longer reviews tend to mix sentiment, which a bag-of-ngrams model handles poorly.
No demographic/temporal disaggregation is possible (Section 3).

## 8. Ethical considerations, caveats, and recommendations

Given the low-stakes local-demo context, harms are limited, but named concretely:

- **Misuse outside the movie-review domain** — confident-looking but unreliable predictions on
  out-of-domain text. *Mitigation:* the out-of-scope list in Section 2; surface it in the UI.
- **Unmeasured demographic bias** — the corpus may encode reviewer-population and topic biases;
  the model is **not validated for fairness**. *Mitigation:* do not use to judge people; obtain
  subgroup-labeled data and run a fairness audit before any consequential use.
- **Overconfidence** — uncalibrated probabilities could mislead a user who reads the score as
  certainty. *Mitigation:* calibrate (e.g., isotonic/Platt) and relabel the UI score before any
  non-demo use.
- **Optimistic headline metric** — the shipped model's resubstitution 0.888 overstates real
  performance. *Mitigation:* this card reports the held-out estimate as the honest number.

**Recommendations before any non-local deployment:** add a proper train/validation/test split
to the training pipeline; calibrate probabilities; tune the decision threshold against the use
case (`tuning-classification-threshold`); add input-domain and language detection; stand up
drift and subgroup monitoring.

## 9. AIBOM addendum

- **Framework:** scikit-learn 1.9.0
- **Direct dependencies (pinned in `requirements.txt`):** pandas 3.0.3, scikit-learn 1.9.0,
  streamlit 1.58.0, joblib 1.5.3
- **Pretrained backbone:** none (trained from scratch; no external weights)
- **Vocabulary:** learned from the training corpus (no external lookup table)
- **Training-data hash (SHA-256):** `dfc447764f82be365fa9c2beef4e8df89d3919e3da95f5088004797d79695aa2`
- **Model artifact hash (SHA-256):** `b3ba5948ea171da3e9b9d2211d33047b4a15008e76acd53389e238b6e0790329`
- **Build environment:** Python 3.13.7, macOS (Apple Silicon)
- **Recommended follow-up:** generate fully hashed dependency pins (`pip install --require-hashes`) for tamper-evident supply-chain integrity.

## 10. Sign-off

- **Maintainer:** Rock Lambros <rock@rockcyber.com>
- **Review date:** 2026-06-15
- **Next review:** before any deployment beyond the local single-user demo
- **Change log:** v1.0.0 — initial model and card (COMP 4450 Assignment 1)
