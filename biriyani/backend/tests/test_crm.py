import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.crm import Customer, Contact, Lead, Deal, Activity
from app.services.auth_service import hash_password, create_access_token
from app.services.crm_service import CRMService
from app.tools.crm_tools import (
    tool_search_customer,
    tool_get_customer_details,
    tool_get_customer_deals,
    tool_get_top_customers,
    tool_get_recent_activities,
    tool_search_deals,
    tool_customer_summary,
    tool_get_pipeline_summary,
)
from app.agents.crm import CRMAgent
from app.agents.state import AgentState

# Single shared in-memory SQLite pool for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Clear prior data
    db.query(Activity).delete()
    db.query(Deal).delete()
    db.query(Contact).delete()
    db.query(Customer).delete()
    db.query(Lead).delete()
    db.query(User).delete()
    db.commit()

    # Create test users
    admin = User(
        id="usr-test-admin",
        name="Test Admin",
        email="testadmin@crm.com",
        password_hash=hash_password("password123"),
        role="admin",
    )
    rep = User(
        id="usr-test-rep",
        name="Test Sales Rep",
        email="testrep@crm.com",
        password_hash=hash_password("password123"),
        role="sales_rep",
    )
    db.add_all([admin, rep])
    db.commit()

    # Create test customers
    c1 = Customer(
        id="cust-abc",
        name="ABC Ltd",
        email="contact@abcltd.com",
        company="ABC Ltd",
        owner_id=admin.id,
    )
    c2 = Customer(
        id="cust-xyz",
        name="XYZ Corp",
        email="info@xyzcorp.com",
        company="XYZ Corp",
        owner_id=rep.id,
    )
    db.add_all([c1, c2])
    db.commit()

    # Create contacts
    cnt1 = Contact(id="cnt-1", customer_id=c1.id, name="John Doe", email="john@abcltd.com", role="CEO")
    db.add(cnt1)

    # Create deals
    d1 = Deal(id="deal-1", customer_id=c1.id, title="Enterprise Contract", value=1200000.0, status="open", owner_id=admin.id)
    d2 = Deal(id="deal-2", customer_id=c1.id, title="Cloud Migration", value=850000.0, status="open", owner_id=admin.id)
    d3 = Deal(id="deal-3", customer_id=c2.id, title="Small Package", value=50000.0, status="won", owner_id=rep.id)
    db.add_all([d1, d2, d3])

    # Create activities
    a1 = Activity(id="act-1", customer_id=c1.id, type="call", subject="Intro Call", notes="Great discussion", owner_id=admin.id)
    db.add(a1)

    # Create leads
    l1 = Lead(id="lead-1", name="Potential Lead", company="Lead Co", status="new", source="website", owner_id=admin.id)
    db.add(l1)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_crm_service_search_customers():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="admin").first()

    res = CRMService.search_customers(db, admin, search="ABC")
    assert res["total"] == 1
    assert res["items"][0]["name"] == "ABC Ltd"
    db.close()


def test_crm_service_get_top_customers():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="admin").first()

    top = CRMService.get_top_customers(db, admin, limit=5)
    assert len(top) == 1
    assert top[0]["name"] == "ABC Ltd"
    assert top[0]["total_open_deal_value"] == 2050000.0
    db.close()


def test_crm_tools_independent_execution():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="admin").first()

    # Tool 1: search_customer
    t1 = tool_search_customer(db, admin, query="ABC Ltd")
    assert t1["total"] >= 1

    # Tool 2: get_customer_details
    t2 = tool_get_customer_details(db, admin, "cust-abc")
    assert t2["customer"]["name"] == "ABC Ltd"
    assert len(t2["deals"]) == 2

    # Tool 3: get_customer_deals
    t3 = tool_get_customer_deals(db, admin, "ABC Ltd", status="open")
    assert t3["total"] == 2

    # Tool 4: get_top_customers
    t4 = tool_get_top_customers(db, admin, limit=5)
    assert len(t4["top_customers"]) >= 1

    # Tool 5: get_recent_activities
    t5 = tool_get_recent_activities(db, admin, customer_id="ABC Ltd")
    assert len(t5["activities"]) == 1

    # Tool 6: search_deals
    t6 = tool_search_deals(db, admin, status="open")
    assert t6["total"] == 2

    # Tool 7: customer_summary
    t7 = tool_customer_summary(db, admin, "cust-abc")
    assert t7["name"] == "ABC Ltd"
    assert t7["total_open_deal_value"] == 2050000.0

    # Tool 8: pipeline_summary
    t8 = tool_get_pipeline_summary(db, admin)
    assert t8["total_open_deals"] == 2
    assert t8["total_open_pipeline_value"] == 2050000.0

    db.close()


def test_crm_agent_intent_and_execution():
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(role="admin").first()
    agent = CRMAgent()

    state: AgentState = {
        "user_query": "Show ABC Ltd's open deals.",
        "history": [],
    }
    out = agent.run(state, db, admin)
    assert out["crm_tool"] == "get_customer_deals"
    assert out["crm_results"]["total"] == 2

    state2: AgentState = {
        "user_query": "Which are the top 5 customers by deal value?",
        "history": [],
    }
    out2 = agent.run(state2, db, admin)
    assert out2["crm_tool"] == "get_top_customers"
    assert len(out2["crm_results"]["top_customers"]) >= 1

    db.close()


def test_auth_and_crm_rest_apis():
    client = TestClient(app)

    # 1. Test Login API
    login_res = client.post("/api/v1/auth/login", json={"email": "testadmin@crm.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Get Me API
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "testadmin@crm.com"

    # 3. Test Customers API
    cust_res = client.get("/api/v1/customers?search=ABC", headers=headers)
    assert cust_res.status_code == 200
    assert cust_res.json()["data"]["total"] == 1

    # 4. Test Customer Details API
    detail_res = client.get("/api/v1/customers/cust-abc", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["customer"]["name"] == "ABC Ltd"

    # 5. Test Deals API
    deals_res = client.get("/api/v1/deals?status=open", headers=headers)
    assert deals_res.status_code == 200
    assert deals_res.json()["data"]["total"] == 2

    # 6. Test Activities API
    act_res = client.get("/api/v1/activities", headers=headers)
    assert act_res.status_code == 200
    assert act_res.json()["data"]["count"] >= 1

    # 7. Test Leads API
    leads_res = client.get("/api/v1/leads", headers=headers)
    assert leads_res.status_code == 200
    assert leads_res.json()["data"]["total"] == 1
