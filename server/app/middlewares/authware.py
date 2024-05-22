from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from typing import Optional

from app.models import User
from app.settings import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_user(username: str) -> Optional[User]:
    return await User.find_one(User.username == username)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    #print(username)
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


async def is_user_doctor(current_user: User = Depends(get_current_user)):
    user_roles = [role.value for role in current_user.role]
    print(user_roles)
    if "Doctor" not in user_roles:
        raise HTTPException(status_code=403, detail="Forbidden: User is not a doctor")
    return current_user


async def is_doctor_or_accountant(current_user: User = Depends(get_current_user)):
    user_roles = [role.value for role in current_user.role]
    print(user_roles)
    if "Doctor" not in user_roles and "Accountant" not in user_roles:
        raise HTTPException(
            status_code=403, detail="Forbidden: User is not a doctor or accountant"
        )
    return current_user


async def is_chew(current_user: User = Depends(get_current_user)):
    user_roles = [role.value for role in current_user.role]
    if "CHEW/RI/others" not in user_roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: User is not authorized to add/update immunization records",
        )
    return current_user


async def is_nurse_or_doctor(current_user: User = Depends(get_current_user)):
    user_roles = [role.value for role in current_user.role]
    if "Nurse" not in user_roles and "Doctor" not in user_roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: User is not authorized to delete immunization records",
        )
    return current_user
