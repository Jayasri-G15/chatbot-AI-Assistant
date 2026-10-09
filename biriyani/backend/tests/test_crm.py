import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.crm_user import Subscription, Payment, UserActivity
from app.services.auth_service import hash_password, create_access_token
from app.tools.crm_tools import (
    tool_get_user_statistics,
    tool_search_users,
    tool_get_user_details,
    tool_get_user_activity,
    tool_get_recent_users,
    tool_get_inactive_users,
    tool_get_subscription_statistics,
    tool_get_users_by_subscription,
    tool_get_payment_statistics,
    tool_get_admin_analytics,
)
from app.agents.crm import CRMAgent
from app.agents.state import AgentState

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

    # Clear prior test data
    db.query(UserActivity).delete()
    db.query(Payment).delete()
    db.query(Subscription).delete()
    db.query(User).delete()
    db.commit()

    now = datetime.now(timezone.utc)

    # 1. Admin user
    admin = User(
        id="usr-test-admin-1",
        name="Admin User",
        email="jayasrijs1501@gmail.com",
        phone="9998887770",
        password_hash=hash_password("password123"),
        role="ADMIN",
        account_status="ACTIVE",
        last_login=now,
        login_count=5,
        created_at=now,
    )
    # 2. Normal user A (Rahul)
    user_a = User(
        id="usr-test-rahul",
        name="Rahul Kumar",
        email="rahul@gmail.com",
        phone="9876543210",
        password_hash=hash_password("password123"),
        role="USER",
        account_status="ACTIVE",
        last_login=now,
        login_count=12,
        created_at=now,
    )
    # 3. Normal user B (Priya)
    user_b = User(
        id="usr-test-priya",
        name="Priya Sharma",
        email="priya@gmail.com",
        phone="9123456780",
        password_hash=hash_password("password123"),
        role="USER",
        account_status="ACTIVE",
        last_login=now,
        login_count=3,
        created_at=now,
    )

    db.add_all([admin, user_a, user_b])
    db.commit()

    # Create Subscriptions
    sub_admin = Subscription(id="sub-admin", user_id=admin.id, plan="ENTERPRISE", status="ACTIVE", start_date=now)
    sub_a = Subscription(id="sub-rahul", user_id=user_a.id, plan="PRO", status="ACTIVE", start_date=now)
    sub_b = Subscription(id="sub-priya", user_id=user_b.id, plan="FREE", status="ACTIVE", start_date=now)
    db.add_all([sub_admin, sub_a, sub_b])

    # Create Payments
    pay_a = Payment(id="pay-1", user_id=user_a.id, provider="stripe", provider_payment_id="pi_123", amount=1499.0, currency="INR", status="PAID", payment_date=now)
    db.add(pay_a)

    # Create Activities
    act_a = UserActivity(id="act-1", user_id=user_a.id, activity_type="SIGNUP", timestamp=now)
    act_b = UserActivity(id="act-2", user_id=user_b.id, activity_type="LOGIN", timestamp=now)
    db.add_all([act_a, act_b])

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()




def test_signup_creates_crm_profile_and_subscription():
    client = TestClient(app)
    signup_payload = {
        "name": "New Test User",
        "email": "newtestuser@example.com",
        "password": "password123",
        "phone": "9898989898",
    }
    res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["email"] == "newtestuser@example.com"
    assert data["user"]["role"] == "USER"
    assert "password_hash" not in data["user"]

    db = TestingSessionLocal()
    new_user = db.query(User).filter_by(email="newtestuser@example.com").first()
    assert new_user is not None
    assert new_user.role == "USER"

    sub = db.query(Subscription).filter_by(user_id=new_user.id).first()
    assert sub is not None
    assert sub.plan == "FREE"

    act = db.query(UserActivity).filter_by(user_id=new_user.id, activity_type="SIGNUP").first()
    assert act is not None
    db.close()


def test_login_updates_last_login_and_records_activity():
    client = TestClient(app)
    login_payload = {
        "email": "rahul@gmail.com",
        "password": "password123",
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token is not None

    db = TestingSessionLocal()
    user_a = db.query(User).filter_by(email="rahul@gmail.com").first()
    assert user_a.login_count >= 13

    login_act = db.query(UserActivity).filter_by(user_id=user_a.id, activity_type="LOGIN").first()
    assert login_act is not None
    db.close()


def test_admin_rbac_access_control():
    client = TestClient(app)

    # 1. Login as Admin
    admin_token = create_access_token({"sub": "usr-test-admin-1", "email": "jayasrijs1501@gmail.com", "role": "ADMIN"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin should get 200 OK on admin routes
    res_admin = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_admin.status_code == 200
    json_body = res_admin.json()
    users_list = json_body.get("data", json_body)
    assert users_list["total"] >= 3

    res_analytics = client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert res_analytics.status_code == 200
    analytics_body = res_analytics.json()
    analytics_data = analytics_body.get("data", analytics_body)
    assert analytics_data["total_users"] >= 3

    # 2. Login as Normal User (Rahul)
    user_token = create_access_token({"sub": "usr-test-rahul", "email": "rahul@gmail.com", "role": "USER"})
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Normal user MUST get 403 Forbidden on admin routes
    res_user_forbidden = client.get("/api/v1/admin/users", headers=user_headers)
    assert res_user_forbidden.status_code == 403

    res_user_analytics_forbidden = client.get("/api/v1/admin/analytics", headers=user_headers)
    assert res_user_analytics_forbidden.status_code == 403

    # 3. Unauthenticated request MUST get 401 Unauthorized
    res_unauth = client.get("/api/v1/admin/users")
    assert res_unauth.status_code == 401



def test_no_password_hash_exposure():
    client = TestClient(app)
    admin_token = create_access_token({"sub": "usr-test-admin-1", "email": "jayasrijs1501@gmail.com", "role": "ADMIN"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    res = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res.status_code == 200
    json_body = res.json()
    data = json_body.get("data", json_body)
    items = data.get("items", [])
    for item in items:
        assert "password" not in item
        assert "password_hash" not in item

    detail_res = client.get("/api/v1/admin/users/usr-test-rahul", headers=admin_headers)
    assert detail_res.status_code == 200
    detail_body = detail_res.json()
    detail_data = detail_body.get("data", detail_body)
    profile = detail_data.get("profile", {})
    assert "password_hash" not in profile


def test_crm_ai_tools():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="ADMIN").first()

    # Tool 1: user statistics
    stats = tool_get_user_statistics(db, current_user=admin)
    assert stats["total_users"] >= 3

    # Tool 2: search users
    search_res = tool_search_users(db, current_user=admin, query="Rahul")
    assert search_res["total"] == 1
    assert search_res["items"][0]["name"] == "Rahul Kumar"

    # Tool 3: subscription statistics
    sub_stats = tool_get_subscription_statistics(db, current_user=admin)
    assert sub_stats["plan_breakdown"]["PRO"] == 1

    # Tool 4: get users by subscription
    pro_users = tool_get_users_by_subscription(db, current_user=admin, plan="PRO")
    assert pro_users["count"] == 1
    assert pro_users["users"][0]["email"] == "rahul@gmail.com"

    # Tool 5: payment statistics
    pay_stats = tool_get_payment_statistics(db, current_user=admin)
    assert pay_stats["payments_count"] == 1
    assert pay_stats["total_revenue"] == 1499.0

    # Tool 6: admin analytics
    analytics = tool_get_admin_analytics(db, current_user=admin)
    assert analytics["total_users"] >= 3

    db.close()


def test_crm_agent_intent_execution():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="ADMIN").first()
    agent = CRMAgent()

    state: AgentState = {
        "user_query": "How many users are on the Pro plan?",
        "history": [],
    }
    out = agent.run(state, db, admin)
    assert out["crm_tool"] == "get_users_by_subscription"
    res_data = out["crm_results"]
    assert res_data["count"] == 1

    state2: AgentState = {
        "user_query": "Show me total revenue and payment metrics.",
        "history": [],
    }
    out2 = agent.run(state2, db, admin)
    assert out2["crm_tool"] == "get_payment_statistics"
    res_data2 = out2["crm_results"]
    assert res_data2["total_revenue"] == 1499.0

    db.close()
