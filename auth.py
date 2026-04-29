from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

from typing import Annotated
from fastapi import Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Task, User
from database import get_db

# Uses the Argon2 algorithm via pwdlib — resistant to brute-force attacks
password_hash = PasswordHash.recommended()

# Tells FastAPI where clients obtain a token; also powers the Authorize button in /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(password: str) -> str:
    # Returns a salted Argon2 hash; never store the raw password
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Timing-safe comparison to prevent timing attacks
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    # "exp" is a standard JWT claim; the decoder rejects tokens past this time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    # Returns the user ID stored in "sub", or None if the token is invalid/expired
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            # Reject tokens that are missing "exp" or "sub" claims outright
            options={"require": ["exp", "sub"]}
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        # "sub" is stored as a string in the JWT payload, so cast it back to int
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalars().first()
    if not user:
        # Token was valid but the account was deleted after it was issued
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    return user


# Reusable type alias — inject this into any endpoint that requires authentication
CurrentUser = Annotated[User, Depends(get_current_user)]