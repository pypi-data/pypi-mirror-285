import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status_data_template_status import StatusDataTemplateStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusDataTemplate")


@_attrs_define
class StatusDataTemplate:
    """
    Attributes:
        last_sync (Union[Unset, datetime.datetime]):
        server_url (Union[Unset, str]):
        status (Union[Unset, StatusDataTemplateStatus]):
        user_email (Union[Unset, str]):
        user_id (Union[Unset, str]):
    """

    last_sync: Union[Unset, datetime.datetime] = UNSET
    server_url: Union[Unset, str] = UNSET
    status: Union[Unset, StatusDataTemplateStatus] = UNSET
    user_email: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        last_sync: Union[Unset, str] = UNSET
        if not isinstance(self.last_sync, Unset):
            last_sync = self.last_sync.isoformat()

        server_url = self.server_url

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        user_email = self.user_email

        user_id = self.user_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if last_sync is not UNSET:
            field_dict["lastSync"] = last_sync
        if server_url is not UNSET:
            field_dict["serverUrl"] = server_url
        if status is not UNSET:
            field_dict["status"] = status
        if user_email is not UNSET:
            field_dict["userEmail"] = user_email
        if user_id is not UNSET:
            field_dict["userID"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _last_sync = d.pop("lastSync", UNSET)
        last_sync: Union[Unset, datetime.datetime]
        if isinstance(_last_sync, Unset):
            last_sync = UNSET
        else:
            last_sync = isoparse(_last_sync)

        server_url = d.pop("serverUrl", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, StatusDataTemplateStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = StatusDataTemplateStatus(_status)

        user_email = d.pop("userEmail", UNSET)

        user_id = d.pop("userID", UNSET)

        status_data_template = cls(
            last_sync=last_sync,
            server_url=server_url,
            status=status,
            user_email=user_email,
            user_id=user_id,
        )

        status_data_template.additional_properties = d
        return status_data_template

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
