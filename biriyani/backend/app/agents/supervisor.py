import json
from collections.abc import AsyncGenerator
from typing import Any
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.agents.research import ResearchAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.document import DocumentAgent
from app.agents.crm import CRMAgent
from app.agents.writer import WriterAgent
from app.models.document import Document
from app.models.user import User
from app.services.llm_service import stream_reply


MAX_AGENT_STEPS = 5


class SupervisorAgent:
    """
    Supervisor Agent / Orchestrator:
    - Decides when to route to Direct Chat vs Tool Execution
    - Executes tools via central ToolRegistry with server-side authorization
    - Binds execution steps to MAX_AGENT_STEPS (5) and detects repeated tool call loops
    - Synthesizes findings using WriterAgent
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.data_analyst_agent = DataAnalystAgent()
        self.document_agent = DocumentAgent()
        self.crm_agent = CRMAgent()
        self.writer_agent = WriterAgent()

    def classify_intent(self, query: str, has_documents: bool) -> str:
        q = query.lower().strip()

        # Direct simple chit-chat & general explanation heuristics
        greetings = {"hi", "hello", "hey", "thanks", "thank you", "good morning", "good evening", "who are you"}
        if q in greetings:
            return "direct_chat"

        # Explicit CRM keywords & entity queries
        crm_keywords = [
            "customer", "customers", "deal", "deals", "pipeline", "lead", "leads",
            "activity", "activities", "sales rep", "sales reps", "abc ltd", "top 5", "top customer",
            "closing this month", "open deal", "highest deal", "profile", "subscription", "usage"
        ]
        has_crm_mention = any(k in q for k in crm_keywords)

        # Explicit document keywords
        doc_keywords = ["document", "pdf", "docx", "file", "upload", "report", "attachment", "dataset", "contract"]
        has_doc_mention = any(w in q for w in doc_keywords)

        # Check for explicit multi-agent / composite triggers
        triggers = 0
        if any(w in q for w in ["search", "web", "find", "latest", "news", "trend", "current", "framework"]):
            triggers += 1
        if any(w in q for w in ["analyze", "data", "csv", "table", "calculate", "stat", "sum", "average"]):
            triggers += 1
        if has_documents and has_doc_mention:
            triggers += 1
        if has_crm_mention:
            triggers += 1

        if triggers >= 2:
            return "composite"
        if has_crm_mention:
            return "crm_query"
        if has_documents and has_doc_mention:
            return "document_query"
        if any(w in q for w in ["analyze", "data", "csv", "table", "calculate", "stat", "sum", "average", "metrics"]) and (has_doc_mention or "csv" in q or "data" in q or "table" in q):
            return "data_analysis"
        if any(w in q for w in ["search", "web", "find", "latest", "news", "trend", "current", "framework", "compare"]):
            return "research"

        return "direct_chat"

    async def process_and_stream(
        self,
        conversation_id: str,
        user_query: str,
        history: list[dict[str, str]],
        document_ids: list[str],
        db: Session,
        current_user: User = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        from app.tools.registry import tool_registry

        # Fetch uploaded documents
        docs = db.query(Document).filter(Document.conversation_id == conversation_id).all()
        has_docs = len(docs) > 0

        intent = self.classify_intent(user_query, has_docs)

        # 1. Direct Chat Route: Fast path directly to stream_reply
        if intent == "direct_chat":
            yield {"type": "agent_step", "agent": "Supervisor", "action": "Direct Chat mode active"}
            
            # Use RAG retriever if documents exist and query references documents
            document_texts = None
            doc_keywords = ["document", "pdf", "docx", "file", "upload", "report", "attachment", "dataset", "contract", "summary", "summarize", "find", "what", "according"]
            if has_docs and any(k in user_query.lower() for k in doc_keywords):
                from app.tools.rag_retriever import retrieve_document_chunks
                chunks = retrieve_document_chunks(user_query, docs)
                if chunks:
                    document_texts = [
                        f"[Source: {c['filename']}, Chunk {c['chunk_index']}/{c['total_chunks']}]\n{c['text']}"
                        for c in chunks
                    ]
            
            async for delta in stream_reply(history, documents_context=document_texts):
                yield {"type": "delta", "content": delta}
            return

        # 2. Multi-Agent & Tool Orchestration Route
        state: AgentState = {
            "conversation_id": conversation_id,
            "user_query": user_query,
            "history": history,
            "document_ids": document_ids,
            "intent": intent,
            "plan": [],
            "research_results": [],
            "data_results": {},
            "document_chunks": [],
            "crm_tool": "",
            "crm_results": {},
            "agent_trace": [],
        }

        yield {
            "type": "agent_step",
            "agent": "Supervisor Agent",
            "action": f"Classified intent: '{intent.upper()}'. Formulating tool plan...",
        }

        # Step B: Planner Agent
        plan = self.planner.create_plan(state)
        state["plan"] = plan
        yield {
            "type": "agent_step",
            "agent": "Planner Agent",
            "action": f"Formulated {len(plan)}-step plan across specialist tools",
        }

        # Step C: Sequential Bounded Execution of Tools
        executed_signatures = set()
        step_count = 0

        for step in plan:
            if step_count >= MAX_AGENT_STEPS:
                yield {
                    "type": "agent_step",
                    "agent": "Supervisor Agent",
                    "action": f"Reached maximum allowed agent step limit ({MAX_AGENT_STEPS}). Concluding loop.",
                }
                break

            agent_name = step.get("agent")
            task_desc = step.get("task", "")

            # Prevent loop on identical repeated steps
            sig = f"{agent_name}:{task_desc}"
            if sig in executed_signatures:
                continue
            executed_signatures.add(sig)

            step_count += 1

            if agent_name == "CRM Agent":
                yield {"type": "agent_step", "agent": "CRM Tool", "action": task_desc}
                crm_out = self.crm_agent.run(state, db, current_user)
                state.update(crm_out)

            elif agent_name == "Document Agent" and has_docs:
                yield {"type": "agent_step", "agent": "RAG Tool", "action": task_desc}
                doc_res = self.document_agent.run(state, db)
                state.update(doc_res)

            elif agent_name == "Research Agent":
                yield {"type": "agent_step", "agent": "Web Tool", "action": task_desc}
                res_out = self.research_agent.run(state)
                state.update(res_out)

            elif agent_name == "Data Analyst Agent":
                yield {"type": "agent_step", "agent": "Data Sandbox Tool", "action": task_desc}
                data_out = self.data_analyst_agent.run(state)
                state.update(data_out)

        # Step D: Writer Agent Response Synthesis
        yield {
            "type": "agent_step",
            "agent": "Writer Agent",
            "action": "Synthesizing tool findings into grounded response...",
        }

        async for delta in self.writer_agent.stream_final_response(state):
            yield {"type": "delta", "content": delta}

