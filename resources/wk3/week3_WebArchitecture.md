---
title: "Web Architecture"
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
content_hash: "d8d1b4d6311a0dfd9153de0da2ba31eca07c3b1ceda43a7eac2a8f4a97452305"
token_estimate: 701
recommended_chunk_level: "h2"
abstract_for_rag: "- Full Stack refers to development of both the front-end (client side) and back-end (server side) parts of a web application. - Front-end : Runs in the user's browser or device -handles presentation and user interaction. - Back-end : Runs on a server - handles data storage, business logic, and serves responses to client requests."
source_file: "week3_WebArchitecture.pdf"
type: "pdf"
extracted_via: "docling"
pages: 10
---

# Web Architecture

## The Big Picture: Why Your Model Needs the Web

## Full Stack Development

- Full Stack refers to development of both the front-end (client side) and back-end (server side) parts of a web application.
- Front-end : Runs in the user's browser or device -handles presentation and user interaction.
- Back-end : Runs on a server - handles data storage, business logic, and serves responses to client requests.

## Client-Server Architecture

- The fundamental pattern of the internet.
- A model where:
- Clients → send requests,
- Servers → process requests & return responses
- By separating roles, servers handle heavy lifting (computations, db queries) while clients handle user interaction - Distributed framework
- Nearly all web services -from email to social networks -use this architecture, which is why we need it

## Key Concepts:

- Client : Requests services (browser, mobile app, another server)
- Server : Provides services (your ML model, database, web application)
- Protocol : Rules for communication (HTTP, HTTPS)
- Stateless : Each request is independent

courtesy: codecademy.com courtesy: codecademy.com

## Key Concepts:

- Client : Requests services (browser, mobile app, another server)
- Server : Provides services (your ML model, database, web application)
- Protocol : Rules for communication (HTTP, HTTPS)
- Stateless : Each request is independent

## Why Client-Server is Essential for MLOps?

## Centralization & Control:

- The model, its weights, and business logic live in one managed place (the server)
- Updates are simple: change it on the server, and every client gets the new version instantly

## Scalability:

- To handle more users, we can scale the server without changing the client.
- Vertical Scaling: Upgrade the server's CPU/RAM.
- Horizontal Scaling: Add more server machines.

## Why Client-Server is Essential for MLOps?

## Security:

- Access to the model is managed at the server.
- Implement authentication and authorization to control who can make prediction requests.

## Separation of Concerns:

- Client: Handles the User Interface (UI) and user interactions.
- Server: Performs the heavy lifting (data processing, model inference).
- Clean and efficient division of labor.

## How Netflix Uses Client-Server Architecture

## The Flow:

- 1.You open Netflix (Client)
- 2.Client requests recommendations from Netflix servers
- 3.Server runs ML models to generate personalized recommendations
- 4.Server sends recommendations back to client
- 5.Client displays movies you might like

## How Netflix Uses Client-Server Architecture

## Why This Architecture Works:

- Netflix can update recommendation algorithms without updating your TV app
- One model serves millions of users
- Works on any device with internet connection

