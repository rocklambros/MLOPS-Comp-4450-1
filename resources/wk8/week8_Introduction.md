---
title: "Advanced Topic: MLOps Week 8"
document_id: ""
version: "1"
date: "2025-08-06"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "d389c275cbf6dc3c9a54bc596d57e4542d5c070895bf3eb05e98784403d82103"
token_estimate: 870
recommended_chunk_level: "h2"
abstract_for_rag: "- Concept of Model Monitoring - The importance of monitoring in MLOps cycle - Listed and discussed Key metrics to track - Understood how monitoring happens in production - Went through a sample use-case and practical example - Ongoing assignment to build a monitoring app"
source_file: "week8_Introduction.pdf"
type: "pdf"
extracted_via: "docling"
pages: 14
---

# Advanced Topic: MLOps Week 8

## Summary from last week

- Concept of Model Monitoring
- The importance of monitoring in MLOps cycle
- Listed and discussed Key metrics to track
- Understood how monitoring happens in production
- Went through a sample use-case and practical example
- Ongoing assignment to build a monitoring app

## Agenda for today

- Understand the importance of CI/CD
- Get to learn about CI/CD in traditional SWE
- A brief walkthrough the components of a CI/CD pipeline
- See how we can adapt it for MLOps
- Compare the difference between traditional SWE and MLOps for CI/CD
- Get to know the tools used
- Go through the steps of building a pipeline in MLOps

## Introduction to CI/CD

## Continuous Integration (CI)

- Practice of frequently merging code changes into a central repo → automated builds and tests run to catch issues early
- In a CI pipeline:
- Code commits triggers a build (and compile)
- Run a suite of tests
- This automation of build & test helps with:
- Detect integration problems early
- Avoid the code from breaking

## Continuous Integration (CI)

- Key Activities in CI:
- Code Commit
- Code Analysis
- Build → Compile & Package
- Unit & Integration Tests

## Continuous Delivery (CD)

- Automates the release process:
- Code changes are automatically deployed to staging or testing environment
- The build is now production-ready -can be released on a button push
- CD ensures that software is always in a deployable state -delivery to a production-like environment is fully automated

## Continuous Deployment (Also CD)

- Goes a step further
- Highest level of automation in the software delivery lifecycle
- It automatically deploys every change that passes all stages of the pipeline directly to production - without any human intervention

## A step-by-step walkthrough

## Stage 1: Source/Commit:

- Initiated by a trigger event (developer pushing a code commit to a branch)
- The starting gun for the entire automated process

## Stage 2: Build:

- CI server detects commit and pulls the latest version of the source code.
- It then executes the build process
- Resolves dependencies, compiles code, and packages app into a single, versioned, and deployable artifact

## A step-by-step walkthrough

## Stage 3: Test:

- The primary quality gate . Artifact undergoes tests to ensure its correctness and stability.
- This phase often includes:
- Unit Tests: Verifying individual functions or components in isolation.
- Integration Tests: Ensuring that different modules of the app work together
- Static and Dynamic Security Scans: Analyzing the code, running app for vulnerabilities
- If tests fail → the pipeline halts → feedback sent to team → Marked 'broken'

## A step-by-step walkthrough

## Stage 4: Deploy:

- The validated artifact is ready for deployment.
- In Continuous Delivery → automatically deploy the artifact to a staging environment.
- Undergoes final User Acceptance Testing (UAT) or performance testing
- Then manual trigger deploys it to production
- In Continuous Deployment → automatically pushes the artifact to live production.

## A step-by-step walkthrough

## Stage 5: Monitor & Feedback:

- Once live, it is continuously monitored for operational health, including:
- performance metrics (latency, CPU usage),
- error rates,
- user activity
- Provides crucial feedback loop, alerting teams to issues in production and informing the next cycle of development.

## A step-by-step walkthrough

