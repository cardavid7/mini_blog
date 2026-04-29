from app.core.db import get_db
from app.api.v1.posts.schemas import PostPublic, PaginatedPost, PostCreate, PostUpdate, PostSummary
from app.api.v1.posts.repository import PostRepository
from app.api.v1.categories.repository import CategoryRepository
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional, Literal, Union, Annotated
from math import ceil
from app.core.security import oauth2_scheme, require_admin, require_editor
from app.services.file_storage import save_uploaded_image
#import time
#import asyncio
#import threading

router = APIRouter(prefix="/posts", tags=["Posts"])

"""
@router.get("/sync")
def sync_endpoint():
    print("SYNC thread: ", threading.current_thread().name)
    time.sleep(10)
    return {"message": "function sync finished"}

@router.get("/async")
async def async_endpoint():
    print("ASYNC thread: ", threading.current_thread().name)
    await asyncio.sleep(10)
    return {"message": "function async finished"}
"""

@router.get("", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None, description="Search query for posts (deprecated)", deprecated=True
    ),
    query: Optional[str] = Query(
        default=None,
        description="Search query for posts",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚñÑ-]+$",
        title="Search query for posts",
    ),
    per_page: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Number of posts to return per page",
        title="Number of posts to return per page",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Number of page of posts to return",
        title="Number of page of posts to return",
    ),
    order_by: Literal["id", "title"] = Query(
        default="id", description="Order by", title="Order by"
    ),
    direction: Literal["asc", "desc"] = Query(
        default="asc", description="Order direction", title="Order direction"
    ),
    db: Session = Depends(get_db),
    ):

    repository = PostRepository(db)
    query = query or text

    total, items = repository.search(query, page, per_page, order_by, direction)

    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, max(1, total_pages))

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )

@router.get("/by-tags", response_model=List[PostPublic])
def get_posts_by_tags(tags: List[str] = Query(..., min_length=1, description="One or more tags"), db: Session = Depends(get_db)):

    repository = PostRepository(db)
    return repository.get_by_tags(tags)

@router.get("/{id}", response_model=Union[PostPublic, PostSummary], response_description="The post with the given ID")
def get_posts(
    id: int = Path(
        ..., 
        ge=1, 
        title="The ID of the post", 
        description="The ID of the post"
    ),
    include_content: bool = Query(
        default=True, 
        description="Include content in the response"
    ),
    db: Session = Depends(get_db)
    ):

    repository = PostRepository(db)
    post = repository.get_by_id(id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)

@router.post("", response_model=PostPublic, response_description="The created post", status_code=status.HTTP_201_CREATED)
def create_posts(post: Annotated[PostCreate, Depends(PostCreate.as_form)], image: Optional[UploadFile] = File(None), db: Session = Depends(get_db), user=Depends(require_editor)):  # ... is ellipsis, means body is required

    saved_image = None
    try:
        repository_category = CategoryRepository(db)
        category = repository_category.get_by_id(post.category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        repository = PostRepository(db)
        if image:
            saved_image = save_uploaded_image(image)

        image_url = saved_image["file_url"] if saved_image else None

        new_post = repository.create_post(
            title=post.title,
            content=post.content,
            user=user,
            category_id=post.category_id,
            tags=[tag.model_dump() for tag in post.tags] if post.tags else None,
            image_url=image_url
        )
        return new_post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error creating post: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating post: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating post: {str(e)}")

@router.put("/{id}", response_model=PostPublic, response_description="The updated post", response_model_exclude_none=True, status_code=status.HTTP_200_OK)
def update_posts(id: int, data: PostUpdate = Body(...), db: Session = Depends(get_db), _editor=Depends(require_editor)):

    repository = PostRepository(db)
    post = repository.get_by_id(id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    try:
        updates = data.model_dump(exclude_unset=True)
        updated_post = repository.update_post(post, updates)
        return updated_post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error updating post: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating post: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating post: {str(e)}")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):

    repository = PostRepository(db)
    post = repository.get_by_id(id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    try:
        repository.delete_post(post)
        return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting post: {str(e)}")

# @router.get("/secure")
# def secure_endpoint(token: str = Depends(oauth2_scheme)):
#     return {"message": "Access with token", "token": token}