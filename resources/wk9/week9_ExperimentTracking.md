---
title: "Experiment Tracking"
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
content_hash: "ab6f17354d3c3356960dc613a1ffd862efbcf9ec60490890483a82db1bb79434"
token_estimate: 719
recommended_chunk_level: "h2"
abstract_for_rag: "- In ML, \" experiment \" refers to a single, unique run of a model training process - Experiment Tracking : the process of saving relevant metadata for each experiment and organizing the experiments."
source_file: "week9_ExperimentTracking.pdf"
type: "pdf"
extracted_via: "docling"
pages: 14
---

# Experiment Tracking

## What is Experiment Tracking?

- In ML, " experiment " refers to a single, unique run of a model training process
- Experiment Tracking : the process of saving relevant metadata for each experiment and organizing the experiments.

## What is Experiment Tracking?

- An ML experiment is a systematic approach to testing a hypothesis , and its relevant metadata contains the experiment's inputs and outputs.
- Examples would be:
- Hypothesis -'If I increase the number of trees, the validation accuracy will increase'
- Inputs -Code, datasets, or hyperparameters
- Outputs -Metrics and models

## Metadata to track:

- Which hyperparameters were used (e.g., learning rate, tree depth, regularization constant),
- Which dataset or data version was used for training,
- The training code version (maybe a Git commit hash or script version),
- Metrics and results (training loss, validation accuracy, confusion matrix, etc.),
- Artifacts produced (the model file, any generated plots or data),
- Environment details (library versions, hardware used, random seed, etc.).

| 5 |
|-----|

## Why do you need to track ML experiments?

- You'll quickly lose sight of what you did in the experiments
- In ML, small changes in input or code can lead to big differences in results, so you need a reliable way to know which change led to which outcome
- Let's you compare results across runs, find the best model, and reproduce those results later.

## Why do you need to track ML experiments?

Helps you answer questions like:

- 'What was the configuration of that one experiment last week that gave 90% accuracy?'
- 'Did increasing the learning rate make things better or worse?

Instead of relying on memory or ad-hoc notes, you have a logged history of all experiments.

## How do you track ML experiments?

Automated tracking with tools is the way to go for anything beyond trivial experiments.

- This means adding code to log information automatically (or using tools that do it for you with minimal setup).

## Popular Tools

## · Weights & Biases (W&B):

- A popular SaaS tool that integrates with many ML frameworks
- Enables logging hyperparams, metrics, model files to W&B and visualize them on a web dashboard.
- MLflow Tracking
- Neptune.ai
- Comet.ml

## What do we gain by tracking experiments?

- Reproducibility & Details
- Comparison & Insights
- Resource Optimization
- Automated Logging & Fewer Mistakes

## Setup

```
import wandb wand.init(project= ' MyProject '
```

## Log Inputs

```
config = wandb.config config.learning_rate = 1e-3
```

## Log Output (such as metrics)

```
wandb.log({ 'acc'
```

```
: accuracy})
```

```
)
```

| 12 |
|------|

## Practical Exercise

- Go to wandb.ai and sign up for a free account.
- Get Your API Key
- Login to W&B: Run this command and paste your API key when prompted:

(in shell)

wandb login
