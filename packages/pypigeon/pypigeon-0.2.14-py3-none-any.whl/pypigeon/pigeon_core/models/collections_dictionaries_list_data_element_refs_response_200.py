from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_reference import DataElementReference
from ..models.pagination import Pagination


T = TypeVar("T", bound="CollectionsDictionariesListDataElementRefsResponse200")


@_attrs_define
class CollectionsDictionariesListDataElementRefsResponse200:
    """CollectionsDictionariesListDataElementRefsResponse200 model

    Attributes:
        elements (List['DataElementReference']):
        pagination (Pagination):
    """

    elements: List["DataElementReference"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        elements = []
        for elements_item_data in self.elements:
            elements_item = elements_item_data.to_dict()
            elements.append(elements_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "elements": elements,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsDictionariesListDataElementRefsResponse200` from a dict"""
        d = src_dict.copy()
        elements = []
        _elements = d.pop("elements")
        for elements_item_data in _elements:
            elements_item = DataElementReference.from_dict(elements_item_data)

            elements.append(elements_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        collections_dictionaries_list_data_element_refs_response_200 = cls(
            elements=elements,
            pagination=pagination,
        )

        return collections_dictionaries_list_data_element_refs_response_200
