---
title: "Advanced Topic: MLOps Week 7"
document_id: ""
version: "1"
date: "2025-07-30"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "3c9fde63e33bf31974d2775ec93738caf1e33116caf58270800ed693e9102063"
token_estimate: 593
recommended_chunk_level: "h2"
abstract_for_rag: "- Challenges with deployment - Aspects to consider while deploying models - Cloud VM vs Serverless Deployment - A comprehensive practical exercise on AWS - EC2 - S3 - DynamoDB"
source_file: "week7_IntroductionToMonitoring.pdf"
type: "pdf"
extracted_via: "docling"
pages: 10
---

# Advanced Topic: MLOps Week 7

## Summary from last week

- Challenges with deployment
- Aspects to consider while deploying models
- Cloud VM vs Serverless Deployment
- A comprehensive practical exercise on AWS
- EC2
- S3
- DynamoDB

## Agenda for today

- Introduce you all to the concept of Model Monitoring
- Emphasize on the importance of monitoring in MLOps cycle
- List and Discuss Key metrics to track
- Understand how monitoring happens in production
- Go through a sample use-case and practical example
- And Quiz (just a refresher)

## Model Monitoring Introduction

## Overview

- Simple Definition → The ongoing process of continuously tracking and analyzing the performance and behavior of ML models in production.
- Focus → model-specific metrics and data quality
- Monitoring ' keeps an eye ' on how well it's predicting on real-world data,
- Monitors ' whether anything has changed that might degrade its performance'

## Overview

Summary of the steps involved:

- Collecting model inputs, outputs, and outcomes over time
- Measuring various indicators (accuracy, errors, data drift, etc.)
- Detect issues early and ensure the model remains accurate and reliable as new data comes in

## Why do you need ML Monitoring?

- Models face changing conditions; degrade performance over time
- Real-world data is not static → behavior shifts, trends emerge, and unforeseen scenarios occur
- Models can silently make poor predictions without throwing errors
- Without continuous monitoring - failures may go unnoticed

## Why do you need ML Monitoring?

Monitoring is therefore essential to:

- Maintain Accuracy : Retrain when the model predictions start to diverge
- Ensure Reliability : Catch 'silent failures' but doesn't crash.
- Prevent Business Loss : Avoid revenue loss if model's decisions deteriorate
- Meet Compliance : (For regulated applications), ensure fairness, safety, or other policy requirements over time

## Why is it Hard?

## · Statistical Complexity

- You need statistical comparisons of data distributions over time
- Mean collecting batches of data and running tests

## · Delayed or Missing Ground Truth

- True outcome is not immediately available e.g., medical diagnosis
- Real-time monitoring is difficult -rely on proxy metrics
- Dynamic Performance Target
- 'Good' Performance is context dependent
- The idea of Silent Failures
