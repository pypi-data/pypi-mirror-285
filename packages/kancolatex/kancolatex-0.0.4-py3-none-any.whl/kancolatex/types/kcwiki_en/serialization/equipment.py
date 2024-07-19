from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SkipValidation
from typing_extensions import Any
from typing_extensions import Optional

from ...const import EquipmentTypes
from ...equipment_id import EquipmentId


class KcwikiEquipment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    aa: bool | int = Field(alias="_aa")
    album_type: Optional[str] = Field(alias="_album_type", default=None)
    asw: bool | int = Field(alias="_asw")
    asw_damage_type: Optional[str] = Field(alias="asw_damage_type", default=None)
    back: Optional[int] = Field(alias="_back", default=None)
    bombing: bool | int = Field(alias="_bombing")
    bonus: SkipValidation[Any] = Field(alias="_bonus", default=None)
    buildable: bool = Field(alias="_buildable")
    can_attack_installations: Optional[bool] = Field(
        alias="can_attack_installations", default=None
    )
    card_japanese_name: Optional[str] = Field(alias="card_japanese_name", default=None)
    card_localized_name: Optional[str] = Field(
        alias="_card_localized_name", default=None
    )
    card_name: Optional[str] = Field(alias="_card_name", default=None)
    card_reading: Optional[str] = Field(alias="_card_reading", default=None)
    comparison_japanese_name: Optional[str] = Field(
        alias="_comparison_japanese_name", default=None
    )
    comparison_name: Optional[str] = Field(alias="_comparison_name", default=None)
    comparison_reading: Optional[str] = Field(alias="_comparison_reading", default=None)
    evasion: bool | int = Field(alias="_evasion")
    firepower: bool | int = Field(alias="_firepower")
    flight_const: Optional[bool | int] = Field(alias="_flight_const", default=None)
    flight_range: Optional[bool | int] = Field(alias="_flight_range", default=None)
    gun_fit_group: Optional[bool | None | str] = Field(
        alias="_gun_fit_group", default=None
    )
    icon: int = Field(alias="_icon")
    id: EquipmentId = Field(alias="_id")
    improvements: SkipValidation[bool | Any] = Field(
        alias="_improvements", default=False
    )
    info: Optional[str] = Field(alias="_info", default=None)
    item_id: Optional[int] = Field(alias="_item_id", default=None)
    japanese_name: str = Field(alias="_japanese_name")
    library_japanese_name: Optional[str] = Field(
        alias="_library_japanese_name", default=None
    )
    library_name: Optional[str] = Field(alias="_library_name", default=None)
    library_reading: Optional[str] = Field(alias="_library_reading", default=None)
    list_japanese_name: Optional[str] = Field(alias="list_japanese_name", default=None)
    list_name: Optional[str] = Field(alias="list_name", default=None)
    list_reading: Optional[str] = Field(alias="list_reading", default=None)
    localized_name: Optional[bool | str] = Field(alias="_localized_name", default=None)
    los: int = Field(alias="_los")
    luck: bool = Field(alias="_luck")
    name: str = Field(alias="_name")
    page: Optional[bool] = Field(alias="_page", default=None)
    range: bool | int = Field(alias="_range")
    rarity: int = Field(alias="_rarity")
    reading: bool | None | str = Field(alias="_reading")
    scrape_ammo: bool | int = Field(alias="_scrape_ammo", default=False)
    scrape_bauxite: bool | int = Field(alias="_scrape_bauxite", default=False)
    scrape_fuel: bool | int = Field(alias="_scrape_fuel", default=False)
    scrape_steel: bool | int = Field(alias="_scrape_steel", default=False)
    shelling_accuracy: bool | int = Field(alias="_shelling_accuracy")
    special: bool | str = Field(alias="_special")
    speed: bool = Field(alias="_speed")
    stars: Optional[int] = Field(alias="_stars", default=None)
    torpedo: bool | int = Field(alias="_torpedo")
    torpedo_accuracy: bool | int = Field(alias="_torpedo_accuracy")
    type: EquipmentTypes = Field(alias="_type")
    types: Optional[list[int]] = Field(alias="_types", default=None)
    version: Optional[int] = Field(alias="_version", default=None)
    wikipedia: Optional[str] = Field(alias="_wikipedia", default=None)
