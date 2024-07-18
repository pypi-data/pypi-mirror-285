from datetime import datetime
from typing import Optional, Union, overload

from ....logging import logger
from ....v1.data_schemas import (
    Channel,
    ChannelDataRangeRequest,
    ChannelDataRequest,
    ChannelDataResponse,
    ChannelRange,
    FirstAndLastDataPoint,
    Log,
    Run,
)
from ..api import IDEXApi
from .utils import url_encode_id


class Channels:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, log: Union[Log, str], include_soft_delete: Optional[bool] = False) -> list[Channel]: ...
    @overload
    def get(self, *, run: Union[Run, str], include_soft_delete: Optional[bool] = False) -> list[Channel]: ...

    def get(
        self,
        *,
        log: Optional[Union[Log, str]] = None,
        run: Optional[Union[Run, str]] = None,
        include_soft_delete: Optional[bool] = False,
    ) -> list[Channel]:
        """
        Get `Channel` objects.

        Parameters
        ----------
        log : Optional[Union[Log,str]]
            Log object (or log ID) to get Channel for.
        run : Optional[Union[Run,str]]
            Run object (or run ID) to get Channel for.
        include_soft_delete : Optional[bool] = False
            Include soft deleted records.

        Returns
        -------
        list[Channel]
            The `Channel` objects.

        """
        log_id, run_id = None, None

        if log is not None:
            log_id = log if isinstance(log, str) else log.id
            logger.debug(f"Getting Channels for Log with ID: {log_id}")
            log_id = url_encode_id(log_id)
            data = self._api.get(url=f"Logs/{log_id}/Channels")
        elif run is not None:
            run_id = run if isinstance(run, str) else run.id
            logger.debug(f"Getting Channels for Run with ID: {run_id}")
            run_id = url_encode_id(run_id)
            data = self._api.get(url=f"Runs/{run_id}/Channels")
        else:
            raise TypeError("Either `log` or `run` must be provided.")

        if data.status_code == 204:
            return []

        records = [Channel.model_validate(row) for row in data.json()]
        if log_id is not None:
            for record in records:
                record.log_id = log_id

        if run_id is not None:
            for record in records:
                record.run_id = run_id

        if include_soft_delete:
            return records

        return [rec for rec in records if rec.deleted_date is None]

    def get_ranges(self, channel_ids: list[str]) -> list[ChannelRange]:
        """
        Get `ChannelRange` objects for a list of known channel ids.

        Parameters
        ----------
        channels : Optional[list[Channel]]
            Channel objects to get Ranges for.
        channel_ids : Optional[list[str]]
            Channel IDs to get Ranges for.

        Returns
        -------
        list[ChannelRange]
            The `ChannelRange` objects.

        """
        logger.debug(f"Getting available ranges for Channels with IDs: {', '.join(channel_ids)}.")
        data = self._api.post(url="ChannelData/AvailableRanges", json=channel_ids)
        if data.status_code == 204:
            return []

        return [ChannelRange.model_validate(row) for row in data.json()]

    def get_first_and_last_datapoints(self, *, channels: list[Channel]) -> list[FirstAndLastDataPoint]:
        """
        Get first and last datapoint for all supplied `Channel` objects.

        Parameters
        ----------
        channels: list[Channel]
            The channels to get first and last datapoints for.

        Returns
        -------
        dict[str, ]

        """
        channel_ids = [channel.id for channel in channels]
        data = self._api.post(url="ChannelData/FirstAndLast", json=channel_ids)
        if data.status_code == 204:
            return []

        return [FirstAndLastDataPoint.model_validate(row) for row in data.json()]

    def get_datapoints_by_range(
        self,
        *,
        channels: list[Channel],
        start: datetime,
        end: datetime,
        limit: int,
        include_outside_pts: bool = True,
    ) -> list[ChannelDataResponse]:
        """
        Get datapoints for one time range, for all channels.

        Parameters
        ----------
        channels : list[Channel]
            Channel objects to get Ranges for.
        start : datetime
            The start time for channel data.
        end : datetime
            The end time for channel data.
        limit : int
            The limit of datapoints to retrieve per channel. Must be between 1 and 10_000.
        include_outside_pts : bool = True
            Include outside points.

        Returns
        -------
        list[ChannelDataResponse]
            The `ChannelDataResponse` objects.

        """
        payload = ChannelDataRequest(
            ids=[channel.id for channel in channels],
            start=start,
            end=end,
            limit=limit,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(url="ChannelData/GetDataRange", data=payload.model_dump_json(by_alias=True))

        if data.status_code == 204:
            return []

        return [ChannelDataResponse.model_validate(row) for row in data.json()]

    def get_datapoints_for_channels(
        self,
        *,
        channels: list[Channel],
        limit: int,
        include_outside_pts: bool = True,
    ) -> list[ChannelDataResponse]:
        """
        Get `ChannelDataResponse` objects.

        Parameters
        ----------
        channels : list[Channel]
            `Channel` objects to get datapoints for.
        limit : int
            The limit of datapoints to retrieve per channel. Must be between 1 and 10_000.
        include_outside_pts : bool = True
            Include outside points.

        Returns
        -------
        list[ChannelDataResponse]
            The `ChannelDataResponse` objects.

        """
        payload = ChannelDataRangeRequest(
            channels=[channel.data_range for channel in channels],
            limit=limit,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(
            url="ChannelData/GetChannelDataRange",
            data=payload.model_dump_json(by_alias=True),
        )

        if data.status_code == 204:
            return []

        return [ChannelDataResponse.model_validate(row) for row in data.json()]

    def get_datapoints_for_channels_compressed(
        self,
        *,
        channels: list[Channel],
        limit: int,
        include_outside_pts: bool = True,
    ) -> bytes:
        """
        Get compressed `ChannelDataResponse` objects as bytes.

        Response is compressed using Brotli compression and MessagePack.

        NOTE: Currently responds with an undocumented 406 error.

        Parameters
        ----------
        channels : list[Channel]
            `Channel` objects to get datapoints for.
        limit : int
            The limit of datapoints to retrieve per channel. Must be between 1 and 10_000.
        include_outside_pts : bool = True
            Include outside points.

        Returns
        -------
        bytes
            The Brotli-compressed and MessagePacked `ChannelDataResponse` objects.

        """
        payload = ChannelDataRangeRequest(
            channels=[channel.data_range for channel in channels],
            limit=limit,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(
            url="ChannelData/GetCompressedChannelDataRange",
            data=payload.model_dump_json(by_alias=True),
            headers={
                "Accept": "application/octet-stream",
                "Accept-Encoding": "br, *",  # Specifying Brotli doesn't work.
            },
        )

        return data.content
