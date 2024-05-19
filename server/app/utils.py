"""
chat utility helper functions
"""

from passlib.context import CryptContext


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