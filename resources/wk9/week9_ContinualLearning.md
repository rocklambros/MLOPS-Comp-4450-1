---
title: "Continual Learning"
document_id: ""
version: "1"
date: "2025-08-13"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "ba70400031912984b8ae7d02f4487f2aa12130af36fc8b74e81f1f62ec3eed26"
token_estimate: 192
recommended_chunk_level: "h2"
source_file: "week9_ContinualLearning.pdf"
type: "pdf"
extracted_via: "docling"
pages: 4
---

# Continual Learning

## CD for ML (Continuous Delivery/Deployment)

- Continuous delivery means automating the deployment of that model to production

## How does model versioning play in?

- At the point of deployment → take the model artifact and register it in the model registry
- Or your deployment step can pull the model from the registry and deploy it
- 'train -> evaluate -> if good, register model version > deploy that version'

## Continual Learning

Continual learning is ' training a sequence of models that can adapt to a continuous stream of data that comes into production ' . - FSDL

The capability of the system to continually update the model as new data arrives or as conditions change, rather than treating model training as a oneand-done task

