from typing import Literal

from ....v1.data_schemas import (
    AsvLeakRateTest,
    BuildUpTest,
    Inflow30MinTest,
    InflowTest,
    LeakRateTest,
    PressureTest,
    SssvLeakRateTest,
)
from ..api import IDEXApi


class Tests:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    def get_buildup_tests(self, kind: Literal["API", "QTS"]) -> list[BuildUpTest]:
        """
        Get `BuildUpTest` objects.

        Returns
        -------
        list[BuildUpTest]

        """
        if kind == "API":
            url = "InterventionTests/ApiBuildUpTest"
        elif kind == "QTS":
            url = "InterventionTests/QtsTests"
        else:
            raise ValueError(f"Invalid kind: {kind}.")

        data = self._api.get(url=url)

        if data.status_code == 204:
            return []

        return [BuildUpTest.model_validate(row) for row in data.json()]

    def get_asv_leak_rate_tests(self) -> list[AsvLeakRateTest]:
        """
        Get `AsvLeakRateTest` objects.

        Returns
        -------
        list[AsvLeakRateTest]

        """
        data = self._api.get(url="InterventionTests/AsvApiLeakRateTests")

        if data.status_code == 204:
            return []

        return [AsvLeakRateTest.model_validate(row) for row in data.json()]

    def get_sssv_leak_rate_tests(self) -> list[SssvLeakRateTest]:
        """
        Get `SssvLeakRateTest` objects.

        Returns
        -------
        list[SssvLeakRateTest]

        """
        data = self._api.get(url="InterventionTests/SssvApiLeakRateTests")

        if data.status_code == 204:
            return []

        return [SssvLeakRateTest.model_validate(row) for row in data.json()]

    def get_inflow_tests(self, kind: Literal["30m", "Regular"]) -> list[InflowTest]:
        """
        Get `InflowTest` objects.

        Parameters
        ----------
        kind : Literal["30m","Regular"]
            The kind of InflowTest to retrieve.

        Returns
        -------
        list[InflowTest]

        """
        if kind == "30m":
            url = "InterventionTests/Inflow30MinTests"
            model: type[InflowTest] = Inflow30MinTest
        elif kind == "Regular":
            url = "InterventionTests/InflowTests"
            model = InflowTest
        else:
            raise ValueError(f"Invalid kind: {kind}.")

        data = self._api.get(url=url)

        if data.status_code == 204:
            return []

        return [model.model_validate(row) for row in data.json()]

    def get_pressure_tests(self) -> list[PressureTest]:
        """
        Get `PressureTest` objects.

        Returns
        -------
        list[PressureTest]

        """
        data = self._api.get(url="InterventionTests/PressureTests")

        if data.status_code == 204:
            return []

        return [PressureTest.model_validate(row) for row in data.json()]

    def get_xmt_leak_rate_tests(self, kind: Literal["HMV", "LMV"]) -> list[LeakRateTest]:
        """
        Get `PressureTest` objects.

        Returns
        -------
        list[PressureTest]

        """
        if kind == "HMV":
            url = "InterventionTests/XmtHmvApiLeakRateTests"
        elif kind == "LMV":
            url = "InterventionTests/XmtLmvApiLeakRateTests"
        else:
            raise ValueError(f"Invalid kind: {kind}.")

        data = self._api.get(url=url)

        if data.status_code == 204:
            return []

        return [LeakRateTest.model_validate(row) for row in data.json()]
