# RAG-Based Enterprise Knowledge Intelligence System

A full-stack document question-answering application that lets users ask
natural-language questions about enterprise PDFs. It uses
Retrieval-Augmented Generation (RAG) to retrieve relevant passages and
provide them as context to a locally hosted language model.

> **Status:** Active development. Verify PDF upload and end-to-end
> ingestion in your environment before treating the project as
> production-ready.

## Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Architecture](#architecture)
-   [Technology Stack](#technology-stack)
-   [How It Works](#how-it-works)
-   [Project Structure](#project-structure)
-   [Prerequisites](#prerequisites)
-   [Configuration](#configuration)
-   [Run Locally](#run-locally)
-   [Docker](#docker)
-   [API Endpoints](#api-endpoints)
-   [Limitations and Roadmap](#limitations-and-roadmap)

## Overview

Enterprise information is often spread across policies, technical
manuals, reports, and PDFs. Finding answers manually can be slow, while
keyword search may miss relevant passages when the user's wording
differs from the document.

This project combines semantic search, keyword search, reranking, and a
local LLM to support document-grounded question answering.

## Features

-   PDF text extraction with PyMuPDF.
-   Text chunking using LangChain's `RecursiveCharacterTextSplitter`.
-   Local embeddings through Ollama using `nomic-embed-text`.
-   Vector search using Qdrant.
-   Keyword retrieval using BM25 (`rank-bm25`).
-   Weighted hybrid retrieval combining normalized vector and keyword
    scores.
-   Cross-encoder reranking using
    `cross-encoder/ms-marco-MiniLM-L-6-v2`.
-   Local answer generation using `qwen2.5:3b` through Ollama.
-   PostgreSQL storage for document metadata and conversation records.
-   React/Vite frontend and FastAPI backend.
-   Docker-based backend setup.

Feature availability depends on the current configuration and successful
end-to-end testing.

## Architecture

``` text
React + Vite Frontend
         |
         v
    FastAPI Backend
         |
         +---- PDF Upload
         |       |
         |       v
         |   PyMuPDF extraction
         |       |
         |       v
         |   Text chunking
         |       |
         |       v
         |   Ollama embeddings ------> Qdrant
         |
         +---- User Question
                 |
                 +---- Vector search (Qdrant)
                 |
                 +---- Keyword search (BM25)
                          |
                          v
                    Hybrid ranking
                          |
                          v
                    CrossEncoder reranking
                          |
                          v
                    Retrieved context
                          |
                          v
                  Ollama qwen2.5:3b
                          |
                          v
                    Answer + sources

PostgreSQL: document metadata and conversation history
Docker: backend and supporting services
```

## Technology Stack

  -----------------------------------------------------------------------
  Component               Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React, Vite             Chat and
                                                  document-management
                                                  interface

  Backend                 Python, FastAPI         API endpoints and RAG
                                                  orchestration

  PDF processing          PyMuPDF                 Extract text and page
                                                  information

  Chunking                LangChain Text          Create overlapping text
                          Splitters               chunks

  Embeddings              Ollama,                 Convert text into
                          `nomic-embed-text`      vector representations

  Vector database         Qdrant                  Store and search
                                                  embeddings

  Keyword retrieval       `rank-bm25`             Match passages using
                                                  lexical relevance

  Reranking               Sentence Transformers   Reorder candidate
                          CrossEncoder            passages

  LLM                     Ollama, `qwen2.5:3b`    Generate answers from
                                                  retrieved context

  Relational database     PostgreSQL              Store document metadata
                                                  and chat history

  Containers              Docker                  Package backend
                                                  services
  -----------------------------------------------------------------------

## How It Works

### 1. Document ingestion

1.  The user selects a PDF.
2.  PyMuPDF extracts text from each page.
3.  LangChain's recursive character splitter divides the text into
    chunks.
4.  Ollama generates an embedding for each chunk.
5.  Qdrant stores vectors with payload metadata, including document
    name, document ID, page number, and chunk ID.
6.  Document metadata is tracked in PostgreSQL.

Current chunking configuration:

-   **Chunk size:** 800 characters
-   **Chunk overlap:** 150 characters

Overlap preserves some context between adjacent chunks. These values can
be tuned using a representative evaluation dataset.

### 2. Retrieval

For a user question, the system performs semantic vector search and BM25
keyword retrieval. The current hybrid scoring approach is:

``` text
hybrid_score = 0.6 * normalized_vector_score
             + 0.4 * normalized_keyword_score
```

The 60/40 weighting is a heuristic, not a universally optimal setting.
It should be evaluated against representative questions and expected
source passages.

### 3. Reranking

Candidate passages are scored using:

``` text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The CrossEncoder evaluates each question--passage pair and reorders the
candidates by relevance. Reranking can improve ordering but adds
inference cost.

### 4. Answer generation

The retrieved passages are provided as context to `qwen2.5:3b`, running
locally through Ollama. The model uses that context to formulate a
response. RAG can reduce unsupported answers, but it does not guarantee
correctness; answers and source citations should be tested.

## Project Structure

The backend contains modules for API routes, ingestion, retrieval,
reranking, keyword search, and generation. A representative layout is:

``` text
enterprise-knowledge-ai/
├── app/
│   ├── api/
│   │   └── documents.py
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   ├── reranker.py
│   │   ├── keyword_search.py
│   │   └── generation.py
│   └── main.py
├── documents/
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

The React frontend is maintained in the frontend portion of the
repository.

## Prerequisites

Install or configure:

-   Python 3.11
-   Node.js and npm
-   Docker Desktop
-   Ollama
-   Git

Pull the local models:

``` powershell
ollama pull nomic-embed-text
ollama pull qwen2.5:3b
ollama list
```

The Docker backend uses `host.docker.internal` to reach Ollama on the
Windows host by default.

## Configuration

The ingestion module supports these environment variables:

  -------------------------------------------------------------------------------------
  Variable                Default                               Purpose
  ----------------------- ------------------------------------- -----------------------
  `OLLAMA_URL`            `http://host.docker.internal:11434`   Ollama API endpoint

  `QDRANT_URL`            `http://qdrant:6333`                  Qdrant endpoint from
                                                                inside the Docker
                                                                network
  -------------------------------------------------------------------------------------

The configured Qdrant collection is `enterprise_documents`, with
768-dimensional vectors using cosine similarity.

Configure the PostgreSQL connection for your environment. Do not commit
passwords, API keys, or other secrets to Git. Use environment variables
or a local environment file excluded from version control.

## Run Locally

### 1. Start supporting services

Start Docker Desktop and ensure PostgreSQL and Qdrant are running on the
Docker network used by the backend.

``` powershell
docker ps
```

From a backend container named `enterprise-backend`, test Qdrant
connectivity with:

``` powershell
docker exec enterprise-backend python -c "import requests; print(requests.get('http://qdrant:6333/collections').text)"
```

This assumes both containers share a Docker network where the hostname
`qdrant` resolves.

### 2. Start the backend

Activate the virtual environment and install dependencies:

``` powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

From the backend project root:

``` powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

-   Swagger UI: `http://127.0.0.1:8001/docs`
-   Health endpoint: `http://127.0.0.1:8001/health`

Use service hostnames appropriate to the environment. Docker network
names such as `enterprise-postgres` and `qdrant` generally do not
resolve automatically from the Windows host.

### 3. Start the frontend

From the frontend directory:

``` powershell
npm install
npm run dev
```

Open the local URL printed by Vite, commonly `http://127.0.0.1:5173`.

## Docker

Build the backend image from the repository root:

``` powershell
docker build -t enterprise-ai-backend:latest .
```

Example command to start the backend on an existing Docker network:

``` powershell
docker run -d `
  --name enterprise-backend `
  --network enterprise-network `
  -p 8001:8001 `
  enterprise-ai-backend:latest
```

If a container with that name already exists, stop and remove it before
recreating it. Ensure PostgreSQL and Qdrant are running on
`enterprise-network` and the backend has the required database
configuration.

**Persistence warning:** Data may be lost when containers are recreated
if persistent volumes are not configured. Use named volumes for
PostgreSQL and Qdrant, and persistent storage for uploaded documents,
before relying on the system for important data.

## API Endpoints

  Endpoint                         Purpose
  -------------------------------- ---------------------------------------
  `GET /health`                    Check backend health
  `POST /documents/upload`         Upload and process a PDF
  `GET /documents/`                List documents
  `DELETE /documents/{filename}`   Delete a document
  `POST /ask`                      Submit a question to the RAG pipeline

Visit `http://127.0.0.1:8001/docs` for the exact request schemas and
current API behavior.

## Limitations and Roadmap

-   [ ] Verify PDF upload, extraction, embedding, and Qdrant insertion
    end-to-end.
-   [ ] Validate answers and source pages using known questions.
-   [ ] Add clearer ingestion status and error reporting.
-   [ ] Support more document formats, such as DOCX and TXT.
-   [ ] Build a repeatable RAG evaluation dataset and measure retrieval
    quality.
-   [ ] Implement authentication and role-based document access.
-   [ ] Add persistent volumes and a reproducible Docker Compose setup.
-   [ ] Improve logging, security, monitoring, and deployment
    reliability.

Known limitations:

-   Document upload and Qdrant writes have required debugging; verify
    the current environment before relying on them.
-   Retrieval quality has not yet been established with a formal
    benchmark.
-   The hybrid score weights are heuristic and need evaluation.
-   Authentication and role-based permissions should be treated as
    future work unless implemented and tested.
-   Local inference performance depends on hardware and concurrent
    workload.

## Learning Outcomes

This project provides practical experience with:

-   Designing a Retrieval-Augmented Generation pipeline.
-   Combining semantic and keyword retrieval.
-   Reranking candidate passages.
-   Integrating local embedding and language models.
-   Building APIs with FastAPI.
-   Using vector and relational databases.
-   Debugging Docker networking and Python dependency issues.

------------------------------------------------------------------------

**Author:** Aayush Mittal\
**Repository:**
[Intelligent-Enterprise-RAG-Pipeline](https://github.com/Aayush-Agarwal007/Intelligent-Enterprise-RAG-Pipeline)
