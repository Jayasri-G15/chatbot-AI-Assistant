from typing import Any
from app.agents.state import AgentState


class PlannerAgent:
    """
    Decomposes multi-step user queries into an ordered sequence of specialist agent tasks.
    """

    def create_plan(self, state: AgentState) -> list[dict[str, Any]]:
        query = state.get("user_query", "").lower()
        has_docs = bool(state.get("document_ids"))
        intent = state.get("intent", "direct_chat")

        plan: list[dict[str, Any]] = []

        if intent == "crm_query":
            plan = [
                {"step": 1, "agent": "CRM Agent", "task": f"Execute controlled CRM tool query for: {query[:60]}"},
                {"step": 2, "agent": "Writer Agent", "task": "Synthesize grounded CRM answer from database results"},
            ]

        elif intent == "composite":
            step_idx = 1
            if any(k in query for k in ["customer", "deal", "pipeline", "lead", "activity", "sales", "abc ltd"]):
                plan.append({
                    "step": step_idx,
                    "agent": "CRM Agent",
                    "task": "Query CRM database for customer, deal, and sales pipeline data",
                })
                step_idx += 1

            if has_docs:
                plan.append({
                    "step": step_idx,
                    "agent": "Document Agent",
                    "task": "Retrieve and extract relevant contextual chunks from uploaded documents",
                })
                step_idx += 1

            if any(k in query for k in ["search", "find", "latest", "news", "trend", "current", "framework", "compare"]):
                plan.append({
                    "step": step_idx,
                    "agent": "Research Agent",
                    "task": f"Perform web search and gather current information for: {query[:60]}",
                })
                step_idx += 1

            if any(k in query for k in ["analyze", "data", "csv", "sum", "stats", "trend", "revenue", "average"]):
                plan.append({
                    "step": step_idx,
                    "agent": "Data Analyst Agent",
                    "task": "Compute numerical metrics, statistics, and table analysis",
                })
                step_idx += 1

            plan.append({
                "step": step_idx,
                "agent": "Writer Agent",
                "task": "Synthesize all specialist findings into a formatted final answer",
            })

        elif intent == "research":
            plan = [
                {"step": 1, "agent": "Research Agent", "task": f"Web search for: {query[:60]}"},
                {"step": 2, "agent": "Writer Agent", "task": "Synthesize research findings into final response"},
            ]
        elif intent == "data_analysis":
            plan = [
                {"step": 1, "agent": "Data Analyst Agent", "task": "Perform tabular & statistical computation"},
                {"step": 2, "agent": "Writer Agent", "task": "Format data insights into final response"},
            ]
        elif intent == "document_query":
            plan = [
                {"step": 1, "agent": "Document Agent", "task": "Retrieve top relevant document chunks"},
                {"step": 2, "agent": "Writer Agent", "task": "Synthesize document citations into answer"},
            ]
        else:
            plan = [
                {"step": 1, "agent": "Writer Agent", "task": "Direct assistant reply"},
            ]

        return plan
