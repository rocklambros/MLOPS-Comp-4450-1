# Final Project

A full-stack machine learning application deployed to the cloud. Worth 20 percent of the course grade and built entirely on the labs and homework assignments that come before it.

## What it has to demonstrate

The project ties the course together: a trained model served behind a web application and RESTful API, packaged in containers, backed by a data store, deployed to a cloud platform, and instrumented for monitoring. Treat it as a production system, not a notebook.

## Layout

Build the project out in this directory once the brief releases (around week 9). A typical split:

```
final-project/
  model/          training and evaluation
  app/            Flask app and REST API
  infra/          containerization and deployment config
  docs/           architecture notes and the project writeup
```

Pull working pieces forward from `../labs/` and `../assignments/` rather than starting from scratch. Keep cloud credentials and large model artifacts out of the repo per [`../CONTRIBUTING.md`](../CONTRIBUTING.md).
