---
title: "Adapting CI/CD for MLOps"
document_id: ""
version: "1"
date: "2025-08-06"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "623567b9b2c9eafa89a793fd66235a0bf228a1f43b4388b82fa755eac0701cf2"
token_estimate: 623
recommended_chunk_level: "h2"
abstract_for_rag: "- Code : Algorithms for model training, serving, feature engineering etc. - Data : For training and validation - Model Parameters : Configuration & hyperparameters"
source_file: "week8_cicd-mlops.pdf"
type: "pdf"
extracted_via: "docling"
pages: 7
---

# Adapting CI/CD for MLOps

A Paradigm Shift

## Why MLOps Needs Its Own CI/CD?

Final product in ML -'Predictions' learned from data

Behavior of an ML System is dictated by:

- Code : Algorithms for model training, serving, feature engineering etc.
- Data : For training and validation
- Model Parameters : Configuration & hyperparameters

Any changes to any of these 3 should trigger a new release cycle

' Change Anything, Change Everything '

## Differences from Traditional CI/CD

## Triggers :

## Traditional SWE

- A code commit (git push)

## MLOps

- Commits (just one of many)
- New data arrival (e.g., a new batch of data is uploaded)
- Detected model performance degradation (a drift)
- A pre-defined schedule for automatic retraining (e.g., retrain every week)

## Differences from Traditional CI/CD

## Testing & Validation:

## Traditional:

- Deterministic → Unit & Integration tests verify code logic
- Clear, binary pass/fail outcomes

## MLOps:

- Probabilistic and multi-faceted → includes several layers of testing:
- Data Validation: Checking data schemas, statistical distributions, and anomalies.
- Model Validation: Evaluate on a holdout set -compare performance against a threshold
- Behavioral Testing: Tests for fairness, robustness to adversarial examples etc.

## Differences from Traditional CI/CD

## Build Stage - Continuous Training (CT):

## Traditional:

- Typically, a fast process of compiling code and packaging it into an artifact
- MLOps:
- Instead, Continuous Training (CT) - complex, automated pipeline
- CT orchestrates the end-to-end process of data ingestion, preprocessing, feature engineering, model training, and evaluation.

## Differences from Traditional CI/CD

## Artifacts:

## Traditional:

- A single, versioned app artifact (like a Docker image)

## MLOps:

- A constellation of versioned artifacts - tracked together for reproducibility.
- A single "build" in MLOps produces - training code, dataset version, feature engineering code, model's hyperparameters, resulting trained model binary, and its evaluation metrics.

## Differences from Traditional CI/CD

## Deployment & Degradation:

## Traditional:

- Software is generally stable - only degrades when new, buggy code is introduced.

## MLOps:

- Almost certainly will, degrade over time even with no code changes .
- Necessitates continuous monitoring of predictions in production and establish a feedback loop that can trigger alerts or automated retraining pipelines.

