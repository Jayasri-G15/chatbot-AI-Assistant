# CRM AGENT ARCHITECTURE & TOOL SPECIFICATION

This document details the design, responsibilities, tools, and security boundaries of the **CRM Agent**.

---

## 1. Responsibilities

The **CRM Agent** acts as an intermediary between natural language user prompts and structured database operations over CRM data.

- **Intent Recognition**: Converts natural language requests into targeted database operations.
- **Controlled Tool Invocation**: Invokes strict, typed Python tools (`crm_tools.py`) to query PostgreSQL/SQLAlchemy.
- **SQL Execution Prohibition**: The LLM is strictly prohibited from generating or executing raw SQL strings directly.
- **Data Grounding**: Supplies structured JSON outputs to the Writer Agent to eliminate hallucinations.

---

## 2. Controlled Tools Registry

All CRM operations pass through 7 safe tools:

1. `search_customer(query: str)`: Searches customer records by name, email, or company.
2. `get_customer_details(customer_id: str)`: Fetches comprehensive customer profile with contacts, deals, and activities.
3. `get_customer_deals(customer_id: str, status: Optional[str])`: Returns deals belonging to a specific customer.
4. `get_top_customers(limit: int)`: Retrieves top customers ranked by open deal value.
5. `get_recent_activities(customer_id: Optional[str], limit: int)`: Returns recent call, meeting, email, or note activities.
6. `search_deals(status: Optional[str], min_value: Optional[float], max_value: Optional[float])`: Filters deals by status and monetary value.
7. `customer_summary(customer_id: str)`: Generates structured facts for AI summarization.

---

## 3. Security & Authorization

- **Server-Side Authorization**: Every tool accepts `current_user: User` and delegates to `CRMService`.
- **RBAC & Isolation Rules**:
  - `admin` / `manager`: Accesses all CRM records across all representatives.
  - `sales_rep` / `user`: Automatically restricted to records where `owner_id == user.id` or `owner_id IS NULL`.

---

## 4. Example Queries & Supported Intent Mapping

| User Query | Intent Classification | Tool Invoked | Grounded Output |
| :--- | :--- | :--- | :--- |
| *"Find customer ABC Ltd."* | `crm_query` | `search_customer(query="ABC Ltd")` | Returns ABC Ltd company profile |
| *"Show ABC Ltd's open deals."* | `crm_query` | `get_customer_deals(customer_id="ABC Ltd", status="open")` | Returns open deals totaling ₹20,50,000 |
| *"Which are the top 5 customers by deal value?"* | `crm_query` | `get_top_customers(limit=5)` | Ranked list of top 5 accounts by pipeline |
| *"Which deals are closing this month?"* | `crm_query` | `search_deals(status="open")` | List of upcoming open deals |
| *"Show recent activities for customer ABC Ltd."* | `crm_query` | `get_recent_activities(customer_id="ABC Ltd")` | Call and meeting log history |
| *"What is the total open pipeline value?"* | `crm_query` | `get_pipeline_summary()` | Aggregated pipeline metrics |

---

## 5. Agent Flow & Failure Handling

```
User Prompt
   ↓
Supervisor Agent (Classifies intent: crm_query)
   ↓
Planner Agent (Formulates step: [1] CRM Agent, [2] Writer Agent)
   ↓
CRM Agent (Interprets entity & selects tool)
   ↓
CRM Tool Validation & RBAC Check
   ↓
PostgreSQL Query via CRMService
   ↓
Structured Result JSON
   ↓
Writer Agent (Formulates Markdown response with ZERO hallucinations)
```

**Failure Handling**:
- If a customer or deal is not found, the tool returns `{"error": "Customer 'XYZ' not found"}`.
- The Writer Agent clearly informs the user without hallucinating fake records.
