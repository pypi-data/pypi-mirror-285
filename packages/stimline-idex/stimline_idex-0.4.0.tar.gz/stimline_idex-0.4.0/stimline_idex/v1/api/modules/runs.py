from typing import Any, Optional, overload

from ....logging import logger
from ....v1.data_schemas import Run, Unit, Wellbore
from ..api import IDEXApi
from .utils import create_params, log_unused_kwargs, url_encode_id


class Runs:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, unit: Unit, include_soft_delete: Optional[bool] = False) -> list[Run]: ...
    @overload
    def get(self, *, wellbore: Wellbore, include_soft_delete: Optional[bool] = False) -> list[Run]: ...
    @overload
    def get(self, *, unit_id: str, include_soft_delete: Optional[bool] = False) -> list[Run]: ...
    @overload
    def get(self, *, wellbore_id: str, include_soft_delete: Optional[bool] = False) -> list[Run]: ...
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
    ) -> list[Run]: ...

    def get(
        self,
        unit: Optional[Unit] = None,
        unit_id: Optional[str] = None,
        wellbore: Optional[Wellbore] = None,
        wellbore_id: Optional[str] = None,
        **kwargs: Any,
    ) -> list[Run]:
        """
        Get `Run` objects.

        Parameters
        ----------
        unit : Optional[Unit]
            Unit object to get Runs for.
        unit_id : Optional[str]
            Unit ID to get Runs for.
        wellbore : Optional[Wellbore]
            Wellbore object to get Runs for.
        wellbore_id : Optional[str]
            Wellbore ID to get Runs for.
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
        list[Run]
            The `Run` objects.

        """
        if unit is not None or unit_id is not None:
            id = unit_id if unit is None else unit.id
            assert id is not None
            logger.debug(f"Getting Runs for Unit with ID: {id}")
            id = url_encode_id(id)
            data = self._api.get(url=f"Units/{id}/Runs")

        elif wellbore is not None or wellbore_id is not None:
            id = wellbore_id if wellbore is None else wellbore.id
            assert id is not None
            logger.debug(f"Getting Runs for Wellbore with ID: {id}")
            id = url_encode_id(id)
            data = self._api.get(url=f"Wellbores/{id}/Runs")

        else:
            kwargs, params = create_params(**kwargs)
            log_unused_kwargs(**kwargs)

            data = self._api.get(url="Runs", params=params)

        if data.status_code == 204:
            logger.debug("No Runs found.")
            return []

        return [Run.model_validate(row) for row in data.json()]
