import jose
import jose.jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import (
    HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
    )
from typing_extensions import Annotated

from ._authn_common import Authentication, User
from ._authn_exceptions import InvalidCredentialsError
from ._jwt import Token, create_access_token, decode_access_token


def http_basic_auth(*, authn_backend, **kwargs) -> Authentication:
    """Create and return an HTTP Basic Auth authentication frontende that
    validates user credentials through the given `authn_backend`.
   
    Args:
        authn_backend: An authentication object providing an
            authenticate(username: str, password: str) -> str
            method

    Returns:
        Authentication: An Authentication object that bundles FastAPI auth
        helper routers and dependencies.
    """
    def authenticate(
            credentials: HTTPBasicCredentials = Depends(HTTPBasic())
            ) -> User:
        """Authenticate LDAP user with given basic auth credentials.
        """
        try:
            authenticated_user = authn_backend.authenticate(
                username=credentials.username, password=credentials.password)
        except InvalidCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
                )
        return User(username=authenticated_user)
    return Authentication(routers=[], dependencies=[Depends(authenticate)])


def oauth2_passwordbearer_auth(
        *, 
        authn_backend,
        token_url,
        access_token_expire_minutes,
        prefix='',
        **kwargs
        ):
    """Create and return an OAuth2 Password Bearer authentication frontend that
    validates user credentials through the given `authn_backend`.

    Args:
        authn_backend: An authentication object providing an
            authenticate(username: str, password: str) -> str
            method
        token_url: URL for access token retrieval
        access_token_expire_minutes: Time in minutes for which an access token
            remains valid

    Returns:
        Authentication: An Authentication object that bundles FastAPI auth
        helper routers and dependencies.
    """
    form_token_url = token_url
    if prefix:
        # Hack: If the FastAPI app includes the returned token_router with URL
        # prefix the Swagger UI Authorize form will still post to the
        # unprefixed token URL.
        form_token_url = f'{prefix}/{token_url.replace("/", "", 1)}'
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=form_token_url)
    token_router = APIRouter()

    @token_router.post(token_url, response_model=Token)
    async def login_for_access_token(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

        try:
            authenticated_user = authn_backend.authenticate(
                username=form_data.username, password=form_data.password)
        except InvalidCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
                )

        access_token = create_access_token(
            data={"sub": authenticated_user},
            access_token_expire_minutes=access_token_expire_minutes
            )
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user_from_token(
            token: Annotated[str, Depends(oauth2_scheme)]
            ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode_access_token(token)
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            return User(username=username)
        except jose.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jose.JWTError:
            raise credentials_exception

    return Authentication(
        routers=[token_router],
        dependencies=[Depends(get_user_from_token)]
        )
