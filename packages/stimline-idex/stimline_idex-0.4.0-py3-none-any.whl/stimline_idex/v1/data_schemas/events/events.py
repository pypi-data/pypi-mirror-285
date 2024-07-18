from datetime import datetime
from typing import Optional

from pydantic import Field

from ..base import IDEX, DoubleNullableUomValue, IDEXAudit, IDEXAuditLite


class Maintenance(IDEXAuditLite):
    """Describes a maintenance event."""

    id: str
    location_id: Optional[str]
    type: Optional[str]
    description: Optional[str]
    repair_notes: Optional[str]
    running_meters: DoubleNullableUomValue
    start_date: datetime
    end_date: Optional[datetime]


class Run(IDEXAudit):
    """Describes a run."""

    id: str
    name: Optional[str] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    status: Optional[str] = Field(default=None)
    run_task: Optional[str] = Field(default=None)
    job_type: Optional[str] = Field(default=None)
    unit_id: Optional[str] = Field(default=None)
    hidden: Optional[bool] = Field(default=None)
    wellbore_id: Optional[str] = Field(default=None)
    log_ids: Optional[list[str]] = Field(default=None)
    work_order_number: Optional[str] = Field(default=None)


class SurveyStation(IDEX):
    """Describes a single survey station."""

    id: str
    md: float
    tvd: Optional[float]
    incl: float
    azi: float
    dls: Optional[float]
    vert_sect: Optional[float]
    disp_ns: Optional[float]
    disp_ew: Optional[float]


class Survey(IDEX):
    """Describes a wellbore survey."""

    id: str
    name: Optional[str] = Field(default=None)
    wellbore_id: Optional[str] = Field(default=None)
    md_uom: Optional[str] = Field(default=None)
    tvd_uom: Optional[str] = Field(default=None)
    inc_uom: Optional[str] = Field(default=None)
    azi_uom: Optional[str] = Field(default=None)
    dls_uom: Optional[str] = Field(default=None)
    vert_sect_uom: Optional[str] = Field(default=None)
    disp_ns_uom: Optional[str] = Field(default=None)
    disp_ew_uom: Optional[str] = Field(default=None)
    audit: Optional[IDEXAudit] = Field(default=None)
    stations: list[SurveyStation] = Field(default=None)


class JobHistory(IDEXAuditLite):
    """Describes a historical job event."""

    id: str
    coiled_tubing_string: Optional[str]
    coiled_tubing_string_id: Optional[str]
    reel_name: Optional[str]
    reel_id: Optional[str]
    customer: Optional[str]
    customer_id: Optional[str]
    well_name: Optional[str]
    well_id: Optional[str]
    well_time_zone: Optional[str]
    added_dhrm: DoubleNullableUomValue = Field(alias="addedDHRM")
    weight_pull_avg: DoubleNullableUomValue = Field(alias="weightPullAverage")
    weight_pull_min: DoubleNullableUomValue
    weight_pull_max: DoubleNullableUomValue
    weight_push_avg: DoubleNullableUomValue = Field(alias="weightPushAverage")
    weight_push_min: DoubleNullableUomValue
    weight_push_max: DoubleNullableUomValue
    speed_pooh_avg: DoubleNullableUomValue = Field(alias="speedPOOHAverage")
    speed_pooh_min: DoubleNullableUomValue = Field(alias="speedPOOHMin")
    speed_pooh_max: DoubleNullableUomValue = Field(alias="speedPOOHMax")
    speed_rih_avg: DoubleNullableUomValue = Field(alias="speedRIHAverage")
    speed_rih_min: DoubleNullableUomValue = Field(alias="speedRIHMin")
    speed_rih_max: DoubleNullableUomValue = Field(alias="speedRIHMax")
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class ScheduledJob(IDEXAuditLite):
    id: str
    name: Optional[str]
    job_plan: Optional[str]
    customer: Optional[str]
    customer_id: Optional[str]
    well_name: Optional[str]
    well_id: Optional[str]
    wellbore_name: Optional[str]
    wellbore_id: Optional[str]
    well_time_zone: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class UnitActiveWellbore(IDEXAudit):
    id: str
    unit_id: str
    wellbore_id: str


class WellboreHistory(IDEXAudit):
    id: str
    unit_id: Optional[str]
    wellbore_id: Optional[str]
    start: datetime
    end: Optional[datetime]
    log_ids: Optional[list[str]]
