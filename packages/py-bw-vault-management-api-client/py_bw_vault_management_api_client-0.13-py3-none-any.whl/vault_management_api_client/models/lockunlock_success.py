from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lockunlock_success_data import LockunlockSuccessData


T = TypeVar("T", bound="LockunlockSuccess")


@_attrs_define
class LockunlockSuccess:
    """
    Attributes:
        data (Union[Unset, LockunlockSuccessData]):
        success (Union[Unset, bool]):
    """

    data: Union[Unset, "LockunlockSuccessData"] = UNSET
    success: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        success = self.success

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.lockunlock_success_data import LockunlockSuccessData

        d = src_dict.copy()
        _data = d.pop("data", UNSET)
        data: Union[Unset, LockunlockSuccessData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = LockunlockSuccessData.from_dict(_data)

        success = d.pop("success", UNSET)

        lockunlock_success = cls(
            data=data,
            success=success,
        )

        lockunlock_success.additional_properties = d
        return lockunlock_success

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
