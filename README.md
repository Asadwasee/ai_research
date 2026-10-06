# AI Research & Report Generation Agent

An agentic AI research system that takes a complex research question, performs structured research across web and academic sources, collects evidence, validates claims, and generates an evidence-grounded research report with source citations.

---

## Overview

The **AI Research & Report Generation Agent** is an Agentic AI application designed to automate the research and report-generation process.

Instead of simply answering a question like a traditional chatbot, the system is designed to break a complex research query into smaller research tasks, gather information from multiple sources, identify relevant evidence, verify claims, and generate a structured final report.

### Example Research Query

```text
Compare RAG, fine-tuning, and long-context LLMs for enterprise customer support.
```

The system is designed to transform a complex query into a structured research workflow:

```text
User Query
    ↓
Research Planning
    ↓
Research Tasks
    ↓
Web / Academic Research
    ↓
Source Collection
    ↓
Evidence Extraction
    ↓
Claim Verification
    ↓
Report Generation
    ↓
Citation Validation
    ↓
Final Research Report
```

---

## Project Goals

The main goals of this project are:

* Build a practical Agentic AI research system
* Use LangGraph for workflow orchestration
* Perform research using multiple information sources
* Collect and normalize research sources
* Ground generated content in retrieved evidence
* Reduce unsupported or hallucinated claims
* Generate structured research reports
* Validate source citations
* Provide a clean API for the frontend
* Build the project using free or free-tier technologies
* Demonstrate production-oriented software architecture

---

## Key Features

### Current Features

The following components have already been implemented and tested:

* FastAPI backend
* Health check API
* Pydantic domain schemas
* Research API foundation
* Research service layer
* LLM abstraction layer
* Gemini API integration
* LangGraph workflow foundation
* Research tool abstraction
* Web search integration with Tavily
* Academic search integration with arXiv
* Normalized research source model
* Deterministic source IDs
* Research tool validation
* Custom research tool exceptions
* Provider error handling
* Timeout handling
* XML parsing for arXiv results
* Mock-based automated tests
* Unit tests for research tools
* Workflow tests
* LLM tests
* API tests

---

## Planned Features

The following components are planned for the next development stages:

* Research Router Agent
* Parallel research execution
* Evidence extraction agent
* Evidence quality evaluation
* Claim verification / fact-checking agent
* Local document RAG
* PDF document ingestion
* Document chunking
* Embedding generation
* Vector database integration
* Semantic search
* Research synthesis
* Report generation agent
* Citation validation
* Citation-aware final response
* Research evaluation
* RAG evaluation
* Observability and logging
* Frontend interface
* Research progress tracking
* Error recovery
* Security improvements
* Performance optimization
* Free deployment

---

# Architecture

The planned high-level architecture is:

```text
                        ┌──────────────────────┐
                        │       User           │
                        │ Research Question    │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │    React Frontend    │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │      FastAPI         │
                        │       Backend        │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │     LangGraph        │
                        │ Workflow Orchestrator│
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Research Planner     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │    Research Router   │
                        └───────┬───────┬──────┘
                                │       │
                  ┌─────────────┘       └──────────────┐
                  ▼                                    ▼
        ┌──────────────────┐                  ┌──────────────────┐
        │   Web Search     │                  │ Academic Search  │
        │     Tavily       │                  │      arXiv       │
        └────────┬─────────┘                  └────────┬─────────┘
                 │                                     │
                 └────────────────┬────────────────────┘
                                  ▼
                        ┌──────────────────────┐
                        │  Evidence Extraction │
                        │        Agent         │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Fact Checker /     │
                        │  Claim Verification  │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Report Generator   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Citation Validator   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Final Research     │
                        │       Report         │
                        └──────────────────────┘
```

---

# Technology Stack

## Backend

* Python 3.12
* FastAPI
* Pydantic
* Pydantic Settings
* Uvicorn

## AI / LLM

* Google Gemini API
* `google-genai`
* LangGraph
* LangChain Core where useful

## Research

* Tavily Web Search
* arXiv API
* Planned: Semantic Scholar
* Planned: Crossref

## RAG

Planned technologies:

* Sentence Transformers
* ChromaDB
* PyMuPDF
* python-docx

## Evaluation

Planned:

* Ragas
* Custom evaluation metrics

## Frontend

Planned:

* React
* Vite
* Tailwind CSS

---

# Project Structure

Current backend structure:

```text
ai-research-agent/
│
├── .gitignore
│
└── backend/
    │
    ├── app/
    │   │
    │   ├── __init__.py
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── routes/
    │   │       ├── __init__.py
    │   │       ├── health.py
    │   │       └── research.py
    │   │
    │   ├── core/
    │   │   ├── __init__.py
    │   │   └── config.py
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── research_service.py
    │   │   ├── workflow_service.py
    │   │   └── llm/
    │   │       ├── __init__.py
    │   │       ├── base.py
    │   │       └── gemini.py
    │   │
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── research.py
    │   │   ├── source.py
    │   │   ├── evidence.py
    │   │   └── report.py
    │   │
    │   └── workflow/
    │       ├── __init__.py
    │       ├── state.py
    │       ├── graph.py
    │       └── nodes/
    │           ├── __init__.py
    │           └── planner.py
    │
    ├── scripts/
    │   └── test_gemini_connection.py
    │
    ├── tests/
    │   ├── __init__.py
    │   ├── test_health.py
    │   ├── test_llm.py
    │   ├── test_planner.py
    │   ├── test_research_api.py
    │   ├── test_research_tools.py
    │   ├── test_schemas.py
    │   ├── test_workflow.py
    │   └── test_workflow_service.py
    │
    ├── main.py
    ├── requirements.txt
    └── .env.example
```

---

# Research Tools Layer

The project uses a common abstraction for research providers.

```text
ResearchTool
    │
    ├── TavilyWebSearchTool
    │
    └── ArxivAcademicSearchTool
```

This allows additional research providers to be added without tightly coupling the workflow to a specific provider.

---

## Web Search

The web research layer uses **Tavily** to retrieve web sources.

The results are normalized into the project's common `ResearchSource` schema.

Example conceptual result:

```text
ResearchSource
├── source_id
├── title
├── url
├── source_type
├── publisher
├── authors
└── published_at
```

---

## Academic Search

The academic research layer currently uses the public arXiv API.

The implementation:

* Sends asynchronous HTTP requests
* Parses Atom XML responses
* Extracts paper metadata
* Extracts authors
* Extracts publication dates
* Generates deterministic source IDs
* Handles malformed XML
* Handles timeout errors
* Handles network errors
* Handles HTTP/provider errors

The project intentionally uses the arXiv API directly instead of depending on an unnecessary Python wrapper package.

---

# LLM Architecture

The project uses an LLM abstraction rather than directly coupling application logic to Gemini.

Conceptually:

```text
LLM Provider Interface
        │
        ▼
Gemini LLM Provider
        │
        ▼
Google Gemini API
```

This design makes it easier to replace or add another model provider in the future.

---

# Workflow Architecture

LangGraph is used as the workflow orchestration layer.

The workflow is designed around explicit states and nodes rather than putting the entire research process inside one large function.

Planned workflow:

```text
START
  ↓
Planner
  ↓
Research Router
  ↓
Research Tools
  ↓
Evidence Extraction
  ↓
Fact Checking
  ↓
Report Generation
  ↓
Citation Validation
  ↓
END
```

---

# Error Handling

The project includes explicit error handling for research providers.

Examples include:

* Invalid research parameters
* Empty queries
* Invalid result limits
* Missing API configuration
* Provider failures
* Network failures
* Request timeouts
* HTTP errors
* Malformed academic XML
* Unexpected provider errors

Custom exceptions are used to keep provider-level failures separate from application-level errors.

---

# Testing

The project uses `pytest` for automated testing.

Testing currently covers:

* API endpoints
* Pydantic schemas
* LLM provider
* Planner
* LangGraph workflow
* Workflow service
* Research tool validation
* Tavily integration behavior
* arXiv integration behavior
* Error handling
* Timeout handling
* Provider failures
* XML parsing

Research provider APIs are mocked during tests so tests do not depend on live external services.

Run the research tool tests:

```bash
python -m pytest tests/test_research_tools.py -vv
```

Run the complete test suite:

```bash
python -m pytest tests/
```

Check installed package consistency:

```bash
pip check
```

---

# Environment Variables

Create a `.env` file inside the `backend` directory.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

TAVILY_API_KEY=your_tavily_api_key
```

> Never commit the real `.env` file or API keys to GitHub.

The repository should only contain `.env.example`.

---

# Installation

## 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd ai-research-agent
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
cd backend
pip install -r requirements.txt
```

## 4. Configure environment variables

Create:

```text
backend/.env
```

and add the required API keys.

## 5. Run the backend

```powershell
uvicorn main:app --reload
```

The API will be available locally through the FastAPI development server.

---

# API

Current API development is centered around the research endpoint and health check.

Health endpoint:

```text
GET /health
```

Research API:

```text
POST /research
```

The API layer will evolve as the complete agent workflow is implemented.

---

# Development Roadmap

## Phase 1 — Backend Foundation

* [x] Project setup
* [x] FastAPI configuration
* [x] Application configuration
* [x] Health endpoint
* [x] Basic tests

## Phase 2 — Domain Architecture

* [x] Research schemas
* [x] Source schema
* [x] Evidence schema
* [x] Report schema
* [x] Research service

## Phase 3 — LLM Layer

* [x] LLM abstraction
* [x] Gemini provider
* [x] Gemini connection testing

## Phase 4 — Agent Workflow

* [x] LangGraph setup
* [x] Workflow state
* [x] Workflow graph
* [x] Planner node
* [x] Workflow service

## Phase 5 — Research Tools

* [x] Research tool abstraction
* [x] Tavily web search
* [x] arXiv academic search
* [x] Source normalization
* [x] Provider error handling
* [x] Research tool tests

## Phase 6 — Evidence Pipeline

* [ ] Research router
* [ ] Evidence extraction
* [ ] Evidence quality scoring
* [ ] Claim verification
* [ ] Evidence-grounded state management

## Phase 7 — RAG

* [ ] PDF ingestion
* [ ] Document parsing
* [ ] Chunking
* [ ] Embeddings
* [ ] ChromaDB
* [ ] Semantic retrieval
* [ ] Local document research

## Phase 8 — Report Generation

* [ ] Research synthesis
* [ ] Structured report generation
* [ ] Citation generation
* [ ] Citation validation
* [ ] Unsupported claim detection

## Phase 9 — Evaluation

* [ ] Research quality evaluation
* [ ] Citation correctness evaluation
* [ ] RAG evaluation
* [ ] Hallucination checks
* [ ] Ragas integration

## Phase 10 — Frontend

* [ ] React application
* [ ] Research query interface
* [ ] Research progress UI
* [ ] Source display
* [ ] Evidence display
* [ ] Final report UI

## Phase 11 — Deployment

* [ ] Frontend deployment
* [ ] Backend deployment
* [ ] Environment configuration
* [ ] Production error handling
* [ ] Performance optimization

---

# Design Principles

This project follows several engineering principles:

### Separation of Concerns

Research providers, LLM providers, workflow logic, schemas, services, and API routes are separated.

### Provider Abstraction

External research providers are accessed through a common interface.

### Testability

External APIs are mocked during tests to make tests deterministic and reliable.

### Explicit Workflow

The research process is represented as explicit LangGraph nodes and state transitions.

### Evidence Grounding

The final system is designed to generate answers based on retrieved evidence instead of relying only on the LLM's internal knowledge.

### Extensibility

The architecture is designed so additional research providers, LLM providers, and retrieval systems can be added later.

---

# Security Considerations

The project is currently a portfolio/demo application.

Before production use, additional security work would be required, including:

* API authentication
* Rate limiting
* Request validation
* API key protection
* Secret management
* Input sanitization
* SSRF protection for URL-based retrieval
* Abuse prevention
* Logging and monitoring
* Production CORS configuration

---

# Current Status

The project is actively under development.

### Completed

```text
Backend Foundation
        ↓
API Architecture
        ↓
Domain Schemas
        ↓
LLM Layer
        ↓
LangGraph Foundation
        ↓
Research Tools
        ↓
Automated Tests
```

### Currently Next

```text
Research Router
        ↓
Evidence Extraction
        ↓
Evidence Verification
        ↓
RAG
        ↓
Report Generation
        ↓
Citation Validation
        ↓
Frontend
        ↓
Deployment
```

---

# Why This Project?

This project demonstrates practical experience with:

* Full-stack AI application architecture
* Agentic AI
* LangGraph
* LLM integration
* Tool calling
* Web research
* Academic research
* RAG
* Vector databases
* Evidence grounding
* Citation validation
* API development
* Automated testing
* Modular software architecture

The primary goal is to demonstrate how an LLM can be integrated into a structured, testable, evidence-grounded software system rather than building a simple chatbot.

---

# License

This project is currently developed as a portfolio/demo project.

License information will be added before public production use.

````

### GitHub par push karne se pehle

Abhi **README ko project ki current reality ke mutabiq rakho**. Jo features abhi nahi bane unko `[ ]` aur “Planned” mein rakha hai — ye important hai, warna GitHub par lagega ke project completed hai jabke abhi development chal rahi hai.

Tumhara next GitHub process roughly ye hoga:

```text
git init
↓
git status
↓
.gitignore verify
↓
README.md add
↓
git add .
↓
git commit
↓
GitHub repository create
↓
git remote add origin ...
↓
git push
````

**Ek important cheez:** `.env` aur API keys GitHub par **bilkul push nahi karni**. `.gitignore` mein `.env` hona chahiye.

Aur README mein maine **fake claims nahi kiye** — Step 1–7 completed hain, baqi clearly roadmap mein hain. Ye portfolio ke liye better approach hai.
