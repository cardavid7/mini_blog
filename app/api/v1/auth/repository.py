
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import UserORM

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> UserORM | None:
        return self.db.get(UserORM, id)

    def get_by_email(self, email: str) -> UserORM | None:
        query = select(UserORM).where(UserORM.email == email)
        return self.db.execute(query).scalar_one_or_none()
    
    def create_user(self, email:str, password:str, full_name:str | None = None) -> UserORM:
        user = UserORM(email=email, password=password, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_role(self, user: UserORM, role: str) -> UserORM:
        user.role = role
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user