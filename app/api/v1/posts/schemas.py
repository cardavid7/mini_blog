from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Literal, Annotated
from fastapi import Form
from app.api.v1.auth.schemas import UserPublic
from app.api.v1.categories.schemas import CategoryPublic

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Tag name", example="Tag1")

    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    user: Optional[UserPublic] = None
    image_url: Optional[str] = None
    category: Optional[CategoryPublic] = None

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the post", example="First Post")
    content: Optional[str] = Field(min_length=10, default="Default content", description="Content of the post", example="This is the first post.")
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("Title cannot contain the word spam")
        return value

    @classmethod
    def as_form(
        cls, 
        title: Annotated[str, Form(min_length=3)],
        content: Annotated[str, Form(min_length=10)],
        category_id: Annotated[Optional[int], Form(gt=0)] = None,
        tags: Annotated[Optional[List[str]], Form()] = None
    ):
        tags_obj = [Tag(name=t) for t in (tags or [])]
        return cls(title=title, content=content, tags=tags_obj, category_id=category_id)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)

class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]
