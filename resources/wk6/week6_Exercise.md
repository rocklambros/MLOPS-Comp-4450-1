---
title: "Comprehensive Exercise"
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
content_hash: "29a5c8f917aa251cc6f3c6445b9f8709a816203ee5e4d102618356e6e230dbf5"
token_estimate: 1265
recommended_chunk_level: "h2"
abstract_for_rag: "- An ML-powered web-service that can handle multiple user requests at once - Train a model on large dataset (Batch Process) - Deploy the model for real-time inference via a web API - Build a simple Streamlit client interface (only for frontend) - Caching strategies for improving system performance"
source_file: "week6_Exercise.pdf"
type: "pdf"
extracted_via: "docling"
pages: 20
---

# Comprehensive Exercise

Building a Recommender System

## Exercise

Deploy a Sentiment Analysis model on AWS

Services to be used: EC2, S3, Lambda and DynamoDB

- An ML-powered web-service that can handle multiple user requests at once
- Train a model on large dataset (Batch Process)
- Deploy the model for real-time inference via a web API
- Build a simple Streamlit client interface (only for frontend)
- Caching strategies for improving system performance

## Overall Workflow

## Train the model (Locally or Cloud)

1. Write a training script for sentiment analysis model
2. Enable the script to save the model
3. Run it:
1. Locally on your machine
2. AWS EC2 instance (preferably with Docker)

## Overall Workflow

## Deploy Model

Load the model on an S3 Bucket

- Instructions to create S3 bucket:
- From AWS Console, choose Services → S3 (under Storage ) → Buckets dashboard.
- Create a bucket to store models (if you don't already have one) → Click Create bucket
- Fill Bucket name -enter a globally unique name
- Pick AWS Region -the same as you'll use for other services in this project
- Leave ACLs disabled and Block all public access (recommended).
- Default encryption -choose SSE-S3 (AWS-managed keys) for at-rest encryption.
- Click Create bucket .

## Deploy Model

- Upload the model file
- Inside the bucket, click Upload .
- Add files → browse to and select model file
- Select Storage class -keep Standard (default)
- Encryption -inherit the bucket default.
- Other settings can remain default.
- Click Upload
- Record the object's URI
- After upload, click the file name in the bucket listing to view Object overview
- You will use the following identifiers later: Key, S3 URI, HTTPS URI

## Overall Workflow

## Create Web Service

- Create a FastAPI application with Model loading and Endpoints
- Understand the boto3 SDK for loading directly from S3
- Create a requirements.txt file
- Create the Dockerfile
- Create an IAM Role for EC2 → Next Slide
- Your EC2 instance needs permission to read from S3

## IAM Role for EC2

Your EC2 instance needs permission to read from S3 and write to DynamoDB.

1. Go to the IAM service in the AWS Console.
2. Navigate to Roles and click "Create role" .
3. For "Trusted entity type" , select " AWS service" .
4. For "Use case" , select "EC2" and click "Next" .
5. On the " Add permissions" page, search for and add the following policy:
- AmazonS3ReadOnlyAccess
6. Click "Next" , give the role a name, and click "Create role" .

## Launch EC2

- Go to the EC2 service in the AWS Console and click "Launch instance" .
- AMI : Search for and select Ubuntu . Choose a recent LTS (Long-Term Support) version, such as Ubuntu Server 22.04 LTS .
- Instance Type : Choose t2.micro (this is eligible for the free tier).
- Key Pair : Select an existing key pair or create a new one.
- Network settings → Click "Edit" → In the Security group , create a new one with the inbound rules:
- Rule 1 : Type SSH, Source My IP.
- Rule 2 : Type Custom TCP, Port 8000, Source Anywhere-IPv4.
- Advanced details --> Expand section and find "IAM instance profile' → Select the Role created earlier
- Click "Launch instance"

## Connect EC2 through SSH

- Follow the instructions on the "SSH client" tab to connect from your local terminal
- Update Packages and Install Docker (script attached with Lecture)
- Transfer Your Project Files
- scp -i <path-to-your-key-pair.pem> -r <local-folder> ubuntu@<YOUR\_EC2\_PUBLIC\_IP>:/home/ubuntu/

## Running application with Docker

## · Build the Docker Image:

```
docker build -t sentiment-api .
```

- Run Docker container:

```
docker run -d -p 8000:8000 \ -e BUCKET_NAME="YOUR_S3_BUCKET_NAME" \ -e MODEL_KEY="models/imdb_sentiment_model.pkl" \ --name sentiment-container \ sentiment-api
```

## Additional Docker Instructions

## To check logs:

docker logs sentiment-container

## To stop the detached container:

docker stop sentiment-container

## To start it again:

docker start sentiment-container

## To stop and remove:

docker rm -f sentiment-container

## Test it with POSTMAN

POST request on http://<YOUR\_EC2\_PUBLIC\_IP>:8000/predict/

## Overall Workflow

## Deploy Streamlit on EC2 (Client Interface)

- Create Streamlit app, with requirements and Dockerfile
- Setup AWS EC2 for Steamlit:
- Only difference → Add Custom TCP rule to expose port 8501
- SSH into the server and install Docker
- Transfer files using SSH
- Build and Run the container

## Running application with Docker

- Build the Docker Image:
- Run Docker container:

```
docker build -t streamlit-frontend-app .
```

```
docker run -d -p 8501:8501 \ -e FASTAPI_URL="http://<YOUR_FASTAPI_EC2_PUBLIC_IP>:8000/predict/" \ --name streamlit-container \ streamlit-frontend-app
```

## Overall Workflow

## Cache with DynamoDB

- Updated main.py file
- Updated Docker command

```
docker run -d -p 8000:8000 \ -e BUCKET_NAME="YOUR_S3_BUCKET_NAME" \ -e MODEL_KEY="models/imdb_sentiment_model.pkl" \ -e DYNAMODB_TABLE_NAME="sentiment-predictions" \ --name sentiment-container \ sentiment-api
```
