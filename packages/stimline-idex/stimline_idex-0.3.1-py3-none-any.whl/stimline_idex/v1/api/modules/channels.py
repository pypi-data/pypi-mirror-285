from datetime import datetime
from typing import Optional, overload

from ....logging import logger
from ....v1.data_schemas import (
    Channel,
    ChannelDataRangeRequest,
    ChannelDataRequest,
    ChannelDataResponse,
    ChannelRange,
    Log,
    Run,
)
from ..api import IDEXApi
from .utils import url_encode_id


class Channels:
    def __init__(self, api: IDEXApi) -> None:
        self._api = api

    @overload
    def get(self, *, log: Log, include_soft_delete: Optional[bool] = False) -> list[Channel]: ...
    @overload
    def get(self, *, log_id: str, include_soft_delete: Optional[bool] = False) -> list[Channel]: ...
    @overload
    def get(self, *, run: Run, include_soft_delete: Optional[bool] = False) -> list[Channel]: ...
    @overload
    def get(self, *, run_id: str, include_soft_delete: Optional[bool] = False) -> list[Channel]: ...

    def get(
        self,
        *,
        log: Optional[Log] = None,
        log_id: Optional[str] = None,
        run: Optional[Run] = None,
        run_id: Optional[str] = None,
        include_soft_delete: Optional[bool] = False,
    ) -> list[Channel]:
        """
        Get `Channel` object(s).

        Parameters
        ----------
        log : Optional[Log]
            Log object to get Channel for.
        log_id : Optional[str]
            Log ID to get Channel for.
        run : Optional[Run]
            Run object to get Channel for.
        run_id : Optional[str]
            Run ID to get Channel for.
        include_soft_delete : Optional[bool] = False
            Include soft deleted records.

        Returns
        -------
        list[Channel]
            The `Channel` object(s).

        """
        log_id_, run_id_ = None, None

        if log is not None or log_id is not None:
            log_id_ = log_id if log is None else log.id
            assert log_id_ is not None
            logger.debug(f"Getting Channels for Log with ID: {id}")
            log_id_ = url_encode_id(log_id_)
            data = self._api.get(url=f"Logs/{log_id_}/Channels")

        elif run is not None or run_id is not None:
            run_id_ = run_id if run is None else run.id
            assert run_id_ is not None
            logger.debug(f"Getting Channels for Run with ID: {id}")
            run_id_ = url_encode_id(run_id_)
            data = self._api.get(url=f"Runs/{run_id_}/Channels")

        else:
            raise TypeError("Either `log`, `log_id`, `run` or `run_id` must be provided.")

        if data.status_code == 204:
            return []

        records = [Channel.model_validate(row) for row in data.json()]

        if log_id_ is not None:
            for record in records:
                record.log_id = log_id_

        if run_id_ is not None:
            for record in records:
                record.run_id = run_id_

        if include_soft_delete:
            return records

        return [rec for rec in records if rec.deleted_date is None]

    @overload
    def get_available_ranges(self, *, channels: list[Channel]) -> list[ChannelRange]: ...
    @overload
    def get_available_ranges(self, *, channel_ids: list[str]) -> list[ChannelRange]: ...

    def get_available_ranges(
        self,
        *,
        channels: Optional[list[Channel]] = None,
        channel_ids: Optional[list[str]] = None,
    ) -> list[ChannelRange]:
        """
        Get `ChannelRange` object(s).

        Parameters
        ----------
        channels : Optional[list[Channel]]
            Channel objects to get Ranges for.
        channel_ids : Optional[list[str]]
            Channel IDs to get Ranges for.

        Returns
        -------
        list[ChannelRange]
            The `ChannelRange` object(s).

        """
        if channels is not None:
            ids = [channel.id for channel in channels]
        elif channel_ids is not None:
            ids = channel_ids
        else:
            raise TypeError("Either `channels` or `channel_ids` must be provided.")

        logger.debug(f"Getting available ranges for Channels with IDs: {', '.join(ids)}.")

        data = self._api.post(url="ChannelData/AvailableRanges", json=ids)

        if data.status_code == 204:
            return []

        return [ChannelRange.model_validate(row) for row in data.json()]

    @overload
    def get_data_range(
        self,
        *,
        channels: list[Channel],
        start_time: datetime,
        end_time: datetime,
        limit: int,
        ignore_unknown_ids: bool = True,
        include_outside_pts: bool = True,
    ) -> list[ChannelDataResponse]: ...
    @overload
    def get_data_range(
        self,
        *,
        channel_ids: list[str],
        start_time: datetime,
        end_time: datetime,
        limit: int,
        ignore_unknown_ids: bool = True,
        include_outside_pts: bool = True,
    ) -> list[ChannelDataResponse]: ...

    def get_data_range(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        limit: int,
        ignore_unknown_ids: bool = True,
        include_outside_pts: bool = True,
        channels: Optional[list[Channel]] = None,
        channel_ids: Optional[list[str]] = None,
    ) -> list[ChannelDataResponse]:
        """
        Get `ChannelDataResponse` object(s).

        Parameters
        ----------
        channels : Optional[list[Channel]]
            Channel objects to get Ranges for.
        channel_ids : Optional[list[str]]
            Channel IDs to get Ranges for.
        start_time : datetime
            The start time for channel data.
        end_time : datetime
            The end time for channel data.
        limit : int
            The limit of datapoints to retrieve per channel.
        ignore_unknown_ids : bool = True
            Ignore unknown channel IDs.
        include_outside_pts : bool = True
            Include outside points.


        Returns
        -------
        list[ChannelDataResponse]
            The `ChannelDataResponse` object(s).

        """
        payload = ChannelDataRequest(
            ids=[channel.id for channel in channels] if channels is not None else channel_ids,  # type: ignore
            start=start_time,
            end=end_time,
            limit=limit,
            ignore_unknown_ids=ignore_unknown_ids,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(url="ChannelData/GetDataRange", data=payload.model_dump_json(by_alias=True))

        if data.status_code == 204:
            return []

        return [ChannelDataResponse.model_validate(row) for row in data.json()]

    def get_channel_datapoints(
        self,
        *,
        channel_ranges: list[ChannelRange],
        limit: int,
        ignore_unknown_ids: bool = True,
        include_outside_pts: bool = True,
    ) -> bytes:
        """
        Get `ChannelDataResponse` object(s).

        Parameters
        ----------
        channels : list[ChannelRange]
            Channel objects to get Ranges for.
        limit : int
            The limit of datapoints to retrieve per channel.
        ignore_unknown_ids : bool = True
            Ignore unknown channel IDs.
        include_outside_pts : bool = True
            Include outside points.


        Returns
        -------
        list[ChannelDataResponse]
            The `ChannelDataResponse` object(s).

        """
        payload = ChannelDataRangeRequest(
            channels=channel_ranges,
            limit=limit,
            ignore_unknown_ids=ignore_unknown_ids,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(
            url="ChannelData/GetChannelDataRange",
            data=payload.model_dump_json(by_alias=True),
        )

        if data.status_code == 204:
            return b""

        return data.content

    def get_compressed_channel_datapoints(
        self,
        *,
        channel_ranges: list[ChannelRange],
        limit: int,
        ignore_unknown_ids: bool = True,
        include_outside_pts: bool = True,
    ) -> bytes:
        """
        Get compressed `ChannelDataResponse` objects as bytes.

        Response is compressed using Brotli compression and MessagePack.

        NOTE: Currently responds with an undocumented 406 error.

        Parameters
        ----------
        channels : list[ChannelRange]
            Channel objects to get Ranges for.
        limit : int
            The limit of datapoints to retrieve per channel.
        ignore_unknown_ids : bool = True
            Ignore unknown channel IDs.
        include_outside_pts : bool = True
            Include outside points.


        Returns
        -------
        bytes
            The compressed `ChannelDataResponse` objects.

        """
        payload = ChannelDataRangeRequest(
            channels=channel_ranges,
            limit=limit,
            ignore_unknown_ids=ignore_unknown_ids,
            include_outside_points=include_outside_pts,
        )

        data = self._api.post(
            url="ChannelData/GetCompressedChannelDataRange",
            data=payload.model_dump_json(by_alias=True),
            headers={"Accept": "application/octet-stream"},
        )

        if data.status_code == 204:
            return b""

        return data.content
