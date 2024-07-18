from typing import Optional

from pydantic import Field

from ..base import IDEX, Approval, IDEXAudit, IDEXAuditLite, TimeDuration


class JobPlan(IDEX):
    """
    Describes a Job Plan.

    Endpoint allows for selecting return columns, need default Nones.
    """

    id: str
    name: Optional[str] = Field(default=None)
    well_name: Optional[str] = Field(default=None)
    well_id: Optional[str] = Field(default=None)
    wellbore_name: Optional[str] = Field(default=None)
    wellbore_id: Optional[str] = Field(default=None)
    field_name: Optional[str] = Field(default=None)
    phase: Optional[str] = Field(default=None)
    service_type: Optional[str] = Field(default=None)
    operator_name: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    project_auto_id: Optional[str] = Field(default=None)
    audit: IDEXAudit


class JobPlanRequest(IDEX):
    """For getting plans that match filter. All properties are optional."""

    well_name: Optional[str] = Field(default=None)
    well_id: Optional[str] = Field(default=None)
    wellbore_name: Optional[str] = Field(default=None)
    wellbore_id: Optional[str] = Field(default=None)
    field_name: Optional[str] = Field(default=None)
    creation_date: Optional[str] = Field(default=None)
    phase: Optional[str] = Field(default=None)
    service_type: Optional[str] = Field(default=None)


class _IDEXActivity:
    id: str
    name: Optional[str]
    type: Optional[str]
    order: int


class JobPlanTask(_IDEXActivity):
    approvals: list[Approval]


class Activity(_IDEXActivity):
    estimated_durations: list[TimeDuration]


class Step(_IDEXActivity): ...


class Document(IDEXAuditLite):
    """
    Describes a Document.

    Endpoint allows for selecting return columns, need default Nones.
    """

    id: str
    job_plan_id: Optional[str]
    job_plan_name: Optional[str] = Field(default=None)
    file_name: Optional[str] = Field(default=None)
    file_type: Optional[str] = Field(default=None)
    document_kind: Optional[str] = Field(default=None)
    asset: Optional[str] = Field(default=None)
    service_type: Optional[str] = Field(default=None)
    job_type: Optional[str] = Field(default=None)
    well_name: Optional[str] = Field(default=None)
    well_id: Optional[str] = Field(default=None)
    wellbore_name: Optional[str] = Field(default=None)
    wellbore_id: Optional[str] = Field(default=None)
    field_name: Optional[str] = Field(default=None)
