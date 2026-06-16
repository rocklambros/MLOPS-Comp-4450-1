# Final Project

A full-stack machine learning application deployed to the cloud. Worth 20 percent of the course grade and built entirely on the labs and homework assignments that come before it.

## What it has to demonstrate

The project ties the course together: a trained model served behind a web application and RESTful API, packaged in containers, backed by a data store, deployed to a cloud platform, and instrumented for monitoring. Treat it as a production system, not a notebook.

## Layout

Build the project out in this directory once the brief releases (around week 9). A typical split:

```
final-project/
  model/          training and evaluation
  app/            FastAPI app and REST API
  infra/          containerization and deployment config
  docs/           architecture notes and the project writeup
```

Pull working pieces forward from `../labs/` and `../assignments/` rather than starting from scratch. Keep cloud credentials and large model artifacts out of the repo per [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## Safe model loading

The brief has the backend load a registered model version from the model registry (Weights & Biases), then deploy on EC2. That load is a trust boundary the earlier assignments never crossed: the artifact now arrives over the network into a process that holds the EC2 instance's IAM role. `joblib.load` and `pickle.load` execute code embedded in the file at load time, so a poisoned artifact means remote code execution in the API process, which hands an attacker the instance role credentials and a path into the cloud account.

Decide the loading strategy before wiring Phase 1 (registry) to Phase 2 (backend), not after:

- Prefer a non-pickle format for the sklearn model. `skops` (`skops.io.dump` / `skops.io.load` with a `trusted` allowlist) is the sklearn-safe serialization Hugging Face recommends, and it removes the deserialization-RCE class outright. `safetensors` does not apply here: it serializes tensors, not a Pipeline with a vocabulary.
- If the registry hands back a pickle, pin the exact artifact version (the W&B artifact digest), verify its SHA-256 against the value recorded in the model card before loading, and load only from your own private registry.
- Never load a third-party or unverified artifact without scanning and sandboxing it (a separate process with no network and no credentials).
- Gate on provenance: record the artifact digest in the model card and AIBOM, and verify it before load.

This is the AI supply-chain risk, and the model registry is where to enforce it. Note that the earlier `assignments/hw1` model stays on `joblib`/`.pkl` on purpose: that assignment requires it, and the artifact there is a trusted file committed to the repo and loaded from a fixed path, so the same risk does not apply.
