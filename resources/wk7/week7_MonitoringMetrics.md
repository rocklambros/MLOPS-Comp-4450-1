---
title: "Key Metrics to Monitor"
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
content_hash: "873b9c9bc0f82b90fbaeb0f817f15d7cc2da1cd694e5d1a8de2503edaebbb98b"
token_estimate: 574
recommended_chunk_level: "h2"
abstract_for_rag: "Are the inputs the model sees in production changing relative to the training data?"
source_file: "week7_MonitoringMetrics.pdf"
type: "pdf"
extracted_via: "docling"
pages: 9
---

# Key Metrics to Monitor

## Data Drift (or Feature Drift)

Are the inputs the model sees in production changing relative to the training data?

Refers to changes in the statistical distribution of the input features over time

Ways to Monitor Drift:

- Tracking summary statistics (mean, variance, etc.)
- Compare production vs reference data using statistical tests

Therefore , a significant drift is a leading indicator that the model's performance might degrade

## Data Drift (or Feature Drift)

## Concept Drift

Has the relationship between inputs and outputs changed?

Occurs when the underlying concept the model is predicting changes

For concept drift even if inputs haven't changed much, the expected output for a given input is different now

Ways to detect:

- Usually detected indirectly -e.g., if you observe the model's accuracy dropping when evaluated on fresh data (with ground truth) even if input distribution looks the same → suggests concept drift
- Testing if the model's predictions vs. actuals have changed in a statistically significant way

## Prediction Drift (or Target Drift)

Are the model's outputs shifting in distribution?

Even without true labels, monitoring the distribution of the model's predictions can be insightful

A significant change might warrant investigation to see if it aligns with reality or if the model is misbehaving

## Outcomes & Feedback from Users

- Probably the most valuable metric
- Can be taken as 'True Labels'
- No on-size-fits-all ways: Depends a lot on the product
- Requires familiarity with product management, user experience.

## Data Quality Issues

- Data pipelines can break.
- Pre-processing code might contain bugs.
- As a result, the model can receive erroneous data inputs -and make unreliable predictions.
- E.g., A spike in missing values, constant values, or anomalies in features should be tracked

## Software Health Monitoring

## Software Health Monitoring

- Serving infrastructure (CPU/GPU utilization, memory, throughput) should be monitored too
- E.g., A model might start consuming more memory over time (memory leak or larger input sizes) which could crash your service
- Or latency might increase if the model faces unexpected input sizes
- These typically fall under standard application monitoring
