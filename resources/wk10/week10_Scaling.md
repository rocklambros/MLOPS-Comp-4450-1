---
title: "Scaling Overview"
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
content_hash: "15a6b70f9c685dcab395b176ba23226ff3b6f7994f8a1eb47295872f1c8b5641"
token_estimate: 948
recommended_chunk_level: "h2"
abstract_for_rag: "- collecting, storing, and transforming large amounts of training data, - collecting and storing large amounts of telemetry data, - processing large numbers of model inference requests, - running large distributed jobs to train models."
source_file: "week10_Scaling.pdf"
type: "pdf"
extracted_via: "docling"
pages: 17
---

Scaling

# Scaling Overview

Systems usually exceed the resources of a single machine Challenges:

- collecting, storing, and transforming large amounts of training data,
- collecting and storing large amounts of telemetry data,
- processing large numbers of model inference requests,
- running large distributed jobs to train models.

## Case Study: Google Photos

4 trillion photos from over a billion users and receive 28 billion new photos per week (that's about 46 thousand photos uploaded per second) -Google Report in 2020

Google Photos provides many ML-powered functions:

- Running object detection to associate images with keywords for search,
- Detecting images that could be cleaned up,
- Suggesting ways of grouping pictures,
- Identifying friends in pictures

## Data Processing at Scale

Discuss 4 main strategies:

1. Services / Microservices
2. Batch Processing
3. Stream Processing
4. Lambda Architecture -combines all 3

## Services/Microservices

- Break system into small, independent modules
- Each service handles one task (e.g., authentication, predictions)
- Optimized for fast response times to individual requests
- Communicate via APIs (REST, gRPC)
- Scalability is achieved by running multiple instances of a service and distributing requests with a load balancer

## Services/Microservices

## Example:

- ML model served as a prediction API
- User account service, payment service, and recommendation service as separate modules

## AWS Services:

- Amazon API Gateway → front door for APIs
- AWS Lambda or Amazon ECS/Fargate → run microservices
- Elastic Load Balancing (ELB) → distribute requests

## Batch Processing

- Performs long-running computations over very large, finite amounts of data.
- Optimized for throughput, not immediate response
- Results are written to data storage for later access.
- Common in ML for:
- Data preparation (ETL)
- Model training on large datasets
- Running inference on huge datasets (e.g., tagging all images)

The classic programming model for this is MapReduce .

## Batch Processing

## Example:

- Process 1 TB of log data every night → generate training dataset for a recommendation model

## AWS Services:

- AWS Batch → runs jobs at scale
- Amazon EMR (Hadoop/Spark) → big data batch jobs

## Stream Processing

- Continuously and incrementally processes data as it arrives from an event stream or message queue.
- Producers send messages to a topic, and Consumers subscribe to that topic to receive and process messages → This decouples the components

## Stream Processing

- Provides near real-time results, with much lower latency than batch processing
- Optimized for handling a continuous, unending flow of data.

## Example:

- Detect anomalies in credit card transactions as they happen
- ML: real-time sentiment analysis on tweets

## Stream Processing

## AWS Services :

- Amazon SQS (Simple Queue Service): A managed message queuing service.
- AWS Lambda : Can be used as a consumer to process events from a stream as they arrive.

## Lambda Architecture

- Combines batch + stream + services
- Batch layer → accurate, large -scale computation
- Speed layer → fast, incremental updates
- Serving layer → provides results to clients (via APIs)
- Balances accuracy, latency, and scalability

## Lambda Architecture

## Example:

- Photo service:
- Batch → retrain friend detection model weekly
- Stream → update with new tags as users add them
- Service → serve predictions to users instantly

## AWS Services:

- Batch layer: EMR (Hadoop/Spark)
- Speed layer: SQS + Lambda
- Serving layer: API Gateway + ECS/Lambda

## Revising Data Processing at Scale

We discussed the 4 main strategies:

1. Services / Microservices
2. Batch Processing
3. Stream Processing
4. Lambda Architecture -combines all 3
