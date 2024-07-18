from typing import Optional

from pydantic import Field

from .base import IDEX


class UomInfo(IDEX):
    id: str


class Uom(UomInfo):
    name: Optional[str]
    description: Optional[str]
    is_base: Optional[bool]
    base_uom_id: Optional[str]


class UnitType(IDEX):
    id: str
    name: str
    member_uoms: list[UomInfo]


class UomConversionRequest(IDEX):
    source_uom_id: str
    target_uom_id: str
    values: list[float]
    include_source_values_in_response: bool = Field(default=False)


class UomConversionResponse(IDEX):
    source_uom_id: str
    target_uom_id: str
    converted_values: list[float]
    source_values: list[float]
