import secrets
from datetime import datetime, timedelta
from typing import Union

from jose import JWTError, jwt
from pydantic import BaseModel

# FIXME: For dev purposes only:
# - Decide if asymmetric crypto makes more sense here
# - Move secret key to separate source (read from env, vault, sops, at least
# some separate secrets config file)
# - Decide if some form of key rotation is sensible
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


def create_access_token(
        data: dict,
        expires_delta: Union[timedelta, None] = None
        ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
