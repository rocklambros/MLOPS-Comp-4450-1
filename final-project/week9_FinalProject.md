---
title: "Final Project"
document_id: ""
version: "1"
date: "2026-06-15"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "103aab5fb3f2362e111c79652211840d90cca62197328dc551b727748caf7ef3"
token_estimate: 1217
recommended_chunk_level: "h2"
abstract_for_rag: "This is the Final project for this course. Your goal is to design, build, and deploy a complete, end-to-end machine learning application that incorporates best practices from across the MLOps lifecycle you learned in the class. You will be responsible for everything from model experimentation and versioning to automated testing, deployment on AWS, and live monitoring."
source_file: "week9_FinalProject.pdf"
type: "pdf"
extracted_via: "docling"
pages: 3
---

# Final Project

25 8/18/2026, 11:59:59 PM Points: Due:

## Final Course Project : Building a Production -Grade MLOps System

This is the Final project for this course. Your goal is to design, build, and deploy a complete, end-to-end machine learning application that incorporates best practices from across the MLOps lifecycle you learned in the class. You will be responsible for everything from model experimentation and versioning to automated testing, deployment on AWS, and live monitoring.

You are recommended to work in pairs.

Due Date: August 18th, 2026

## Project Overview

You are tasked with building a production-ready ML service. You have the freedom to one of the 4 given problems, but the system you build must meet a rigorous set of technical requirements.

## Core System Requirements

Your final system must be a multi-component application that includes the following, all deployed on AWS:

1. Experiment Tracking & Model Registry: A system to log experiment parameters/metrics and manage model versions.
2. ML Model Backend: A FastAPI application to serve your registered model.
3. Persistent Data Store: A cloud-native database (SQL or NoSQL) for storing prediction logs, user feedback, or other relevant data.
4. Frontend Interface: A user-facing application for interacting with your model.
5. Model Monitoring Dashboard: A dashboard to visualize model performance and data drift in production.
6. CI/CD Pipeline: An automated workflow to test and validate code changes.

## Phase 1: Experimentation and Model Management

## · 1.1. Model Development:

%æ Choose a dataset and train a baseline machine learning model.

## · 1.2. Experiment Tracking:

%æ Integrate an experiment tracking tool like Weights & Biases .

- %æ Log all relevant information for each training run: code version (Git commit), hyperparameters, performance metrics (e.g., accuracy, F1-score), and data versions.

## · 1.3. Model Versioning & Registry:

%æ Save your trained models as artifacts within your experiment tracking tool.

- %æ Use the Model Registry feature to version your models. Promote your best-performing model to a "Staging" or "Production" stage.

## Phase 2: Backend API and Database Integration

## · 2.1. FastAPI Backend:

%æ Create a robust FastAPI application.

- %æ This API must load a specific model version (e.g., the latest "Production" model) from your Model Registry and serve predictions.

## · 2.2. Cloud Database:

%æ %þ %þ Choose and set up a managed database on AWS. SQL Option: AWS RDS (e.g., PostgreSQL). NoSQL Option: Amazon DynamoDB .

%æ Your FastAPI service must connect to this database to log every prediction request, its output, and a timestamp. This will be used for monitoring. Your FastAPI service can also cache some predictions to avoid making predictions on frequent requests. E.g., store recommendations for frequent users to DynamoDB and pull recommendations from the store if they already exist for a user.

## Phase 3: Frontend and Live Monitoring

- 3.1. User Interface:

%æ Build a user-facing frontend.

%þ Option A (Recommended): A Streamlit dashboard.

- %þ Option B (Advanced): A React-based interface.

%æ The frontend should allow a user to send data to your FastAPI backend and see the model's prediction.

## · 3.2. Model Monitoring Dashboard:

%æ This should be a separate frontend application (on a different EC2 server - data will be exchanged through a Database, not JSON files)

%æ The dashboard must connect to your cloud database (RDS/DynamoDB) and visualize key monitoring metrics from the prediction logs, such as:

- %þ Prediction latency over time.
- %þ Distribution of predicted classes (target drift).
- %þ A mechanism to collect user feedback on model predictions to calculate live accuracy.

## Phase 4: Testing and CI/ CD Automation

- %æ %æ · %æ %æ 4.1. Comprehensive Testing: Unit Tests: Write tests for individual functions (e.g., data preprocessing logic). Integration Tests: Write tests for your FastAPI endpoints to ensure they work as expected. Use pytest . 4.2. CI/CD Pipeline: Set up a GitHub Actions workflow ( .github/workflows/ci.yml ). The workflow must automatically trigger on pull requests to the main branch.
- %æ It must run a linter (e.g., flake8 or ruff ) and execute your full test suite ( pytest ). A pull request cannot be merged if these checks fail.

## Phase 5: Containerization and Deployment

- 5.1. Docker Packaging:

%æ Containerize your application components (e.g., one container for the FastAPI backend, one for the frontend).

- 5.2. AWS Deployment:

%æ Deploy your containerized application to separate EC2 instances with Docker installed.

- 5.3. Documentation:

%æ Create a high-quality README.md in your GitHub repository. It must be a complete guide to your project, including setup instructions, deployment steps, and example requests by user.
