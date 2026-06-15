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
content_hash: "51ccccad1ec5f21fdc7a6ee71eb4de6f0f1f1ac0220633931e89245a7968b165"
token_estimate: 1244
recommended_chunk_level: "h2"
abstract_for_rag: "- While ML has enabled us to develop great products, there are engineering challenges of transitioning from a model prototype to a production-ready system. - ML in production has multiple archetypes: Software 2.0, Human-in-the-loop, Autonomous. - MLOps offers tools and practices that assist with developing end-to-end ML Systems - ML projects lifecycle is purposefully iterative and circuitous."
source_file: "week2_WhenToUseML.pdf"
type: "pdf"
extracted_via: "docling"
pages: 17
---

# Advanced Topic: MLOps Week 2

## Review from last lecture

- While ML has enabled us to develop great products, there are engineering challenges of transitioning from a model prototype to a production-ready system.
- ML in production has multiple archetypes: Software 2.0, Human-in-the-loop, Autonomous.
- MLOps offers tools and practices that assist with developing end-to-end ML Systems
- ML projects lifecycle is purposefully iterative and circuitous. It may introduce characteristics that are different from many traditional software engineering projects*

## When to use ML

## Whether to use ML or not?

Image-based quality inspection on a factory line (detect surface defects)

System Calculating Payroll and Tax Withholdings for a Company's Employees Online store for local Ski-gear recommends add-ons from a catalog of 20 items Personalized news feed for a global media app

## Discussion: Why do you think so?

## Overview

- Modern products, from search to supply-chain tools, routinely embed ML components.

## · but ML projects fail more often

- Industry studies show higher cost overruns, schedule slips, and unmet objectives compared with traditional software.

## Overview

## · Rule of Thumb

- Adopt ML only when the expected business or user value justifies both the build cost and the extra operational complexity.

## · Prefer simpler solutions when they work

- Rule-based or analytic approaches are cheaper, safer, and easier to maintain when they meet the requirements.
- E.g. Calculating Payroll/Tax Withholdings

## Problems that Benefit from Machine Learning

## When the Problem is Intrinsically Hard

- Speech recognition, image classification, NLU - too complex to solve with rules*
- ML can uncover patterns where hand-coded solutions fall short.

## When the Problem is Large-Scale

- Rule-based systems become unmanageable for massive domains (e.g., music recommendation, web search).
- ML scales better by learning from data rather than manually coding rules.

## Problems that Benefit from Machine Learning

## When the Problem is Continuously Changing

- In dynamic environments (e.g., music trends, preferences), hardcoded logic quickly becomes outdated.
- ML systems can adapt automatically with fresh data.

## Before Starting an ML Project, Ask Y ourself...

## 1. Are we ML-ready?

- Is there a solid product vision
- Does a reliable data collection & storage system exist?

## 2. Is ML the right tool?

- Is there a clearly defined problem and measurable value?
- Ensure no simpler rule-based or statistical solution that already meets the need

## 3. Is it responsible to apply ML here?

- Ethical, legal, and social implications considered (fairness, privacy, transparency, potential harm)

## How to Pick Problems to Solve with ML

You want to look for use cases that have high impact and low cost :

## High-Impact Projects

## 1. Make the impossible affordable

- Target decisions where ML can drop the cost of prediction from prohibitive to practical.

## 2. Serve a pressing product need

- Focus on features that directly move key user or business metrics
- Check Spotify's: Three Principles for Designing ML-Powered Products

## High-Impact Projects

## 3. Automate 'Software 2.0' pain points

- Replace large, brittle rule-sets or heuristics with learned models that scale and adapt.

## 4. Learn from the front-runners

- Track case studies, papers, and tech blogs from both Big Tech and nimble startups.

## Low-Cost Projects

## 1. Data availability & quality

- Ease of collection, labeling effort, volume needed, stability, and security constraints.

## 2. Required accuracy

- Business / ethical cost of errors and the target performance threshold.
- Costs often rise super-linearly as you chase the last few points of accuracy.

## 3. Problem difficulty

- Clarity of the task, existing research baselines, and compute demands.
- Well-studied, narrow problems are cheaper than open-ended or novel ones.

## How to Pick Problems to Solve with ML

You want to look for use cases that have high impact and low cost :

## ML Risk and Tolerance

- Accept that ML makes mistakes
- Models are probabilistic, not deterministic; 'always -right' is unattainable.
- Deploy only where errors are tolerable
- Low-stakes use cases (e.g., music recommendations) can absorb occasional misses.

## · Beware hidden harm & bias

- Even 'harmless' domains can unfairly disadvantage users or content creators.
- Mitigate, monitor, and involve humans
- Feedback loops, appeal channels, and human review can keep risk within limits.

## ML Feasibility Assessment

1. Challenge the need for ML -Whether simpler methods could solve the problem just as well?
2. Define success & ethics -Agree on measurable objectives. Examine ethical impacts
3. Survey the landscape -Review relevant papers, open-source projects, and case studies to gauge technical feasibility.
4. Build a "minimum" viable model using manual rules or simple heuristics.

