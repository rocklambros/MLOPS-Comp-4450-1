---
title: "Fairness"
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
content_hash: "3f71b9b7abb9776b1afaf4758774c96b8c8696a62f741c09774726af322e362d"
token_estimate: 332
recommended_chunk_level: "h2"
source_file: "week10_Ethics.pdf"
type: "pdf"
extracted_via: "docling"
pages: 6
---

# Fairness

## Case Study: Mortgage Applications

## Covering the Concepts

There is no single, universal definition of fairness . The right approach depends on context and societal goals.

- Equality (Equality of Opportunity)
- Loan decisions based purely on an applicant's predicted ability to repay, ignoring group membership like race or gender.
- Equity (Equality of Outcome)
- Accept more risky loans from a historically disadvantaged group to help reduce past wealth and income disparities.

## Where does this Bias come from?

Historical Bias: The data reflects a biased world, not the world we want to build.

Sample Size Disparity: Some groups are underrepresented in the training data, leading to poorer model performance for them.

Proxies: The model uses seemingly neutral features that are correlated with protected attributes

## How do we measure Fairness?

- Anti-Classification : The model should not use protected attributes (e.g., race, gender) in its decision-making.
- Group Fairness (Demographic Parity): Ensures the rate of positive outcomes is similar across groups. Aligns with the legal concept of disparate impact.
- Equalized Odds: Ensures the error rates (False Positive Rate & False Negative Rate) are similar across groups. Aligns with equality of opportunity.

## How do we measure Fairness?

