"""
authentication endpoints
"""

from secrets import token_hex
from typing import Annotated
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.database import CACHE
from app.models import UserRegister, ResponseModel, User, UserLogin
from app.middlewares.auth import register_user, authenticate, login_user


auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@auth_router.post("/register", status_code=201)
async def register(user: UserRegister) -> ResponseModel:
    """registration route"""
    username = user.username
    email = user.email
    passwd = user.password
    roles = user.roles

    user = await register_user(email, username, passwd, roles)

    return ResponseModel(
        message="user registered successfully",
        status_code=201,
    )


@auth_router.post("/login", status_code=200)
async def login(credentials: UserLogin, response: JSONResponse) -> ResponseModel:
    """logs in a user"""

    login_id = credentials.username or credentials.email
    password = credentials.password

    user = await login_user(login_id, password, response)

    return ResponseModel(
        message="login successful",
        status_code=200,
        data=user.model_dump(),
    )


@auth_router.get("/is_authenticated")
async def is_authenticated(
    user: User = Depends(authenticate),
) -> ResponseModel:
    """verify if a user is logged in"""

    return ResponseModel(
        message="authenticated",
        status_code=200,
        data=user.model_dump(),
    )


@auth_router.get("/logout", status_code=200)
async def logout(
    user: User = Depends(authenticate),
) -> ResponseModel:
    """logs out a user"""

    await CACHE.delete(f"users:{user.username}")

    return ResponseModel(
        message="logged out successfully",
        status_code=200,
    )


@auth_router.get("/forgot_password")
async def get_reset_token(
    email: str,
    response: JSONResponse,
) -> ResponseModel:
    """generates a reset token"""

    user = await User.find_one(User.email == email)
    if not user:
        return HTTPException(status_code=404, detail="User does not exist")

    reset_token = token_hex()

    user.reset_token = reset_token
    user.save()

    response.headers["X-Reset-Token"] = reset_token

    # FIXME: Add logic to send email to user with a link pointing to form
    # where they can change password.
    # format of link:
    #        https://<domain>/reset_password/{reset_token}
    #       HTTP method = GET

    return ResponseModel(
        message="reset token generated successfully",
        status_code=200,
    )


# TODO: Once user confirms through email and a reset token is created,
# the token is used to access this endpoint that will reset the password
@auth_router.post("/reset_password/{reset_token}")
async def reset_password(
    reset_token: str,
    new_password: Annotated[str, Form()],
):
    user = await User.find_one(User.reset_token == reset_token)
    if not user:
        return HTTPException(status_code=404, detail="invalid reset token")

    user.set_password(new_password)
    user.reset_token = None
    user.save()

    return ResponseModel(
        message="password reset successful",
        status_code=200,
    )
