from ....v1.data_schemas import UnitType, Uom
from ....v1.data_schemas.uoms import UomConversionRequest, UomConversionResponse
from ..api import IDEXApi


class Uoms:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    def get_uoms(self) -> list[Uom]:
        """
        Get `Uom` objects.

        Returns
        -------
        list[Uom]
            The `Uom` objects.

        """
        data = self._api.get(url="UnitOfMeasure/Uoms")
        return [Uom.model_validate(row) for row in data.json()]

    def get_unit_types(self) -> list[UnitType]:
        """
        Get `UnitType` objects.

        Returns
        -------
        list[UnitType]
            The `UnitType` objects.

        """
        data = self._api.get(url="UnitOfMeasure/UnitTypes")
        return [UnitType.model_validate(row) for row in data.json()]

    def convert_scalars(
        self,
        from_uom: str,
        to_uom: str,
        values: list[float],
    ) -> list[float]:
        """
        Convert scalar values from one unit of measure to another.

        Parameters
        ----------
        from_uom : str
            The source unit of measure.
        to_uom : str
            The target unit of measure.
        values : list[float]
            The values to convert.

        Returns
        -------
        list[float]
            The converted values.

        """
        payload = UomConversionRequest.model_construct(
            source_uom_id=from_uom,
            target_uom_id=to_uom,
            values=values,
        )
        data = self._api.post(
            url="UnitOfMeasure/Convert",
            data=payload.model_dump_json(by_alias=True),
        )
        return UomConversionResponse.model_validate_json(data.text).converted_values
