import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self, skip: int = 0, limit: int = 50, search: Optional[str] = None) -> list[User]:
        query = self.db.query(User)
        if search:
            like = f"%{search}%"
            query = query.filter(
                (User.full_name.ilike(like)) | (User.email.ilike(like))
            )
        return query.offset(skip).limit(limit).all()

    def count_all(self, search: Optional[str] = None) -> int:
        query = self.db.query(User)
        if search:
            like = f"%{search}%"
            query = query.filter(
                (User.full_name.ilike(like)) | (User.email.ilike(like))
            )
        return query.count()
