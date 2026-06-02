"""User repository (DB-backed)."""
from sqlalchemy.orm import Session
from app.models.db_models import UserProfile
from datetime import datetime


class UserRepository:
    def get(self, db: Session, user_id: str):
        return db.get(UserProfile, user_id)

    def upsert(self, db: Session, user_id: str, **data):
        user = db.get(UserProfile, user_id)
        if not user:
            user = UserProfile(user_id=user_id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)

        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()