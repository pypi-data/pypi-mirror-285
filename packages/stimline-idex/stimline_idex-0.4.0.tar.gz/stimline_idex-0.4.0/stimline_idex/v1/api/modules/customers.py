from typing import Any, Optional, Union, overload

from ....logging import logger
from ....v1.data_schemas import Customer
from ..api import IDEXApi
from .utils import create_params, log_unused_kwargs


class Customers:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, id: str) -> Customer: ...
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
    ) -> list[Customer]: ...

    def get(
        self,
        id: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Customer, list[Customer]]:
        """
        Get `Customer` object(s).

        Parameters
        ----------
        id : Optional[str]
            Customer to retrieve.
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
        Union[Customer, list[Customer]]
            The `Customer` object(s).

        """
        if id is not None:
            logger.debug(f"Getting Customer with ID: {id}")
            data = self._api.get(url=f"Customers/{id}")
            return Customer.model_validate(data.json())

        kwargs, params = create_params(**kwargs)
        log_unused_kwargs(**kwargs)

        data = self._api.get(url="Customers", params=params)

        if data.status_code == 204:
            logger.debug("No Customers found.")
            return []

        return [Customer.model_validate(row) for row in data.json()]
