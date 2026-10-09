from typing import Any
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.models.document import Document
from app.tools.rag_retriever import retrieve_document_chunks


class DocumentAgent:
    """
    Document Agent: Connects existing document uploads to RAG retriever with top-k chunking and citations.
    """

    def run(self, state: AgentState, db: Session) -> dict[str, Any]:
        query = state.get("user_query", "")
        conversation_id = state.get("conversation_id", "")
        trace = state.get("agent_trace", [])

        trace.append({
            "agent": "Document Agent",
            "action": "Querying RAG retriever over uploaded conversation documents...",
        })

        # Fetch conversation documents from database
        docs = (
            db.query(Document)
            .filter(Document.conversation_id == conversation_id)
            .all()
        )

        chunks = retrieve_document_chunks(query, docs)

        trace.append({
            "agent": "Document Agent",
            "action": f"Retrieved {len(chunks)} relevant document chunks with source tags.",
        })

        return {
            "document_chunks": chunks,
            "agent_trace": trace,
        }
