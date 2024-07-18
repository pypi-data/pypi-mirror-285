from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LockunlockSuccessData")


@_attrs_define
class LockunlockSuccessData:
    """
    Attributes:
        message (Union[Unset, str]):
        no_color (Union[Unset, bool]):
        object_ (Union[Unset, str]):
        title (Union[Unset, str]):
    """

    message: Union[Unset, str] = UNSET
    no_color: Union[Unset, bool] = UNSET
    object_: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        message = self.message

        no_color = self.no_color

        object_ = self.object_

        title = self.title

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if no_color is not UNSET:
            field_dict["noColor"] = no_color
        if object_ is not UNSET:
            field_dict["object"] = object_
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message", UNSET)

        no_color = d.pop("noColor", UNSET)

        object_ = d.pop("object", UNSET)

        title = d.pop("title", UNSET)

        lockunlock_success_data = cls(
            message=message,
            no_color=no_color,
            object_=object_,
            title=title,
        )

        lockunlock_success_data.additional_properties = d
        return lockunlock_success_data

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
