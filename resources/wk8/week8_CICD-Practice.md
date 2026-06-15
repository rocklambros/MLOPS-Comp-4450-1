---
title: "Practical Demo"
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
content_hash: "a9a4e3fd869224940af359780fc808c8ec2dd863a39bd189b24530f836bbcc4a"
token_estimate: 322
recommended_chunk_level: "h2"
source_file: "week8_CICD-Practice.pdf"
type: "pdf"
extracted_via: "docling"
pages: 6
---

# Practical Demo

CI/CD pipeline on GitHub Actions

## Practical Demo -GitHub Actions

## Steps involved

1. Develop a simple Streamlit app
2. Write test functions
3. Create environment with Docker
4. Write a YAML file (contains GitHub actions workflow)
5. Setup GitHub repo and push
6. Pull from repo for deployment on EC2 (production) server

## How the CI/CD Pipeline Works

## Triggers Pipeline runs on:

- Push to main or develop branches
- Pull requests to main branch

## Test Job :

- Sets up Python environment & installs dependencies
- Runs pytest tests
- Tests Streamlit app startup

## Code Quality Job :

- Runs flake8 linting
- Checks for syntax errors
- Reports code quality metrics

## Components of GitHub Actions

Read in detail on: docs.github.com/en/actions/get-started/understand-github-actions

## The Value Prop?

## · Accelerated Velocity and Productivity :

- Eliminate time-consuming & error-prone manual tasks
- Frees developers' time to focus on critical work

## · Improved Code Quality and Reliability :

- Bugs are detected early -easier, cheaper to fix then
- Results in stable, reliable app for users

## · Reduced Deployment Risk :

- Small, incremental updates reduce risk with each deployment
- Easy rollback and revert reducing faults and downtime
