---
title: "Distributed ML Algorithm"
document_id: ""
version: "1"
date: "2025-08-23"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "df1d8a3a8aa2aafd6701450b7066c05a0e9ac2ec7f0ca7a568c1a7a7a74ce4a9"
token_estimate: 586
recommended_chunk_level: "h2"
abstract_for_rag: "- The practice of training ML models across multiple machines (nodes) working in coordination."
source_file: "week10_DistributedML.pdf"
type: "pdf"
extracted_via: "docling"
pages: 9
---

# Distributed ML Algorithm

## Distributed Machine Learning (ML)

## What is Distributed Machine Learning (ML)?

- The practice of training ML models across multiple machines (nodes) working in coordination.

## Why do we need it?

- The Data is Too Big (Data Parallelism)
- The Model is Too Big (Model Parallelism)

Primary Goal: To drastically reduce the time it takes to train a model by dividing the work. What might take a year on one machine can be done in days or weeks.

## Approach 1: Data Parallelism

## Concept :

- You make a copy of the entire model on each worker machine
- Then, split the massive dataset into smaller chunks and give one chunk to each worker

Simple Example: Training a model to detect cats in 10 million images using 10 worker machines . Each machine gets a copy of the cat-detector model and 1 million unique images .

## Approach 1: Data Parallelism

## How it Works (Parameter Server Model):

- Each worker trains its copy of the model on its unique slice of data.
- This training computes "updates" (gradients) that suggest how the model should improve.
- The workers send these updates to a central "parameter server."
- The server averages all the updates and applies them to the master model.
- The newly updated model is sent back to all the workers, and the process repeats.

Image: Anyscale.com

## Approach 2: Model Parallelism

## Concept :

- Used when the model itself is too big for one machine's memory
- You split the model , not the data, across multiple workers

Simple Example: Training a massive 96-layer language model (like GPT-3). You could put layers 1-48 on GPU 1 and layers 49-96 on GPU 2. The data flows through GPU 1 and then to GPU 2 in a pipeline.

## Approach 2: Model Parallelism

## How it Works (Pipeline Parallelism):

- Different layers of a deep neural network are placed on different machines.
- A batch of data goes into the first set of layers on Machine 1.
- The output from Machine 1 is passed over the network to become the input for the layers on Machine 2.
- This continues down the line until the final prediction is made. The process then reverses to update all the model parts.

Image: Anyscale.com

## Tools and Frameworks for Distributed ML

- Deep Learning Frameworks (Integrated Support)
- PyTorch
- Tensorflow
- Big Data Platforms
- Apache Spark Mllib

