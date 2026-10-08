from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import or_, func, desc
from sqlalchemy.orm import Session

from app.models.crm import Customer, Contact, Lead, Deal, Activity
from app.models.user import User


class CRMService:
    """
    CRM Service implementing server-side RBAC and data isolation:
    - admin: full access to all CRM records
    - manager: full access to team records
    - sales_rep: records owned by user or unassigned
    - user: assigned records
    """

    @staticmethod
    def _apply_owner_isolation(query, model, current_user: User):
        if current_user.role in ("admin", "manager"):
            return query
        # sales_rep or user: filter records where owner_id == user.id or owner_id IS NULL
        return query.filter(or_(model.owner_id == current_user.id, model.owner_id.is_(None)))

    @classmethod
    def search_customers(
        cls,
        db: Session,
        current_user: User,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = db.query(Customer)
        query = cls._apply_owner_isolation(query, Customer, current_user)

        if search and search.strip():
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(s),
                    Customer.email.ilike(s),
                    Customer.company.ilike(s),
                    Customer.phone.ilike(s),
                )
            )

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()

        results = []
        for c in items:
            deals_count = db.query(Deal).filter_by(customer_id=c.id).count()
            total_val = (
                db.query(func.sum(Deal.value))
                .filter(Deal.customer_id == c.id, Deal.status == "open")
                .scalar()
                or 0.0
            )
            results.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone": c.phone,
                    "company": c.company,
                    "owner_id": c.owner_id,
                    "deals_count": deals_count,
                    "open_deal_value": total_val,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
            )

        return {
            "items": results,
            "page": page,
            "limit": limit,
            "total": total,
        }

    @classmethod
    def get_customer_details(
        cls, db: Session, current_user: User, customer_id: str
    ) -> Optional[dict[str, Any]]:
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            # Also try matching customer name if ID search failed
            c = db.query(Customer).filter(Customer.name.ilike(f"%{customer_id}%")).first()
        if not c:
            return None

        contacts = db.query(Contact).filter_by(customer_id=c.id).all()
        deals = db.query(Deal).filter_by(customer_id=c.id).order_by(desc(Deal.created_at)).all()
        activities = (
            db.query(Activity)
            .filter_by(customer_id=c.id)
            .order_by(desc(Activity.activity_date))
            .limit(10)
            .all()
        )

        return {
            "customer": {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "company": c.company,
                "owner_id": c.owner_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            },
            "contacts": [
                {
                    "id": cnt.id,
                    "name": cnt.name,
                    "email": cnt.email,
                    "phone": cnt.phone,
                    "role": cnt.role,
                }
                for cnt in contacts
            ],
            "deals": [
                {
                    "id": d.id,
                    "title": d.title,
                    "value": d.value,
                    "status": d.status,
                    "close_date": d.close_date.isoformat() if d.close_date else None,
                }
                for d in deals
            ],
            "activities": [
                {
                    "id": a.id,
                    "type": a.type,
                    "subject": a.subject,
                    "activity_date": a.activity_date.isoformat() if a.activity_date else None,
                    "notes": a.notes,
                }
                for a in activities
            ],
        }

    @classmethod
    def get_top_customers(cls, db: Session, current_user: User, limit: int = 5) -> list[dict[str, Any]]:
        limit = min(max(1, limit), 50)

        # Aggregate open deal values per customer
        subq = (
            db.query(
                Deal.customer_id.label("customer_id"),
                func.sum(Deal.value).label("total_value"),
                func.count(Deal.id).label("deal_count"),
            )
            .filter(Deal.status == "open")
            .group_by(Deal.customer_id)
            .subquery()
        )

        query = (
            db.query(Customer, subq.c.total_value, subq.c.deal_count)
            .join(subq, Customer.id == subq.c.customer_id)
            .order_by(desc(subq.c.total_value))
        )
        query = cls._apply_owner_isolation(query, Customer, current_user)

        rows = query.limit(limit).all()

        results = []
        for c, total_val, deal_cnt in rows:
            results.append(
                {
                    "customer_id": c.id,
                    "name": c.name,
                    "company": c.company,
                    "email": c.email,
                    "total_open_deal_value": float(total_val or 0.0),
                    "open_deals_count": int(deal_cnt or 0),
                    "owner_id": c.owner_id,
                }
            )
        return results

    @classmethod
    def search_deals(
        cls,
        db: Session,
        current_user: User,
        status: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        close_date_from: Optional[datetime] = None,
        close_date_to: Optional[datetime] = None,
        owner_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = db.query(Deal).join(Customer, Deal.customer_id == Customer.id)
        query = cls._apply_owner_isolation(query, Deal, current_user)

        if status and status.strip():
            query = query.filter(Deal.status.ilike(status.strip()))
        if min_value is not None:
            query = query.filter(Deal.value >= min_value)
        if max_value is not None:
            query = query.filter(Deal.value <= max_value)
        if close_date_from:
            query = query.filter(Deal.close_date >= close_date_from)
        if close_date_to:
            query = query.filter(Deal.close_date <= close_date_to)
        if owner_id:
            query = query.filter(Deal.owner_id == owner_id)
        if customer_id:
            query = query.filter(Deal.customer_id == customer_id)

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(desc(Deal.value)).offset(offset).limit(limit).all()

        results = []
        for d in items:
            c = db.query(Customer).filter_by(id=d.customer_id).first()
            results.append(
                {
                    "id": d.id,
                    "title": d.title,
                    "customer_id": d.customer_id,
                    "customer_name": c.name if c else "Unknown",
                    "company": c.company if c else "Unknown",
                    "value": d.value,
                    "status": d.status,
                    "close_date": d.close_date.isoformat() if d.close_date else None,
                    "owner_id": d.owner_id,
                }
            )

        return {
            "items": results,
            "page": page,
            "limit": limit,
            "total": total,
        }

    @classmethod
    def get_recent_activities(
        cls,
        db: Session,
        current_user: User,
        customer_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        limit = min(max(1, limit), 50)
        query = db.query(Activity).join(Customer, Activity.customer_id == Customer.id)
        query = cls._apply_owner_isolation(query, Activity, current_user)

        if customer_id:
            query = query.filter(Activity.customer_id == customer_id)
        if activity_type:
            query = query.filter(Activity.type.ilike(activity_type))

        items = query.order_by(desc(Activity.activity_date)).limit(limit).all()

        results = []
        for a in items:
            c = db.query(Customer).filter_by(id=a.customer_id).first()
            results.append(
                {
                    "id": a.id,
                    "customer_id": a.customer_id,
                    "customer_name": c.name if c else "Unknown",
                    "type": a.type,
                    "subject": a.subject,
                    "activity_date": a.activity_date.isoformat() if a.activity_date else None,
                    "notes": a.notes,
                    "owner_id": a.owner_id,
                }
            )
        return results

    @classmethod
    def get_leads(
        cls,
        db: Session,
        current_user: User,
        status: Optional[str] = None,
        source: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = db.query(Lead)
        query = cls._apply_owner_isolation(query, Lead, current_user)

        if status:
            query = query.filter(Lead.status.ilike(status))
        if source:
            query = query.filter(Lead.source.ilike(source))

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(desc(Lead.created_at)).offset(offset).limit(limit).all()

        results = [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "status": l.status,
                "source": l.source,
                "owner_id": l.owner_id,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in items
        ]

        return {"items": results, "page": page, "limit": limit, "total": total}

    @classmethod
    def get_pipeline_summary(cls, db: Session, current_user: User) -> dict[str, Any]:
        total_open_deals = db.query(Deal).filter(Deal.status == "open").count()
        total_open_value = (
            db.query(func.sum(Deal.value)).filter(Deal.status == "open").scalar() or 0.0
        )
        total_won_value = (
            db.query(func.sum(Deal.value)).filter(Deal.status == "won").scalar() or 0.0
        )
        total_customers = db.query(Customer).count()
        total_leads = db.query(Lead).count()

        top_customers = cls.get_top_customers(db, current_user, limit=5)

        return {
            "total_customers": total_customers,
            "total_leads": total_leads,
            "total_open_deals": total_open_deals,
            "total_open_pipeline_value": float(total_open_value),
            "total_won_value": float(total_won_value),
            "top_5_customers": top_customers,
        }
