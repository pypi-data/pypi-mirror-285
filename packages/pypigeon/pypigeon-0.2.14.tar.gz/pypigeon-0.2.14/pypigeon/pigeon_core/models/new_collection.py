from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.new_collection_metadata import NewCollectionMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="NewCollection")


@_attrs_define
class NewCollection:
    """New collection request

    Attributes:
        description (str): The collection's full description
        name (str): The collection's short human-readable name
        account_id (Union[Unset, str]): The account into which the collection should be created
        metadata (Union[Unset, NewCollectionMetadata]): Arbitrary user-defined metadata, key-value pairs
    """

    description: str
    name: str
    account_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "NewCollectionMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        name = self.name
        account_id = self.account_id
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "name": name,
            }
        )
        if account_id is not UNSET:
            field_dict["account_id"] = account_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewCollection` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        name = d.pop("name")

        account_id = d.pop("account_id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, NewCollectionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = NewCollectionMetadata.from_dict(_metadata)

        new_collection = cls(
            description=description,
            name=name,
            account_id=account_id,
            metadata=metadata,
        )

        return new_collection
