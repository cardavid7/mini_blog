from contextlib import contextmanager
from typing import Optional
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.user import UserORM
from app.models.category import CategoryORM
from app.models.tag import TagORM
from app.seeds.data.categories import CATEGORIES
from app.seeds.data.tags import TAGS
from app.seeds.data.users import USERS

def hash_password(plain_password: str) -> str:
    return PasswordHash.recommended().hash(plain_password)
    
@contextmanager
def atomic(db: Session):
    try:
        yield
        db.commit()
    except:
        db.rollback()
        raise

def _user_by_email(db:Session, email:str) -> Optional[UserORM]:
    return db.execute(select(UserORM).where(UserORM.email == email)).scalars().first()

def _category_by_slug(db:Session, slug:str) -> Optional[CategoryORM]:
    return db.execute(select(CategoryORM).where(CategoryORM.slug == slug)).scalars().first()

def _tag_by_name(db:Session, name:str) -> Optional[TagORM]:
    return db.execute(select(TagORM).where(TagORM.name == name)).scalars().first()

def seed_users(db:Session):
    with atomic(db):
        for user in USERS:
            user_db = _user_by_email(db, user["email"])
            if user_db:
                print(f"User {user_db.email} already exists")
                changed = False
                if user_db.full_name != user.get("full_name"):
                    user_db.full_name = user.get("full_name")
                    changed = True
                
                if user.get("password"):
                    user_db.password = hash_password(user.get("password"))
                    changed = True

                if user.get("role"):
                    user_db.role = user.get("role")
                    changed = True

                if changed:
                    db.add(user_db)
                    print(f"Updated user {user_db.email}")
                
            else:
                db.add(
                    UserORM(
                        email = user.get("email"),
                        full_name=user.get("full_name"),
                        password=hash_password(user.get("password")),
                        role = user.get("role")
                    )
                )

def seed_categories(db:Session):
    with atomic(db):
        for category in CATEGORIES:
            category_db = _category_by_slug(db, category["slug"])
            if category_db:
                if category_db.name != category["name"]:
                    category_db.name = category["name"]
                    db.add(category_db)
            else:
                db.add(
                    CategoryORM(
                        name = category["name"],
                        slug = category["slug"]
                    )
            )

def seed_tags(db:Session):
    with atomic(db):
        for tag in TAGS:
            tag_db = _tag_by_name(db, tag["name"])
            if tag_db:
                if tag_db.name != tag["name"]:
                    tag_db.name = tag["name"]
                    db.add(tag_db)
            else:
                db.add(
                    TagORM(
                        name = tag["name"],
                    )
                )

def run_all():
    with SessionLocal() as db:
        seed_users(db)
        seed_categories(db)
        seed_tags(db)

def run_users():
    with SessionLocal() as db:
        seed_users(db)
    
def run_categories():
    with SessionLocal() as db:
        seed_categories(db)

def run_tags():
    with SessionLocal() as db:
        seed_tags(db)

