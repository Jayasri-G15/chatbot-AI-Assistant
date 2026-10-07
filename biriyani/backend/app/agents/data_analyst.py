from typing import Any
from app.agents.state import AgentState
from app.tools.data_sandbox import calculate_data_metrics


class DataAnalystAgent:
    """
    Data Analyst Agent: Analyzes tabular data, calculates statistics, and derives insights.
    Runs inside a controlled, isolated execution sandbox.
    """

    def run(self, state: AgentState) -> dict[str, Any]:
        query = state.get("user_query", "")
        chunks = state.get("document_chunks", [])
        trace = state.get("agent_trace", [])

        trace.append({
            "agent": "Data Analyst Agent",
            "action": "Analyzing numerical and tabular data in sandbox...",
        })

        # Combine text from query and document chunks to find tabular data or numbers
        combined_text = query + "\n\n" + "\n\n".join(c.get("text", "") for c in chunks)
        data_results = calculate_data_metrics(combined_text)

        trace.append({
            "agent": "Data Analyst Agent",
            "action": f"Data analysis complete: {data_results.get('summary', 'Metrics computed.')}",
        })

        return {
            "data_results": data_results,
            "agent_trace": trace,
        }
