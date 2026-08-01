---
title: "Assignment 5 - Model Monitoring"
document_id: ""
version: "2"
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
extracted_via: "docling, re-extracted by hand 2026-08-01"
pages: 2
---

<!--
EXTRACTION NOTE (2026-08-01)
The original docling pass truncated this document mid-sentence in the "Model Accuracy &
User Feedback" bullet and dropped everything after it. Three graded sections were lost:
the accuracy/precision and alerting requirements, the entire Evaluation Script section,
and the Packaging, Documentation, and Submission sections. The text below is transcribed
from the source PDF (2 pages) so the repository carries the complete requirements. The
content_hash above still refers to the original truncated extraction and is left
unchanged for traceability.
-->

# Assignment 5 - Model Monitoring

Points: 15   Due: 8/11/2026, 11:59:00 PM

Objective: This assignment will introduce you to the MLOps practice of model monitoring.
You will build a system that not only serves predictions but also actively monitors the
model's performance and data integrity. You will create and run two distinct services, a
FastAPI backend and a Streamlit dashboard, as separate Docker containers communicating
over a shared network.

Note: This assignment is not based on Week 7 Labs

For this assignment, you need to have:

- A full understanding of the previous assignments covering FastAPI, Streamlit, and Docker.
- You will need the `IMDB Dataset.csv` and a trained `sentiment_model.pkl` file.

Due Date: 11/05/2025

## System Architecture

You will build a multi-container application where two services run independently but
communicate with each other:

1. FastAPI Prediction Service: A container running a FastAPI app that serves sentiment
   predictions and logs every request and response to a shared Docker volume.
2. Streamlit Monitoring Dashboard: A second container running a Streamlit app that reads
   the logs from the same shared volume to visualize model performance.
3. Docker Volume: A named volume to persist log data and share it between the two containers.

## The FastAPI Prediction Service

This service should:

- Build a simple FastAPI app with a prediction endpoint: `POST /predict`.
- For every request to `/predict`, your app must log a JSON object to a file named
  `prediction_logs.json` located in a `/logs` directory.
- Each log entry must be a new line in the JSON file and contain:
  - `timestamp`
  - `request_text`
  - `predicted_sentiment`
  - `true_sentiment`: This should be provided by the user through the feedback form (We
    won't have a frontend with a feedback form in this exercise). All requests will be mad
    through POSTMAN

## The Streamlit Monitoring Dashboard

(In a separate directory) This service should:

- Include a Streamlit app will that will read and parse the `prediction_logs.json` file
  from the shared `/logs` directory.
- The dashboard must display the following monitoring plots:
  - Data Drift Analysis: Create a histogram or density plot comparing the distribution of
    sentence lengths from your `IMDB Dataset.csv` against the lengths from the logged
    inference requests.
  - Target Drift Analysis: Create a bar chart showing the distribution of predicted
    sentiments from the logs vs trained sentiments
  - Model Accuracy & User Feedback:
    - From the true_sentiment logged in the logs
    - Calculate and display the model's accuracy and precision based on all collected
      feedback.
    - Implement Alerting: If the calculated accuracy drops below 80%, display a prominent
      warning banner at the top of the dashboard using `st.error()`.

## Evaluation Script

This part focuses on creating a script to systematically evaluate your API's performance.

Create the Evaluation Script (`evaluate.py`):

- Create this script in the root directory of your project.
- Use the `test_data.json` file: `[{"text": "...", "true_label": "positive"}, ...]`.
  (Provided at the end of this page)
- Your script must read the file, loop through each item, send the text to the running
  FastAPI service's `/predict` endpoint (e.g., at `http://localhost:8000/predict`), and
  print a final accuracy score.
- You may use the requests library from Python to do this.

## Packaging and Documentation

You will package the entire application using two separate Dockerfiles and a Makefile to
orchestrate them.

1. Two `Dockerfile`s:
   - Create a `api/Dockerfile` for the FastAPI service.
   - Create a `monitoring/Dockerfile` for the Streamlit service.
2. `Makefile`: It must handle
   - `build`, `run`, and `clean` (to stop containers and remove the network/volume).
3. `README.md`: Your README must be updated to explain the new multi-container
   architecture and provide clear, step-by-step instructions on how to use the `Makefile`
   to run the entire stack. It must also include `curl` examples for the API and
   instructions for the `evaluate.py` script.

## Submission

- Create a new public GitHub repository (Please do not use the ones created for previous
  assignments; else you will lose points)

Use this file to provide test inputs through your evaluate.py script (rather than having
to type it all with POSTMAN) --> test.json
