---
title: "Key Aspects & Challenges of Deployment"
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
content_hash: "8a0e5fd49a806482c46d954263966a89b04ab9bcc2177b1c71b1d2bd8ca75eb2"
token_estimate: 489
recommended_chunk_level: "h2"
source_file: "week6_DeploymentChallenges.pdf"
type: "pdf"
extracted_via: "docling"
pages: 8
---

# Key Aspects & Challenges of Deployment

## Latency & Performance

Image: testmyspeed.com/insights/what-is-latency

## Latency & Performance

- For real-time services, low latency is critical
- The cloud infrastructure must be chosen and configured to minimize the prediction time
- This could mean using appropriate instance types (CPU vs GPU) or caching and loading techniques for models
- E.g., loading large models into memory can be done at server startup (or outside the Lambda handler) to avoid delays on each request

## Throughput

- Measures the capacity of the system
- Defined as the number of prediction requests it can handle within a period
- It is a direct indicator of the system's ability to handle concurrent users
- Throughput & Latency are often in direct opposition
- E.g., Batching requests may increase throughput, at the cost of latency
- Some ways to increase throughput:
- Caching common requests
- Auto-scaling

## Reliability & Availability

- The service should be reliable (minimal downtime) and available to users when needed
- In practice → means planning for failover and using managed services that reduce downtime
- Cloud platforms allow:
- Deployment across multiple AZs
- Load balancers to ensure high availability

## Reliability & Availability

- On EC2 → Elastic Load Balancer in front of multiple instances;
- If one instance goes down, others can continue serving traffic.
- Lambda inherently runs in a highly available, multi-AZ infrastructure, so it abstracts a lot of this concern.

## Scaling

- Cloud deployment should handle varying loads efficiently
- Model service could receive many requests concurrently
- To serve a large number of requests without compromising performance, the system can:
- Scale out (adding more compute instances) or
- Scale up (using more powerful instances)
- EC2 → Use Auto Scaling Group
- Lambda → Handles Automatically

## Environment Consistency

Just Stick with Docker

