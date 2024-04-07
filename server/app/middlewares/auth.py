"""
authentication middlewares
"""
from datetime import datetime, UTC
from typing import Annotated, List

from fastapi import HTTPException, Security, Cookie
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessCookie
from beanie.operators import Or

from app.models import User, Roles
from app.utils import create_passwd_hash, verify_passwd
from app.settings import settings



JWT = JwtAccessCookie(
    secret_key=settings.SECRET_KEY,
    auto_error=True,
    access_expires_delta=settings.ACCESS_TOKEN_DELTA,
)


async def authenticate(
    token: Annotated[str, Cookie(alias=settings.ACCESS_COOKIE_KEY)],
    claims: JwtAuthorizationCredentials = Security(JWT),
) -> User:
    """Authenticate a user."""
    username = claims.subject.get("username")
    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # cached_token = SESSION_CACHE.get(str(user.id))
    # if not cached_token or token != cached_token:
    #     raise HTTPException(status_code=401, detail="you are not logged in")

    return user


async def register_user(
    email: str, username: str, passwd: str, roles: List[str]
) -> User:
    """creates a new user"""
    if await User.find_one(User.username == username):
        raise HTTPException(status_code=409, detail="username already exists")

    if await User.find_one(User.email == email):
        raise HTTPException(status_code=409, detail="email already exists")

    new_user = User(
        username=username, email=email, password=create_passwd_hash(passwd), roles=roles
    )

    try:
        await new_user.insert()
    except Exception as err:
        raise HTTPException(status_code=500, detail="user registration failed")

    return new_user


async def login_user(
    login_id: str, passwd: str, response: JSONResponse
) -> User:
    """logs in a user"""

    if not login_id or not passwd:
        raise HTTPException(status_code=400, detail="missing credentials")

    user = await User.find_one(
        Or(User.email == login_id, User.username == login_id)
    )

    if not user:
        raise HTTPException(
            status_code=404, detail="invalid username or email"
        )

    if not verify_passwd(passwd, user.password):
        raise HTTPException(status_code=401, detail="invalid password")

    token = JWT.create_access_token(
        {"username": user.username},
    )

    response.set_cookie(
        settings.ACCESS_COOKIE_KEY,
        token,
        expires=datetime.now(UTC) + settings.ACCESS_TOKEN_DELTA,
        httponly=True,
        samesite="strict",
    )
    # prev_token = SESSION_CACHE.get(str(user.id))
    # if prev_token:
    #     SESSION_CACHE.delete(str(user.id))

    # SESSION_CACHE.setex(str(user.id), token)

    return user
