---
title: "Assignment 5 - Model Monitoring"
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
content_hash: "39d92abd69a076b3bc02b0bf077770031b9ccd4d4fbb79100248181c825c1710"
token_estimate: 638
recommended_chunk_level: "h2"
abstract_for_rag: "Objective: This assignment will introduce you to the MLOps practice of model monitoring . You will build a system that not only serves predictions but also actively monitors the model's performance and data integrity. You will create and run two distinct services-a FastAPI backend and a Streamlit dashboard-as separate Docker containers communicating over a shared network."
source_file: "week7_Assignment5ModelMonitoring.pdf"
type: "pdf"
extracted_via: "docling"
pages: 2
---

# Assignment 5 - Model Monitoring

15 8/11/2026, 11:59:00 PM Points: Due:

Objective: This assignment will introduce you to the MLOps practice of model monitoring . You will build a system that not only serves predictions but also actively monitors the model's performance and data integrity. You will create and run two distinct services-a FastAPI backend and a Streamlit dashboard-as separate Docker containers communicating over a shared network.

Note: This assignment is not based on Week 7 Labs

For this assignment, you need to have:

- A full understanding of the previous assignments covering FastAPI, Streamlit, and Docker.
- You will need the IMDB Dataset.csv and a trained sentiment\_model.pkl file.

Due Date:

11/05/2025

## System Architecture

You will build a multi-container application where two services run independently but communicate with each other:

1. FastAPI Prediction Service: A container running a FastAPI app that serves sentiment predictions and logs every request and response to a shared Docker volume.
2. Streamlit Monitoring Dashboard: A second container running a Streamlit app that reads the logs from the same shared volume to visualize model performance.
3. Docker Volume: A named volume to persist log data and share it between the two containers.

## The FastAPI Prediction Service :

```
This service should: %æ %æ %æ %þ %þ %þ Build a simple FastAPI app with a prediction endpoint: POST /predict . For every request to /predict , your app must log a JSON object to a file named prediction_logs.json located in a /logs directory. Each log entry must be a new line in the JSON file and contain: timestamp request_text predicted_sentiment
```

- : This should be provided by the user through the feedback form (We won't have a frontend with a feedback form in this exercise). All requests will be mad through POSTMAN %þ true\_sentiment

## The Streamlit Monitoring Dashboard

- %æ %æ %æ %æ %æ (In a separate directory) This service should: Include a Streamlit app will that will read and parse the prediction\_logs.json file from the shared /logs directory. The dashboard must display the following monitoring plots: Data Drift Analysis: Create a histogram or density plot comparing the distribution of sentence lengths from your IMDB Dataset.csv against the lengths from the logged inference requests. Target Drift Analysis: Create a bar chart showing the distribution of predicted sentiments from the logs vs trained sentiments Model Accuracy & User Feedback:

From the true\_sentiment logged in the logs %þ
