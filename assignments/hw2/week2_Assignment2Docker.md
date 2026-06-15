---
title: "Assignment 2 - Docker"
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
content_hash: "d6b695105b8c2dc926ada91aceb1de6f12c6d29c948b58ff6f448d21c5a4af2d"
token_estimate: 558
recommended_chunk_level: "h2"
abstract_for_rag: "Objective: The goal of this assignment is to take the sentiment analysis application you built in Assignment 1 and package it into a standard, reproducible container using Docker. This is a foundational skill for deploying machine learning models in a real-world production environment as mentioned in class. You must have Docker installed and running on your machine for this assignment."
source_file: "week2_Assignment2Docker.pdf"
type: "pdf"
extracted_via: "docling"
pages: 2
---

# Assignment 2 - Docker

10 Points:

7/7/2026, 11:59:00 PM Due:

## Homework Assignment : Packaging Your Streamlit App with Docker

Objective: The goal of this assignment is to take the sentiment analysis application you built in Assignment 1 and package it into a standard, reproducible container using Docker. This is a foundational skill for deploying machine learning models in a real-world production environment as mentioned in class. You must have Docker installed and running on your machine for this assignment.

Due Date: Friday, 26th September. 11.59 pm MT

## Tasks & Project Structure

You will create several new files to containerize your application. When you are finished, your project folder should look like this:

```
. % % % .gitignore % % % Dockerfile % % % Makefile % % % README.md % % % app.py % % % requirements.txt % % % model.pkl
```

```
Step 1: Create a .gitignore file
```

- This file tells Git which files or folders to ignore.
- Create a .gitignore file and add entries for common Python artifacts (e.g., \_\_pycache\_\_/ , .pyc ) and any local environment files (e.g., *.env ).

## Step 2: Create a Dockerfile

- This is the blueprint for building your Docker image.
- Your Dockerfile must perform the following steps:
1. Start from an official Python base image (e.g., python:3.9-slim ).
2. Set a working directory inside the container (e.g., /app ).
3. Copy the requirements.txt file into the container.
4. Install the Python dependencies using pip .
5. Copy the rest of your application files ( app.py ) into the container.
6. Expose the port that Streamlit runs on (default is 8501 ).
7. Define the command ( CMD ) to run the Streamlit app when the container starts.

## Step 3: Create a Makefile

- A Makefile simplifies complex Docker commands into simple ones. This is a common practice in many development teams.
- Your Makefile should provide at least three commands:
- %æ build : This command should build the Docker image and give it a name (e.g., sentiment-app ).
- %æ run : This command should run a container from your image, mapping the container's port to a port on your local machine so you can access the app in your browser.
- : This command should delete the image. %æ clean
