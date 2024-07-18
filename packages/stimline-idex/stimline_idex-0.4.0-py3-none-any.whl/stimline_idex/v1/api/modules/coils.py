from ....v1.data_schemas import Coil
from ..api import IDEXApi


class Coils:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    def get(self, manufacturer: str) -> list[Coil]:
        """
        Get `Coil` object(s).

        Parameters
        ----------
        manufacturer : str
            Manufacturer to retrieve `Coil` objects for.

        Returns
        -------
        list[Coil]
            The `Coil` object(s).

        """
        data = self._api.get(url=f"Coils/{manufacturer}")

        return [Coil.model_validate(d) for d in data.json()]
