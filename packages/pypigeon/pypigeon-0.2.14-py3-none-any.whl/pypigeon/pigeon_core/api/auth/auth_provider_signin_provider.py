"""Starts a provider-specific sign-in flow."""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.auth_provider_signin_provider_provider import (
    AuthProviderSigninProviderProvider,
)
from ...models.auth_provider_signin_provider_response_200 import (
    AuthProviderSigninProviderResponse200,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    provider: AuthProviderSigninProviderProvider,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/auth/signin/{provider}".format(
            provider=provider,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[AuthProviderSigninProviderResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuthProviderSigninProviderResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ServerError.from_dict(response.json())

        return response_404

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AuthProviderSigninProviderResponse200, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    provider: AuthProviderSigninProviderProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AuthProviderSigninProviderResponse200, ServerError]]:
    """Starts a provider-specific sign-in flow.

    Args:
        provider (AuthProviderSigninProviderProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AuthProviderSigninProviderResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider: AuthProviderSigninProviderProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[AuthProviderSigninProviderResponse200]:
    """Starts a provider-specific sign-in flow.

    Args:
        provider (AuthProviderSigninProviderProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AuthProviderSigninProviderResponse200]
    """

    response = sync_detailed(
        provider=provider,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    provider: AuthProviderSigninProviderProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AuthProviderSigninProviderResponse200, ServerError]]:
    """Starts a provider-specific sign-in flow.

    Args:
        provider (AuthProviderSigninProviderProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AuthProviderSigninProviderResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        provider=provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider: AuthProviderSigninProviderProvider,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[AuthProviderSigninProviderResponse200]:
    """Starts a provider-specific sign-in flow.

    Args:
        provider (AuthProviderSigninProviderProvider):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AuthProviderSigninProviderResponse200]
    """

    response = await asyncio_detailed(
        provider=provider,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
