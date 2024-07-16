from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collections_items_create_item_json_new_item_request_content_checksum import (
    CollectionsItemsCreateItemJsonNewItemRequestContentChecksum,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsItemsCreateItemJsonNewItemRequestContent")


@_attrs_define
class CollectionsItemsCreateItemJsonNewItemRequestContent:
    """If uploading a small file, the contents can be provided.

    Attributes:
        data (str): File content, either plain text or base-64 encoded.
        checksum (Union[Unset, CollectionsItemsCreateItemJsonNewItemRequestContentChecksum]):
        is_base_64_encoded (Union[Unset, bool]): True if the data has been base-64 encoded. Default: False.
    """

    data: str
    checksum: Union[
        Unset, "CollectionsItemsCreateItemJsonNewItemRequestContentChecksum"
    ] = UNSET
    is_base_64_encoded: Union[Unset, bool] = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        data = self.data
        checksum: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.checksum, Unset):
            checksum = self.checksum.to_dict()
        is_base_64_encoded = self.is_base_64_encoded

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
            }
        )
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if is_base_64_encoded is not UNSET:
            field_dict["isBase64Encoded"] = is_base_64_encoded

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsCreateItemJsonNewItemRequestContent` from a dict"""
        d = src_dict.copy()
        data = d.pop("data")

        _checksum = d.pop("checksum", UNSET)
        checksum: Union[
            Unset, CollectionsItemsCreateItemJsonNewItemRequestContentChecksum
        ]
        if isinstance(_checksum, Unset):
            checksum = UNSET
        else:
            checksum = (
                CollectionsItemsCreateItemJsonNewItemRequestContentChecksum.from_dict(
                    _checksum
                )
            )

        is_base_64_encoded = d.pop("isBase64Encoded", UNSET)

        collections_items_create_item_json_new_item_request_content = cls(
            data=data,
            checksum=checksum,
            is_base_64_encoded=is_base_64_encoded,
        )

        return collections_items_create_item_json_new_item_request_content
