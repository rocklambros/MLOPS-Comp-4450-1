---
title: "Networking Basics"
document_id: ""
version: "1"
date: "2025-07-02"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "92398bcb93e2ae9e04ae494c895afd9e859cdb86361d42f32c521a62787c48a4"
token_estimate: 1090
recommended_chunk_level: "h2"
abstract_for_rag: "- Every device has an address (like 192.168.1.1) - Like a postal address for computers - Enables routing of messages"
source_file: "week3_Networking.pdf"
type: "pdf"
extracted_via: "docling"
pages: 15
---

# Networking Basics

## How Computers Communicate?

## Internet Protocol (IP):

- Every device has an address (like 192.168.1.1)
- Like a postal address for computers - Enables routing of messages

## Domain Names:

- Human-readable addresses (like google.com)
- DNS translates to IP addresses - Easier to remember than numbers

## How Computers Communicate?

## Ports:

- Specific entry points on a server (like apartment numbers)
- Port 80 for HTTP, Port 443 for HTTPS
- Like Streamlit, your FastAPI app will run on a specific port

## The Journey of a Prediction Request

## A High-Level Walkthrough:

- 1.User Action (Client): User fills a form → clicks "Predict" → browser prepares a request.
- 2.DNS Lookup: Browser asks a DNS server → IP of my-ml-service.com
- 3.HTTP Request: Browser messages server's IP → Message contains the feature data
- 4.Server Processing: ML App receives request → passes data to model → gets prediction
- 5.HTTP Response: Server packages the prediction into a response message → sends it back
- 6.Display Result (Client): Browser receives response → updates webpage to show prediction

## HTTP -The Foundation of Web Communication

- The core protocol for data exchange on the Web.
- Defines how clients request resources and how servers respond.
- HTTP is a stateless, text-based request-response protocol
- Statelessness: Each HTTP request is independent -the server does not retain information about past requests.
- If state is needed (e.g., user login sessions), it must be handled via cookies, sessions, or tokens on top of HTTP

- Request-Response Cycle: Client sends an HTTP request, and the server returns an HTTP response with a status code and possibly data.
- HTTPS: HTTP Secure is HTTP over TLS/SSL encryption -essential for protecting data in transit (e.g., when sending sensitive input to a model)

## Anatomy of an HTTP Request

- Method (Verb): The action to perform.
- GET : Retrieve data (safe, cacheable)
- POST : Submit data for processing (not safe, not cached)
- Path: The target resource (e.g., /predict ).
- Headers: Metadata (e.g., Content-Type: application/json ).
- Body: The data payload (e.g., {"age": 45, "bmi": 22.5,...} ) Used with POST .

## Anatomy of an HTTP Response

- Status Code: Outcome of the request.
- 200 OK : Success.
- 404 Not Found : The path doesn't exist.
- 422 Unprocessable Entity : Invalid input data.
- 500 Internal Server Error : A crash on our server.
- Headers: Response metadata
- Body: Data sent back (e.g., {"predicted\_price": 250000}).

## REST APIs -Communicating with Web Services

## · API Basics - Application Programming Interface:

- Allows different software systems to communicate.
- In web context, an API typically exposes endpoints (URLs) that clients can call to perform operations or retrieve data.

## · REST (Representational State Transfer):

- An architectural style for designing networked applications (especially web services).

## REST APIs -Communicating with Web Services

## Why REST for ML services:

- RESTful APIs are language-independent and widely used
- It's a standard way to deploy ML models for consumption

## Example:

- Sentiment analysis model → deployed at an endpoint /predict-sentiment
- Client POSTs JSON → {"text": "I love this product"} to that URL
- Server responds → {"sentiment": "positive"}

The interaction uses HTTP and follows REST principles

## REST API - Structure

API request consists of 4 main components:

1. HTTP method (GET, POST, PUT, DELETE)
2. Endpoint (URL) - https://api.weatherservice.com/current?city=London
1. Base URL - https://api.weatherservice.com
2. Resource Path - /current
3. Query parameters - ?city=London
3. Headers
4. Body (optional)

## Exercise: Test REST API

Using Postman and Shell

## SSH -Secure Shell for Remote Access

- A network protocol for secure remote login and command execution on servers.

## SSH -Secure Shell for Remote Access

- Establishes an encrypted connection between a client (your laptop) and a remote machine (e.g., a cloud server hosting your web app).

## · Use in Deployment:

- MLOps often involves deploying models to cloud or remote servers (for example, an EC2 instance on AWS).
- SSH is the primary way to connect to such Linux servers to configure them, install your web application, run Docker, etc.
- It ensures all communication is encrypted.

