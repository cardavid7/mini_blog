

from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.tags.schemas import TagPublic
from app.models.post import PostORM, post_tags
from app.models.tag import TagORM
from app.services.pagination import paginated_query


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id:int) -> Optional[TagORM]:
        tag = self.db.execute(select(TagORM).where(TagORM.id == id)).scalar_one_or_none()
        return tag

    def list_tags(self, search: Optional[str]=None, page: int=1, per_page: int=10, order_by: str="id", direction: str="asc"):
        
        query = select(TagORM)
        if search:
            query = query.where(func.lower(TagORM.name).ilike(f"%{search.lower()}%"))

        allowed_order = {
            "id": TagORM.id,
            "name": func.lower(TagORM.name)
        } 

        result = paginated_query(
            db=self.db, 
            model=TagORM, 
            base_query=query, 
            page=page, 
            per_page=per_page, 
            order_by=order_by, 
            direction=direction, 
            allowed_order=allowed_order
        ) 
        
        result["items"] = [TagPublic.model_validate(item) for item in result["items"]]

        return result

    def create_tag(self, name: str) -> TagORM:
        
        tag = name.strip().lower()

        tag_obj = self.db.execute(select(TagORM).where(func.lower(TagORM.name) == tag)).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=tag)
            self.db.add(tag_obj)
            self.db.commit()
            self.db.refresh(tag_obj)
        return tag_obj

    def update(self, id: int, name: str) -> Optional[TagORM]:
        
        tag = self.get_by_id(id)

        if not tag:
            return None
        if name:
            tag.name = name.strip().lower()
            self.db.add(tag)
            self.db.commit()    
            self.db.refresh(tag)

        return tag

    def delete(self, id:int) -> bool:
        tag = self.get_by_id(id)
        if not tag:
            return False
        self.db.delete(tag)
        self.db.commit()
        return True

    def most_popular_tags(self) -> dict | None:

        row = (
            self.db.execute(
                select(
                    TagORM.id.label("tag_id"),
                    TagORM.name.label("name"),
                    func.count(PostORM.id).label("uses")
                )
                .join(post_tags, post_tags.columns.tag_id == TagORM.id)
                .join(PostORM, post_tags.columns.post_id == PostORM.id)
                .group_by(TagORM.id, TagORM.name)
                .order_by(func.count(PostORM.id).desc(), func.lower(TagORM.name).asc())
                .limit(1)
            )
            .mappings()
            .first()
        )

        return dict(row) if row else None