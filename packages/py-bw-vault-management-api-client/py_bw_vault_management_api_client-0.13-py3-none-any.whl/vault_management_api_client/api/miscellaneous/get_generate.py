from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    length: Union[Unset, int] = UNSET,
    uppercase: Union[Unset, bool] = UNSET,
    lowercase: Union[Unset, bool] = UNSET,
    number: Union[Unset, bool] = UNSET,
    special: Union[Unset, bool] = UNSET,
    passphrase: Union[Unset, bool] = UNSET,
    words: Union[Unset, int] = UNSET,
    separator: Union[Unset, str] = UNSET,
    capitalize: Union[Unset, bool] = UNSET,
    include_number: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["length"] = length

    params["uppercase"] = uppercase

    params["lowercase"] = lowercase

    params["number"] = number

    params["special"] = special

    params["passphrase"] = passphrase

    params["words"] = words

    params["separator"] = separator

    params["capitalize"] = capitalize

    params["includeNumber"] = include_number

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/generate",
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
    length: Union[Unset, int] = UNSET,
    uppercase: Union[Unset, bool] = UNSET,
    lowercase: Union[Unset, bool] = UNSET,
    number: Union[Unset, bool] = UNSET,
    special: Union[Unset, bool] = UNSET,
    passphrase: Union[Unset, bool] = UNSET,
    words: Union[Unset, int] = UNSET,
    separator: Union[Unset, str] = UNSET,
    capitalize: Union[Unset, bool] = UNSET,
    include_number: Union[Unset, bool] = UNSET,
) -> Response[Any]:
    """Generate a password or passphrase.

     Generate a password or passphrase. By default, `/generate` will generate a 14-character password
    with uppercase characters, lowercase characters, and numbers.

    Args:
        length (Union[Unset, int]):
        uppercase (Union[Unset, bool]):
        lowercase (Union[Unset, bool]):
        number (Union[Unset, bool]):
        special (Union[Unset, bool]):
        passphrase (Union[Unset, bool]):
        words (Union[Unset, int]):
        separator (Union[Unset, str]):
        capitalize (Union[Unset, bool]):
        include_number (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        length=length,
        uppercase=uppercase,
        lowercase=lowercase,
        number=number,
        special=special,
        passphrase=passphrase,
        words=words,
        separator=separator,
        capitalize=capitalize,
        include_number=include_number,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    length: Union[Unset, int] = UNSET,
    uppercase: Union[Unset, bool] = UNSET,
    lowercase: Union[Unset, bool] = UNSET,
    number: Union[Unset, bool] = UNSET,
    special: Union[Unset, bool] = UNSET,
    passphrase: Union[Unset, bool] = UNSET,
    words: Union[Unset, int] = UNSET,
    separator: Union[Unset, str] = UNSET,
    capitalize: Union[Unset, bool] = UNSET,
    include_number: Union[Unset, bool] = UNSET,
) -> Response[Any]:
    """Generate a password or passphrase.

     Generate a password or passphrase. By default, `/generate` will generate a 14-character password
    with uppercase characters, lowercase characters, and numbers.

    Args:
        length (Union[Unset, int]):
        uppercase (Union[Unset, bool]):
        lowercase (Union[Unset, bool]):
        number (Union[Unset, bool]):
        special (Union[Unset, bool]):
        passphrase (Union[Unset, bool]):
        words (Union[Unset, int]):
        separator (Union[Unset, str]):
        capitalize (Union[Unset, bool]):
        include_number (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        length=length,
        uppercase=uppercase,
        lowercase=lowercase,
        number=number,
        special=special,
        passphrase=passphrase,
        words=words,
        separator=separator,
        capitalize=capitalize,
        include_number=include_number,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
