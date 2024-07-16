from typing import Any
from typing import cast
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.column_schema_type import ColumnSchemaType
from ..models.item_column_enum_map import ItemColumnEnumMap
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="ItemColumn")


@_attrs_define
class ItemColumn:
    """ItemColumn model

    Attributes:
        name (str):
        data_element_ref (Union[Unset, str]): A URL referencing a specific data element (and optional
            version) within a PDD, CDE set, or other data element
            source.
        enum_map (Union[Unset, ItemColumnEnumMap]): When provided, defines the mapping between the values
            present in the column and the permissible values defined
            in the referenced data element.
        represents_pv (Union[Unset, int, str]): When provided, this indicates that this column
            represents one of the permissible values from the
            referenced data element. The desired permissible value
            must be placed in this field, and the column type must
            be either 'Categorical' or 'Boolean'.
        type (Union[Unset, ColumnSchemaType]):
    """

    name: str
    data_element_ref: Union[Unset, str] = UNSET
    enum_map: Union[Unset, "ItemColumnEnumMap"] = UNSET
    represents_pv: Union[Unset, int, str] = UNSET
    type: Union[Unset, ColumnSchemaType] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        name = self.name
        data_element_ref = self.data_element_ref
        enum_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.enum_map, Unset):
            enum_map = self.enum_map.to_dict()
        represents_pv: Union[Unset, int, str]
        if isinstance(self.represents_pv, Unset):
            represents_pv = UNSET
        else:
            represents_pv = self.represents_pv
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if data_element_ref is not UNSET:
            field_dict["data_element_ref"] = data_element_ref
        if enum_map is not UNSET:
            field_dict["enum_map"] = enum_map
        if represents_pv is not UNSET:
            field_dict["represents_pv"] = represents_pv
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ItemColumn` from a dict"""
        d = src_dict.copy()
        name = d.pop("name")

        data_element_ref = d.pop("data_element_ref", UNSET)

        _enum_map = d.pop("enum_map", UNSET)
        enum_map: Union[Unset, ItemColumnEnumMap]
        if isinstance(_enum_map, Unset):
            enum_map = UNSET
        else:
            enum_map = ItemColumnEnumMap.from_dict(_enum_map)

        def _parse_represents_pv(data: object) -> Union[Unset, int, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int, str], data)

        represents_pv = _parse_represents_pv(d.pop("represents_pv", UNSET))

        _type = d.pop("type", UNSET)
        type: Union[Unset, ColumnSchemaType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = ColumnSchemaType(_type)

        item_column = cls(
            name=name,
            data_element_ref=data_element_ref,
            enum_map=enum_map,
            represents_pv=represents_pv,
            type=type,
        )

        return item_column
