"""Lazy abstraction for HTTP client."""

from typing import Any
from urllib.parse import urljoin

from requests import Response, Session

from ...logging import logger
from .auth import IDEXAuth


class IDEXApi:
    def __init__(
        self,
        *,
        auth: IDEXAuth,
        session: Session,
    ):
        self.auth = auth
        self.session = session

    @property
    def base_url(self):
        return self.auth.base_url

    def _authenticate(self) -> None:
        new_auth = self.auth.get_auth_header(base_url=self.base_url)
        self.session.headers.update(new_auth)

    def _send_request(self, *, method: str, url: str, **kwargs: Any) -> Response:
        self._authenticate()
        request_url = urljoin(self.base_url, url)
        kwargs = handle_select_clause(**kwargs)
        rsp = self.session.request(method=method, url=request_url, **kwargs)
        rsp.raise_for_status()
        return rsp

    def get(self, *, url: str, **kwargs: Any) -> Response:
        return self._send_request(method="GET", url=url, **kwargs)

    def post(self, *, url: str, **kwargs: Any) -> Response:
        if "headers" in kwargs:
            headers = kwargs.pop("headers")
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
            if "Accept" not in headers:
                headers["Accept"] = "application/json"
        else:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
        return self._send_request(method="POST", url=url, headers=headers, **kwargs)


def handle_select_clause(**kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Check for select clause in params and remove it if present.

    Currently the API returns an invalid response JSON when a select clause is present.
    It appears the response keys change from camelCase to PascalCase.
    """
    if "params" not in kwargs:
        return kwargs

    params = kwargs.pop("params")

    if "$select" in params:
        logger.warning("Select clause changes API return format. Removing clause.")
        params.pop("$select")
    kwargs["params"] = params
    return kwargs
