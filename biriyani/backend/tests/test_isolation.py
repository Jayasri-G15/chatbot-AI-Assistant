import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.document import Document
from app.services.auth_service import hash_password, create_access_token

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()



    now = datetime.now(timezone.utc)

    # User A
    user_a = User(
        id="usr-isolation-a",
        name="User Alpha",
        email="alpha@example.com",
        password_hash=hash_password("password123"),
        role="USER",
        account_status="ACTIVE",
        created_at=now,
    )
    # User B
    user_b = User(
        id="usr-isolation-b",
        name="User Beta",
        email="beta@example.com",
        password_hash=hash_password("password123"),
        role="USER",
        account_status="ACTIVE",
        created_at=now,
    )

    db.add_all([user_a, user_b])
    db.commit()

    # User A Conversation & Data
    conv_a = Conversation(id="conv-user-a", user_id=user_a.id, title="Alpha Chat")
    db.add(conv_a)
    db.commit()
    msg_a = Message(id="msg-a-1", conversation_id=conv_a.id, role="user", content="USER_A_PRIVATE_MESSAGE_123")
    doc_a = Document(id="doc-a-1", conversation_id=conv_a.id, filename="alpha.txt", file_type="txt", file_size=30, extracted_text="USER_A_SECRET_TEST_STRING_12345")
    db.add_all([msg_a, doc_a])

    # User B Conversation & Data
    conv_b = Conversation(id="conv-user-b", user_id=user_b.id, title="Beta Chat")
    db.add(conv_b)
    db.commit()
    msg_b = Message(id="msg-b-1", conversation_id=conv_b.id, role="user", content="USER_B_PRIVATE_MESSAGE_456")
    doc_b = Document(id="doc-b-1", conversation_id=conv_b.id, filename="beta.txt", file_type="txt", file_size=30, extracted_text="USER_B_SECRET_TEST_STRING_67890")
    db.add_all([msg_b, doc_b])

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()




def test_unauthenticated_access_rejected():
    client = TestClient(app)
    # GET /conversations without token -> 401
    res = client.get("/api/v1/conversations")
    assert res.status_code == 401

    # GET /conversations/{id}/messages without token -> 401
    res_msg = client.get("/api/v1/conversations/conv-user-a/messages")
    assert res_msg.status_code == 401

    # GET /conversations/{id}/documents without token -> 401
    res_doc = client.get("/api/v1/conversations/conv-user-a/documents")
    assert res_doc.status_code == 401


def test_user_a_cannot_access_user_b_conversations():
    client = TestClient(app)
    token_a = create_access_token({"sub": "usr-isolation-a", "email": "alpha@example.com", "role": "USER"})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A lists conversations -> only sees conv-user-a
    res = client.get("/api/v1/conversations", headers=headers_a)
    assert res.status_code == 200
    convs = res.json()
    conv_ids = [c["id"] for c in convs]
    assert "conv-user-a" in conv_ids
    assert "conv-user-b" not in conv_ids

    # User A tries to GET User B's conversation directly -> 404
    res_b = client.get("/api/v1/conversations/conv-user-b", headers=headers_a)
    assert res_b.status_code == 404


def test_user_a_cannot_access_user_b_messages():
    client = TestClient(app)
    token_a = create_access_token({"sub": "usr-isolation-a", "email": "alpha@example.com", "role": "USER"})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A tries to list messages for User B's conversation -> 404
    res = client.get("/api/v1/conversations/conv-user-b/messages", headers=headers_a)
    assert res.status_code == 404

    # User A tries to send message to User B's conversation -> 404
    res_send = client.post("/api/v1/conversations/conv-user-b/messages", json={"content": "Malicious message"}, headers=headers_a)
    assert res_send.status_code == 404


def test_user_a_cannot_access_user_b_documents():
    client = TestClient(app)
    token_a = create_access_token({"sub": "usr-isolation-a", "email": "alpha@example.com", "role": "USER"})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A tries to list documents for User B's conversation -> 404
    res = client.get("/api/v1/conversations/conv-user-b/documents", headers=headers_a)
    assert res.status_code == 404

    # User A tries to delete User B's document -> 404
    res_del = client.delete("/api/v1/conversations/conv-user-b/documents/doc-b-1", headers=headers_a)
    assert res_del.status_code == 404


def test_rag_and_chat_history_leakage_prevention():
    client = TestClient(app)
    token_a = create_access_token({"sub": "usr-isolation-a", "email": "alpha@example.com", "role": "USER"})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A messages only contain User A's private messages
    res_a = client.get("/api/v1/conversations/conv-user-a/messages", headers=headers_a)
    assert res_a.status_code == 200
    msgs_a = [m["content"] for m in res_a.json()]
    assert "USER_A_PRIVATE_MESSAGE_123" in msgs_a
    assert "USER_B_PRIVATE_MESSAGE_456" not in msgs_a

    # User A documents only contain User A's documents
    res_docs_a = client.get("/api/v1/conversations/conv-user-a/documents", headers=headers_a)
    assert res_docs_a.status_code == 200
    docs_a = res_docs_a.json()
    assert len(docs_a) == 1
    assert docs_a[0]["filename"] == "alpha.txt"
