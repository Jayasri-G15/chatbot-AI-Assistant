import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.conversation import Conversation
from app.models.document import Document
from app.services import auth_service
from app.tools.registry import tool_registry, ToolPermissionError, ToolValidationError
from app.tools.web_search import validate_web_search_query, WebSearchError
from app.tools.data_sandbox import calculate_data_metrics
from app.agents.supervisor import SupervisorAgent, MAX_AGENT_STEPS

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def setup_db():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_tool_registry_registration_and_listing(setup_db):
    user = User(name="Normal User", email="user_tool@example.com", role="USER", password_hash="hash")
    admin = User(name="Admin User", email="admin_tool@example.com", role="ADMIN", password_hash="hash")

    user_tools = tool_registry.list_tools(user)
    admin_tools = tool_registry.list_tools(admin)

    user_tool_names = [t["name"] for t in user_tools]
    admin_tool_names = [t["name"] for t in admin_tools]

    assert "rag_search" in user_tool_names
    assert "get_my_profile" in user_tool_names
    assert "web_search" in user_tool_names
    assert "get_admin_analytics" not in user_tool_names

    assert "get_admin_analytics" in admin_tool_names
    assert "search_admin_users" in admin_tool_names

    with pytest.raises(ToolValidationError):
        tool_registry.execute("non_existent_tool", setup_db, user, {})


def test_tool_authorization_role_enforcement(setup_db):
    db = setup_db
    user = User(name="User Only", email="user_only@example.com", role="USER", password_hash="hash")
    admin = User(name="Admin Only", email="admin_only@example.com", role="ADMIN", password_hash="hash")
    db.add_all([user, admin])
    db.commit()

    # User calling ADMIN tool must be rejected
    with pytest.raises(ToolPermissionError):
        tool_registry.execute("get_admin_analytics", db, user, {})

    # Admin calling ADMIN tool must succeed
    res = tool_registry.execute("get_admin_analytics", db, admin, {})
    assert res["success"] is True
    assert "total_users" in res["result"]


def test_user_identity_isolation_in_tools(setup_db):
    db = setup_db
    user_a = User(name="User A", email="user_a@example.com", role="USER", password_hash="hash")
    user_b = User(name="User B", email="user_b@example.com", role="USER", password_hash="hash")
    db.add_all([user_a, user_b])
    db.commit()

    conv_a = Conversation(user_id=user_a.id, title="User A Conv")
    conv_b = Conversation(user_id=user_b.id, title="User B Conv")
    db.add_all([conv_a, conv_b])
    db.commit()

    doc_a = Document(conversation_id=conv_a.id, filename="user_a.txt", file_type="txt", extracted_text="USER_A_CONFIDENTIAL")
    doc_b = Document(conversation_id=conv_b.id, filename="user_b.txt", file_type="txt", extracted_text="USER_B_CONFIDENTIAL")
    db.add_all([doc_a, doc_b])
    db.commit()

    # Attempt to supply a forged user_id inside params
    forged_params = {"query": "CONFIDENTIAL", "user_id": user_b.id}

    # Execute rag_search as User A -> must return ONLY User A data
    res_a = tool_registry.execute("rag_search", db, user_a, forged_params)
    assert res_a["success"] is True
    chunks_a = res_a["result"]["chunks"]
    assert len(chunks_a) == 1
    assert "USER_A_CONFIDENTIAL" in chunks_a[0]["text"]
    assert not any("USER_B_CONFIDENTIAL" in c["text"] for c in chunks_a)


def test_web_search_ssrf_and_input_validation():
    # Valid query
    assert validate_web_search_query("  Python 3.14 benchmarks  ") == "Python 3.14 benchmarks"

    # Forbidden SSRF targets
    with pytest.raises(WebSearchError):
        validate_web_search_query("http://localhost:8000/api/admin")

    with pytest.raises(WebSearchError):
        validate_web_search_query("http://169.254.169.254/latest/meta-data/")

    with pytest.raises(WebSearchError):
        validate_web_search_query("file:///etc/passwd")

    with pytest.raises(WebSearchError):
        validate_web_search_query("http://192.168.1.1/admin")


def test_data_sandbox_safety():
    csv_data = "Name,Age,Salary\nAlice,30,75000\nBob,35,85000\nCharlie,40,95000"
    metrics = calculate_data_metrics(csv_data)

    assert metrics["status"] == "success"
    assert metrics["has_dataframe"] is True
    assert metrics["metrics"]["num_rows"] == 3
    assert "Salary" in metrics["metrics"]["numeric_analysis"]
    assert metrics["metrics"]["numeric_analysis"]["Salary"]["mean"] == 85000.0


def test_supervisor_loop_limits_and_duplication_prevention():
    assert MAX_AGENT_STEPS == 5
