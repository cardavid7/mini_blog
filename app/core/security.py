import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Literal, Optional
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from app.api.v1.auth.repository import UserRepository
from app.core.config import Settings as settings
from app.core.db import get_db
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.models.user import UserORM

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def raise_expire_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Don't have permission to perform this action",
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_invalid_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(payload=to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#     return encoded_jwt

def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + (timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": sub, "exp": expire}, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        #username: Optional[str] = payload.get("username")

        if sub is None: #or username is None:
            raise credentials_exception

        user_id = int(sub)

    except ExpiredSignatureError:
        raise raise_expire_token()
    except InvalidTokenError:
        raise raise_invalid_token()
    except PyJWTError:
        raise raise_invalid_credentials()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error decoding token: {str(e)}")

    user = db.get(UserORM, user_id)
    if not user or not user.is_active:
        raise raise_invalid_credentials
    return user


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hash_password: str) -> bool:
    return password_hash.verify(plain_password, hash_password)

def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {
        "user": 0,
        "editor": 1,
        "admin": 2
    }
    
    def evaluation(user: UserORM = Depends(get_current_user)) -> UserORM:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user

    return evaluation

async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)

    user = repository.get_by_email(form.username)
    if not user or not verify_password(form.password, user.password):
        raise raise_invalid_credentials()

    access_token = create_access_token(sub=str(user.id))

    return {"access_token": access_token, "token_type": "bearer"}

require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")