import json
from collections.abc import AsyncGenerator
from typing import Any

from app.agents.state import AgentState
from app.services.llm_service import stream_reply, LLMServiceError


class WriterAgent:
    """
    Writer Agent: Synthesizes findings from Research, Data Analyst, Document, and CRM agents into
    a polished, customer-ready final response formatted in markdown with bold headers, tables, and citations.
    """

    def prepare_synthesized_prompt(self, state: AgentState) -> str:
        sections = []

        # 1. CRM Database Results (Highest Grounding Priority)
        crm_res = state.get("crm_results", {})
        crm_tool = state.get("crm_tool", "")
        if crm_res:
            crm_text = f"### Grounded CRM Database Results (Tool: `{crm_tool}`):\n"
            crm_text += json.dumps(crm_res, indent=2, default=str)
            crm_text += "\n\nCRITICAL GROUNDING RULES FOR CRM:\n"
            crm_text += "- You MUST strictly rely ONLY on the above CRM Database JSON results.\n"
            crm_text += "- NEVER invent customer names, deal values, deal titles, or activity notes not present in the JSON.\n"
            crm_text += "- If the result list is empty, state clearly that no matching records were found in the CRM database.\n"
            crm_text += "- Format monetary values cleanly (e.g. ₹12,00,000 or $1,200,000) and present lists in clean Markdown tables.\n"
            sections.append(crm_text)

        # 2. Research findings
        research = state.get("research_results", [])
        if research:
            research_text = "### Web Research Findings:\n"
            for item in research:
                research_text += f"- **{item.get('title')}** ({item.get('url')})\n  {item.get('summary')}\n"
            sections.append(research_text)

        # 3. Data Analyst findings
        data_res = state.get("data_results", {})
        if data_res and data_res.get("summary"):
            data_text = f"### Data Analyst Insights:\n{data_res.get('summary')}\n"
            if data_res.get("metrics"):
                data_text += f"Metrics: {data_res.get('metrics')}\n"
            sections.append(data_text)

        # 4. Document RAG chunks
        chunks = state.get("document_chunks", [])
        if chunks:
            doc_text = "### Relevant Uploaded Document Chunks:\n"
            for c in chunks:
                doc_text += f"- [File: {c.get('filename')}, Chunk {c.get('chunk_index')}/{c.get('total_chunks')}]: {c.get('text')}\n"
            sections.append(doc_text)

        context_block = "\n\n".join(sections)
        return context_block

    async def stream_final_response(
        self, state: AgentState
    ) -> AsyncGenerator[str, None]:
        user_query = state.get("user_query", "")
        history = state.get("history", [])
        synthesized_context = self.prepare_synthesized_prompt(state)

        # Prepare system instructions for Writer Agent
        writer_history = list(history)
        if synthesized_context:
            augmented_query = (
                f"{user_query}\n\n"
                f"[AGENT WORKFLOW CONTEXT & FINDINGS]:\n{synthesized_context}\n\n"
                f"Instructions for Writer Agent:\n"
                f"1. Explain the answer in simple, crystal-clear language that anyone can easily understand.\n"
                f"2. Use helpful formatting like Markdown tables, clean bullet points, and bold section headers (**Header**).\n"
                f"3. Avoid robotic meta-phrases like 'Based on the agent workflow context' or 'The tool returned'.\n"
                f"4. If CRM database data is present, present exact numbers and titles from the CRM context."
            )
            if writer_history and writer_history[-1]["role"] == "user":
                writer_history[-1] = {"role": "user", "content": augmented_query}
            else:
                writer_history.append({"role": "user", "content": augmented_query})

        async for delta in stream_reply(writer_history):
            yield delta
