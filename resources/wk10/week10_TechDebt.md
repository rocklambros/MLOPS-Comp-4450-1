---
title: "Technical Debt"
document_id: ""
version: "1"
date: "2025-08-23"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "312ea913596f4b6d0fc5214aeee42dd55a79cc4c5a706507c1158cf10f4cf85b"
token_estimate: 300
recommended_chunk_level: "h2"
source_file: "week10_TechDebt.pdf"
type: "pdf"
extracted_via: "docling"
pages: 8
---

# Technical Debt

## What is it?

'design or implementation constructs that are expedient in the short term, but set up a technical context that can make a future change more costly or impossible . '

2

## Categorizing Tech Debt

## Categorizing Tech Debt

## Case Study: Delivery Robot

## Tech Debt in ML

- Data Debt: The quality of your data changes over time, but you haven't built tools to monitor it.
- Infrastructure Debt: You develop a model in a notebook and manually copy it to production.
- Observability Debt: Your model is in production, but you have no visibility into its real-world performance.

## Managing Technical Debt

## Make it a Deliberate Decision:

Don't accumulate debt by accident. When taking a shortcut, discuss the longterm costs and decide if the short-term benefit is worth it.

## Track Your Debt:

If you decide to take on debt, log it. Add it to your issue tracker or product backlog just like a feature or a bug.

## Managing Technical Debt

## Assign Ownership & Repay It:

Make a specific person or team responsible for the debt.

Schedule time to pay it back. Some organizations use "fix-it weeks" where all development focuses on addressing technical debt.
