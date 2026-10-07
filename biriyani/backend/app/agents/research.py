from typing import Any
from app.agents.state import AgentState
from app.tools.web_search import search_web


class ResearchAgent:
    """
    Research Agent: Discovers, gathers, and extracts relevant web information.
    Never fabricates sources or links.
    """

    def run(self, state: AgentState) -> dict[str, Any]:
        query = state.get("user_query", "")
        trace = state.get("agent_trace", [])

        trace.append({
            "agent": "Research Agent",
            "action": f"Searching web for: '{query[:50]}...'",
        })

        findings = search_web(query, max_results=4)

        trace.append({
            "agent": "Research Agent",
            "action": f"Retrieved {len(findings)} web sources with verified citations.",
        })

        return {
            "research_results": findings,
            "agent_trace": trace,
        }
