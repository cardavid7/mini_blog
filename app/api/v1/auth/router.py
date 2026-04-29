from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.api.v1.auth.schemas import RoleUpdate, TokenResponse, UserCreate, UserLogin, UserPublic
from app.core.security import auth2_token, create_access_token, get_current_user, hash_password, verify_password, require_admin

from app.models.user import Role, UserORM

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    
    repository = UserRepository(db)
    if repository.get_by_email(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    user = repository.create_user(
        email=user.email, 
        password=hash_password(user.password), 
        full_name=user.full_name
    )

    return UserPublic.model_validate(user)

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):

    repository = UserRepository(db)
    user = repository.get_by_email(login_data.email)
    
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token, token_type="bearer", user=UserPublic.model_validate(user))

@router.get("/me", response_model=UserPublic)
async def read_me(current_user : UserORM = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)


@router.put("/role/{id}", response_model=UserPublic)
def set_role(
    id: int = Path(...,ge=1),
    role: RoleUpdate | None = None,
    db: Session = Depends(get_db),
    _admin: UserORM = Depends(require_admin)
    ):

    repository = UserRepository(db)
    user = repository.get_by_id(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = repository.set_role(user, role.role)
    return UserPublic.model_validate(user)

@router.post("/token")
async def token_endpoint(response = Depends(auth2_token)):
    return response