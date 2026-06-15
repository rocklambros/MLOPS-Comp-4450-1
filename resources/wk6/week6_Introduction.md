---
title: "Advanced Topic: MLOps Week 6"
document_id: ""
version: "1"
date: "2025-07-25"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "32edb6678f239a6e78e764422320bb275ab3c853baa33f04129c9e70c654f8d5"
token_estimate: 252
recommended_chunk_level: "h2"
source_file: "week6_Introduction.pdf"
type: "pdf"
extracted_via: "docling"
pages: 5
---

# Advanced Topic: MLOps Week 6

## Summary from last week

- Fundamentals of Cloud Computing
- Cloud Service Models and Deployment Models
- AWS Services for Compute
- Data Services in AWS
- Brought it all together → ML Workflow with AWS
- Labs: Covered EC2 and Lambda with hands-on exercises

## Agenda for today

- Challenges with deployment
- Aspects to consider while deploying models
- Cloud VM vs Serverless Deployment
- A comprehensive practical exercise on AWS
- Additional deployment related concepts (if time allows)

## Overview

Goal → Serve predictions to end users

For this, we will deploy an ML model as a Web Service

This involves:

- Setting up the necessary infrastructure (using AWS services)
- exposing the model via an API or web interface so that users can interact

## Start with prototyping

A quick way to start your ML System... is... to deploy a Minimum Viable Model

The key is → Keep it simple, add complexity later

Simply: 1) have a basic UI and 2) Put it behind a Web URL

