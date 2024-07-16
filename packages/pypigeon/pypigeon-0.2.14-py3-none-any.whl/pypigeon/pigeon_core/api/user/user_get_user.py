"""Get metadata on the user"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.federation_user import FederationUser
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    user_name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/user/{user_name}".format(
            user_name=user_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[FederationUser, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = FederationUser.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[FederationUser, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[FederationUser, ServerError]]:
    """Get metadata on the user

    Retrieve the user information

    Args:
        user_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FederationUser, ServerError]]
    """

    kwargs = _get_kwargs(
        user_name=user_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[FederationUser]:
    """Get metadata on the user

    Retrieve the user information

    Args:
        user_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FederationUser]
    """

    response = sync_detailed(
        user_name=user_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    user_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[FederationUser, ServerError]]:
    """Get metadata on the user

    Retrieve the user information

    Args:
        user_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FederationUser, ServerError]]
    """

    kwargs = _get_kwargs(
        user_name=user_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[FederationUser]:
    """Get metadata on the user

    Retrieve the user information

    Args:
        user_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FederationUser]
    """

    response = await asyncio_detailed(
        user_name=user_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
