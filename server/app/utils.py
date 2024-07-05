"""
chat utility helper functions
"""

from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_passwd_hash(passwd: str) -> str:
    """
    returns the hash of the password
    """
    return HASHER.hash(passwd)


def verify_passwd(passwd: str, passwd_hash: str) -> bool:
    """
    verifies the password
    """
    return HASHER.verify(passwd, passwd_hash)


def encode_input(data) -> dict:
    data = jsonable_encoder(data)
    data = {k: v for k, v in data.items() if v is not None}
    return data
