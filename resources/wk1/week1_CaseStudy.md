---
title: "Advanced Topic: MLOps Week 1"
document_id: ""
version: "1"
date: "2025-06-19"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "e43723df984061c83fbb6ef40ddef518c50a64b26c638b9b3f207ca6ac4efe39"
token_estimate: 759
recommended_chunk_level: "h2"
abstract_for_rag: "- Sidney, a university-based data scientist, spent years advancing speech recognition, focusing on domain-specific terminology - Developed a method using large-scale training (e.g."
source_file: "week1_CaseStudy.pdf"
type: "pdf"
extracted_via: "docling"
pages: 10
---

# Advanced Topic: MLOps Week 1

## Example Case Study

Automated Transcription Start-up

## Context:

- Sidney, a university-based data scientist, spent years advancing speech recognition, focusing on domain-specific terminology
- Developed a method using large-scale training (e.g., PBS transcripts) + transfer learning on small expert-labeled datasets
- Demonstrated high transcription accuracy in:
- o Doctor-patient conversations
- o Academic talks on poverty & inequality
- o Local programming meetups (e.g., Ruby talks)
- Published findings in top ML conferences.

## The Startup Idea

## The Startup Idea

- Discovered a need among researchers for accurate, fast, and affordable transcription for long interviews.
- Existing services :
- o Human-based, slow (days), and costly (~$1.50/min)
- o Automated tools (like YouTube captions) lacked accuracy with technical vocabulary.
- Noticed similar pain points with live captioning at conferences -expensive or low quality.
- Decided to commercialize the research via a start-up:
- o Focus: Affordable, high-quality domain-specific transcription and live captioning.
- o Target customers: Academic researchers and conference organizers.

## Breakout Discussion

List likely challenges in building the commercial product

- One machine-learning challenge
- One engineering challenge in building the product
- One challenge from operating and updating the product
- One team or management challenge
- One business challenge
- One safety or ethics challenge

## Research Prototype to Production Reality: Challenges

## · Academic vs. Real-World Data

- Research models performed well on clean benchmark data
- In Sydney's case, audio files from customers were noisy
- Real-world audio is noisy, degrading model performance

## · Latency & Scalability

- Research settings ignored runtime; customers expect fast results
- Getting impatient if not transcribed within 15 minutes
- Live captioning requires low latency -often unrealistic without costly hardware

## Research Prototype to Production Reality: Challenges

## · Cost & Profitability

- Model training/inference is compute-intensive and expensive
- Cloud costs threaten profit margins; pricing is a major challenge
- LLM APIs and self-hosting efforts add financial & technical strain

## · Productization & Engineering Gaps

- No prior experience building web UIs or payment systems
- Poor UX and system reliability led to customer frustration
- Communication issues between researchers and engineers

## Research Prototype to Production Reality: Challenges

## · Operational & DevOps Bottlenecks

- Manual training pipelines are fragile and time-consuming
- Fear of library updates; outages caused by failed model updates
- Lacked monitoring, version control, and deployment automation

## · Model Limitations in Production

- Model errors harmed user trust (e.g., medical misdiagnoses, dialect bias)
- No observability into model behavior unless users complained
- Only now collecting customer feedback and retention data

