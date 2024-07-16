from typing import Any, Optional, Union, overload

from ....logging import logger
from ....v1.data_schemas import Field as Installation
from ..api import IDEXApi
from .utils import create_params, log_unused_kwargs


class Installations:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, id: str) -> Installation: ...
    @overload
    def get(
        self,
        *,
        filter: Optional[str] = None,
        select: Optional[list[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        order_by: Optional[str] = None,
        include_soft_delete: Optional[bool] = False,
    ) -> list[Installation]: ...

    def get(self, id: Optional[str] = None, **kwargs: Any) -> Union[Installation, list[Installation]]:
        """
        Get `Installation` object(s).

        Parameters
        ----------
        id : Optional[str]
            Installation to retrieve.
        filter : Optional[str]
            OData filter string.
        select : list[str] | None
            Provide a list of columns to retrieve from output.
        top : Optional[int]
            Limit the number of results returned.
        skip : Optional[int]
            Skip the first N results.
        order_by : Optional[str]
            Order the results by columns.
        include_soft_delete : Optional[bool] = False
            Include soft deleted records.

        Returns
        -------
        Union[Installation, list[Installation]]
            The `Installation` object(s).

        """
        if id is not None:
            logger.debug(f"Getting Installation with ID: {id}")
            data = self._api.get(url=f"Installations/{id}")
            return Installation.model_validate(data.json())

        kwargs, params = create_params(**kwargs)
        log_unused_kwargs(**kwargs)

        data = self._api.get(url="Installations", params=params)

        if data.status_code == 204:
            logger.debug("No Installations found.")
            return []

        return [Installation.model_validate(row) for row in data.json()]
