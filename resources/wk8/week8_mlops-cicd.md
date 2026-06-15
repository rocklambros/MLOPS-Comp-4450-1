---
title: "MLOps Pipeline with CI/CD"
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
content_hash: "74f0b25386364d515f512c9fda9365003d27a49ca7be811311069fe31757890e"
token_estimate: 471
recommended_chunk_level: "h2"
source_file: "week8_mlops-cicd.pdf"
type: "pdf"
extracted_via: "docling"
pages: 7
---

# MLOps Pipeline with CI/CD

## CI for ML

## A. Code & Environment Validation (The Sanity Check) :

- Focuses on the static components of the ML system -the code and its dependencies
- Includes:
- Standard software quality checks
- Linting, bug analysis, unit tests
- E.g., pytest script testing clean\_text() function in sentiment app
- Also includes environment validation (Docker build correctly?)

## CI for ML

## B. Data Validation (Quality Gate) :

- Involves running a series of automated checks, or "tests," against a dataset to ensure it conforms to expectations.
- Key Checks to Perform:
- Schema Validation
- Integrity & Format Check
- Distribution Checks

## CI for ML (Great Expectations)

## CI for ML

## C. Model Validation (Performance Gate) :

- An automated evaluation stage that assesses the newly trained "challenger" model's performance from multiple angles
- Key checks:
- Performance against Baseline
- Performance on critical data slices
- Fairness & Biasness Evaluation
- Model Training Process Validation
- E.g., 'workflow fails if the new model's F1 -score on the 'negative' class is more than 5% lower than the production model's F1score on the same data slice'

## CI for ML

## Continuous Training (CT) :

- A multi-step pipeline that takes code and data as input and produces a trained, validated model as output.
- Workflow:
1. Fetch Versioned Data
2. Data Preprocessing & Feature Engineering
3. Model Training
4. Model Evaluation
5. Model Registration

## Continuous Delivery (CD) for ML

Continuous Delivery for ML is the process of taking a validated model from the CI/CT pipeline and deploying it reliably and safely into production

## The Model Registry: The Heart of ML CD :

A specialized db and artifact store that provides versioning, metadata storage, and stage management for ML models.

Learn more about it in the next class → MLflow
