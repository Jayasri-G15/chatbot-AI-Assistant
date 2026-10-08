import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
import app.models  # ensure models are loaded
from app.models.user import User
from app.models.crm import Customer, Contact, Lead, Deal, Activity


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def seed_db(db: Session = None):
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Check if already seeded
        if db.query(User).count() > 0 and db.query(Customer).count() >= 20:
            print("Database already seeded.")
            return

        print("Seeding CRM Database...")

        # 1. Users
        users_data = [
            {"id": "usr-admin-01", "name": "Admin User", "email": "admin@crm.com", "role": "admin"},
            {"id": "usr-mgr-01", "name": "Sarah Connor (Manager)", "email": "sarah@crm.com", "role": "manager"},
            {"id": "usr-rep-01", "name": "Rahul Sharma (Sales Rep)", "email": "rahul@crm.com", "role": "sales_rep"},
            {"id": "usr-rep-02", "name": "Priya Patel (Sales Rep)", "email": "priya@crm.com", "role": "sales_rep"},
        ]
        
        users_map = {}
        for u in users_data:
            existing = db.query(User).filter_by(email=u["email"]).first()
            if not existing:
                user_obj = User(
                    id=u["id"],
                    name=u["name"],
                    email=u["email"],
                    password_hash=hash_password("password123"),
                    role=u["role"],
                )
                db.add(user_obj)
                db.commit()
                db.refresh(user_obj)
                users_map[u["id"]] = user_obj
            else:
                users_map[u["id"]] = existing

        rep1_id = users_map["usr-rep-01"].id
        rep2_id = users_map["usr-rep-02"].id
        mgr_id = users_map["usr-mgr-01"].id

        # 2. Customers (22 customers)
        company_names = [
            ("ABC Ltd", "contact@abcltd.com", "+91 98765 43210", rep1_id),
            ("Apex Global Solutions", "info@apexglobal.com", "+91 98765 43211", rep1_id),
            ("TechCorp Inc", "hello@techcorp.io", "+91 98765 43212", rep2_id),
            ("Biriyani Palace Corp", "orders@biriyanipalace.com", "+91 98765 43213", rep1_id),
            ("Nexus Systems", "contact@nexus.co", "+91 98765 43214", rep2_id),
            ("Vortex Logistics", "support@vortex.in", "+91 98765 43215", rep1_id),
            ("Zenith Analytics", "queries@zenith.ai", "+91 98765 43216", rep2_id),
            ("Starlight Media", "biz@starlight.com", "+91 98765 43217", mgr_id),
            ("Omni Healthcare", "info@omnihealth.org", "+91 98765 43218", rep1_id),
            ("Horizon Retailers", "sales@horizon.com", "+91 98765 43219", rep2_id),
            ("Quantum Financial", "wealth@quantum.com", "+91 98765 43220", rep1_id),
            ("Solaris Energy", "green@solaris.io", "+91 98765 43221", rep2_id),
            ("CloudScale Corp", "contact@cloudscale.net", "+91 98765 43222", rep1_id),
            ("Urban Foods Ltd", "supply@urbanfoods.com", "+91 98765 43223", rep2_id),
            ("Titan Mobility", "fleet@titan.co", "+91 98765 43224", rep1_id),
            ("CyberShield Security", "info@cybershield.sec", "+91 98765 43225", rep2_id),
            ("BlueWave Digital", "hello@bluewave.com", "+91 98765 43226", rep1_id),
            ("Summit Ventures", "partners@summit.vc", "+91 98765 43227", mgr_id),
            ("Velocity Commerce", "sales@velocity.shop", "+91 98765 43228", rep2_id),
            ("Pinnacle Construction", "contact@pinnacle.build", "+91 98765 43229", rep1_id),
            ("SpiceRoute Exports", "info@spiceroute.com", "+91 98765 43230", rep2_id),
            ("Zest Hospitality", "events@zest.com", "+91 98765 43231", rep1_id),
        ]

        created_customers = []
        for name, email, phone, owner_id in company_names:
            existing = db.query(Customer).filter_by(name=name).first()
            if not existing:
                c = Customer(
                    name=name,
                    email=email,
                    phone=phone,
                    company=name,
                    owner_id=owner_id,
                )
                db.add(c)
                db.commit()
                db.refresh(c)
                created_customers.append(c)
            else:
                created_customers.append(existing)

        abc_ltd = next((c for c in created_customers if "ABC Ltd" in c.name), created_customers[0])

        # 3. Contacts (32 contacts)
        contact_roles = ["CEO", "CTO", "Procurement Director", "VP Sales", "Operations Head", "IT Lead"]
        contacts_count = 0
        for idx, cust in enumerate(created_customers):
            # Create 1 or 2 contacts per customer
            num_contacts = 2 if idx < 10 else 1
            for j in range(num_contacts):
                c_name = f"{cust.name.split()[0]} Contact {j+1}"
                if cust.name == "ABC Ltd":
                    c_name = "John Doe" if j == 0 else "Jane Smith"
                
                c_email = f"{c_name.lower().replace(' ', '.')}@{cust.email.split('@')[-1]}"
                role = contact_roles[(idx + j) % len(contact_roles)]
                
                existing = db.query(Contact).filter_by(email=c_email).first()
                if not existing:
                    cnt = Contact(
                        customer_id=cust.id,
                        name=c_name,
                        email=c_email,
                        phone=cust.phone,
                        role=role,
                    )
                    db.add(cnt)
                    contacts_count += 1
        db.commit()

        # 4. Leads (22 leads)
        lead_sources = ["website", "referral", "event", "outreach", "cold_call"]
        lead_statuses = ["new", "contacted", "qualified", "unqualified", "converted"]
        leads_data = [
            ("Grand Biriyani Chain", "Grand Foods", "qualified", "event", rep1_id),
            ("Royal Flavors", "Royal Foods", "new", "website", rep2_id),
            ("HydraTech Systems", "HydraTech", "contacted", "outreach", rep1_id),
            ("Aura Software", "Aura Inc", "qualified", "referral", rep2_id),
            ("Kavya Enterprises", "Kavya Ent", "converted", "website", rep1_id),
            ("Frontier Logistics", "Frontier", "new", "cold_call", rep2_id),
            ("Nova Infra", "Nova Group", "contacted", "event", mgr_id),
            ("Matrix Cloud", "Matrix Labs", "qualified", "website", rep1_id),
            ("Bistro 360", "Bistro Hospitality", "unqualified", "cold_call", rep2_id),
            ("Silverline Retail", "Silverline", "new", "outreach", rep1_id),
            ("Dynamic AI", "Dynamic Labs", "qualified", "referral", rep2_id),
            ("Metro Caterers", "Metro Group", "contacted", "event", rep1_id),
            ("Pacific Traders", "Pacific Co", "new", "website", rep2_id),
            ("Atlas Pharma", "Atlas Health", "converted", "referral", rep1_id),
            ("BrightFuture Edu", "BrightFuture", "qualified", "outreach", rep2_id),
            ("Genesis Energy", "Genesis Corp", "contacted", "event", rep1_id),
            ("Vanguard Security", "Vanguard", "new", "cold_call", rep2_id),
            ("Prime Warehousing", "Prime Logistics", "qualified", "website", rep1_id),
            ("Crestline Real Estate", "Crestline", "contacted", "referral", rep2_id),
            ("Gourmet Express", "Gourmet Foods", "converted", "event", rep1_id),
            ("Hyperion Networks", "Hyperion Tech", "new", "outreach", rep2_id),
            ("Zenith Cloud Services", "Zenith Soft", "qualified", "website", rep1_id),
        ]
        for name, comp, stat, src, owner in leads_data:
            existing = db.query(Lead).filter_by(name=name).first()
            if not existing:
                ld = Lead(name=name, company=comp, status=stat, source=src, owner_id=owner)
                db.add(ld)
        db.commit()

        # 5. Deals (32 deals)
        # ABC Ltd open deals specifically requested for test prompt "Show ABC Ltd's open deals"
        now = datetime.now(timezone.utc)
        deals_data = [
            # ABC Ltd deals
            (abc_ltd.id, "Enterprise Cloud Contract", 1200000.0, "open", now + timedelta(days=15), abc_ltd.owner_id),
            (abc_ltd.id, "Infrastructure Migration", 850000.0, "open", now + timedelta(days=25), abc_ltd.owner_id),
            (abc_ltd.id, "Support & Maintenance Renewal", 320000.0, "won", now - timedelta(days=10), abc_ltd.owner_id),
        ]

        # Other deals across customers
        deal_titles = [
            "AI Assistant Deployment",
            "Annual Software Subscription",
            "Custom ERP Integration",
            "Security Audit & Compliance",
            "Data Analytics Platform",
            "Cloud Infrastructure Setup",
            "Managed Services Agreement",
            "Mobile App Development",
            "Staff Augmentation Contract",
            "Hardware Refresh Program",
        ]
        
        statuses = ["open", "open", "won", "won", "lost"]
        
        for idx, cust in enumerate(created_customers):
            if cust.id == abc_ltd.id:
                continue
            # 1 to 2 deals per customer
            n_deals = 2 if idx % 2 == 0 else 1
            for k in range(n_deals):
                title = f"{cust.name} - {deal_titles[(idx + k) % len(deal_titles)]}"
                val = float(150000 + ((idx * 37 + k * 91) % 15) * 100000)
                stat = statuses[(idx + k) % len(statuses)]
                days_offset = ((idx * 7) % 60) - 15  # Some closing this month, some past, some future
                close_dt = now + timedelta(days=days_offset)
                
                deals_data.append((cust.id, title, val, stat, close_dt, cust.owner_id))

        for cid, title, val, stat, close_dt, owner in deals_data:
            existing = db.query(Deal).filter_by(customer_id=cid, title=title).first()
            if not existing:
                dl = Deal(
                    customer_id=cid,
                    title=title,
                    value=val,
                    status=stat,
                    close_date=close_dt,
                    owner_id=owner,
                )
                db.add(dl)
        db.commit()

        # 6. Activities (55 activities)
        activity_types = ["call", "meeting", "email", "note"]
        act_subjects = [
            "Initial Discovery Call",
            "Product Demonstration Meeting",
            "Proposal Review Email",
            "Contract Negotiation Call",
            "Quarterly Business Review",
            "Technical Architecture Discussion",
            "Pricing & Discount Note",
            "Follow-up on Requirement Specifications",
        ]

        activities_count = 0
        for idx, cust in enumerate(created_customers):
            # 2 to 3 activities per customer
            num_acts = 3 if idx < 10 else 2
            for a in range(num_acts):
                atype = activity_types[(idx + a) % len(activity_types)]
                subj = act_subjects[(idx + a) % len(act_subjects)]
                date_offset = -1 * ((idx * 3 + a * 5) % 45)  # Recent past days
                adate = now + timedelta(days=date_offset)
                notes = f"Discussed {subj.lower()} with {cust.name}. Key action items captured."
                
                act = Activity(
                    customer_id=cust.id,
                    type=atype,
                    subject=subj,
                    activity_date=adate,
                    notes=notes,
                    owner_id=cust.owner_id,
                )
                db.add(act)
                activities_count += 1
        db.commit()

        print(f"CRM Database seeded successfully! Created {len(created_customers)} customers, {contacts_count} contacts, {len(leads_data)} leads, {len(deals_data)} deals, {activities_count} activities.")

    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_db()
