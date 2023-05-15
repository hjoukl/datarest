from dataclasses import dataclass
from typing import Type, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer,
    OAuth2PasswordRequestForm)
from fastapi.security.base import SecurityBase
from . import _cfgfile
from ._app_config import config


@dataclass
class AuthnScheme:
    scheme: SecurityBase
    CredentialsType: Union[Type[str], Type[HTTPBasicCredentials]]


def create_authn(authn: _cfgfile.Authn):
    """
    Args:
        authn: Authentication config model

    Returns:
        A list of authentication dependency callables
        ([authenticate_func, ...])
    """
    AuthnEnum = _cfgfile.AuthnEnum
    if authn.authn_type == AuthnEnum.HTTPBasic_LDAP:
        authn_deps =  [
            _ldap_authentication(
                ldap=authn.ldap,
                authn_scheme=_httpbasic_scheme())
            ]
    elif authn.authn_type == AuthnEnum.OAuth2PasswordBearer_LDAP:
        authn_deps = [
            _ldap_authentication(
                ldap=authn.ldap,
                authn_scheme=_oauth2_passwordbearer_scheme()
                )
            ]

    return authn_deps


def _httpbasic_scheme():
    return AuthnScheme(
        scheme=HTTPBasic(), CredentialsType=HTTPBasicCredentials )


def _ldap_authentication(ldap: _cfgfile.LDAP, authn_scheme: AuthnScheme):
    """Create and return an LDAP-backed auth function.

    Returns:
        authenticate where authenticate is a callable that expects an
        authn_scheme.CredentialsType arg and returns the (authenticated)
        username on successful LDAP authentication.
    """
    from . import _ldap_authn
    authn_backend = _ldap_authn.LDAPAuth(
        bind_dn=ldap.bind_dn, server=ldap.server)

    def authenticate(
            credentials: authn_scheme.CredentialsType = Depends(
                authn_scheme.scheme)
            ):
        """Authenticate LDAP user with given basic auth credentials.

        Returns: Authenticated username
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
    return authenticate


def _oauth2_passwordbearer_scheme():
    raise NotImplementedError()
