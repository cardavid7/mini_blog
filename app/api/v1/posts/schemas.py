from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Literal

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Tag name", example="Tag1")

    model_config = ConfigDict(from_attributes=True)

class Author(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Author name", example="Author1")
    email: EmailStr = Field(..., min_length=2, max_length=30, description="Author email", example="correo@gmail.com")

    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the post", example="First Post")
    content: Optional[str] = Field(min_length=10, default="Default content", description="Content of the post", example="This is the first post.")
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    # author: Optional[Author] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("Title cannot contain the word spam")
        return value

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int

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
