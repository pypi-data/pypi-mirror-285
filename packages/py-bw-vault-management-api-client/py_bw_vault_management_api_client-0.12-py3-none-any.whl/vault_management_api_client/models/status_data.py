from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.status_data_object import StatusDataObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.status_data_template import StatusDataTemplate


T = TypeVar("T", bound="StatusData")


@_attrs_define
class StatusData:
    """
    Attributes:
        object_ (Union[Unset, StatusDataObject]):
        template (Union[Unset, StatusDataTemplate]):
    """

    object_: Union[Unset, StatusDataObject] = UNSET
    template: Union[Unset, "StatusDataTemplate"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        template: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.template, Unset):
            template = self.template.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if object_ is not UNSET:
            field_dict["object"] = object_
        if template is not UNSET:
            field_dict["template"] = template

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.status_data_template import StatusDataTemplate

        d = src_dict.copy()
        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, StatusDataObject]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = StatusDataObject(_object_)

        _template = d.pop("template", UNSET)
        template: Union[Unset, StatusDataTemplate]
        if isinstance(_template, Unset):
            template = UNSET
        else:
            template = StatusDataTemplate.from_dict(_template)

        status_data = cls(
            object_=object_,
            template=template,
        )

        status_data.additional_properties = d
        return status_data

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
