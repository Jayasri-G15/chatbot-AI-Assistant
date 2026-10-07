from app.agents.supervisor import SupervisorAgent
from app.agents.planner import PlannerAgent
from app.agents.writer import WriterAgent
from app.agents.state import AgentState


def test_supervisor_intent_classification():
    sup = SupervisorAgent()
    
    # Direct chat
    assert sup.classify_intent("hello", has_documents=False) == "direct_chat"
    
    # Research intent
    assert sup.classify_intent("search for latest AI agent frameworks 2026", has_documents=False) == "research"
    
    # Data analysis intent
    assert sup.classify_intent("analyze this sales data table and sum metrics", has_documents=False) == "data_analysis"
    
    # Composite intent (document + search + analysis)
    assert sup.classify_intent("search for market trends and analyze our uploaded report data", has_documents=True) == "composite"

    # General explanation with documents attached defaults to direct chat without forcing document query
    assert sup.classify_intent("explain machine learning simply", has_documents=True) == "direct_chat"


def test_planner_creates_structured_plan():
    planner = PlannerAgent()
    state: AgentState = {
        "user_query": "search for AI agent frameworks and analyze data",
        "intent": "composite",
        "document_ids": ["doc1"],
    }
    plan = planner.create_plan(state)
    assert len(plan) >= 2
    agent_names = [p["agent"] for p in plan]
    assert "Writer Agent" in agent_names


def test_writer_agent_synthesizes_context():
    writer = WriterAgent()
    state: AgentState = {
        "user_query": "summarize research",
        "research_results": [{"title": "Frameworks", "url": "https://example.com", "summary": "LangGraph is popular."}],
        "data_results": {"summary": "Sales increased 20%"},
        "document_chunks": [{"filename": "report.pdf", "chunk_index": 1, "total_chunks": 1, "text": "Q3 Revenue $1M"}],
    }
    context = writer.prepare_synthesized_prompt(state)
    assert "Frameworks" in context
    assert "Sales increased 20%" in context
    assert "report.pdf" in context
