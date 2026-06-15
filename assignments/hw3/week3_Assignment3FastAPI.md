---
title: "Assignment 3 - FastAPI"
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
content_hash: "06dce19209fcb8db30bbd2f20d81afb8bd8a6847628c8f25531d9d194e20b32a"
token_estimate: 533
recommended_chunk_level: "h2"
abstract_for_rag: "Objective: In this assignment, you will develop a dedicated API backend. You will wrap your sentiment analysis model (created in assignment 1) in an API using FastAPI. You will then containerize this backend with Docker and prepare it for deployment by pushing it to a GitHub repository."
source_file: "week3_Assignment3FastAPI.pdf"
type: "pdf"
extracted_via: "docling"
pages: 2
---

# Assignment 3 - FastAPI

10 7/14/2026, 11:59:00 PM Points: Due:

Objective: In this assignment, you will develop a dedicated API backend. You will wrap your sentiment analysis model (created in assignment 1) in an API using FastAPI. You will then containerize this backend with Docker and prepare it for deployment by pushing it to a GitHub repository.

## Prerequisites:

- You must have Docker installed and running on your machine.
- You must have a GitHub account and Git installed.
- You should start with the sentiment\_model.pkl from Assignment 1 and the IMDB Dataset.csv file.

Due Date: 12th October, 2025

## Part 1: Building the FastAPI Application

```
1. %æ %æ %æ 2. %æ %æ %æ %æ 3. %æ %æ %æ %æ 4. %æ %æ %æ Your primary task is to create a main.py file that serves your model. The API must provide four distinct endpoints. API Endpoints: Health Check ( /health ) Method: GET Purpose: A simple endpoint to confirm that the API is running. Response: A JSON object, e.g., {"status": "ok"} . Predict Sentiment ( /predict ) Method: POST Purpose: Takes a text input and returns the predicted sentiment. Request Body: A JSON object with a single key, text , e.g., {"text": "This movie was a masterpiece!"} . Response: A JSON object with the predicted sentiment, e.g., {"sentiment": "positive"} . Predict with Probability ( /predict_proba ) Method: POST Purpose: Takes a text input and returns the predicted sentiment along with its confidence score. Request Body: Same as /predict . Response: A JSON object with the sentiment and the probability, e.g., {"sentiment": "positive", "probability": 0.95} . Get Training Example ( /example ) Method: GET Purpose: Returns a random review from the original IMDB training dataset. This is useful for testing the prediction endpoints. Response: A JSON object with a random review, e.g., {"review": "I watched this with my kids and we all loved it."} .
```

Tip: Use Pydantic models to define the structure of your request bodies for robust data validation.

## Part 2: Packaging and Documentation

Once your FastAPI application is working locally, you will package it for distribution.
