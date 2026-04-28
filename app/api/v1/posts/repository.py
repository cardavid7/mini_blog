from sqlalchemy.orm import Session, selectinload, joinedload
from typing import Optional, List
from sqlalchemy import select, func
from app.models import PostORM, AuthorORM, TagORM
from math import ceil

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[PostORM]:
        post_db = select(PostORM).where(PostORM.id == id)
        return self.db.execute(post_db).scalar_one_or_none()

    def search(self, query: str, page: int, per_page: int, order_by: str, direction: str) -> tuple[int, list[PostORM]]:
        
        results = select(PostORM)

        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))

        total = self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        if total == 0:
            return 0, []

        current_page = min(page, max(1, ceil(total/per_page)))

        order_col = PostORM.id if order_by == "id" else func.lower(PostORM.title)

        results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())

        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(per_page).offset(start)).scalars().all()

        return total, items

    def get_by_tags(self, tags: List[str]) -> List[PostORM]:

        normalized_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]
        if not normalized_tag_names:
            return []

        post_list = (select(PostORM).options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author),
        ).where(
            PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names))
        ).order_by(PostORM.id.asc()))

        return self.db.execute(post_list).scalars().all()

    def ensure_author(self, name:str, email:str) -> AuthorORM:

        author_obj = self.db.execute(select(AuthorORM).where(AuthorORM.email == email)).scalar_one_or_none()
        if not author_obj:
            author_obj = AuthorORM(name=name, email=email)
            self.db.add(author_obj)
            self.db.flush()
        return author_obj

    def ensure_tags(self, tag: str) -> TagORM:

        tag = tag.strip().lower()

        tag_obj = self.db.execute(select(TagORM).where(func.lower(TagORM.name) == tag)).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=tag)
            self.db.add(tag_obj)
            self.db.flush()
        return tag_obj

    def create_post(self, title: str, content: str, author: Optional[dict], tags: List[dict], image_url: Optional[str]) -> PostORM:
        
        author_obj = None
        if author:
            author_obj = self.ensure_author(author["username"], author["email"])

        tag_objs = []
        if tags:
            for tag in tags:
                names = tag["name"].split(",")
                for name in names:
                    name = name.strip().lower()
                    if not name:
                        continue
                    tag_objs.append(self.ensure_tags(name))

        post = PostORM(title=title, content=content, author=author_obj, tags=tag_objs, image_url=image_url)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update_post(self, post: PostORM, updates: dict) -> PostORM:
        
        for key, value in updates.items():
            setattr(post, key, value)

        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post: PostORM) -> None:
        self.db.delete(post)
        self.db.commit()

    
