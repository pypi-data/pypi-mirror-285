from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.item_card_brand import ItemCardBrand
from ..types import UNSET, Unset

T = TypeVar("T", bound="ItemCard")


@_attrs_define
class ItemCard:
    """
    Attributes:
        brand (Union[Unset, ItemCardBrand]):
        cardholder_name (Union[Unset, str]):
        code (Union[Unset, str]):
        exp_month (Union[Unset, str]):
        exp_year (Union[Unset, str]):
        number (Union[Unset, str]):
    """

    brand: Union[Unset, ItemCardBrand] = UNSET
    cardholder_name: Union[Unset, str] = UNSET
    code: Union[Unset, str] = UNSET
    exp_month: Union[Unset, str] = UNSET
    exp_year: Union[Unset, str] = UNSET
    number: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        brand: Union[Unset, str] = UNSET
        if not isinstance(self.brand, Unset):
            brand = self.brand.value

        cardholder_name = self.cardholder_name

        code = self.code

        exp_month = self.exp_month

        exp_year = self.exp_year

        number = self.number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if brand is not UNSET:
            field_dict["brand"] = brand
        if cardholder_name is not UNSET:
            field_dict["cardholderName"] = cardholder_name
        if code is not UNSET:
            field_dict["code"] = code
        if exp_month is not UNSET:
            field_dict["expMonth"] = exp_month
        if exp_year is not UNSET:
            field_dict["expYear"] = exp_year
        if number is not UNSET:
            field_dict["number"] = number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _brand = d.pop("brand", UNSET)
        brand: Union[Unset, ItemCardBrand]
        if isinstance(_brand, Unset):
            brand = UNSET
        else:
            brand = ItemCardBrand(_brand)

        cardholder_name = d.pop("cardholderName", UNSET)

        code = d.pop("code", UNSET)

        exp_month = d.pop("expMonth", UNSET)

        exp_year = d.pop("expYear", UNSET)

        number = d.pop("number", UNSET)

        item_card = cls(
            brand=brand,
            cardholder_name=cardholder_name,
            code=code,
            exp_month=exp_month,
            exp_year=exp_year,
            number=number,
        )

        item_card.additional_properties = d
        return item_card

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
