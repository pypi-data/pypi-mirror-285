from datetime import datetime
from typing import Optional, Union

from pydantic import Field, field_validator

from .base import IDEX, IDEXAudit


class ChannelRange(IDEX):
    """Describes a Range."""

    channel_id: str = Field(alias="id")
    start: datetime
    end: datetime


class TimeRange(IDEX):
    """Describes a Time Range."""

    start: datetime
    end: datetime


class DataPoint(IDEX):
    time: datetime
    value: Union[float, str]


class ChannelDataResponse(IDEX):
    id: str
    points: list[DataPoint]

    @property
    def x(self) -> list[datetime]:
        """Get x-axis values for channel data."""
        return [point.time for point in self.points]

    @property
    def y(self) -> list[Union[float, str]]:
        """Get y-axis values for channel data."""
        return [point.value for point in self.points]


class FirstAndLastDataPoint(ChannelDataResponse):
    @property
    def ordered_points(self) -> list[DataPoint]:
        return sorted(self.points, key=lambda x: x.time)

    @property
    def first(self) -> DataPoint:
        return self.ordered_points[0]

    @property
    def last(self) -> DataPoint:
        return self.ordered_points[-1]


class _DataRequest(IDEX):
    limit: int
    include_outside_points: bool
    ignore_unknown_ids: bool = Field(default=True)

    @field_validator("limit")
    @classmethod
    def check_is_positive(cls, value: int):
        if int(value) <= 0:
            raise ValueError("`limit` must be positive.")
        elif int(value) > 10_000:
            raise ValueError("`limit` must be max 10_000.")
        return value


class ChannelDataRequest(_DataRequest):
    ids: list[str]
    start: Optional[datetime]
    end: Optional[datetime]


class ChannelDataRangeRequest(_DataRequest):
    channels: list[ChannelRange]


class Channel(IDEXAudit):
    id: str
    name: Optional[str]
    global_name: Optional[str]
    description: Optional[str]
    uom: Optional[str]
    uom_class: Optional[str]
    data_type: Optional[str]
    index_type: Optional[str]
    status: Optional[str]
    range: TimeRange
    log_id: Optional[str] = Field(default=None)  # Added manually
    run_id: Optional[str] = Field(default=None)  # Added manually

    @property
    def data_range(self) -> ChannelRange:
        return ChannelRange(
            id=self.id,
            start=self.range.start,
            end=self.range.end,
        )
