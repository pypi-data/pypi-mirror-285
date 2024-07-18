import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.send_template_type import SendTemplateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.send_text import SendText


T = TypeVar("T", bound="SendTemplate")


@_attrs_define
class SendTemplate:
    """
    Attributes:
        deletion_date (Union[Unset, datetime.datetime]):
        disabled (Union[Unset, bool]):
        expiration_date (Union[Unset, datetime.datetime]):
        file (Union[Unset, str]):
        hide_email (Union[Unset, bool]):
        max_access_count (Union[Unset, int]):
        name (Union[Unset, str]):
        notes (Union[Unset, str]):
        password (Union[Unset, str]):
        text (Union[Unset, SendText]):
        type (Union[Unset, SendTemplateType]):
    """

    deletion_date: Union[Unset, datetime.datetime] = UNSET
    disabled: Union[Unset, bool] = UNSET
    expiration_date: Union[Unset, datetime.datetime] = UNSET
    file: Union[Unset, str] = UNSET
    hide_email: Union[Unset, bool] = UNSET
    max_access_count: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    text: Union[Unset, "SendText"] = UNSET
    type: Union[Unset, SendTemplateType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deletion_date: Union[Unset, str] = UNSET
        if not isinstance(self.deletion_date, Unset):
            deletion_date = self.deletion_date.isoformat()

        disabled = self.disabled

        expiration_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_date, Unset):
            expiration_date = self.expiration_date.isoformat()

        file = self.file

        hide_email = self.hide_email

        max_access_count = self.max_access_count

        name = self.name

        notes = self.notes

        password = self.password

        text: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.text, Unset):
            text = self.text.to_dict()

        type: Union[Unset, int] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deletion_date is not UNSET:
            field_dict["deletionDate"] = deletion_date
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date
        if file is not UNSET:
            field_dict["file"] = file
        if hide_email is not UNSET:
            field_dict["hideEmail"] = hide_email
        if max_access_count is not UNSET:
            field_dict["maxAccessCount"] = max_access_count
        if name is not UNSET:
            field_dict["name"] = name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if password is not UNSET:
            field_dict["password"] = password
        if text is not UNSET:
            field_dict["text"] = text
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.send_text import SendText

        d = src_dict.copy()
        _deletion_date = d.pop("deletionDate", UNSET)
        deletion_date: Union[Unset, datetime.datetime]
        if isinstance(_deletion_date, Unset):
            deletion_date = UNSET
        else:
            deletion_date = isoparse(_deletion_date)

        disabled = d.pop("disabled", UNSET)

        _expiration_date = d.pop("expirationDate", UNSET)
        expiration_date: Union[Unset, datetime.datetime]
        if isinstance(_expiration_date, Unset):
            expiration_date = UNSET
        else:
            expiration_date = isoparse(_expiration_date)

        file = d.pop("file", UNSET)

        hide_email = d.pop("hideEmail", UNSET)

        max_access_count = d.pop("maxAccessCount", UNSET)

        name = d.pop("name", UNSET)

        notes = d.pop("notes", UNSET)

        password = d.pop("password", UNSET)

        _text = d.pop("text", UNSET)
        text: Union[Unset, SendText]
        if isinstance(_text, Unset):
            text = UNSET
        else:
            text = SendText.from_dict(_text)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SendTemplateType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SendTemplateType(_type)

        send_template = cls(
            deletion_date=deletion_date,
            disabled=disabled,
            expiration_date=expiration_date,
            file=file,
            hide_email=hide_email,
            max_access_count=max_access_count,
            name=name,
            notes=notes,
            password=password,
            text=text,
            type=type,
        )

        send_template.additional_properties = d
        return send_template

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
