import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
import app.models  # ensure models are loaded
from app.models.user import User
from app.models.crm_user import Subscription, Payment, UserActivity
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.auth_service import hash_password

ADMIN_EMAIL = "jayasrijs1501@gmail.com"



def seed_db(db: Session = None):
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        now = datetime.now(timezone.utc)

        # 1. Clean up demo users if present
        demo_emails = ["rahul@gmail.com", "priya@gmail.com", "arun@gmail.com", "sneha@gmail.com", "vikram@gmail.com"]
        demo_users = db.query(User).filter(User.email.in_(demo_emails)).all()
        for du in demo_users:
            db.query(UserActivity).filter_by(user_id=du.id).delete()
            db.query(Payment).filter_by(user_id=du.id).delete()
            db.query(Subscription).filter_by(user_id=du.id).delete()
            convs = db.query(Conversation).filter_by(user_id=du.id).all()
            for c in convs:
                db.query(Message).filter_by(conversation_id=c.id).delete()
                db.delete(c)
            db.delete(du)
        db.commit()

        # 2. Ensure Initial Admin User exists: jayasrijs1501@gmail.com
        admin_user = db.query(User).filter_by(email=ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                id="usr-admin-initial",
                name="Jayasri",
                email=ADMIN_EMAIL,
                phone="+91 98765 00000",
                password_hash=hash_password("password123"),
                role="ADMIN",
                account_status="ACTIVE",
                last_login=now,
                last_active_at=now,
                login_count=1,
                created_at=now,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Add Admin Subscription & Activity
            db.add(Subscription(user_id=admin_user.id, plan="ENTERPRISE", status="ACTIVE", start_date=now))
            db.add(UserActivity(user_id=admin_user.id, activity_type="SIGNUP", metadata_json=json.dumps({"ip": "127.0.0.1", "role": "ADMIN"}), timestamp=now))
            db.commit()
        else:
            if admin_user.role != "ADMIN":
                admin_user.role = "ADMIN"
                db.commit()

        print("Database cleaned: 0 demo users. Admin account initialized.")

    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_db()
