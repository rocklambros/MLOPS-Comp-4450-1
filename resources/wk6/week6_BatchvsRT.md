---
title: "Batch vs Real Time Inference"
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
content_hash: "536202552f0b5615f745683f35c9969324f3af97451bc70118f5dfb552452ba8"
token_estimate: 225
recommended_chunk_level: "h2"
source_file: "week6_BatchvsRT.pdf"
type: "pdf"
extracted_via: "docling"
pages: 5
---

# Batch vs Real Time Inference

With Examples from AWS

## Batch Inference (Offline Predictions)

## Batch Inference (Offline Predictions)

- Model generates predictions on large collection of data at once - usually on a schedule or as needed for analysis
- Suitable where immediate results are not needed
- Make full-use of resources by scheduling jobs at off-peak hours
- The tradeoff is Latency
- Predictions can be saved in data storage for later use

## Real-Time Inference (Online Predictions)

## Real-Time Inference (Online Predictions)

- Live service - can handle single/few data points and return predictions immediately
- E.g., Instant Translation
- Requires a persistent server or serverless function listening for requests and producing predictions with minimal delay
- Advantage: Immediate response + improved user experience
- Challenge: Requires robust, lo -latency infrastructure
