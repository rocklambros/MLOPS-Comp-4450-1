---
title: "Advanced Topic: MLOps Week 4"
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
content_hash: "a1a67b9b12e79ad40c1cdeff5924171a2d6a3d7c4e28e7b9b5266801659fa3c6"
token_estimate: 361
recommended_chunk_level: "h2"
source_file: "week4_Introduction.pdf"
type: "pdf"
extracted_via: "docling"
pages: 7
---

# Advanced Topic: MLOps Week 4

## Summary from last week

- Fundamentals of Web Architecture -Client-Server
- Why is this architecture useful and relevant for MLOps
- Networking Basics: HTTP, REST, SSH
- Overview of Python Web Frameworks with focus on FastAPI
- Built our first FastAPI app
- Learned about Path, Query and Body Parameters
- Lab: Concurrency and async, Error Handling, Fully-functional Backend

## Agenda for today

- Data Storage and Management for ML in Production
- Data related challenges in ML systems
- Cover Basics of Data Storage
- Go through Database Systems: Relational vs NoSQL
- Architecting Data for Scale
- What are Feature Stores?

## Data Challenges in MLOps

- The success of ML in production heavily depends on how we store, organize, and access data.
- An ML system is not merely an application; it is a data factory
- Data pipelines and storage infrastructure are more complex, more expensive to maintain, and more susceptible to failure
- Choosing the right storage architecture is critical

courtesy: codecademy.com

## Overview

## · Structured vs Unstructured Data:

- structured data (tables, labeled records)
- unstructured data (images, text, logs)

## · Local vs Distributed Storage:

- Start local file systems,
- Then scale up to distributed storage and big data

## · Persistence and Accessibility:

- Might need quick access for inference
- May also need long-term storage for training/analysis

