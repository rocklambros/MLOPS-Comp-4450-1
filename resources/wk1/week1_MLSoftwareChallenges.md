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
content_hash: "76247a51ee7313898656f75dd329db080463c6bf88e423e33706722a97dcd4fb"
token_estimate: 882
recommended_chunk_level: "h2"
abstract_for_rag: "- Rely on abstraction, reuse, and composition to build modular systems. - Components are built around clear specifications enabling isolated development and testing. - Enables parallel work and integration of opaque components (e.g., third-party libraries)"
source_file: "week1_MLSoftwareChallenges.pdf"
type: "pdf"
extracted_via: "docling"
pages: 12
---

# Advanced Topic: MLOps Week 1

## Challenges in ML Software

## Lack of Specifications

## In Traditional Software Practices:

- Rely on abstraction, reuse, and composition to build modular systems.
- Components are built around clear specifications enabling isolated development and testing.
- Enables parallel work and integration of opaque components (e.g., third-party libraries)

## Lack of Specifications

## In ML Systems:

- No clear specifications for how models behave -only the task is described, not the exact input-output mapping.
- ML is often used precisely because we can't manually specify or implement the solution.
- With prompts to LLMs -we hope the model understands our intention.

## Lack of Specifications

## Shift in Reasoning Paradigm:

- From deductive (rule-based) to inductive (pattern-based) reasoning.
- ML models are evaluated empirically , not proven correct.
- Systems must be designed to tolerate errors and uncertainty .

## Implications for System Design:

- ML components behave probabilistically , not deterministically.
- Requires robust system-level design to handle imperfect model outputs.
- Testing focuses on average-case performance and system integration .
- However, ML doesn't break engineeringit extends existing uncertainty-handling practices .

## Interacting with the Real World

## Real-World Impact

- ML systems interact with the physical and social world (e.g., medical transcriptions, shopping recommendations).
- Failures can lead to physical harm, stress, or large-scale disruptions .

## Bias and Fairness Concerns

- Models trained on biased or skewed data (e.g., TV subtitles, historic patterns) can perpetuate inequality.
- Issues like poor transcription for dialects or underrepresented groups are common.

## Interacting with the Real World

## Feedback Loops and Systemic Risks

- ML predictions can influence the environment and reinforce their own biases .
- E.g : YouTube's recommendation system amplified conspiracy

## User Adaptation and Adversarial Behavior

- Users may change behavior in response to ML outputs (e.g., speakers adjusting pronunciation)
- Systems are vulnerable to adversarial inputs designed to exploit model weaknesses (e.g., spoofing face recognition)

## Interacting with the Real World

## Data and Concept Drift

- User behavior and environment evolve over time , making models outdated or inaccurate without retraining.

## Safety Isn't New -but Now Harder

- Traditional software has also caused serious harm (e.g., medical overdoses, spacecraft crashes).
- Engineers use requirements analysis, threat modeling, and hazard analysis to build safe systems.

## Data Focused and Scalable

- Scale Drives Performance: MLs get the 'specs' from data; Larger the better
- Models are deployed via distributed systems, cloud platforms, or edge devices.
- Large models (e.g., LLMs) require expensive, high-end hardware , even for inference.

## Data Focused and Scalable

- Scaling ML systems involves:
- Massive compute and storage
- Sophisticated deployment pipelines
- Robust data infrastructure
- Requires new skills and tight collaboration with DevOps and infrastructure teams.
- However, ML systems amplify the demands on data management, reliability, and cost.

## From Traditional Software to Machine Learning

- Challenges introduced by production systems require SWE practices and knowledge
- For ML projects - likely need to level up engineering practices
- We tend to attempt much more ambitious and risky projects with ML

