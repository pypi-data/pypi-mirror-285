from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.uris_match import UrisMatch
from ..types import UNSET, Unset

T = TypeVar("T", bound="Uris")


@_attrs_define
class Uris:
    """
    Attributes:
        match (Union[Unset, UrisMatch]):
        uri (Union[Unset, str]):
    """

    match: Union[Unset, UrisMatch] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        match: Union[Unset, int] = UNSET
        if not isinstance(self.match, Unset):
            match = self.match.value

        uri = self.uri

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match is not UNSET:
            field_dict["match"] = match
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _match = d.pop("match", UNSET)
        match: Union[Unset, UrisMatch]
        if isinstance(_match, Unset):
            match = UNSET
        else:
            match = UrisMatch(_match)

        uri = d.pop("uri", UNSET)

        uris = cls(
            match=match,
            uri=uri,
        )

        uris.additional_properties = d
        return uris

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
