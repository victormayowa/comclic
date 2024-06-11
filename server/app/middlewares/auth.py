"""
authentication middlewares
"""

from datetime import datetime, UTC
from typing import Optional
from redis import Redis

from fastapi import HTTPException, Security, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessCookie
from starlette.status import HTTP_401_UNAUTHORIZED
from beanie.operators import Or

from app.models import User, Roles, Perm
from app.utils import create_passwd_hash, verify_passwd
from app.settings import settings
from app.database import CACHE


JWT = JwtAccessCookie(
    secret_key=settings.SECRET_KEY,
    auto_error=True,
    access_expires_delta=settings.ACCESS_TOKEN_DELTA,
)


async def authenticate(
    req: Request,
    claims: JwtAuthorizationCredentials = Security(JWT),
) -> User:
    """Authenticate a user."""
    username = claims.subject.get("username")
    token = req.cookies.get(settings.ACCESS_COOKIE_KEY)
    cached_token = str(await CACHE.get(f"users:{username}"))
    if not cached_token or token != cached_token:
        await CACHE.delete(f"users:{username}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="you are not logged in"
        )

    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid token")

    return user


async def register_user(
    email: str, username: str, passwd: str, role: list[Roles]
) -> User:
    """creates a new user"""
    if await User.find_one(User.username == username):
        raise HTTPException(status_code=409, detail="username already exists")

    if await User.find_one(User.email == email):
        raise HTTPException(status_code=409, detail="email already exists")

    new_user = User(
        username=username, email=email, password=create_passwd_hash(passwd), role=role
    )

    try:
        await new_user.insert()
    except Exception:
        raise HTTPException(status_code=500, detail="user registration failed")

    return new_user


async def login_user(
    login_id: str,
    passwd: str,
    response: JSONResponse,
) -> User:
    """logs in a user"""

    if not login_id or not passwd:
        raise HTTPException(status_code=400, detail="missing credentials")

    user = await User.find_one(Or(User.email == login_id, User.username == login_id))

    if not user:
        raise HTTPException(status_code=404, detail="invalid username or email")

    if not verify_passwd(passwd, user.password):
        raise HTTPException(status_code=401, detail="invalid password")

    access_token = JWT.create_access_token(
        {"username": user.username},
    )

    response.set_cookie(
        settings.ACCESS_COOKIE_KEY,
        access_token,
        expires=datetime.now(UTC) + settings.ACCESS_TOKEN_DELTA,
        httponly=True,
        samesite="strict",
    )

    cached_token = await CACHE.get(f"users:{user.username}")
    if cached_token:
        await CACHE.delete(f"users:{user.username}")

    await CACHE.setex(f"users:{user.username}", settings.REDIS_TTL, access_token)

    return user


async def get_user(username: str) -> Optional[User]:
    return await User.find_one(User.username == username) or await User.find_one(
        User.email == username
    )


async def has_roles(user: User, roles: list[Roles]) -> Perm:
    """Verify if user has the required roles"""

    for role in roles:
        if role not in user.roles:
            return Perm(user, False)

    return Perm(user, True)


async def is_user_doctor(user: User = Depends(authenticate)) -> User:
    perm = await has_roles(user, [Roles.DR])
    if not perm.authorized:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: not a Doctor",
        )

    return perm.user


async def is_doctor_or_accountant(user: User = Depends(authenticate)) -> User:
    perm = await has_roles(user, [Roles.DR, Roles.AC])
    if not perm.authorized:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: not a Doctor or Accountant",
        )

    return perm.user


async def is_chew(user: User = Depends(authenticate)) -> User:
    perm = await has_roles(user, [Roles.CH])
    if not perm.authorized:
        raise HTTPException(
            status_code=403,
            detail=f"Unauthorized: not a {Roles.CH}",
        )

    return perm.user


async def is_nurse_or_doctor(user: User = Depends(authenticate)) -> User:
    perm = await has_roles(user, [Roles.NR, Roles.DR])
    if not perm.authorized:
        raise HTTPException(
            status_code=403,
            detail="unauthorized: not a nurse or doctor",
        )

    return perm.user
