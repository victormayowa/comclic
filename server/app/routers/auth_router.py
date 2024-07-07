"""
authentication endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.models import InvalidatedToken, PasswordResetRequest, UserRegister, ResponseModel, User, Token
from app.middlewares.auth import register_user # authenticate
from app.middlewares.authware import create_access_token, oauth2_scheme, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from fastapi.security import OAuth2PasswordRequestForm


from beanie.operators import Or

from app.utils import send_email, verify_passwd


auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={401: {"description": "Not authenticated"}},
)


@auth_router.post("/register", status_code=201)
async def register(user: UserRegister) -> ResponseModel:
    """registration route"""
    username = user.username
    email = user.email
    
    passwd = user.password
    role = user.role

    user = await register_user(email, username, passwd, role)

    return ResponseModel(
        message="user registered successfully",
        status_code=201,
    )


@auth_router.post("/login", response_model=Token)
@auth_router.post("/token", status_code=200)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """logs in a user"""

    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="missing credentials")

    user = await User.find_one(
        Or(User.email == form_data.username, User.username == form_data.username)
    )

    if not user:
        raise HTTPException(status_code=401, detail="invalid username or email or password")

    if not verify_passwd(form_data.password, user.password):
        raise HTTPException(
            status_code=401, detail="invalid username or email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/is_authenticated")
async def is_authenticated(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "roles": [role.value for role in current_user.role],
    }


# @auth_router.get("/is_authenticated")
# async def is_authenticated(
#     user: User = Depends(authenticate),
# ) -> ResponseModel:
#     """verify if a user is logged in"""

#     return ResponseModel(
#         message="authenticated",
#         status_code=200,
#         data=user.model_dump(),
#     )


@auth_router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)
):
    # Store the token in the invalidated tokens collection
    invalidated_token = InvalidatedToken(token=token, invalidated_at=datetime.utcnow())
    await invalidated_token.insert()
    return {"message": "Successfully logged out"}


# @auth_router.get("/logout", status_code=200)
# async def logout(user: User = Depends(authenticate)) -> ResponseModel:
#     """logs out a user"""

#     #SESSION_CACHE.delete(str(user.id))

#     return ResponseModel(
#         message="logged out successfully",
#         status_code=200,
#     )


# @auth_router.get("/forgot_password")
# async def get_reset_token(
#     email: str,
#     response: JSONResponse,
# ) -> ResponseModel:
#     """generates a reset token"""

#     user = await User.find_one(User.email == email)
#     if not user:
#         return HTTPException(status_code=404, detail="User does not exist")

#     reset_token = token_hex()

#     user.reset_token = reset_token
#     user.save()

#     response.headers["X-Reset-Token"] = reset_token

#     # FIXME: Add logic to send email to user with a link pointing to form
#     # where they can change password.
#     # format of link:
#     #        https://<domain>/reset_password/{reset_token}
#     #       HTTP method = GET

#     return ResponseModel(
#         message="reset token generated successfully",
#         status_code=200,
#     )

# TODO: Once user confirms through email and a reset token is created,
# the token is used to access this endpoint that will reset the password


@auth_router.post("/forgot_password")
async def forgot_password(request: PasswordResetRequest):
    user = await User.find_one(User.email == request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token_expires = timedelta(hours=1)
    reset_token = create_access_token(
        data={"sub": user.username}, expires_delta=reset_token_expires
    )
    reset_url = f"http://frontend-route.com/reset_password?token={reset_token}"
    email_subject = "Password Reset Request"
    email_body = f"Hi {user.username},\n\nPlease use the following link to reset your password:\n{reset_url}\n\nIf you did not request a password reset, please ignore this email."
    #user_email : EmailSchema = {"email": [user.email]}
    await send_email(email_subject, [user.email], email_body)
    return {"message": "Password reset token sent"}


# @auth_router.post("/reset_password/{reset_token}")
# async def reset_password(
#     reset_token: str,
#     new_password: Annotated[str, Form()],
# ):
#     user = await User.find_one(User.reset_token == reset_token)
#     if not user:
#         return HTTPException(status_code=404, detail="invalid reset token")

#     user.set_password(new_password)
#     user.save()

#     return ResponseModel(
#         message="password reset successful",
#         status_code=200,
#     )
