# WEEK 9 ARCHITECTURE SPECIFICATION
## MULTI-AGENT AI ASSISTANT

**Project Name**: MULTI-AGENT AI ASSISTANT  
**Phase**: Week 9 - AI Agent Architecture, Tool Calling, Planning, Memory & Multi-Agent Collaboration  
**Foundation**: Biriyani AI Chatbot Application  
**Author**: Senior AI Architect & Full-Stack Engineer  

---

## 1. Executive Summary

This document establishes the architectural blueprint for upgrading the existing **Biriyani AI Chatbot** into an enterprise-grade **Multi-Agent AI Assistant** without rewriting the core application, breaking existing features, or altering the established stack. 

The upgraded system introduces:
- **Hierarchical Multi-Agent Orchestration** (Supervisor / Orchestrator pattern based on LangChain / CrewAI / AutoGen principles)
- **Dynamic Task Planning & Intent Routing** (Direct Chat vs. Single-Agent vs. Multi-Agent Workflows)
- **Specialized Worker Agents**: Research Agent, Data Analyst Agent, Document (RAG) Agent, and Writer Agent
- **Safe Sandboxed Tool Execution**: Controlled web search and isolated Python data analytics
- **Agent Memory & Shared Blackboard State**: Context propagation across agents
- **Real-Time Agent Activity Streaming**: Server-Sent Events (SSE) telemetry displaying agent thoughts and tool calls in the UI

---

## 2. Inspection of the Existing Project

### 2.1 Current Architecture & Technology Stack

| Layer | Technologies & Libraries | Current Status |
| :--- | :--- | :--- |
| **Frontend UI** | React 19, TypeScript, Vite 8, Tailwind CSS v4, `@tanstack/react-query`, `react-markdown` | Fully functional single-page chat interface with conversation drawer, voice recognition, and dark/light themes. |
| **Backend API** | Python 3.14 / FastAPI, Uvicorn, Pydantic v2, `pydantic-settings` | High-performance async REST API with Server-Sent Events (SSE) streaming for message delivery. |
| **Database** | SQLite 3 via SQLAlchemy 2.0 ORM (`backend/chat.db`) | Relational schema storing conversations, chronological messages, and uploaded document metadata. |
| **LLM Integration** | `openai` Python SDK (AsyncOpenAI client) targeting NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`) | Direct token streaming with fallback logic and system prompt safety enforcement. |
| **Document Processing** | `pypdf`, `python-docx`, native text decode | Upload endpoint extracts raw text up to 10MB per file; stores raw string in database. |
| **RAG System** | Basic context injection | Raw document text is dumped entirely into system prompt. No chunking, vector indexing, or semantic retrieval present. |
| **MCP System** | None | Model Context Protocol is not currently implemented. |
| **Authentication** | None | Single local user application by design. No session tokens, cookies, or user auth tables. |
| **Environment Config** | Pydantic Settings (`backend/.env`) | `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, `NVIDIA_MODEL`, `DATABASE_URL`, `CORS_ORIGINS`. |
| **Guardrails & Security** | In-memory regex rule engine (`guardrail_service.py`) | Proactively blocks jailbreak prompts, hacking queries, and system self-exposure attempts. |
| **Rate Limiting** | Sliding window rate limiter (`rate_limit_service.py`) | Caps requests at 10 requests / 60 seconds per client IP. |
| **Testing** | Pytest (`pytest-9.0.3`) | 18 passing tests covering conversation CRUD, document extraction, guardrails, and rate limiting. |

### 2.2 Current Chat Flow

```
                      +-------------------+
                      |   User Input      |
                      |  (Text / Voice)   |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |  Composer.tsx     |
                      | (Web Speech API)  |
                      +---------+---------+
                                |  POST /api/v1/conversations/{id}/messages
                                v
                      +-------------------+
                      |  FastAPI Router   |
                      |  (messages.py)    |
                      +---------+---------+
                                |
             +------------------+------------------+
             |                                     |
     [Rate Limit Check]                    [Guardrail Check]
     (Blocks >10 req/min)                  (Blocks jailbreaks)
             |                                     |
             +------------------+------------------+
                                |
                                v
                      +-------------------+
                      | Document Context  | (Dumps entire document text
                      | Concatenation     |  into prompt - No RAG)
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |  llm_service.py   |
                      |  (NVIDIA API)     |
                      +---------+---------+
                                |
                                v  SSE (data: {"type": "delta", "content": "..."})
                      +-------------------+
                      |  ChatWindow.tsx   |
                      | (MessageBubble)   |
                      +-------------------+
```

### 2.3 Existing Features & Capabilities
1. **Conversation Management**: Create, list, rename, delete chats, auto-titling from the first user prompt.
2. **Dual-Input Modalities**: Native keyboard typing plus hands-free browser Web Speech API voice recognition.
3. **Document Attachments**: Multipart upload for `.pdf`, `.docx`, `.txt`, `.md` up to 10MB with preview cards and deletion.
4. **Safety & Compliance**: Regex guardrails intercepting prompt injections and security exploitation before LLM invocation.
5. **Streaming Rendering**: Chunked SSE delivery rendered through `react-markdown` with code highlighting.
6. **Error Recovery**: Non-destructive draft retention allowing 1-click retry on connection or auth failures.

### 2.4 Missing Capabilities for Multi-Agent AI Assistant
1. **No Orchestration / Agent Division**: All prompts follow a linear single-call path to a single LLM prompt.
2. **No Tool Execution**: System cannot query live external data, browse the web, calculate formulas, or execute Python.
3. **No True RAG**: Document text is naively injected in its entirety into the prompt, risking context overflow and hallucinations for large files.
4. **No Plan Decomposition**: Complex multi-step queries (e.g., "Find the latest financial results, analyze quarterly revenue variance, and write an executive briefing") cannot be broken down and delegated.
5. **No Intermediate Agent Telemetry**: The UI has no mechanism to inform the user which agent is currently acting or what tools are being invoked.

---

## 3. Upgraded Target Multi-Agent Architecture

### 3.1 Architectural Diagram

```
                                  USER
                                    |
                                    v
                             CHAT INTERFACE
                    (Voice / Text / Document Attach)
                                    |
                                    v
                           FASTAPI CHAT ROUTER
                        (Guardrails & Rate Limit)
                                    |
                                    v
                         SUPERVISOR AGENT
                    +------------------------------+
                    | - Analyzes User Intent       |
                    | - Decides Agent Routing      |
                    | - Direct Chat vs Agent Flow  |
                    +---------------+--------------+
                                    |
                                    v
                              PLANNER MODULE
                    +------------------------------+
                    | - Decomposes Complex Tasks   |
                    | - Formulates Step Sequences  |
                    +---------------+--------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
          v                         v                         v
   RESEARCH AGENT           DATA ANALYST AGENT         DOCUMENT AGENT
+--------------------+    +--------------------+    +--------------------+
| - Web Search Tool  |    | - Sandboxed Python |    | - Text Chunking    |
| - Source Tracking  |    | - Pandas / NumPy   |    | - Semantic / RAG   |
| - Fact Extraction  |    | - Trend Analysis   |    | - Page Citation    |
+---------+----------+    +---------+----------+    +---------+----------+
          |                         |                         |
          +-------------------------+-------------------------+
                                    |
                                    v
                           SHARED AGENT STATE
                     (Blackboard / Memory Context)
                                    |
                                    v
                              WRITER AGENT
                    +------------------------------+
                    | - Synthesizes Findings       |
                    | - Enforces Cohesive Tone     |
                    | - Inlines Verifiable Sources |
                    +---------------+--------------+
                                    |
                                    v (Streamed SSE: Deltas + Agent Steps)
                             FINAL ANSWER
                                    |
                                    v
                             CHAT INTERFACE
```

---

## 4. Agent Specifications & Responsibilities

### 4.1 Supervisor Agent (Orchestrator)
- **Role**: Coordinates the entire lifecycle of a request.
- **Decision Engine**:
  - `DIRECT_CHAT`: Simple greetings, general knowledge, or conversational queries bypass sub-agents for instantaneous streaming.
  - `RESEARCH`: Queries requiring fresh real-world information, news, competitive intelligence, or web facts.
  - `DATA_ANALYSIS`: Queries with tabular data, numerical arrays, CSV/Excel attachments, or statistical calculation requests.
  - `DOCUMENT_QUERY`: Queries asking questions against uploaded documents (`.pdf`, `.docx`, `.txt`).
  - `COMPOSITE_TASK`: Multi-step requests requiring coordination (e.g., Document retrieval + Data analysis + Web comparison).
- **Control Loop**:
  1. Inspect user query, attached documents, and chat history.
  2. If single direct task: dispatch to relevant specialist agent.
  3. If multi-step task: invoke Planner, sequentially execute agent steps, feed results to Shared State.
  4. Hand over compiled context to the Writer Agent.

### 4.2 Research Agent
- **Role**: Discovers, gathers, and synthesizes up-to-date web intelligence.
- **Tool**: `search_web(query: str, max_results: int = 5)`
- **Output Schema**:
  ```json
  {
    "query": "latest AI agent frameworks 2026",
    "findings": [
      {
        "title": "State of Multi-Agent Systems in 2026",
        "url": "https://example.com/ai-agents",
        "summary": "Key trends including LangGraph, AutoGen 0.4, and CrewAI enterprise architectures..."
      }
    ]
  }
  ```
- **Integrity Rule**: Never hallucinate URLs or fabricate search results. When results are sparse, acknowledge constraints explicitly.

### 4.3 Data Analyst Agent
- **Role**: Computes statistics, identifies patterns, analyzes CSV/tabular data, and calculates trends.
- **Execution Sandbox**:
  - Controlled Python execution environment using a strict AST whitelist and isolated local scope.
  - Pre-imported utilities: `pandas as pd`, `numpy as np`, `math`, `statistics`.
  - Prohibited: `os`, `sys`, `subprocess`, `socket`, `open`, `__import__`, `eval`, `exec` on unvetted code.
- **Input Types**: Pasted tables/CSV in chat or attached data files.
- **Output**: Structured statistical summary, computed values, and table-ready insights.

### 4.4 Document Agent (Enhanced RAG)
- **Role**: Semantic retrieval and answer grounding over user-uploaded documents.
- **Upgrade from Current Baseline**:
  - Preserves existing document uploads (`pypdf`, `docx`, `txt`).
  - Introduces chunking (sliding window: 500 characters, 100 character overlap).
  - Implements lexical/TF-IDF and embedding similarity search to retrieve Top-K (K=3 to 5) most relevant chunks per query.
  - Attaches source citations (`[filename, Chunk #X]`) to each retrieved fragment.

### 4.5 Writer Agent
- **Role**: Generates the final, customer-ready markdown response.
- **Capabilities**:
  - Unifies multi-agent findings into a coherent narrative.
  - Enforces formatting standards: bold headers (`**Header**`), clean bullet points, code blocks with syntax tags.
  - Automatically appends a structured **Sources & References** section when research or document agents were utilized.

---

## 5. Agent Flow, Tool Flow, Memory Flow & Planning Flow

### 5.1 Planning Flow
```
User Prompt: "Compare our uploaded Q3 sales PDF with the current 2026 market growth rate."
     |
     v
Supervisor classifies as COMPOSITE_TASK
     |
     v
Planner decomposes into Execution Plan:
  Step 1: [Document Agent] -> Extract Q3 sales metrics from uploaded PDF
  Step 2: [Research Agent] -> Search 2026 market growth rate benchmarks
  Step 3: [Data Analyst Agent] -> Compute growth variance between company and market
  Step 4: [Writer Agent] -> Compose executive comparative analysis
```

### 5.2 Shared Agent State (Blackboard Pattern)
All agents interact through a typed state dictionary:
```python
class AgentState(TypedDict):
    conversation_id: str
    user_query: str
    history: list[dict[str, str]]
    document_ids: list[str]
    intent: str  # direct_chat | research | data_analysis | document_query | composite
    plan: list[dict[str, Any]]
    research_results: list[dict[str, Any]]
    data_results: dict[str, Any]
    document_chunks: list[dict[str, Any]]
    agent_trace: list[dict[str, str]]  # Telemetry emitted via SSE
    final_response: str
```

### 5.3 Streaming Telemetry Protocol
The SSE protocol is extended to send real-time agent updates to the frontend without breaking existing streaming:
```
data: {"type": "agent_step", "agent": "Supervisor", "action": "Analyzing intent & planning workflow..."}
data: {"type": "agent_step", "agent": "Research Agent", "action": "Searching web for: latest AI agent frameworks..."}
data: {"type": "agent_step", "agent": "Writer Agent", "action": "Synthesizing findings into final response..."}
data: {"type": "delta", "content": "Here is the "}
data: {"type": "delta", "content": "comparative analysis..."}
data: {"type": "done"}
```

---

## 6. Directory Structure & File Map

```
Biriyani-Chatbot-main/
├── WEEK9_ARCHITECTURE.md              <-- This document
└── biriyani/
    ├── backend/
    │   ├── app/
    │   │   ├── agents/               <-- NEW AGENT MODULE
    │   │   │   ├── __init__.py
    │   │   │   ├── state.py          <-- Shared blackboard state definition
    │   │   │   ├── supervisor.py     <-- Intent routing & execution supervisor
    │   │   │   ├── planner.py        <-- Step decomposition planner
    │   │   │   ├── research.py       <-- Web search & discovery agent
    │   │   │   ├── data_analyst.py   <-- Safe sandboxed calculation agent
    │   │   │   ├── document.py       <-- Document RAG retriever agent
    │   │   │   └── writer.py         <-- Synthesis & formatting agent
    │   │   ├── tools/                <-- NEW AGENT TOOLS
    │   │   │   ├── __init__.py
    │   │   │   ├── web_search.py     <-- DuckDuckGo/Tavily/Open search implementation
    │   │   │   ├── data_sandbox.py   <-- Isolated AST-checked Python runner
    │   │   │   └── rag_retriever.py  <-- Document chunking & similarity retriever
    │   │   ├── api/
    │   │   │   ├── messages.py       <-- Updated to stream agent steps & final answer
    │   │   │   ├── conversations.py  <-- Unchanged (preserves CRUD)
    │   │   │   └── documents.py      <-- Unchanged (preserves CRUD)
    │   │   ├── core/
    │   │   │   ├── config.py         <-- Add optional search / agent config settings
    │   │   │   └── database.py       <-- Unchanged
    │   │   ├── models/               <-- Unchanged (Conversation, Message, Document)
    │   │   ├── schemas/              <-- Unchanged
    │   │   └── services/
    │   │       ├── conversation_service.py <-- Unchanged
    │   │       ├── document_service.py     <-- Enhanced with chunking helper
    │   │       ├── guardrail_service.py    <-- Unchanged
    │   │       ├── llm_service.py          <-- Enhanced with structured reasoning helper
    │   │       └── rate_limit_service.py   <-- Unchanged
    │   └── tests/
    │       ├── test_agents.py        <-- NEW comprehensive test suite for all agents
    │       ├── test_tools.py         <-- NEW tests for web search, sandbox, and RAG
    │       └── ... (existing 18 tests remain 100% passing)
    └── frontend/
        └── src/
            ├── components/
            │   ├── AgentStepsBadge.tsx <-- NEW subtle badge showing active agent steps
            │   ├── ChatWindow.tsx      <-- Displays agent step stream before typing
            │   └── ... (all existing components preserved)
            ├── api/client.ts           <-- Typed for agent_step events
            └── hooks/useChat.ts        <-- Tracks current active agent & plan steps
```

---

## 7. Migration & Non-Regression Strategy

1. **Zero Database Migrations Required**: The existing SQLite schema (`Conversation`, `Message`, `Document`) fully supports multi-agent responses because all agent outputs compile cleanly into standard assistant message records.
2. **Backward Compatibility**: Any input not requiring agentic tools continues down the lightweight conversational path with sub-millisecond overhead.
3. **Guardrail Continuity**: All guardrail checks in `guardrail_service.py` execute *before* the Supervisor Agent evaluates intent, ensuring security invariants are preserved.
4. **Mock / Fallback Resilience**: If external LLM or Web Search APIs are offline or encounter rate limits, mock implementations automatically step in so developers can test all multi-agent features end-to-end.
5. **Full Test Suite Retention**: All 18 existing pytest test cases continue passing without regression.

---

## 8. Implementation Phases

- **Phase 1: Architecture Sign-Off**: Verification and acceptance of `WEEK9_ARCHITECTURE.md`.
- **Phase 2: Core Tool Implementation**: Web search tool, isolated Python data sandbox, and RAG chunking retriever.
- **Phase 3: Agent Architecture Implementation**: Supervisor, Planner, Research, Data Analyst, Document, and Writer agents.
- **Phase 4: Message Pipeline Integration**: Connecting `messages.py` to the Supervisor Agent with SSE telemetry.
- **Phase 5: Frontend Agent Step Visualization**: Displaying real-time agent activity badges in the chat interface.
- **Phase 6: Verification & Testing**: Comprehensive unit tests, end-to-end multi-agent scenario validation.
