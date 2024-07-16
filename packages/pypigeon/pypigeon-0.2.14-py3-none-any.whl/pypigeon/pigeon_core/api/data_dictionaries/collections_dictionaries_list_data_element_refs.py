"""Retrieve data element references from a data dictionary"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_dictionaries_list_data_element_refs_response_200 import (
    CollectionsDictionariesListDataElementRefsResponse200,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    item_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/dictionaries/{item_id}/refs".format(
            collection_id=collection_id,
            version_id=version_id,
            item_id=item_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionsDictionariesListDataElementRefsResponse200.from_dict(
            response.json()
        )

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ServerError.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]
]:
    """Retrieve data element references from a data dictionary

    TODO

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
) -> Union[CollectionsDictionariesListDataElementRefsResponse200]:
    """Retrieve data element references from a data dictionary

    TODO

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsDictionariesListDataElementRefsResponse200]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]
]:
    """Retrieve data element references from a data dictionary

    TODO

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsDictionariesListDataElementRefsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
) -> Union[CollectionsDictionariesListDataElementRefsResponse200]:
    """Retrieve data element references from a data dictionary

    TODO

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsDictionariesListDataElementRefsResponse200]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
