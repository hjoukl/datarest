from typing import Callable, List, Protocol

from fastapi import APIRouter

import attrs


@attrs.define
class User:
    username: str


@attrs.define
class Authentication:
    routers: List[APIRouter]
    dependencies: List[Callable]


class Authenticator(Protocol):
    def authenticate(**credentials) -> User:
        ... 
