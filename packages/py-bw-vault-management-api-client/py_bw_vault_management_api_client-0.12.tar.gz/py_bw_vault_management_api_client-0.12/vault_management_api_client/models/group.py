from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """
    Attributes:
        hide_passwords (Union[Unset, bool]):
        id (Union[Unset, str]):
        read_only (Union[Unset, bool]):
    """

    hide_passwords: Union[Unset, bool] = UNSET
    id: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hide_passwords = self.hide_passwords

        id = self.id

        read_only = self.read_only

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hide_passwords is not UNSET:
            field_dict["hidePasswords"] = hide_passwords
        if id is not UNSET:
            field_dict["id"] = id
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hide_passwords = d.pop("hidePasswords", UNSET)

        id = d.pop("id", UNSET)

        read_only = d.pop("readOnly", UNSET)

        group = cls(
            hide_passwords=hide_passwords,
            id=id,
            read_only=read_only,
        )

        group.additional_properties = d
        return group

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
