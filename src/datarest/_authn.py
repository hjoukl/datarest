from fastapi import Depends, FastAPI, HTTPException, status

from ._cfgfile import AuthnEnum
from ._app_config import config


# TODO: Does a more elaborate design make sense here? Can we decouple authn API
# (e.g. HTTP Basic Auth) from backend/authenticator (e.g. LDAP)?
def create_authn(authn: AuthnEnum):
    """
    Args:
        authn: Authentication model

    Returns:
        A list of FastAPI authentication dependencies ([Depends(...)])
    """
    if authn.authn_type == AuthnEnum.HTTPBasic_LDAP:
        return _httpbasic_ldap()
    elif authn.authn_type == AuthnEnum.OAuth2PasswordBearer_LDAP:
        return _oauth2_passwordbearer_ldap()
    return []


def _httpbasic_ldap():
    """Create and return a HTTPBasicCredentials-based auth function dependency.

    Returns:
        [Depends(authenticate)] where authenticate is a function that expects a
        HTTPBasicCredentials arg and returns the (authenticated) username on
        successful LDAP authentication.
    """
    from fastapi.security import HTTPBasic, HTTPBasicCredentials
    from . import _ldap_authn
    security = HTTPBasic()
    authn_backend = _ldap_authn.LDAPAuth(                     
        bind_dn=config.datarest.fastapi.authn.ldap.bind_dn,
        server=config.datarest.fastapi.authn.ldap.server)

    def authenticate(
            credentials: HTTPBasicCredentials = Depends(security)
            ):
        """Authenticate LDAP user with given basic auth credentials.
        """
        try:                                      
            ldap_user = authn_backend.authenticate(
                credentials.username, credentials.password)
        except _ldap_authn.InvalidCredentialsError:  
            raise HTTPException(                  
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",     
                headers={"WWW-Authenticate": "Basic"},
                )                                 
        return credentials.username
    return [Depends(authenticate)]


def _oauth2_passwordbearer_ldap():
    from fastapi.security import (
        OAuth2PasswordBearer, OAuth2PasswordRequestForm)
    raise NotImplementedError()
