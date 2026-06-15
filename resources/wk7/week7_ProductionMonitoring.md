---
title: "Model Monitoring in Production"
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
content_hash: "c0a51ad5af93597fc7ab340df4c174bdb258a20dc0b7a8895de292875cb11d52"
token_estimate: 348
recommended_chunk_level: "h2"
source_file: "week7_ProductionMonitoring.pdf"
type: "pdf"
extracted_via: "docling"
pages: 9
---

# Model Monitoring in Production

## How are Models Monitored in Production?

## How are Models Monitored in Production?

1. An architecture that logs model activity and analyzes it continually
- Create a system to capture key data for each prediction -inputs, outputs (predictions), and eventually the true outcome (if available later)
2. A separate monitoring component will then aggregate these logs and compute metrics on them
3. The metrics computed by the monitoring service are then sent to visualization and alerting

## Model Monitoring Lifecycle in Production

## · Deployment:

- Start of a model's 'real life.'

## · Continuous Monitoring :

- Start collecting data from Day One
- Ongoing process, often automated
- Set baseline for normal behaviour

## · Detection of Issues :

- Set Alert Triggers
- E.g., Data drift has become significant OR Accuracy has dropped

## Model Monitoring Lifecycle in Production

## · Diagnosis :

- Perform 'root cause analysis'
- Dashboards may help pinpoint
- E.g., Drift coming from a new product category

## · Data Collections & Feedback Loop :

- Collect new examples and labels
- Maybe get true labels (from human labelers)

## · Model Retraining & Improvement :

- Update the model. Often Automated
- Repeat

## Model Monitoring Lifecycle in Production

Monitor → Detect → Collect → Retrain → Redeploy

## Exercise Using Evidently AI

8

