from datetime import datetime
from .base import IDEX


class AuthenticateRequest(IDEX):
    """Describes a request to authenticate a user."""

    username: str
    password: str


class AuthenticateResponse(IDEX):
    """Describes a response to an authentication request."""

    id: str
    first_name: str
    last_name: str
    username: str
    token: str
    token_expire: datetime
    refresh_token: str
    refresh_token_expire: datetime


class RefreshTokenRequest(IDEX):
    """Describes a request to refresh a user token."""

    refresh_token: str


class RefreshTokenResponse(IDEX):
    """Describes a response to a token refresh request."""

    token: str
    token_expire: datetime
