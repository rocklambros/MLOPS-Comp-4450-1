---
title: "Cloud Service Models"
document_id: ""
version: "1"
date: "2025-07-16"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "7a3770ba6b584c803e672a7bd42898484d7aebaab21d04f61871ab99d2cd8e2c"
token_estimate: 315
recommended_chunk_level: "h2"
source_file: "week5_ServiceModels.pdf"
type: "pdf"
extracted_via: "docling"
pages: 5
---

# Cloud Service Models

## Infrastructure as a Service (IaaS)

- Delivers fundamental infrastructure:
- Virtual servers/VMs,
- Storage, networks,
- Basic computing resources -on demand
- Customer is responsible for the OS and everything above
- Gives the most control to the user → you manage OS and software, but don't worry about the physical hardware
- E.g.,: AWS EC2 provides virtual compute
- Analogous to renting raw computing hardware in the cloud

## Platform as a Service (PaaS)

- Provider manages hardware & OS
- Customers can develop, run, and manage applications
- without dealing with low-level infra
- You focus on application code and data; the cloud platform takes care of OS, runtime, patching, scaling, etc.
- E.g., AWS Lambda - serverlessmodel -just provide code/triggers, and the cloud runs it
- PaaS increases developer; Cost → limited control over the environment

## Software as a Service (SaaS)

- Fully functional application or service, managed entirely by the provider
- Application runs on the provider's infrastructure; users just interact through a web browser or client.
- E.g.,: Web-based, Enterprise tools, Slack
- Everything from infrastructure to application is managed by the vendor; the customer just uses the software.

