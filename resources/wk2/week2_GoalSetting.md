---
title: "Advanced Topic: MLOps Week 2"
document_id: ""
version: "1"
date: "2025-06-25"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "f4d823b1871f7b468e45e001c2dcf6fbfe41cc9f31a11a3f77949dbaca678b79"
token_estimate: 649
recommended_chunk_level: "h2"
abstract_for_rag: "- Typically, projects focus on optimizing ML models for accuracy - Align four perspectives - Model - Product - User - Organization - Ideally, define goals in measurable terms"
source_file: "week2_GoalSetting.pdf"
type: "pdf"
extracted_via: "docling"
pages: 10
---

# Advanced Topic: MLOps Week 2

## Goal Setting for ML

## Overview

- Typically, projects focus on optimizing ML models for accuracy
- Align four perspectives
- Model
- Product
- User
- Organization
- Ideally, define goals in measurable terms

## Case Study

Context: Marketing platform for law firms wants to add an AI chatbot to convert site visitors into clients.

- Develop a modern chatbot (for lawyers) where potential clients can ask questions over a text chat
- Use a knowledge base and language models to understand and answer the clients' questions

## Case Study

The chatbot will:

- Schedule meetings
- Answer some questions directly
- Provide initial pointers to clients' legal problems e.g. child custody rules
- Collect contact / case details for attorney follow-up.

The team has a good amount of training data from the old chat service with human operators.

## Case Study

Non-AI guided chat was too limited

- Cannot enumerate problems
- Hard to match against open entries ('I want to file for bankruptcy' vs 'I have no money')
- Involving human operators very expensive
- Old-fashioned

## Setting Goals

- Clear and understandable goals help frame the direction
- Risk - Members might focus on sub-local problem,
- Get carried away by the excitement about tech - Instead focusing on the goals of the product
- Establishing high-level project goals is usually one of the first steps in eliciting the requirements for the system
- Goals also provide guidance on how to measure the success of the system.

## Untangling Goals

## · Organizational:

- Business outcomes: Revenue, profit, market share
- E.g., Increase subscription revenue from attorneys
- KPIs: Licenses, referrals, customer satisfaction

## · Product:

- What the software aims to achieve regarding behavior/quality
- E.g., Generate leads quickly, provide modern web experience

## Untangling Goals

## · User:

- Multiple stakeholder, assess needs for each; including indirect
- E.g., Attorney wants clients, clients want legal help

## · Model:

- Technical objective for ML components
- E.g., NLP accuracy for legal intent recognition

## Relationship between Goals

- Alignment : Satisfied users usually support business & model goals through better engagement and monetization
- Conflicts : Improved model answers may reduce attorney satisfaction by bypassing their expertise

' a good enough model may just be good enough for the organizational goals, product goals, and some user goals.'

- Trade-offs : Early identification and explicit balancing of conflicting goals is critical to product success
