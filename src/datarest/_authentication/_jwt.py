import secrets
import datetime
from typing import Union

import jose
import jose.jwt
from pydantic import BaseModel

# FIXME: For dev purposes only:
# - Decide if asymmetric crypto makes more sense here
# - Move secret key to separate source (read from env, vault, sops, at least
# some separate secrets config file)
# - Decide if some form of key rotation is sensible
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(
        data: dict,
        access_token_expire_minutes: int
        ) -> str:
    """Create a JWT access token.

    Args:
        data: Token data dictionary.
        access_token_expire_minutes: Token expiry time in minutes.

    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()
    expire = ( 
        datetime.datetime.utcnow() +
        datetime.timedelta(minutes=access_token_expire_minutes)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jose.jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode a JWT encoded token, verifying the signature.

    Args:
        token: The encoded token string.

    Returns:
        The token data dict representation.
    """
    return jose.jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
