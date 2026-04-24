from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import Token, UserPublic
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, get_current_user
from datetime import timedelta

FAKE_USERS = {
    "carlos@example.com": {"email": "carlos@example.com", "username": "carlos", "password": "secret123"},
    "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
}

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = FAKE_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": user["email"], "username": user["username"]},
        expires_delta=timedelta(minutes=30)
    )

    return Token(access_token=token, token_type="bearer")

@router.get("/me", response_model=UserPublic)
async def read_me(current_user : UserPublic = Depends(get_current_user)):
    return current_user