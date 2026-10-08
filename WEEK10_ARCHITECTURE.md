# WEEK 10 ARCHITECTURE SPECIFICATION
## AI-POWERED CRM ASSISTANT

**Project Name**: AI CRM ASSISTANT  
**Phase**: Week 10 - AI-Powered CRM Integration, Role-Based Access Control, CRM Tools & Natural Language Analytics  
**Foundation**: Multi-Agent AI Assistant (Week 9 Baseline)  
**Author**: Senior Full-Stack AI Engineer & Software Architect  

---

## 1. Executive Summary

This specification defines the architectural design to transform the existing **Multi-Agent AI Assistant** into an **AI-Powered CRM Assistant**. 

The Week 10 project extends the existing:
- Multi-Agent Architecture (Supervisor, Planner, Research, Data Analyst, Document RAG, Writer)
- Server-Sent Events (SSE) streaming API & Real-time Telemetry
- Fast API / Python backend & React 19 / TypeScript / Vite frontend
- Document extraction & RAG retriever
- Security Guardrails & Sliding-window Rate Limiter

By adding:
- **Full CRM Domain Entities**: Users, Customers, Contacts, Leads, Deals, Activities
- **Database Migrations & Seed Data**: PostgreSQL compatibility via SQLAlchemy ORM & Alembic migrations with realistic seed data (20+ customers, 30+ contacts, 20+ leads, 30+ deals, 50+ activities)
- **Role-Based Access Control (RBAC) & Data Isolation**: `admin`, `manager`, `sales_rep`, `user` roles with owner-level record filtering
- **Secure Authentication System**: JWT token-based authentication (`/api/v1/auth/login`, `/api/v1/auth/me`)
- **Controlled CRM Tools for AI Agents**: 7 safe CRM tools (`search_customer`, `get_customer_details`, `get_customer_deals`, `get_top_customers`, `get_recent_activities`, `search_deals`, `customer_summary`) - preventing direct LLM SQL generation
- **Natural Language CRM Querying & Analytics**: Pipeline summarization, top customer analysis, closing deals, and activity tracking
- **Integrated CRM UI Views**: Dedicated Customer, Lead, Deal, and Activity management tabs alongside the Chat Interface

---

## 2. Inspection of the Existing Project

### 2.1 Current Architecture & Technology Stack Verification

| Dimension | Component / Technology | Detailed Status & Assessment |
| :--- | :--- | :--- |
| **1. Frontend Framework** | React 19, TypeScript 5, Vite 8, `@tailwindcss/vite` v4, `@tanstack/react-query` v5, `react-markdown` v10 | Modern SPA in `biriyani/frontend/src`. Features message streaming, document attachments, voice recognition, theme toggle. |
| **2. Frontend Folder Structure** | `frontend/src/` -> `api/`, `components/`, `hooks/`, `App.tsx`, `main.tsx`, `index.css` | Component-driven structure (`ChatWindow`, `MessageBubble`, `Composer`, `Sidebar`, `SettingsModal`). |
| **3. Backend Framework** | Python 3.14, FastAPI 0.115.0, Uvicorn 0.30.6, Pydantic v2, `pydantic-settings` 2.5.0 | High-performance async REST API with custom exception handling and SSE streaming wrappers. |
| **4. Backend Folder Structure** | `backend/app/` -> `agents/`, `api/`, `core/`, `models/`, `schemas/`, `services/`, `tools/`, `main.py` | Modular layout separating API routers, ORM models, business logic services, agent definitions, and tools. |
| **5. Database** | SQLite 3 (`sqlite:///./chat.db`) via SQLAlchemy 2.0 ORM | Relational database. Will be upgraded for PostgreSQL support via SQLAlchemy ORM & Alembic migrations. |
| **6. Database Models** | `Conversation`, `Message`, `Document` | SQLite/SQLAlchemy tables with UUID primary keys and foreign key relationships. |
| **7. Authentication** | Currently None (Single local user mode) | Will add JWT authentication (`POST /api/v1/auth/login`) with `bcrypt` password hashing. |
| **8. Authorization** | Currently None | Will add server-side RBAC (`admin`, `manager`, `sales_rep`, `user`) & user-level isolation (`owner_id`). |
| **9. LLM Provider** | `openai` AsyncOpenAI targeting NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`, `meta/llama-3.2-11b-vision-instruct`) | Token streaming with fallback/mock capability for offline development. |
| **10. Existing Agent Arch** | Hierarchical Multi-Agent Orchestrator | Supervisor Agent -> Planner Agent -> Specialist Agents (Research, Data Analyst, Document) -> Shared State -> Writer Agent. |
| **11. Tool System** | Controlled internal tool functions | `search_web` (DuckDuckGo/Tavily), `data_sandbox` (AST-checked Python runner), `rag_retriever` (TF-IDF sliding-window matcher). |
| **12. Memory System** | Conversation context history | Chronological database messages loaded into `AgentState["history"]`. |
| **13. Planning System** | `PlannerAgent` (`planner.py`) | Decomposes composite requests into sequential agent steps. |
| **14. Existing RAG** | Sliding-window chunking & TF-IDF retriever | 500-character window, 100-character overlap chunking with top-K relevance scoring. |
| **15. Document Processing** | `pypdf` 5.1.0, `python-docx` 1.1.2 | Text extraction from PDF, DOCX, TXT, MD up to 10MB per file. |
| **16. Existing OCR** | Raw string extractors | Extractable PDF text and plain text parsing. |
| **17. Existing MCP** | None | Model Context Protocol not in current codebase. |
| **18. Existing API Endpoints** | `/health`, `/ready`, `/api/v1/conversations`, `/api/v1/messages`, `/api/v1/documents` | REST endpoints supporting JSON and Server-Sent Events. |
| **19. Streaming Impl.** | Server-Sent Events (SSE) | Yields JSON lines (`type: agent_step`, `type: delta`, `type: error`, `type: done`). |
| **20. Existing Tests** | Pytest 8.3.3 suite in `backend/tests/` | Unit and integration test coverage across API, agents, tools, guardrails, rate limiting. |
| **21. Environment Variables** | `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, `NVIDIA_MODEL`, `DATABASE_URL`, `CORS_ORIGINS` | Managed via `pydantic-settings` from `.env`. |
| **22. Docker Configuration** | None | Local python/node development environment. |

---

## 3. Preserved Baseline vs. New Additions

### What Will Be Preserved (100% Non-Breaking):
1. **Existing Chat Interface & Messaging Flow**: General conversational chat, voice input, document attachments, and history.
2. **Existing Multi-Agent Orchestration**: Supervisor Agent, Planner Agent, Research Agent, Data Analyst Agent, Document RAG Agent, Writer Agent.
3. **Existing Security Guardrails & Rate Limiting**: Prompt injection protection and client rate limits.
4. **Existing Database Entities**: `conversations`, `messages`, `documents`.
5. **Existing REST API Contracts**: `/api/v1/conversations`, `/api/v1/documents`, `/api/v1/messages`.

### What Will Be Added for Week 10 CRM Assistant:
1. **Authentication & User Management**:
   - `User` database entity (`id`, `name`, `email`, `password_hash`, `role`, `created_at`, `updated_at`).
   - Authentication endpoints (`POST /api/v1/auth/login`, `GET /api/v1/auth/me`).
   - JWT authorization header middleware (`Bearer <token>`).
2. **CRM Domain Database Schema**:
   - `customers` (`id`, `name`, `email`, `phone`, `company`, `owner_id`, `created_at`, `updated_at`).
   - `contacts` (`id`, `customer_id`, `name`, `email`, `phone`, `role`, `created_at`, `updated_at`).
   - `leads` (`id`, `name`, `company`, `status`, `source`, `owner_id`, `created_at`, `updated_at`).
   - `deals` (`id`, `customer_id`, `title`, `value`, `status`, `close_date`, `owner_id`, `created_at`, `updated_at`).
   - `activities` (`id`, `customer_id`, `type`, `subject`, `activity_date`, `notes`, `owner_id`, `created_at`, `updated_at`).
3. **CRM REST APIs**:
   - `GET /api/v1/customers` (search, pagination, filtering)
   - `GET /api/v1/customers/{id}` (full customer details with contacts, deals, activities)
   - `GET /api/v1/deals` (filtering by status, value, date, owner)
   - `GET /api/v1/activities` (filtering by customer, owner, type, date range)
   - `GET /api/v1/leads` (filtering by status, owner)
4. **CRM AI Agent & Tools**:
   - `CRMAgent` integrated into Supervisor Agent flow.
   - 7 Controlled CRM Tools:
     - `search_customer`
     - `get_customer_details`
     - `get_customer_deals`
     - `get_top_customers`
     - `get_recent_activities`
     - `search_deals`
     - `customer_summary`
5. **Frontend CRM Interface**:
   - Navigation bar: **Chat**, **Customers**, **Leads**, **Deals**, **Activities**.
   - Rich Data Tables with Search, Filter, Pagination, and Detail Drawers.
   - Structured CRM Result Cards inside Chat Messages.

---

## 4. CRM Architecture & Request Lifecycle

### 4.1 System Architecture Diagram

```
                                  USER
                                    |
                                    v
                           EXISTING FRONTEND SPA
                +-------------------+-------------------+
                |                                       |
                v                                       v
         CHAT INTERFACE                           CRM DASHBOARD VIEWS
       (Voice/Text/Docs)                      (Customers/Deals/Activities)
                |                                       |
                +-------------------+-------------------+
                                    |
                                    v (HTTP Bearer JWT Header)
                            AUTHENTICATION API
                                    |
                                    v
                           BACKEND FASTAPI ENGINE
                +-------------------+-------------------+
                |                                       |
                v                                       v
          CHAT API ROUTER                         CRM REST ROUTER
       (/api/v1/messages)                      (/api/v1/customers, etc)
                |                                       |
                v                                       v
         SUPERVISOR AGENT                          CRM SERVICE LAYER
        +---------------+                      (RBAC & Data Isolation)
        | Intent Router |                               |
        +-------+-------+                               |
                |                                       |
                v                                       v
           CRM AGENT                             CRM REPOSITORIES
        +---------------+                               |
        | CRM Tool Selection | <-------------------------+
        +-------+-------+
                |
                v
       CONTROLLED CRM TOOLS
    - search_customer
    - get_customer_details
    - get_customer_deals
    - get_top_customers
    - get_recent_activities
    - search_deals
    - customer_summary
                |
                v
       POSTGRESQL / SQLALCHEMY
     (Users, Customers, Contacts, Leads, Deals, Activities)
                |
                v
       STRUCTURED CRM RESULT
                |
                v
          WRITER AGENT
     (Grounded Natural Language Response)
                |
                v (SSE Stream)
       FRONTEND CHAT INTERFACE
```

### 4.2 End-to-End Request Lifecycle Example

**User Prompt**: *"Show me the top 5 customers by open deal value."*

1. **Frontend Request**: Frontend sends `POST /api/v1/conversations/{id}/messages` with JWT Auth Header `Authorization: Bearer <token>`.
2. **Authentication & Authorization**: FastAPI dependency `get_current_user` validates JWT token, extracts `user_id` and `role`.
3. **Supervisor Routing**: Supervisor Agent evaluates prompt intent -> classifies as `CRM_QUERY`.
4. **CRM Agent Dispatch**: CRM Agent selects controlled tool `get_top_customers(limit=5)`.
5. **Tool Validation & Authorization**:
   - Validates `1 <= limit <= 50`.
   - Passes `current_user` to CRM Service.
6. **CRM Service Execution**: Executes parameterised SQLAlchemy query over PostgreSQL tables:
   ```sql
   SELECT c.id, c.name, c.company, SUM(d.value) as total_deal_value 
   FROM customers c 
   JOIN deals d ON c.id = d.customer_id 
   WHERE d.status = 'open' 
   GROUP BY c.id, c.name, c.company 
   ORDER BY total_deal_value DESC 
   LIMIT 5;
   ```
7. **Structured Result**: Returns JSON data object containing 5 top customers with calculated deal totals.
8. **Writer Agent Grounding**: Writer Agent synthesizes natural language response using **ONLY** the returned JSON data. System prompt forbids inventing unreturned records or values.
9. **SSE Response**: Frontend receives real-time `agent_step` trace and streamed markdown text with a clean tabular summary.

---

## 5. Security & Authorization Model

### 5.1 Role-Based Access Control (RBAC)
- **`admin`**: Full access to all CRM records across all owners.
- **`manager`**: Full read/write access to company CRM records and team management.
- **`sales_rep`**: Access to records owned by the sales representative (`owner_id == user.id`) or unassigned records.
- **`user`**: Read-only access to assigned CRM records.

### 5.2 Strict Security Invariants
- **No Direct SQL LLM Execution**: The LLM NEVER receives raw database connections or SQL execution capabilities. It ONLY calls validated, typed python tools.
- **Server-Side Data Isolation**: All database queries enforce filtering by `owner_id` according to the caller's role.
- **Input Validation**: All tool arguments and REST parameters are strictly validated using Pydantic schemas.

---

## 6. Implementation Plan & Deliverables

1. **Phase 1**: Architecture Specification (`WEEK10_ARCHITECTURE.md`).
2. **Phase 2**: CRM Database Models, Alembic Migrations, and Seed Data (`20+ customers`, `30+ contacts`, `20+ leads`, `30+ deals`, `50+ activities`).
3. **Phase 3**: Authentication & Authorization Module (`auth_service.py`, `User` model, JWT tokens).
4. **Phase 4**: CRM Backend Services & Repositories (`customer_service`, `deal_service`, `activity_service`).
5. **Phase 5**: CRM REST API Endpoints (`/api/v1/auth`, `/api/v1/customers`, `/api/v1/deals`, `/api/v1/activities`, `/api/v1/leads`).
6. **Phase 6**: Controlled CRM Tools & CRM Agent (`crm_tools.py`, `crm_agent.py`, `supervisor.py` integration).
7. **Phase 7**: Frontend CRM Navigation & Views (Customer list/details, Deals board, Activities feed, Leads table).
8. **Phase 8**: Verification, Automated Pytest Suite & E2E Validation.
