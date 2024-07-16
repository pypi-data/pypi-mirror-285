""" Contains some shared types for properties """
from collections.abc import MutableMapping
from http import HTTPStatus
from typing import BinaryIO
from typing import Generic
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import TypeVar

from attrs import define


class Unset:
    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "Unset"


UNSET: Unset = Unset()

FileJsonType = Tuple[Optional[str], BinaryIO, Optional[str]]


@define
class File:
    """Contains information for file uploads"""

    payload: BinaryIO
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    def to_tuple(self) -> FileJsonType:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


T = TypeVar("T")


@define
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: HTTPStatus
    content: bytes
    headers: MutableMapping[str, str]
    parsed: T


__all__ = ["File", "Response", "FileJsonType"]
