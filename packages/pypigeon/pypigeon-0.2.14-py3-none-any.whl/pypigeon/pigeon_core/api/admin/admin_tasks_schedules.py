"""List scheduled tasks"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...models.tasks_schedules import TasksSchedules
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/admin/tasks/schedules",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, TasksSchedules]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TasksSchedules.from_dict(response.json())

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
) -> Response[Union[ServerError, TasksSchedules]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, TasksSchedules]]:
    """List scheduled tasks

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, TasksSchedules]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Union[TasksSchedules]:
    """List scheduled tasks

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[TasksSchedules]
    """

    response = sync_detailed(
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, TasksSchedules]]:
    """List scheduled tasks

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, TasksSchedules]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Union[TasksSchedules]:
    """List scheduled tasks

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[TasksSchedules]
    """

    response = await asyncio_detailed(
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
