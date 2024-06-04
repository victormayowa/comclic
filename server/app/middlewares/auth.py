"""
authentication middlewares
"""
from datetime import datetime, UTC
from typing import Annotated, Optional

from fastapi import HTTPException, Security, Cookie, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessCookie
from starlette.status import HTTP_401_UNAUTHORIZED
from beanie.operators import Or

from app.models import User, Roles, Perm
from app.utils import create_passwd_hash, verify_passwd
from app.settings import settings


JWT = JwtAccessCookie(
    secret_key=settings.SECRET_KEY,
    auto_error=True,
    access_expires_delta=settings.ACCESS_TOKEN_DELTA,
)


async def authenticate(
    req: Request,
    claims: JwtAuthorizationCredentials = Security(JWT)
) -> User:
    """Authenticate a user."""
    token = req.cookies.get(settings.ACCESS_COOKIE_KEY)
    username = claims.subject.get("username")
    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # cached_token = SESSION_CACHE.get(str(user.id))
    # if not cached_token or token != cached_token:
    #     raise HTTPException(status_code=401, detail="you are not logged in")

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


# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return payload
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


async def get_user(username: str) -> Optional[User]:
    return await User.find_one(User.username == username) or await User.find_one(User.email == username)


async def has_roles(
        roles: list[str],
        user: User = Depends(authenticate)) -> Perm:
    """Verify if user has the required roles"""

    for role in roles:
        if Roles(role) not in user.roles:
            return False

    return user, True


async def is_user_doctor(roles: list[str] = ["Doctor"], perm: Perm = Depends(has_roles)) -> User:
    if not perm.authorized:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="unauthorized: not a doctor",
        )
    
    return perm.user


async def is_doctor_or_accountant(roles: list[str] = ["Doctor", "Accountant"], perm: Perm = Depends(has_roles)) -> User:
    if not perm.authorized:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="unauthorized: not a doctor or accountant",
        )
    
    return perm.user


async def is_chew(roles: list[str] = ["CHEW/RI/others"], perm: Perm = Depends(has_roles)) -> User:
    if not perm.authorized:
        raise HTTPException(
            status_code=403,
            detail="unauthorized: not a CHEW/RI/others",
        )

    return perm.user


async def is_nurse_or_doctor(roles: list[str] = ["Nurse", "Doctor"], perm: Perm = Depends(has_roles)) -> User:
    if not perm.authorized:
        raise HTTPException(
            status_code=403,
            detail="unauthorized: not a nurse or doctor",
        )

    return perm.user

