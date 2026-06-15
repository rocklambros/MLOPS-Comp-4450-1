---
title: "Storage for Big Data"
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
content_hash: "7015ab1c49df8a10d4f67f2423e4fd287af4c72c6fa0577e6d138ec4c5715f55"
token_estimate: 570
recommended_chunk_level: "h2"
abstract_for_rag: "- Central Analytical DB for aggregated, historical data - Optimized for BI and analytics at scale - Warehouses store large volumes of structured data - often integrating data from many sources - Data is processed through ETL before stored - Ensures data consistency -offering single source of truth - ML uses : source of engineered features (e.g."
source_file: "week4_BigData.pdf"
type: "pdf"
extracted_via: "docling"
pages: 10
---

# Storage for Big Data

## Data Warehouses

- Central Analytical DB for aggregated, historical data
- Optimized for BI and analytics at scale
- Warehouses store large volumes of structured data - often integrating data from many sources
- Data is processed through ETL before stored
- Ensures data consistency -offering single source of truth
- ML uses : source of engineered features (e.g., summary stats), evaluating model outcomes over large historical data

3

## Data lakes

- Data lake is a vast, centralized repo that stores all organization's data
- Stores structured, semi-structured, and unstructured data -in its raw, native format.
- It is typically built on top of low-cost object storage
- Data is loaded first and transformed later as needed
- To explore raw insights in ML, dumping data for training

## Feature Stores

- Central hub for ML features -compute once, use for both training and inference
- Ensures consistency - no mismatch between features used to train vs serve

## Feature Stores

- Typically includes an offline store (bulk feature storage for model training) and online store (real-time feature service)
- Low-latency feature serving for live models
- In MLOps : Feature reuse & governance, faster model iteration

## Bringing it all together

- Raw data from various sources → Data Lake (built on Object Store)
- ETL pipeline processes and moves structured data into → Data Warehouse (for BI)
- Another pipeline feeds this to → Feature Store (For Training and Inference)
- Model trained from Offline Store and Data Warehouse; queries online store for low-latency predictions
- Predictions and cached data can be stored in another NoSQL key-value store

## Final Takeaway

- Filesystem/Object storage → great for bulk data, cold storage, unstructured files.
- Relational DB → great for structured, transactional data and small -scale feature serving.
- NoSQL DB → great for scalability and flexible data, especially in real -time serving contexts.
- Data Warehouse → great for analytics and integrating data for insights or feature building.
- Data Lake → great for retaining everything and feeding the rest of the pipeline.
- Feature Store → purpose -built for ML needs, ensuring the right data is at the right place for training vs inference.
