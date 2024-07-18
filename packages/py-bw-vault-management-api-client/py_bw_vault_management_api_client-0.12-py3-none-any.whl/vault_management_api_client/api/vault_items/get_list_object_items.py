from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: Union[Unset, str] = UNSET,
    collection_id: Union[Unset, str] = UNSET,
    folderid: Union[Unset, str] = UNSET,
    url_query: Union[Unset, str] = UNSET,
    trash: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["organizationId"] = organization_id

    params["collectionId"] = collection_id

    params["folderid"] = folderid

    params["url"] = url_query

    params["trash"] = trash

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/list/object/items",
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
    *,
    client: Union[AuthenticatedClient, Client],
    organization_id: Union[Unset, str] = UNSET,
    collection_id: Union[Unset, str] = UNSET,
    folderid: Union[Unset, str] = UNSET,
    url_query: Union[Unset, str] = UNSET,
    trash: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Retrieve a list of items in your vault.

     Retrieve a list of existing items in your vault. By default, this will return a list of all existing
    items in your vault, however you can specify filters or search terms as query parameters to narrow
    list results.<br><br>Using multiple filters will perform a logical `OR` operation. Using filters
    **and** search terms will perform a logical `AND` operation.

    Args:
        organization_id (Union[Unset, str]):
        collection_id (Union[Unset, str]):
        folderid (Union[Unset, str]):
        url_query (Union[Unset, str]):
        trash (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        collection_id=collection_id,
        folderid=folderid,
        url_query=url_query,
        trash=trash,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    organization_id: Union[Unset, str] = UNSET,
    collection_id: Union[Unset, str] = UNSET,
    folderid: Union[Unset, str] = UNSET,
    url_query: Union[Unset, str] = UNSET,
    trash: Union[Unset, bool] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Retrieve a list of items in your vault.

     Retrieve a list of existing items in your vault. By default, this will return a list of all existing
    items in your vault, however you can specify filters or search terms as query parameters to narrow
    list results.<br><br>Using multiple filters will perform a logical `OR` operation. Using filters
    **and** search terms will perform a logical `AND` operation.

    Args:
        organization_id (Union[Unset, str]):
        collection_id (Union[Unset, str]):
        folderid (Union[Unset, str]):
        url_query (Union[Unset, str]):
        trash (Union[Unset, bool]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        collection_id=collection_id,
        folderid=folderid,
        url_query=url_query,
        trash=trash,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
