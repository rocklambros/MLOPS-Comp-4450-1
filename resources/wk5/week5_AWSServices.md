---
title: "AWS Services"
document_id: ""
version: "1"
date: "2025-07-16"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "54f3756f44f3f1435acf2aaf426fd1bef03c46a2c0cfd52c7a21b0dd66914bd3"
token_estimate: 358
recommended_chunk_level: "h2"
source_file: "week5_AWSServices.pdf"
type: "pdf"
extracted_via: "docling"
pages: 5
---

# AWS Services

## Main Service Categories

- Compute: Services that provide processing power: virtual servers, containers, serverless functions.
- Storage: Services to store data, either as objects, files, or block storage
- Databases: Managed DB services; relational and NoSQL + data warehousing.
- Networking: Virtual networks, load balancers, DNS, and content delivery.
- Analytics & Big Data: Tools for data processing and analysis
- Machine Learning: Services for building and deploying ML models

## AWS Compute

## Amazon EC2 :

- Launch virtual servers on demand with variety of OS and configurations
- Full control over the OS level
- Resizable virtual servers, known as "instances," in the cloud
- Easily scale up by launching more instances
- Equivalents → GCP : Google Compute Engine; Azure : Azure Virtual Machines

## AWS Compute

## AWS Lambda :

- AWS's serverless compute service for running small units of code
- Doesn't need management of servers
- Just upload the code and set a trigger
- Functions as a Service (FaaS) -you pay only for execution time and don't worry about underlying servers
- Equivalents → GCP : Google Cloud Functions; Azure : Azure Functions

## AWS Storage

- Object Storage: Amazon S3

- Block Storage: Amazon EBS

- File Storage: Amazon EFS (and FSx)

- Relational Databases: Amazon RDS (plus Aurora)

- NoSQL Databases: Amazon DynamoDB (and others)

- Data Warehousing: Amazon Redshift
