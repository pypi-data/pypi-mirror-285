from typing import Optional, overload

from ....logging import logger
from ....v1.data_schemas import Unit, UnitActiveWellbore, Wellbore
from ..api import IDEXApi
from .utils import url_encode_id


class UnitActiveWellbores:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, include_soft_delete: Optional[bool] = False) -> list[UnitActiveWellbore]: ...
    @overload
    def get(self, *, unit: Unit, include_soft_delete: Optional[bool] = False) -> list[UnitActiveWellbore]: ...
    @overload
    def get(self, *, unit_id: str, include_soft_delete: Optional[bool] = False) -> list[UnitActiveWellbore]: ...
    @overload
    def get(self, *, wellbore: Wellbore, include_soft_delete: Optional[bool] = False) -> list[UnitActiveWellbore]: ...
    @overload
    def get(self, *, wellbore_id: str, include_soft_delete: Optional[bool] = False) -> list[UnitActiveWellbore]: ...

    def get(
        self,
        *,
        unit: Optional[Unit] = None,
        unit_id: Optional[str] = None,
        wellbore: Optional[Wellbore] = None,
        wellbore_id: Optional[str] = None,
        include_soft_delete: Optional[bool] = False,
    ) -> list[UnitActiveWellbore]:
        """
        Get `UnitActiveWellbore` objects.

        Parameters
        ----------
        unit : Optional[Unit]
            Unit object to get UnitActiveWellbore for.
        unit_id : Optional[str]
            Unit ID to get UnitActiveWellbore for.
        wellbore : Optional[Wellbore]
            Wellbore object to get UnitActiveWellbore for.
        wellbore_id : Optional[str]
            Wellbore ID to get UnitActiveWellbore for.
        include_soft_delete : Optional[bool] = False
            Include soft deleted records.

        Returns
        -------
        list[UnitActiveWellbore]
            The `UnitActiveWellbore` objects.

        """
        if unit is not None or unit_id is not None:
            id = unit_id if unit is None else unit.id
            assert id is not None
            logger.debug(f"Getting UnitActiveWellbores for Unit with ID: {id}")
            id = url_encode_id(id)
            data = self._api.get(url=f"UnitActiveWellbore/{id}")

        elif wellbore is not None or wellbore_id is not None:
            id = wellbore_id if wellbore is None else wellbore.id
            assert id is not None
            logger.debug(f"Getting UnitActiveWellbores for Wellbore with ID: {id}")
            id = url_encode_id(id)
            data = self._api.get(url=f"UnitActiveWellbore/{id}")

        else:
            data = self._api.get(url="UnitActiveWellbore")

        if data.status_code == 204:
            return []

        records = [UnitActiveWellbore.model_validate(row) for row in data.json()]

        if include_soft_delete:
            return records

        return [rec for rec in records if rec.deleted_date is None]
