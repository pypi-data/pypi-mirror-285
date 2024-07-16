from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.update_collection_metadata import UpdateCollectionMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="UpdateCollection")


@_attrs_define
class UpdateCollection:
    """Update core collection properties

    Attributes:
        account_id (Union[Unset, str]): The account into which the collection should be moved
        description (Union[Unset, str]): The collection's full description
        metadata (Union[Unset, UpdateCollectionMetadata]): Arbitrary user-defined metadata, key-value pairs
        name (Union[Unset, str]): The collection's short human-readable name
    """

    account_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "UpdateCollectionMetadata"] = UNSET
    name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        description = self.description
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if account_id is not UNSET:
            field_dict["account_id"] = account_id
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UpdateCollection` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id", UNSET)

        description = d.pop("description", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, UpdateCollectionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateCollectionMetadata.from_dict(_metadata)

        name = d.pop("name", UNSET)

        update_collection = cls(
            account_id=account_id,
            description=description,
            metadata=metadata,
            name=name,
        )

        return update_collection
