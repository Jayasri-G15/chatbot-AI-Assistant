import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.crm import Customer
from app.models.crm_user import ApplicationEvent, UserActivity, Subscription, Payment
from app.services import auth_service, conversation_service, document_service
from app.services.crm_user_service import CRMUserService
from app.services.event_service import ApplicationEventService, sanitize_event_metadata

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


def test_mandatory_end_to_end_event_pipeline(setup_db):
    db = setup_db

    # 1. Signup -> USER_SIGNED_UP
    user = User(name="CRM Test User", email="crm_event_user@example.com", password_hash=auth_service.hash_password("Pass123!"))
    db.add(user)
    db.commit()

    ev_signup = ApplicationEventService.record_event(
        db,
        event_type="USER_SIGNED_UP",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        metadata={"email": user.email, "role": "USER"},
        event_id=f"signup-{user.id}",
    )
    db.commit()

    # Customer profile synchronized
    cust = db.query(Customer).filter_by(email=user.email).first()
    assert cust is not None
    assert cust.name == "CRM Test User"

    # 2. Login -> USER_LOGGED_IN
    ev_login = ApplicationEventService.record_event(
        db,
        event_type="USER_LOGGED_IN",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
    )
    db.commit()
    assert user.login_count == 1

    # 3. Create Conversation -> CONVERSATION_CREATED
    conv = conversation_service.create_conversation(db, user_id=user.id)
    assert conv.user_id == user.id

    # 4. Message Sent -> CHAT_MESSAGE_SENT
    msg = conversation_service.add_message(db, conv, "user", "Hello assistant!")
    assert msg.role == "user"

    # 5. Document Upload -> DOCUMENT_UPLOADED & COMPLETED
    doc = document_service.save_document(db, conv, "report.pdf", "pdf", 1024, "Sample extracted PDF text")
    assert doc.filename == "report.pdf"

    # 6. Subscription Update -> SUBSCRIPTION_UPDATED
    sub = CRMUserService.upsert_subscription(db, user.id, plan="PRO", status="ACTIVE")
    assert sub.plan == "PRO"

    # 7. Payment Succeeded -> PAYMENT_SUCCEEDED
    pmt = CRMUserService.record_payment(db, user.id, amount=999.0, currency="INR", status="PAID")
    assert pmt.amount == 999.0

    # Verify Timeline Events
    events = db.query(ApplicationEvent).filter_by(user_id=user.id).all()
    event_types = [e.event_type for e in events]

    assert "USER_SIGNED_UP" in event_types
    assert "USER_LOGGED_IN" in event_types
    assert "CONVERSATION_CREATED" in event_types
    assert "CHAT_MESSAGE_SENT" in event_types
    assert "DOCUMENT_UPLOADED" in event_types
    assert "DOCUMENT_PROCESSING_COMPLETED" in event_types
    assert "SUBSCRIPTION_CREATED" in event_types
    assert "PAYMENT_SUCCEEDED" in event_types


def test_mandatory_idempotency_test(setup_db):
    db = setup_db
    user = User(name="Idempotency User", email="idempotency@example.com", password_hash="hash")
    db.add(user)
    db.commit()

    event_id = "unique-event-id-12345"

    # Record event first time
    ev1 = ApplicationEventService.record_event(
        db,
        event_type="DOCUMENT_UPLOADED",
        user_id=user.id,
        entity_type="document",
        entity_id="doc-123",
        metadata={"filename": "doc.pdf"},
        event_id=event_id,
    )
    db.commit()

    # Record exact same event second time
    ev2 = ApplicationEventService.record_event(
        db,
        event_type="DOCUMENT_UPLOADED",
        user_id=user.id,
        entity_type="document",
        entity_id="doc-123",
        metadata={"filename": "doc.pdf"},
        event_id=event_id,
    )
    db.commit()

    assert ev1.id == ev2.id

    # Verify only 1 ApplicationEvent record exists in DB
    event_count = db.query(ApplicationEvent).filter_by(event_id=event_id).count()
    assert event_count == 1


def test_mandatory_privacy_sanitization_test():
    raw_meta = {
        "password": "secretpassword123",
        "password_hash": "$2b$12$hashvalue",
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "api_key": "nvapi-secretkey",
        "filename": "annual_report.pdf",
        "file_size": 2048,
        "extracted_text": "A" * 1000,
    }

    sanitized = sanitize_event_metadata(raw_meta)

    # Sensitive keys must be completely stripped
    assert "password" not in sanitized
    assert "password_hash" not in sanitized
    assert "jwt" not in sanitized
    assert "api_key" not in sanitized
    assert "extracted_text" not in sanitized

    # Safe keys remain preserved
    assert sanitized["filename"] == "annual_report.pdf"
    assert sanitized["file_size"] == 2048


def test_mandatory_security_user_isolation(setup_db):
    db = setup_db
    user_a = User(name="User A", email="user_a_ev@example.com", role="USER", password_hash="hash")
    user_b = User(name="User B", email="user_b_ev@example.com", role="USER", password_hash="hash")
    db.add_all([user_a, user_b])
    db.commit()

    ApplicationEventService.record_event(db, "USER_SIGNED_UP", user_a.id, "user", user_a.id)
    ApplicationEventService.record_event(db, "USER_SIGNED_UP", user_b.id, "user", user_b.id)
    db.commit()

    events_a = db.query(ApplicationEvent).filter_by(user_id=user_a.id).all()
    events_b = db.query(ApplicationEvent).filter_by(user_id=user_b.id).all()

    assert len(events_a) == 1
    assert len(events_b) == 1
    assert events_a[0].user_id == user_a.id
    assert events_b[0].user_id == user_b.id
