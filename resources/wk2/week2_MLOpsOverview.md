---
title: "Advanced Topic: MLOps Week 2"
document_id: ""
version: "1"
date: "2025-06-25"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "3352787becacbb7dc0de591c2897e55378e4a8a5c74c655804498bce9a1f8956"
token_estimate: 668
recommended_chunk_level: "h2"
abstract_for_rag: "- A model that works in a Jupyter Notebook is not a finished product. - ML systems are complex: Code + Models + Data - ML models can degrade in performance: - Data Drift : The statistical properties of production data change. - Concept Drift : The relationship between data features and the target variable changes."
source_file: "week2_MLOpsOverview.pdf"
type: "pdf"
extracted_via: "docling"
pages: 9
---

# Advanced Topic: MLOps Week 2

## MLOps Overview

## The Challenge

- A model that works in a Jupyter Notebook is not a finished product.
- ML systems are complex: Code + Models + Data
- ML models can degrade in performance:
- Data Drift : The statistical properties of production data change.
- Concept Drift : The relationship between data features and the target variable changes.

## Overview

- A set of practices that combines M achine L earning, Dev elopment, and Op eration s
- Leverages DevOps, tailored for unique challenges in ML workflows
- Goal: To automate and streamline the end-to-end machine learning lifecycle.
- Result: Deploy and maintain ML models in production reliably, efficiently, and at scale.

## Core Principles

## · Automation

- Automate every stage → from data ingestion and model training to deployment.
- Reduces manual effort, minimizes human error, and ensures consistency.

## · Version Control

- Track changes in all ML assets: code, data, and models.
- Ensures that every result is reproducible and auditable*.

## · Collaboration

- Fosters close collaboration between data scientists, engineers, and stakeholders.
- Creates a common language and shared responsibility for the ML system.

## Core Principles

- Continuous X (CI/CD/CT/CM)
- CI (Continuous Integration): Automatically test and validate code, data, models
- CD (Continuous Delivery): Automatically deploy validated models to production.
- CT (Continuous Training): Automatically retrain models on new data to keep them fresh.
- CM (Continuous Monitoring): Continuously monitor both operational health and model performance
- Governance & Monitoring
- Manage the entire process for security, compliance, and ethics.
- Monitor for performance degradation, data drift, and other production issues.

## MLOps Lifecycle

## 1. Data Acquisition & Understanding

- I. Gather and Store data

## 2. Data Preparation & Versioning

- I. Collect, clean, validate, and version the data (Automate)
- II. Data version tags

## 3. Model Development & Experiment Tracking

- I. Track all experiments: log parameters, metrics, and model artifacts
- II. Compare runs in dashboard

## MLOps Lifecycle

4. Training & Hyper-parameter Tuning
- I. Checkpoint to model registry
5. Validation & Quality Gates
- I. Add statistical Tests
6. Packaging & Registry
- I. Containerize model + preprocessing in Docker

## MLOps Lifecycle

7. Deployment (CI/CD)
- I. Automation first -pipelines > notebooks
8. Monitoring & Feedback
- I. Monitor system health (latency, errors)
- II. Model performance (drift, accuracy)
- III. Alert if Drift > threshold → automated retraining

The Cycle repeats...

