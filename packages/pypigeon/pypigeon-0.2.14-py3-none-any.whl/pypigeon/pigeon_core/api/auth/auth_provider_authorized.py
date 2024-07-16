"""Handles returning requests from OAuth services during sign-in."""
from http import HTTPStatus
from typing import Any
from typing import cast
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.auth_provider_authorized_provider import AuthProviderAuthorizedProvider
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    provider: AuthProviderAuthorizedProvider,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/auth/{provider}/authorized".format(
            provider=provider,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Any, ServerError]:
    if response.status_code == HTTPStatus.FOUND:
        response_302 = cast(Any, {"attribute": "None", "return_type": "None"})
        return response_302
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ServerError.from_dict(response.json())

        return response_404

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    provider: AuthProviderAuthorizedProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ServerError]]:
    """Handles returning requests from OAuth services during sign-in.

    Args:
        provider (AuthProviderAuthorizedProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider: AuthProviderAuthorizedProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Any]:
    """Handles returning requests from OAuth services during sign-in.

    Args:
        provider (AuthProviderAuthorizedProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = sync_detailed(
        provider=provider,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    provider: AuthProviderAuthorizedProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ServerError]]:
    """Handles returning requests from OAuth services during sign-in.

    Args:
        provider (AuthProviderAuthorizedProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider: AuthProviderAuthorizedProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Any]:
    """Handles returning requests from OAuth services during sign-in.

    Args:
        provider (AuthProviderAuthorizedProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = await asyncio_detailed(
        provider=provider,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
