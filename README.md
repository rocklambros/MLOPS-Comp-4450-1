# COMP 4450: Machine Learning Operations

This repository holds the coursework for COMP 4450, Machine Learning Operations, in the MS in Applied Data Science and AI at the University of Denver. It collects the graded homework assignments, the weekly labs they build on, the weekly lecture notes, and the final project in one version-controlled place, which the course requires for every submission.

The course covers how machine learning systems are engineered and shipped: the move from a model in a notebook to a service that other people depend on. The work runs in Python and touches Streamlit apps, FastAPI services, containers, databases, cloud deployment, monitoring, and CI/CD.

## What is in here

```
.
├── coursedocs/        syllabus and course outline (source of truth for scope)
├── resources/         weekly lecture notes, wk1 through wk10
├── assignments/       graded homework, one directory per course week (see the map)
├── labs/              weekly practical lab modules
├── final-project/     full-stack ML app deployed to the cloud
├── CONTRIBUTING.md    setup, branch and commit flow, pair-work rules, secret handling
└── LICENSE            All Rights Reserved
```

## Assignment map

Folders are named by course week, not by assignment number, because weeks 4 and 6 carry no homework. So `hw5` holds the week-5 work, which is Assignment 4.

| Folder | Week | Assignment | Topic | Status |
|---|---|---|---|---|
| `assignments/hw1` | 1 | 1 | Streamlit sentiment-analysis app | built |
| `assignments/hw2` | 2 | 2 | Docker packaging | spec only |
| `assignments/hw3` | 3 | 3 | FastAPI backend | spec only |
| `assignments/hw5` | 5 | 4 | AWS compute (EC2, Lambda) | spec only |
| `assignments/hw7` | 7 | 5 | Model monitoring | spec only |
| `assignments/hw8` | 8 | 6 | CI/CD and testing | spec only |
| `final-project/` | 9 | final | Production-grade MLOps system | spec only |

Specs for assignments 1 through 6 have released. The syllabus counts seven graded homeworks in total; the remaining one releases later in the term. To start an assignment, open its directory, fill in the stub `README.md`, and add the code next to it.

## Setup

The work is Python. Use a per-clone virtual environment so each assignment's dependencies stay isolated and reproducible.

```bash
git clone https://github.com/rocklambros/MLOPS-Comp-4450-1.git
cd MLOPS-Comp-4450-1
python3 -m venv .venv
source .venv/bin/activate
```

Each assignment pins its own dependencies in a `requirements.txt` inside its directory. Install those when you start the assignment, not globally.

The containerized assignments build on `python:3.13-slim`. See [COURSE_STATE.md](COURSE_STATE.md) for the stack-baseline rationale.

## A typical assignment

Modules release the day of class, and assignments are due end of day the following Tuesday. A normal pass through one assignment:

```bash
git checkout -b hw3                  # branch per assignment
cd assignments/hw3
# fill in README.md, write the solution, pin requirements.txt
git add -A && git commit -m "hw3: serve the classifier behind a FastAPI endpoint"
git push -u origin hw3
```

If you are working in a pair, open a pull request so both partners' commits are on the record. The branch and review flow is in [CONTRIBUTING.md](CONTRIBUTING.md).

## What the course covers

The ten-week arc moves from concept to a deployed, monitored system:

1. Production lifecycle of machine learning models
2. Machine learning systems and MLOps
3. Web application design for ML
4. Data management
5. Cloud computing
6. Model deployment and serving
7. Model monitoring and versioning
8. CI/CD and testing
9. Retraining, continual learning, experiment tracking, and the model registry
10. Scaling, ethics, and project management

A few terms recur across the assignments. *Model serving* means exposing a trained model so other software can call it, usually as a REST endpoint built with FastAPI. *Containerization* packages the model and its dependencies so the same image runs on a laptop and in the cloud. *Monitoring* watches a deployed model for drift and failure after it ships, which is where MLOps differs from training a model once and walking away.

## Grading

| Component | Weight |
|---|---|
| Homework assignments | 70 percent |
| Attendance and bi-weekly quizzes | 10 percent |
| Final project | 20 percent |

## Where to go next

- [coursedocs/](coursedocs/) for the syllabus, grading scale, and honor code
- [resources/](resources/) for the weekly lecture notes
- [assignments/](assignments/) for the homework directories and the schedule note
- [labs/](labs/) for the weekly practical modules
- [final-project/](final-project/) for the capstone application
- [CONTRIBUTING.md](CONTRIBUTING.md) for how to set up, branch, and collaborate
- Primary textbook: [Machine Learning in Production](https://mlip-cmu.github.io/book/01-introduction.html) (Carnegie Mellon)
