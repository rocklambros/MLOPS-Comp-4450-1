---
title: "Model Versioning & Registry"
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
content_hash: "0ce7ef3e082743434d5e8fa53c44e66d0d2a12332f23f972ae58b94071c97160"
token_estimate: 552
recommended_chunk_level: "h2"
abstract_for_rag: "- Model versioning means systematically managing different iterations of a ML model throughout its lifecycle - Every time you train a new model → new version of model - With proper versioning, you can: - Trace back which model produced the results - Reproduce any past experiments - Roll back to previous model (in case of issues)"
source_file: "week9_ModelVersioning.pdf"
type: "pdf"
extracted_via: "docling"
pages: 9
---

# Model Versioning & Registry

## What is Model Versioning?

- Model versioning means systematically managing different iterations of a ML model throughout its lifecycle
- Every time you train a new model → new version of model
- With proper versioning, you can:
- Trace back which model produced the results
- Reproduce any past experiments
- Roll back to previous model (in case of issues)

Image: docs.aws.amazon.com

## What is Model Registry?

- A centralized repo or model store where you keep all your validated models, along with their versions and metadata
- Model entry in the registry typically has:
- A name (e.g., "CustomerChurnModel"),
- Versions (e.g., version v1.0),
- Metadata: training parameters, dataset used, timestamp, metrics, who trained it, etc.,
- Possibly a status or stage (e.g., 'Staging', 'Production', ' Archived')
- The single source of truth for data lineage

## Why use a Model Registry?

- Version Control & Traceability
- Reproducibility (since registry stores model artifacts with metadata)
- Streamlined Deployment (Handy for CI/CD)
- Lifecycle Management (organize models by project or use-case)

## How do we implement them?

In Weights & Biases ecosystem , these concepts are implemented through a powerful and general-purpose abstraction called W&B Artifacts .

An Artifact is a versioned, typed collection of files and directories. It can be used to track:

- Models,
- Datasets,
- Evaluation results,
- Any other file-based asset in the ML workflow

## Initialize a W&B run

```
run = wandb.init(project="mlops-lecture-demo", job_type="training")
```

## Log Inputs

```
model_artifact = wandb.Artifact( "sentiment-model", type="model", description="A simple sentiment analysis model") model_artifact.add_file(model_path)
```

## Log the artifact to run

```
run.log_artifact(model_artifact) run.finish()
```

## The Matter of Fairness & Trust

- Data lineage supports compliance with data privacy and governance regulations, such as GDPR or HIPAA.
- It does that by making it easier to track and manage sensitive data.
- Data lineage helps build trust in AI systems by providing the transparency needed to audit, explain, and continuously improve AI outcomes.
