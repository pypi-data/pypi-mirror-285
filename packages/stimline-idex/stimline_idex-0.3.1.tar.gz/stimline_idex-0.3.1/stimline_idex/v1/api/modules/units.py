from typing import Any

from ....logging import logger
from ....v1.data_schemas import Unit
from ..api import IDEXApi
from .utils import create_params, log_unused_kwargs


class Units:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    def get(self, **kwargs: Any) -> list[Unit]:
        """
        Get `Unit` objects.

        Parameters
        ----------
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
        list[Unit]
            The `Unit` objects.

        """
        kwargs, params = create_params(**kwargs)
        log_unused_kwargs(**kwargs)

        data = self._api.get(url="Units", params=params)

        if data.status_code == 204:
            logger.debug("No Units found.")
            return []

        return [Unit.model_validate(row) for row in data.json()]
