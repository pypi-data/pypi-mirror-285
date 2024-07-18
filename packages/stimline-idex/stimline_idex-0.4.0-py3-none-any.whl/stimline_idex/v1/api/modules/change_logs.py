from ....v1.data_schemas import ChangeLog
from ..api import IDEXApi


class ChangeLogs:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    def get_max_anchor(self) -> int:
        """
        Get change log max anchor.

        Returns
        -------
        int
            The maximum anchor value.

        """
        return self._api.get(url="ChangeLog/MaxAnchor").json()

    def get_changelogs(self, anchor_larger_than: int) -> list[ChangeLog]:
        """
        Get `ChangeLog` objects.

        Parameters
        ----------
        anchor_larger_than : int
            The anchor value for which returned `ChangeLog` objects should have a larger anchor value.

        Returns
        -------
        list[ChangeLog]
            The `ChangeLog` objects.

        """
        data = self._api.get(url=f"ChangeLog/Anchor/{anchor_larger_than}")

        return [ChangeLog.model_validate(d) for d in data.json()]
