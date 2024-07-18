from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response


def _get_kwargs(
    id: str,
    *,
    itemid: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["itemid"] = itemid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/object/attachment/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    itemid: str,
) -> Response[Any]:
    """Retrieve an attachment.

     Retreive an attachment by specifying the attachment id (e.g. `o4lrz575u84koanvu9f5gqv9a9ab92gf`) in
    the path and item id (e.g. `ba624b21-1c8a-43b3-a713-ae0000eabdec`) as a query parameter.<br><br>If
    you're retrieving any file type other than plaintext, we recommend posting the request through a
    browser window for immediate download.

    Args:
        id (str):
        itemid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        itemid=itemid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    itemid: str,
) -> Response[Any]:
    """Retrieve an attachment.

     Retreive an attachment by specifying the attachment id (e.g. `o4lrz575u84koanvu9f5gqv9a9ab92gf`) in
    the path and item id (e.g. `ba624b21-1c8a-43b3-a713-ae0000eabdec`) as a query parameter.<br><br>If
    you're retrieving any file type other than plaintext, we recommend posting the request through a
    browser window for immediate download.

    Args:
        id (str):
        itemid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        itemid=itemid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
