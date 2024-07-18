from typing import Optional, Union, overload

from ....logging import logger
from ....v1.data_schemas import Log, Unit
from ..api import IDEXApi
from .utils import url_encode_id


class Logs:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, id: str) -> Log: ...
    @overload
    def get(self, *, unit: Unit) -> list[Log]: ...
    @overload
    def get(self, *, unit_id: str) -> list[Log]: ...

    def get(
        self,
        *,
        id: Optional[str] = None,
        unit: Optional[Unit] = None,
        unit_id: Optional[str] = None,
    ) -> Union[Log, list[Log]]:
        """
        Get `Log` object(s).

        Parameters
        ----------
        id : Optional[str]
            Log to retrieve.
        unit : Optional[Unit]
            Unit object to get Logs for.
        unit_id : Optional[str]
            Unit ID to get Logs for.

        Returns
        -------
        Union[Log, list[Log]]
            The `Log` object(s).

        """
        if id is not None:
            logger.debug(f"Getting Wellbore with ID: {id}")
            data = self._api.get(url=f"Logs/{id}")
            return Log.model_validate(data.json())

        if unit is not None:
            logger.debug(f"Getting Logs for Unit with ID: {unit.id}")
            id = url_encode_id(unit.id)
        elif unit_id is not None:
            logger.debug(f"Getting Logs for Unit with ID: {unit_id}")
            id = url_encode_id(unit_id)
        else:
            raise ValueError("Either `unit` or `unit_id` must be provided.")

        data = self._api.get(url=f"Units/{id}/Logs")
        if data.status_code == 204:
            return []

        return [Log.model_validate(row) for row in data.json()]
