from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import or_, func, desc
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.crm_user import Subscription, Payment, UserActivity
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.document import Document


class CRMUserService:
    """
    CRM Service operating over REAL application registered users:
    - User profiles & account metadata
    - Subscriptions & Payments
    - User Activity Event Tracking
    - Usage & Conversation statistics
    """

    @classmethod
    def list_admin_users(
        cls,
        db: Session,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        plan: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = db.query(User)

        if search and search.strip():
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.name.ilike(s),
                    User.email.ilike(s),
                    User.phone.ilike(s),
                )
            )

        if role:
            query = query.filter(User.role.ilike(role))
        if status:
            query = query.filter(User.account_status.ilike(status))

        if plan:
            query = query.join(Subscription, User.id == Subscription.user_id).filter(
                Subscription.plan.ilike(plan)
            )

        total = query.count()
        offset = (page - 1) * limit
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

        results = []
        for u in users:
            sub = db.query(Subscription).filter_by(user_id=u.id).first()
            conv_cnt = db.query(Conversation).filter_by(user_id=u.id).count()
            msg_cnt = (
                db.query(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .filter(Conversation.user_id == u.id)
                .scalar()
                or 0
            )
            doc_cnt = (
                db.query(func.count(Document.id))
                .join(Conversation, Document.conversation_id == Conversation.id)
                .filter(Conversation.user_id == u.id)
                .scalar()
                or 0
            )

            results.append(
                {
                    "user_id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "phone": u.phone,
                    "role": u.role,
                    "account_status": u.account_status,
                    "subscription_plan": sub.plan if sub else "FREE",
                    "subscription_status": sub.status if sub else "ACTIVE",
                    "last_login": u.last_login.isoformat() if u.last_login else None,
                    "login_count": u.login_count or 0,
                    "conversation_count": conv_cnt,
                    "message_count": msg_cnt,
                    "document_count": doc_cnt,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
            )

        return {
            "items": results,
            "page": page,
            "limit": limit,
            "total": total,
        }

    @classmethod
    def get_user_crm_profile(cls, db: Session, user_id: str) -> Optional[dict[str, Any]]:
        u = db.query(User).filter(User.id == user_id).first()
        if not u:
            # Fallback match by email or name if ID string passed was name/email
            u = db.query(User).filter(or_(User.email.ilike(user_id), User.name.ilike(f"%{user_id}%"))).first()
        if not u:
            return None

        sub = db.query(Subscription).filter_by(user_id=u.id).first()
        payments = db.query(Payment).filter_by(user_id=u.id).order_by(desc(Payment.payment_date)).all()
        activities = (
            db.query(UserActivity)
            .filter_by(user_id=u.id)
            .order_by(desc(UserActivity.timestamp))
            .limit(20)
            .all()
        )
        conversations = db.query(Conversation).filter_by(user_id=u.id).order_by(desc(Conversation.created_at)).all()

        conv_cnt = len(conversations)
        msg_cnt = (
            db.query(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Conversation.user_id == u.id)
            .scalar()
            or 0
        )
        doc_cnt = (
            db.query(func.count(Document.id))
            .join(Conversation, Document.conversation_id == Conversation.id)
            .filter(Conversation.user_id == u.id)
            .scalar()
            or 0
        )

        total_paid = sum(p.amount for p in payments if p.status == "PAID")

        return {
            "user": {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "role": u.role,
                "account_status": u.account_status,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "last_active_at": u.last_active_at.isoformat() if u.last_active_at else None,
                "login_count": u.login_count or 0,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            },
            "subscription": {
                "plan": sub.plan if sub else "FREE",
                "status": sub.status if sub else "ACTIVE",
                "billing_cycle": sub.billing_cycle if sub else "monthly",
                "start_date": sub.start_date.isoformat() if sub and sub.start_date else None,
            } if sub else None,
            "payments": [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status,
                    "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                }
                for p in payments
            ],
            "total_paid_amount": total_paid,
            "usage": {
                "conversation_count": conv_cnt,
                "message_count": msg_cnt,
                "document_count": doc_cnt,
            },
            "recent_activities": [
                {
                    "id": a.id,
                    "activity_type": a.activity_type,
                    "metadata": a.metadata_json,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                }
                for a in activities
            ],
            "conversations": [
                {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in conversations[:10]
            ],
        }

    @classmethod
    def get_admin_analytics(cls, db: Session) -> dict[str, Any]:
        total_users = db.query(User).count()
        admin_count = db.query(User).filter(User.role == "ADMIN").count()
        user_count = db.query(User).filter(User.role == "USER").count()

        free_users = (
            db.query(Subscription).filter(Subscription.plan == "FREE").count()
        )
        paid_users = (
            db.query(Subscription).filter(Subscription.plan.in_(["PRO", "PREMIUM", "ENTERPRISE"])).count()
        )

        total_conversations = db.query(Conversation).count()
        total_messages = db.query(Message).count()
        total_documents = db.query(Document).count()
        total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "PAID").scalar() or 0.0

        top_active_users = cls.list_admin_users(db, page=1, limit=5)["items"]

        return {
            "total_users": total_users,
            "admin_count": admin_count,
            "user_count": user_count,
            "free_users": free_users,
            "paid_users": paid_users,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_documents": total_documents,
            "total_revenue": float(total_revenue),
            "top_users": top_active_users,
        }

    @classmethod
    def list_activities(cls, db: Session, limit: int = 30) -> list[dict[str, Any]]:
        items = db.query(UserActivity).order_by(desc(UserActivity.timestamp)).limit(limit).all()
        results = []
        for a in items:
            u = db.query(User).filter_by(id=a.user_id).first()
            results.append(
                {
                    "id": a.id,
                    "user_id": a.user_id,
                    "user_name": u.name if u else "Unknown",
                    "user_email": u.email if u else "Unknown",
                    "activity_type": a.activity_type,
                    "metadata": a.metadata_json,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                }
            )
        return results

    @classmethod
    def list_subscriptions(cls, db: Session) -> list[dict[str, Any]]:
        subs = db.query(Subscription).order_by(desc(Subscription.created_at)).all()
        results = []
        for s in subs:
            u = db.query(User).filter_by(id=s.user_id).first()
            results.append(
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "user_name": u.name if u else "Unknown",
                    "user_email": u.email if u else "Unknown",
                    "plan": s.plan,
                    "status": s.status,
                    "billing_cycle": s.billing_cycle,
                    "start_date": s.start_date.isoformat() if s.start_date else None,
                }
            )
        return results

    @classmethod
    def list_payments(cls, db: Session) -> list[dict[str, Any]]:
        pmts = db.query(Payment).order_by(desc(Payment.payment_date)).all()
        results = []
        for p in pmts:
            u = db.query(User).filter_by(id=p.user_id).first()
            results.append(
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "user_name": u.name if u else "Unknown",
                    "user_email": u.email if u else "Unknown",
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status,
                    "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                }
            )
        return results

    @classmethod
    def upsert_subscription(
        cls, db: Session, user_id: str, plan: str = "FREE", status: str = "ACTIVE"
    ) -> Subscription:
        now = datetime.now(timezone.utc)
        sub = db.query(Subscription).filter_by(user_id=user_id).first()
        event_type = "SUBSCRIPTION_UPDATED" if sub else "SUBSCRIPTION_CREATED"

        if not sub:
            sub = Subscription(user_id=user_id, plan=plan, status=status, start_date=now)
            db.add(sub)
        else:
            sub.plan = plan
            sub.status = status
            sub.updated_at = now

        db.commit()

        from app.services.event_service import ApplicationEventService
        ApplicationEventService.record_event(
            db,
            event_type=event_type,
            user_id=user_id,
            entity_type="subscription",
            entity_id=sub.id,
            metadata={"plan": plan, "status": status},
            event_id=f"sub-{sub.id}-{plan}-{status}",
        )
        db.commit()
        return sub

    @classmethod
    def record_payment(
        cls,
        db: Session,
        user_id: str,
        amount: float,
        currency: str = "INR",
        status: str = "PAID",
        provider: str = "stripe",
        provider_payment_id: Optional[str] = None,
    ) -> Payment:
        now = datetime.now(timezone.utc)
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status=status,
            provider=provider,
            provider_payment_id=provider_payment_id,
            payment_date=now,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        event_type = "PAYMENT_SUCCEEDED" if status == "PAID" else "PAYMENT_FAILED"
        from app.services.event_service import ApplicationEventService
        ApplicationEventService.record_event(
            db,
            event_type=event_type,
            user_id=user_id,
            entity_type="payment",
            entity_id=payment.id,
            metadata={"amount": amount, "currency": currency, "status": status, "provider": provider},
            event_id=f"pmt-{payment.id}",
        )
        db.commit()
        return payment

