# AI Research & Report Generation Agent

An agentic AI research system that takes a complex research question, performs structured research across web and academic sources, and generates an evidence-grounded research report with real-time progress streaming and source citations.

---

## Overview

The **AI Research & Report Generation Agent** is a full-stack Agentic AI application designed to automate the research and report-generation process.

Instead of simply answering a question like a traditional chatbot, the system uses **LangGraph** to break a complex query into smaller tasks, gathers information from multiple sources, and streams its thought process (Planning → Searching → Writing) in real-time to a modern React frontend.

### Example Research Query

```text
Compare RAG, fine-tuning, and long-context LLMs for enterprise customer support.
```

## Key Features (Completed)

- **Real-Time Agentic Workflow:** LangGraph orchestration (Planner → Researcher → Writer) with Server-Sent Events (SSE) streaming progress to the UI.
- **Modern Frontend Dashboard:** React + Vite + Tailwind v4 interface featuring a clean, enterprise-grade Zinc/Indigo minimalist design.
- **Multi-Source Research:** Integration with Tavily (Web) and arXiv (Academic) APIs to gather diverse data points.
- **Structured Output Validation:** FastAPI backend utilizing Pydantic v2 to enforce strict data schemas for sources, claims, and final reports.
- **Rich Text & Exports:** React-Markdown integration for beautiful report rendering, complete with "Copy to Clipboard" and "Download as .md" functionality.
- **Robust Error Handling:** Self-correcting retry loops within the AI agent, custom exceptions, and timeout management.

## Technology Stack

**Backend & AI Orchestration:**

- Python 3.12, FastAPI, Uvicorn
- LangGraph, Pydantic v2
- Google Gemini API (`google-genai`)

**Frontend:**

- React 18, Vite, TypeScript
- Tailwind CSS v4, Lucide React, Framer Motion
- React-Markdown

**Research Integrations:**

- Tavily Search API
- arXiv Public API

## High-Level Architecture

```text
 ┌──────────────────────┐      ┌──────────────────────┐
 │    User Interface    │ ◄──► │    FastAPI Backend   │
 │ (React/Vite/Tailwind)│ SSE  │ (Streaming Endpoint) │
 └──────────┬───────────┘      └──────────┬───────────┘
            │                             │
            ▼                             ▼
 ┌──────────────────────┐      ┌──────────────────────┐
 │    Export Options    │      │ LangGraph Orchestrator│
 │ (Markdown Download)  │      └──────────┬───────────┘
 └──────────────────────┘                 │
                                          ▼
                               ┌──────────────────────┐
                               │   Research Planner   │
                               └──────────┬───────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │   Research Router    │
                               ├──────────┬───────────┤
                               ▼          ▼           ▼
                         ┌────────┐ ┌────────┐ ┌────────┐
                         │ Tavily │ │ arXiv  │ │ Custom │
                         └────────┘ └────────┘ └────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │   Report Generator   │
                               │ (Markdown Synthesis) │
                               └──────────────────────┘
```

## Installation & Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd ai-research-agent
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```ini
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the backend server:

```bash
uvicorn main:app --reload
```

### 3. Frontend Setup

Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

## Development Roadmap

### Phase 1-3: Backend & AI Foundation

- [x] FastAPI configuration & Health endpoints
- [x] Pydantic domain schemas (Report, Evidence, Source)
- [x] Gemini LLM integration & testing

### Phase 4-5: Agent Workflow & Tools

- [x] LangGraph setup (State, Nodes, Graph)
- [x] Tavily web search integration
- [x] arXiv academic search & XML parsing
- [x] Provider error handling & automated mocked tests

### Phase 6: Frontend & Streaming API

- [x] Server-Sent Events (SSE) streaming endpoint
- [x] React + Vite + Tailwind v4 setup
- [x] Real-time workflow progress UI
- [x] Professional report viewer with React-Markdown
- [x] Markdown download & Copy to clipboard features

### Phase 7: RAG & Document Ingestion (Planned)

- [ ] PDF document parsing
- [ ] Embedding generation & ChromaDB integration
- [ ] Semantic search & local document research

### Phase 8: Advanced Evaluation (Planned)

- [ ] Ragas integration for response quality
- [ ] Automated hallucination checks
- [ ] Citation correctness evaluation

## Security & Deployment Note

This project is currently developed as a portfolio/demo application. The `.env` file is excluded via `.gitignore` to prevent API key leakage. Before production deployment, implement rate limiting, authentication, and secure CORS policies.
