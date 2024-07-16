"""Some helper utils relevant across modules."""

from typing import Any
from urllib.parse import quote

from ....logging import logger


def url_encode_id(id: str) -> str:
    """
    Encode a non-UUID ID for use in a URL.

    >>> id = "1/3-K-1"
    >>> assert url_encode_id(id) == "1%2F3-K-1"
    """
    return quote(id, safe="")


def _check_select(select: list[str]) -> list[str]:
    """Ensure that select clause includes the `id` field."""
    if "id" not in select:
        select.append("id")
        logger.debug("Adding `id` to select clause.")
    return select


def create_params(**kwargs: dict[str, Any]):
    """
    Create params for a query type request.

    Removes the following keys from the returned kwargs:
    - filter
    - select
    - top
    - skip
    - order_by
    - include_soft_delete

    Returns
    -------
    tuple[dict[str, Any], dict[str, Any]]
        kwargs, params

    Supports
    --------
    filter : str
        Filter the results.
    select : list[str]
        Select columns to retrieve from output.
    top : int
        Limit the number of results returned.
    skip : int
        Skip the first N results.
    order_by : str
        Order the results by columns.

    """
    params: dict[str, Any] = {}
    kwargs, filter = _get_filter(**kwargs)

    if filter:
        params["$filter"] = filter

    if "select" in kwargs:
        select = kwargs.pop("select")

        for v in select:
            if not isinstance(v, str):  # type: ignore
                raise TypeError(f"The `select` clause must be a list of strings, not {type(select)}.")

        select = _check_select(select)  # type: ignore
        params["$select"] = ",".join(select)

    if "top" in kwargs:
        params["$top"] = kwargs.pop("top")

    if "skip" in kwargs:
        params["$skip"] = kwargs.pop("skip")

    if "order_by" in kwargs:
        params["$orderby"] = kwargs.pop("order_by")

    return kwargs, params


def _get_filter(**kwargs: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Create filter statement for a query type request.

    Removes the following keys from the returned kwargs:
    - include_soft_delete
    - filter

    Returns
    -------
    tuple[dict[str, Any], str]
        kwargs, filter

    """
    include_soft_delete = False
    filter = ""

    if "include_soft_delete" in kwargs:
        include_soft_delete = kwargs.pop("include_soft_delete")  # type: ignore
        logger.debug("Query setting `include_soft_delete`: %s", include_soft_delete)

    if "filter" in kwargs:
        filter = str(kwargs.pop("filter"))
        if "deleteddate" in filter.lower() and not include_soft_delete:
            raise ValueError("Cannot filter on `deletedDate` without setting `include_soft_delete` kwarg to `True`.")

    if not include_soft_delete and filter:
        filter = f"({filter}) and deletedDate eq null"
    elif not include_soft_delete:
        filter = "deletedDate eq null"

    logger.debug("Query setting `filter`: '%s'", filter)
    return kwargs, filter  # type: ignore


def log_unused_kwargs(**kwargs: Any):
    """Log any unused kwargs."""
    if kwargs:
        unused = kwargs.keys()
        logger.debug("Found unused kwargs: %s", ",".join(unused))
