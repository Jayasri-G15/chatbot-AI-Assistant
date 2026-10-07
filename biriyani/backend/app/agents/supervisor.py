from collections.abc import AsyncGenerator
import json
from typing import Any
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.agents.research import ResearchAgent
from app.agents.data_analyst import DataAnalystAgent
from app.agents.document import DocumentAgent
from app.agents.writer import WriterAgent
from app.models.document import Document
from app.services.llm_service import stream_reply


class SupervisorAgent:
    """
    Supervisor Agent / Orchestrator:
    - Understands user request intent
    - Decides routing (Direct Chat vs Specialist Agents)
    - Coordinates Planner, Research, Data Analyst, Document, and Writer agents
    - Emits live agent telemetry traces over SSE
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.data_analyst_agent = DataAnalystAgent()
        self.document_agent = DocumentAgent()
        self.writer_agent = WriterAgent()

    def classify_intent(self, query: str, has_documents: bool) -> str:
        q = query.lower().strip()

        # Direct simple chit-chat & general explanation heuristics
        greetings = {"hi", "hello", "hey", "thanks", "thank you", "good morning", "good evening", "who are you"}
        if q in greetings:
            return "direct_chat"

        # Explicit document keywords
        doc_keywords = ["document", "pdf", "docx", "file", "upload", "report", "attachment", "dataset", "contract"]
        has_doc_mention = any(w in q for w in doc_keywords)

        # Check for explicit multi-agent / composite triggers
        triggers = 0
        if any(w in q for w in ["search", "web", "find", "latest", "news", "trend", "current", "framework"]):
            triggers += 1
        if any(w in q for w in ["analyze", "data", "csv", "table", "calculate", "stat", "sum", "average", "metrics"]):
            triggers += 1
        if has_documents and has_doc_mention:
            triggers += 1

        if triggers >= 2:
            return "composite"
        if has_documents and has_doc_mention:
            return "document_query"
        if any(w in q for w in ["analyze", "data", "csv", "table", "calculate", "stat", "sum", "average", "metrics"]) and (has_doc_mention or "csv" in q or "data" in q):
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
    ) -> AsyncGenerator[dict[str, Any], None]:
        # Fetch uploaded documents
        docs = db.query(Document).filter(Document.conversation_id == conversation_id).all()
        has_docs = len(docs) > 0

        intent = self.classify_intent(user_query, has_docs)

        # 1. Direct Chat Route: Fast path directly to stream_reply
        if intent == "direct_chat":
            yield {"type": "agent_step", "agent": "Supervisor", "action": "Direct Chat mode active"}
            
            # Only pass document context if query asks about documents
            document_texts = None
            doc_keywords = ["document", "pdf", "docx", "file", "upload", "report", "attachment", "dataset", "contract"]
            if has_docs and any(k in user_query.lower() for k in doc_keywords):
                document_texts = [
                    f"--- Document: {doc.filename} ---\n{doc.extracted_text}"
                    for doc in docs if doc.extracted_text
                ]
            
            async for delta in stream_reply(history, documents_context=document_texts):
                yield {"type": "delta", "content": delta}
            return

        # 2. Multi-Agent Orchestration Route
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
            "agent_trace": [],
        }

        # Step A: Supervisor Intent Classification
        yield {
            "type": "agent_step",
            "agent": "Supervisor Agent",
            "action": f"Classified intent: '{intent.upper()}'. Planning agent workflow...",
        }

        # Step B: Planner Agent
        plan = self.planner.create_plan(state)
        state["plan"] = plan
        yield {
            "type": "agent_step",
            "agent": "Planner Agent",
            "action": f"Formulated {len(plan)}-step plan across specialist agents",
        }

        # Step C: Sequential Execution of Planned Worker Agents
        for step in plan:
            agent_name = step.get("agent")
            task_desc = step.get("task", "")

            if agent_name == "Document Agent" and has_docs:
                yield {"type": "agent_step", "agent": "Document Agent", "action": task_desc}
                doc_res = self.document_agent.run(state, db)
                state.update(doc_res)

            elif agent_name == "Research Agent":
                yield {"type": "agent_step", "agent": "Research Agent", "action": task_desc}
                res_out = self.research_agent.run(state)
                state.update(res_out)

            elif agent_name == "Data Analyst Agent":
                yield {"type": "agent_step", "agent": "Data Analyst Agent", "action": task_desc}
                data_out = self.data_analyst_agent.run(state)
                state.update(data_out)

        # Step D: Writer Agent Response Synthesis
        yield {
            "type": "agent_step",
            "agent": "Writer Agent",
            "action": "Synthesizing multi-agent findings into final response...",
        }

        async for delta in self.writer_agent.stream_final_response(state):
            yield {"type": "delta", "content": delta}
