from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.uris import Uris


T = TypeVar("T", bound="ItemLogin")


@_attrs_define
class ItemLogin:
    """
    Attributes:
        password (Union[Unset, str]):
        totp (Union[Unset, str]):
        uris (Union[Unset, Uris]):
        username (Union[Unset, str]):
    """

    password: Union[Unset, str] = UNSET
    totp: Union[Unset, str] = UNSET
    uris: Union[Unset, "Uris"] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        password = self.password

        totp = self.totp

        uris: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.uris, Unset):
            uris = self.uris.to_dict()

        username = self.username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if password is not UNSET:
            field_dict["password"] = password
        if totp is not UNSET:
            field_dict["totp"] = totp
        if uris is not UNSET:
            field_dict["uris"] = uris
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.uris import Uris

        d = src_dict.copy()
        password = d.pop("password", UNSET)

        totp = d.pop("totp", UNSET)

        _uris = d.pop("uris", UNSET)
        uris: Union[Unset, Uris]
        if isinstance(_uris, Unset):
            uris = UNSET
        else:
            uris = Uris.from_dict(_uris)

        username = d.pop("username", UNSET)

        item_login = cls(
            password=password,
            totp=totp,
            uris=uris,
            username=username,
        )

        item_login.additional_properties = d
        return item_login

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
