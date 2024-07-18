from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ItemIdentity")


@_attrs_define
class ItemIdentity:
    """
    Attributes:
        address1 (Union[Unset, str]):
        address2 (Union[Unset, str]):
        address3 (Union[Unset, str]):
        city (Union[Unset, str]):
        company (Union[Unset, str]):
        country (Union[Unset, str]):
        email (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        license_number (Union[Unset, str]):
        middle_name (Union[Unset, str]):
        passport_number (Union[Unset, str]):
        phone (Union[Unset, str]):
        postal_code (Union[Unset, str]):
        ssn (Union[Unset, str]):
        state (Union[Unset, str]):
        title (Union[Unset, str]):
        username (Union[Unset, str]):
    """

    address1: Union[Unset, str] = UNSET
    address2: Union[Unset, str] = UNSET
    address3: Union[Unset, str] = UNSET
    city: Union[Unset, str] = UNSET
    company: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    license_number: Union[Unset, str] = UNSET
    middle_name: Union[Unset, str] = UNSET
    passport_number: Union[Unset, str] = UNSET
    phone: Union[Unset, str] = UNSET
    postal_code: Union[Unset, str] = UNSET
    ssn: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        address1 = self.address1

        address2 = self.address2

        address3 = self.address3

        city = self.city

        company = self.company

        country = self.country

        email = self.email

        first_name = self.first_name

        last_name = self.last_name

        license_number = self.license_number

        middle_name = self.middle_name

        passport_number = self.passport_number

        phone = self.phone

        postal_code = self.postal_code

        ssn = self.ssn

        state = self.state

        title = self.title

        username = self.username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if address1 is not UNSET:
            field_dict["address1"] = address1
        if address2 is not UNSET:
            field_dict["address2"] = address2
        if address3 is not UNSET:
            field_dict["address3"] = address3
        if city is not UNSET:
            field_dict["city"] = city
        if company is not UNSET:
            field_dict["company"] = company
        if country is not UNSET:
            field_dict["country"] = country
        if email is not UNSET:
            field_dict["email"] = email
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if license_number is not UNSET:
            field_dict["licenseNumber"] = license_number
        if middle_name is not UNSET:
            field_dict["middleName"] = middle_name
        if passport_number is not UNSET:
            field_dict["passportNumber"] = passport_number
        if phone is not UNSET:
            field_dict["phone"] = phone
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if ssn is not UNSET:
            field_dict["ssn"] = ssn
        if state is not UNSET:
            field_dict["state"] = state
        if title is not UNSET:
            field_dict["title"] = title
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        address1 = d.pop("address1", UNSET)

        address2 = d.pop("address2", UNSET)

        address3 = d.pop("address3", UNSET)

        city = d.pop("city", UNSET)

        company = d.pop("company", UNSET)

        country = d.pop("country", UNSET)

        email = d.pop("email", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        license_number = d.pop("licenseNumber", UNSET)

        middle_name = d.pop("middleName", UNSET)

        passport_number = d.pop("passportNumber", UNSET)

        phone = d.pop("phone", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        ssn = d.pop("ssn", UNSET)

        state = d.pop("state", UNSET)

        title = d.pop("title", UNSET)

        username = d.pop("username", UNSET)

        item_identity = cls(
            address1=address1,
            address2=address2,
            address3=address3,
            city=city,
            company=company,
            country=country,
            email=email,
            first_name=first_name,
            last_name=last_name,
            license_number=license_number,
            middle_name=middle_name,
            passport_number=passport_number,
            phone=phone,
            postal_code=postal_code,
            ssn=ssn,
            state=state,
            title=title,
            username=username,
        )

        item_identity.additional_properties = d
        return item_identity

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
