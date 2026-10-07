from app.tools.web_search import search_web
from app.tools.data_sandbox import calculate_data_metrics, parse_csv_or_table
from app.tools.rag_retriever import chunk_text, retrieve_document_chunks
from app.models.document import Document


def test_web_search_returns_structured_results():
    results = search_web("AI agent frameworks 2026", max_results=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "url" in results[0]
    assert "summary" in results[0]


def test_data_sandbox_numerical_extraction():
    res = calculate_data_metrics("Revenue Q1 was 100, Q2 was 200, Q3 was 300")
    assert res["status"] == "success"
    assert res["metrics"]["count"] == 3
    assert res["metrics"]["sum"] == 600.0
    assert res["metrics"]["mean"] == 200.0


def test_data_sandbox_csv_parsing():
    csv_data = "Product,Sales\nWidgetA,500\nWidgetB,300"
    df = parse_csv_or_table(csv_data)
    assert df is not None
    assert len(df) == 2
    assert "Sales" in df.columns


def test_rag_retriever_chunking_and_scoring():
    text = "Artificial Intelligence agents automate complex tasks. Machine learning models power modern agent systems."
    chunks = chunk_text(text, chunk_size=40, overlap=10)
    assert len(chunks) >= 2

    doc = Document(id="doc1", conversation_id="conv1", filename="ai.txt", file_type="txt", extracted_text=text)
    retrieved = retrieve_document_chunks("machine learning", [doc], top_k=2)
    assert len(retrieved) > 0
    assert retrieved[0]["filename"] == "ai.txt"
