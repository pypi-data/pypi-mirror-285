from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMoveItemidOrganizationIdBody")


@_attrs_define
class PostMoveItemidOrganizationIdBody:
    """
    Attributes:
        array (Union[Unset, List[str]]):
    """

    array: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        array: Union[Unset, List[str]] = UNSET
        if not isinstance(self.array, Unset):
            array = self.array

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if array is not UNSET:
            field_dict["array"] = array

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        array = cast(List[str], d.pop("array", UNSET))

        post_move_itemid_organization_id_body = cls(
            array=array,
        )

        post_move_itemid_organization_id_body.additional_properties = d
        return post_move_itemid_organization_id_body

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
