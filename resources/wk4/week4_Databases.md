---
title: "Databases"
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
content_hash: "fd6f599611959ef7c5d5a47d6f3c3d7c8ab10da53e0040ee2f43a9d478111d96"
token_estimate: 952
recommended_chunk_level: "h2"
abstract_for_rag: "- Relational Databases are the workhorses of structured data storage - Structured, table-based storage with strict schema and SQL for queries - Ensure data integrity ( ACID transactions), great for relational data and complex joins"
source_file: "week4_Databases.pdf"
type: "pdf"
extracted_via: "docling"
pages: 14
---

# Databases

## Relational Databases

- Relational Databases are the workhorses of structured data storage
- Structured, table-based storage with strict schema and SQL for queries
- Ensure data integrity ( ACID transactions), great for relational data and complex joins

## Relational Databases

## Examples:

- PostgreSQL -good default choice (open-source, supports JSON, scalable)
- MySQL -also open-source and widely used
- SQLite - for small/local projects

## Relational Databases (In ML Systems)

## Relational Databases (In ML Systems)

- Structured metadata for ML lifecycle
- Includes: Experiment runs, Hyperparameters, Performance metrics
- Model Registry (tags, versioning, deployment status of models)
- Application data that a model's API needs (user profiles, feature logs)
- Business Intelligence on Model Outputs
- Predictions written back to Relational DB for BI analysis and reports

## Relational Databases (In ML Systems)

- Generally advised not to store large binary data (images, etc.) directly in a relational DB;
- Instead store a reference (like a file path or object storage URL)
- Often functions as the control plane for the system.
- Whereas Training data (the data plane ) may reside in object storage
- SQL DB serves as the system of record for the state of the ML lifecycle
- These require the strong consistency guarantees that database can provide

```
import sqlite3 from fastapi import FastAPI app = FastAPI() conn = sqlite3.connect("ml_data.db") @app.get("/patients/{patient_id}") def read_patient(patient_id: int): cur = conn.cursor() cur.execute("SELECT * FROM patients WHERE id=?", (patient_id,)) row = cur.fetchone() return {"patient_id": row[0], "name": row[1], "age": row[2]}
```

7

## NoSQL Databases

- NoSQL - data stores that do not use the traditional relational model
- Developed to handle scenarios where relational DBs may not be the best fit:
- e.g. massive scale, flexible schema, or specialized data types
- Types of NoSQL Databases include:
- Documents stores (e.g. JSON docs)
- Key-value stores,
- Wide-column stores,
- Graph Databases

## NoSQL: Key-Value Stores

- Simplest NoSQL model -like Python dictionary
- Each key is unique and used for fast data retrieval
- Ideal for tasks requiring low-latency data access e.g., Storing Predictions
- Used for caching frequently accessed data (e.g., to speed-up model inference)

## NoSQL: Document Stores

- Store data in flexible, semi-structured documents, typically JSON-like format
- Documents can have nested structures ; can be queried based on the content of any field
- Best when data doesn't fit a rigid schema
- Example use cases:
- User profiles with varying attributes
- Social Media posts and replies/comments

## NoSQL: Wide-Column Stores

- Store data in tables, rows, and dynamic columns
- Flexible - different rows can have different sets of columns
- Optimized for queries over large datasets that retrieve data by column families.
- Excel at handling massive-scale timeseries data, such as metrics from IoT devices or application event logs.

## NoSQL: Graph DB

- Stores entities as nodes and the relationship between nodes as edges
- Optimized for traversing these relationships -uncovers complex patterns/relationships
- Example use cases:
- Recommendation Systems -' customers who bought this product also viewed these other products '
- Fraud Detection
- Knowledge Graphs

## Which model to choose?

## · Data Structure:

- Highly structured with well-defined relationships → favoring SQL
- Semi-structured, unstructured, or rapidly evolving → favoring NoSQL

## · Scalability Requirements:

- Horizontal scaling, need more servers → NoSQL
- Vertical scaling on a single server → SQL
- Query Complexity:
- Complex JOINS across multiple tables? SQL
- Lookups for documents → NoSQL
