from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_authentication_additional_property_type_0_type import (
    SystemConfigurationAuthenticationAdditionalPropertyType0Type,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationAuthenticationAdditionalPropertyType0")


@_attrs_define
class SystemConfigurationAuthenticationAdditionalPropertyType0:
    """SystemConfigurationAuthenticationAdditionalPropertyType0 model

    Attributes:
        enabled (Union[Unset, bool]):  Default: True.
        type (Union[Unset, SystemConfigurationAuthenticationAdditionalPropertyType0Type]):
    """

    enabled: Union[Unset, bool] = True
    type: Union[
        Unset, SystemConfigurationAuthenticationAdditionalPropertyType0Type
    ] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        enabled = self.enabled
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationAuthenticationAdditionalPropertyType0` from a dict"""
        d = src_dict.copy()
        enabled = d.pop("enabled", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationAuthenticationAdditionalPropertyType0Type]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationAuthenticationAdditionalPropertyType0Type(_type)

        system_configuration_authentication_additional_property_type_0 = cls(
            enabled=enabled,
            type=type,
        )

        system_configuration_authentication_additional_property_type_0.additional_properties = (
            d
        )
        return system_configuration_authentication_additional_property_type_0

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
