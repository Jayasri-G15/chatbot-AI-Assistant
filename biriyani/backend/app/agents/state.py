from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    conversation_id: str
    user_query: str
    history: list[dict[str, str]]
    document_ids: list[str]
    intent: str  # "direct_chat" | "research" | "data_analysis" | "document_query" | "crm_query" | "composite"
    plan: list[dict[str, Any]]
    research_results: list[dict[str, Any]]
    data_results: dict[str, Any]
    document_chunks: list[dict[str, Any]]
    crm_tool: str
    crm_results: dict[str, Any]
    agent_trace: list[dict[str, str]]  # Telemetry items: {"agent": "...", "action": "..."}
    final_response: str
