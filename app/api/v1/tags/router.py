
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user, require_editor, require_admin, require_user


router = APIRouter(prefix="/tags", tags=["Tags"])

@router.get("", response_model=dict)
def list_tags(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    order_by: str = Query(default="id", pattern="^(id|name)$"),
    direction: str = Query(default="asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):
    repository = TagRepository(db)
    return repository.list_tags(page=page, per_page=per_page, order_by=order_by, direction=direction, search=search)

@router.post("", response_model=TagPublic, response_description="The created tag", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), _editor=Depends(require_editor)):
    
    try:
        repository = TagRepository(db)
        new_tag = repository.create_tag(tag.name)
        return new_tag
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating tag: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating tag: {str(e)}")

@router.put("/{id}", response_model=TagPublic, response_description="The updated tag", response_model_exclude_none=True, status_code=status.HTTP_200_OK)
def update_tag(id: int, tag: TagUpdate, db: Session = Depends(get_db), _editor=Depends(require_editor)):
    try:
        repository = TagRepository(db)
        updated_tag = repository.update(id, tag.name)
        if updated_tag is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        return TagPublic.model_validate(updated_tag, from_attributes=True)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating tag: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating tag: {str(e)}")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    try:
        repository = TagRepository(db)
        delete = repository.delete(id)
        if not delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        return
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting tag: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting tag: {str(e)}")

@router.get("/popular/top")
def get_most_popular_tag(db: Session= Depends(get_db), _user=Depends(require_user)):
    repository = TagRepository(db)
    result = repository.most_popular_tags()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Most popular tag not found")
    
    return result