from typing import Optional, overload

from ....logging import logger
from ....v1.data_schemas import Wellbore, WellboreLiveStatus
from ..api import IDEXApi
from .utils import url_encode_id


class WellboreLiveStatuses:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, include_soft_delete: Optional[bool] = False) -> list[WellboreLiveStatus]: ...
    @overload
    def get(self, *, wellbore: Wellbore, include_soft_delete: Optional[bool] = False) -> list[WellboreLiveStatus]: ...
    @overload
    def get(self, *, wellbore_id: str, include_soft_delete: Optional[bool] = False) -> list[WellboreLiveStatus]: ...

    def get(
        self,
        *,
        wellbore: Optional[Wellbore] = None,
        wellbore_id: Optional[str] = None,
        include_soft_delete: Optional[bool] = False,
    ) -> list[WellboreLiveStatus]:
        """
        Get `WellboreLiveStatus` objects.

        Parameters
        ----------
        wellbore : Optional[Wellbore]
            Well object to get WellboreLiveStatus for.
        wellbore_id : Optional[str]
            Wellbore ID to get WellboreLiveStatus for.
        include_soft_delete : Optional[bool] = False
            Include soft deleted records.

        Returns
        -------
        list[WellboreLiveStatus]
            The `WellboreLiveStatus` objects.

        """
        if wellbore is not None or wellbore_id is not None:
            id = wellbore_id if wellbore is None else wellbore.id
            assert id is not None
            logger.debug(f"Getting WellboreLiveStatus for Wellbore with ID: {id}")
            id = url_encode_id(id)
            data = self._api.get(url=f"WellboreLiveStatus/{id}")

        else:
            data = self._api.get(url="WellboreLiveStatus")

        if data.status_code == 204:
            return []

        records = [WellboreLiveStatus.model_validate(row) for row in data.json()]

        if include_soft_delete:
            return records

        return [rec for rec in records if rec.deleted_date is None]
