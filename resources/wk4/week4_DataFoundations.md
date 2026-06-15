---
title: "Data Storage Foundations"
document_id: ""
version: "1"
date: "2025-07-10"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "1df416df6f0d84b4b8f1732e33a5acc34e2f6fdc9a4ccaef850756c47641dbec"
token_estimate: 560
recommended_chunk_level: "h2"
abstract_for_rag: "- Fundamental way to store data on disk as files and directories - Tabular: csv, parquet; Image: JPEG, PNG - Usually refers to disk storage attached to a machine - Files can be read/written with low latency locally - Great for local, small-to-medium data; simple read/write API (e.g., open() in Python)"
source_file: "week4_DataFoundations.pdf"
type: "pdf"
extracted_via: "docling"
pages: 8
---

# Data Storage Foundations

## Filesystems

- Fundamental way to store data on disk as files and directories
- Tabular: csv, parquet; Image: JPEG, PNG
- Usually refers to disk storage attached to a machine - Files can be read/written with low latency locally
- Great for local, small-to-medium data; simple read/write API (e.g., open() in Python)

## Filesystems

- Storing training data locally (e.g., images, audio) is simple and effective
- Many ML frameworks load datasets from files
- However, file storage is more suitable for storing source code and configuration files
- Even smaller, human-readable datasets during the exploratory phase
- Difficult to scale for the massive, unstructured datasets in modern ML

## Filesystems

- Limits - A single-machine filesystem has size limits and doesn't scale out easily
- For very large datasets or multiple consumers, we may need distributed filesystems or other storage.
- Also, concurrency and sharing are limited on local disks.

## Object Storage

- Object storage stores files (objects) in a flat address space via an API
- Often used in cloud and distributed systems
- Like a filesystem accessible over the network, where each object (file) is identified by a key rather than a folder path
- Object storage provides an API over low-level file storage
- Interact with it via HTTP-based calls instead of local file I/O
- Each object can have a unique identifier

## Object Storage (Performance)

- Object storage trades some speed for scalability
- Typically, slightly slower latency than direct disk, but handles huge data volumes
- Virtually unlimited scalability, high durability, and low cost per gigabyte
- Its API-first access model, massive scalability, and cost-effectiveness make it ideal for storing petabyte-scale datasets, including images, videos, audio files, and logs.

## Object Storage (In ML Systems)

- Common in ML for data lakes & model storage (e.g., 'store once, access anywhere' via HTTP)
- In production ML, object stores are used to store large datasets, model checkpoints, and artifacts
- They act as data lakes backing analytics and ML training.
- During training, data is pulled from object storage to compute
- Offers decoupling of compute and storage
