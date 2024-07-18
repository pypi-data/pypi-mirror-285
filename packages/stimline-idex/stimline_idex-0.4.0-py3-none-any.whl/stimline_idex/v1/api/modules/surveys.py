from typing import Any, Optional, overload

from ....logging import logger
from ....v1.data_schemas import Survey, SurveyStation, Wellbore
from ..api import IDEXApi
from .utils import create_params, log_unused_kwargs


class Surveys:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(
        self,
        *,
        filter: Optional[str] = None,
        select: Optional[list[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> list[Survey]: ...

    @overload
    def get(self, *, wellbore: Wellbore) -> list[Survey]: ...
    @overload
    def get(self, *, wellbore_id: str) -> list[Survey]: ...

    def get(
        self, *, wellbore: Optional[Wellbore] = None, wellbore_id: Optional[str] = None, **kwargs: Any
    ) -> list[Survey]:
        """
        Get `Survey` objects.

        Parameters
        ----------
        wellbore : Optional[Wellbore]
            Wellbore object to get Surveys for.
        wellbore_id : Optional[str]
            Wellbore ID to get Surveys for.
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

        Returns
        -------
        list[Survey]
            The `Survey` objects.

        """
        if wellbore is not None:
            # Get for singular wellbore
            logger.debug(f"Getting Surveys for Wellbore with ID: {wellbore.id}")
            data = self._api.get(url=f"Wellbores/{wellbore.id}/Surveys")

        elif wellbore_id is not None:
            # Get for singular wellbore
            logger.debug(f"Getting Surveys for Wellbore with ID: {wellbore_id}")
            data = self._api.get(url=f"Wellbores/{wellbore_id}/Surveys")

        else:
            # Get all surveys matching filters
            kwargs, params = create_params(**kwargs)
            log_unused_kwargs(**kwargs)

            data = self._api.get(url="Surveys", params=params)

        if data.status_code == 204:
            return []

        return [Survey.model_validate(row) for row in data.json()]

    def _get_stations(self, survey_id: str) -> list[SurveyStation]:
        data = self._api.get(url=f"Surveys/{survey_id}/Stations")
        if data.status_code == 204:
            return []
        return [SurveyStation.model_validate(row) for row in data.json()]

    @overload
    def get_stations(self, *, survey: Survey) -> list[SurveyStation]: ...
    @overload
    def get_stations(self, *, survey_id: str) -> list[SurveyStation]: ...

    def get_stations(
        self,
        *,
        survey: Optional[Survey] = None,
        survey_id: Optional[str] = None,
    ) -> list[SurveyStation]:
        if all(v is None for v in [survey, survey_id]):
            raise ValueError("Must provide either a Survey object or a survey_id.")

        if survey is not None:
            return self._get_stations(survey.id)
        elif survey_id is not None:
            return self._get_stations(survey_id)
        else:
            raise ValueError("Invalid input. Must provide either a Survey object or a survey_id.")
