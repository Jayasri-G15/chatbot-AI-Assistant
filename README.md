# MULTI-AGENT AI ASSISTANT

A production-oriented Multi-Agent AI Assistant built with FastAPI, React, TypeScript, and Vite. Features dynamic multi-agent orchestration (Supervisor, Planner, Research Agent, Data Analyst Agent, Document Agent RAG, and Writer Agent), streaming LLM responses (NVIDIA API), Web Speech voice input, document attachments, and regex guardrails.

---

## 🛠️ Stack
- **Frontend**: React 19 + TypeScript + Vite 8 + Tailwind CSS v4 + TanStack Query + Web Speech API
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + SQLite (local file, `backend/chat.db`)
- **Agents & Tools**: Supervisor Agent, Planner Agent, Research Agent (`search_web`), Data Analyst Agent (sandboxed Python/Pandas), Document Agent (sliding-window RAG retriever), Writer Agent (synthesis & markdown formatting)
- **LLM**: NVIDIA NIM / AsyncOpenAI API, streamed token-by-token with real-time agent telemetry

---

## 🚀 Setup & Execution (macOS / Linux)

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # edit .env and set your NVIDIA_API_KEY
uvicorn app.main:app --reload --port 8000
```

> **Note for Windows users**: Activate the virtual environment with `.\.venv\Scripts\activate` instead of `source .venv/bin/activate`.

---

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** in your web browser. The Vite dev server automatically proxies `/api` requests to the FastAPI backend on port 8000.

---

## 🧪 Running Tests (macOS / Linux)

```bash
cd backend
python3 -m pytest
```

Running pytest executes all 25 unit and integration tests across conversation CRUD, document extraction, guardrails, rate limiting, agent tools, and multi-agent orchestration.

---

## ✨ Features & Architecture

- **Multi-Agent Orchestration**: Supervisor Agent analyzes intent and routes tasks through dynamic Planner, Research, Data Analyst, Document, and Writer agents.
- **Real-Time Agent Telemetry**: Server-Sent Events (SSE) stream live agent thoughts (`Supervisor Agent: Planning workflow...`, `Research Agent: Searching web...`) into the chat UI before response streaming.
- **Dual-Input Modalities**: Native keyboard multiline composer plus hands-free Web Speech API voice-to-text recognition.
- **Document Attachments & RAG**: Upload `.pdf`, `.docx`, `.txt`, `.md` files (up to 10MB) with top-K sliding-window RAG chunking and source citations.
- **Sandboxed Data Analytics**: Data Analyst Agent parses CSV/tabular data and computes summary statistics safely.
- **Backend Guardrails & Rate Limiting**: Intercepts prompt injections, hacking queries, and system exposure attempts, with sliding-window client IP rate limiting.
- **Robust Error Recovery**: Non-destructive draft retention allowing 1-click retry on connection or auth failures.
