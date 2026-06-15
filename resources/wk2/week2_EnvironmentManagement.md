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
content_hash: "204a02b9b67fc9fc7dad52de71bc04a3c215085728e9a587634c6d69ca0294a3"
token_estimate: 1093
recommended_chunk_level: "h2"
abstract_for_rag: "- Goal for MLOps → build robust, scalable and automated ML Systems - A big challenge is environment inconsistency, summarized by 2 recurrent problems: 1. Dependency Hell - Minute, yet critical, differences in software dependencies - Difficult to debug, can halt collaborative progress 2."
source_file: "week2_EnvironmentManagement.pdf"
type: "pdf"
extracted_via: "docling"
pages: 16
---

# Advanced Topic: MLOps Week 2

## Environment Management in MLOps

## Need for Reproducibility

- Goal for MLOps → build robust, scalable and automated ML Systems
- A big challenge is environment inconsistency, summarized by 2 recurrent problems:
1. Dependency Hell
- Minute, yet critical, differences in software dependencies
- Difficult to debug, can halt collaborative progress
2. System incompatibility -'Works on my machine!'
- Root cause → OS-level incompatibilities, missing system libraries, different environment variable configurations
- Introduce delays, unpredictability and manual interventions

## Spectrum of Isolation

- Solution for environment inconsistency? → ' isolation '
- A spectrum of technologies offering different level of separation at a different cost.
- We will discuss:
1. Virtual Environments
2. Virtual Machines
3. Containers

## Virtual Environment

- The most basic → Python virtual environments
- Common tools: venv or conda
- Creates isolated space at application level
- Sets directory with specific version of Python interpreter and set of packages
- Benefit: Solves the ' dependency hell ' problem for Python packages
- Limitations: Shallow isolation → An application that works within a venv on one machine may still fail on another

## Virtual Machines

- A complete emulation of a physical computer, providing full hardware-level isolation
- VMs operate on a software layer known as a hypervisor
- What's a hypervisor ?
- Sits on the host machine's hardware
- Creates virtualized instances of the CPU, RAM, storage, and networking components

## Virtual Machines

- Encapsulates a complete guest OS -including kernel, libraries, and application code
- Benefit:
- Highest degree of isolation possible
- Great for running entirely different OS
- Limitation:
- Significant performance and resource cost
- Consume substantial CPU and memory and slow to start

## The Sweet Spot: Containers

- Offers benefits of VMs, without the overhead
- Lightweight, standalone and executable
- Includes everything an application needs to run: the code, runtime, system tools, and libraries.
- How do they achieve this? Through efficient form of virtualization at the OS level

## Container Architecture

- Virtualizes the OS itself
- Multiple containers on a machine -share host OS's kernel
- Each container is an isolated user-space instance
- Lightweight and efficient
- Ideal packaging mechanism for microservices
- Great for MLOps → enable small, independently deployable services that work together to form a larger application

## Introducing Docker

- Open platform for developing, shipping, and running applications by using containers
- Key components:
- Docker Engine: Background service on the host - responsible for building, running, and managing containers.
- Docker CLI: CLI that users interact with - Sends instructions to the Docker daemon
- Docker Hub / Registry: Cloud-based repo - Stores and shares container images

## Key terms

- Image:
- A single, immutable artifact called
- Acts as a blueprint
- When a container is run from this image, it guarantees that the environment is identical everywhere -from a developer's laptop to a production cloud server.

## · Dockerfile

- A text file containing a set of instructions used to automate the creation of Docker image

## Docker for MLOps

## · Reproducibility and Consistency:

- Solves the "it works on my machine" problem
- Packages code, runtime, libraries, and dependencies into an image .

## · Portability:

- Docker's slogan is "Build Once, Run Anywhere'
- Can run on any OS

## · Simplified Dependency Management:

- Environment dependencies declared in Dockerfile.
- Serves as "environment-as-code," - can be version-controlled in Git alongside the code.

## · Scalability:

- Perfectly suited for scaling applications to meet variable demand.
- Orchestration with Kubernetes

## Lab and Assignment

## Lab Overview

1. Docker Setup and Installation
2. Core Concepts
3. Creating and running first container
4. Persisting Volumes
5. Containerizing a production app
6. GitHub and Docker best practices

## Assignment 2

- Docker the app created in Assignment 1

## Readings

- Chapter 2, 4 and 5 of Machine Learning in Production -Kastner
- (optional) insights.sei.cmu.edu/blog/software-isolation-why-it-matters-tosoftware-evolution-and-why-everybody-puts-it-off/
