from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Any
from typing_extensions import Literal
from typing_extensions import Optional

from ...database import DATABASE
from ...logger import LOGGER


@dataclass(slots=True)
class TranslatorBuilder:
    ships_en: Optional[dict[str, Any]] = None
    equipments_en: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.ships_en is not None:
            nonStrValue = {
                k: v for k, v in self.ships_en.items() if not isinstance(v, str)
            }
            if nonStrValue:
                LOGGER.error(
                    "FOLLOWING VALUE ARE NOT STRING, USER SUPPLY SHIPS TRANSLATION WILL BE FULLY IGNORED !!!"
                )
                for k, v in nonStrValue.items():
                    LOGGER.error(
                        f"key: {k!r} found non string value, type: {type(v)}, value: {v}"
                    )
                self.ships_en = dict()

        if self.equipments_en is not None:
            nonStrValue = {
                k: v for k, v in self.equipments_en.items() if not isinstance(v, str)
            }
            if nonStrValue:
                LOGGER.error(
                    "FOLLOWING VALUE ARE NOT STRING, USER SUPPLY EQUIPMENTS TRANSLATION WILL BE FULLY IGNORED !!!"
                )
                for k, v in nonStrValue.items():
                    LOGGER.error(
                        f"key: {k!r} found non string value, type: {type(v)}, value: {v}"
                    )
                self.equipments_en = dict()


@dataclass(slots=True)
class Translator:
    builder: InitVar[Optional[TranslatorBuilder]]

    ships_en: dict[str, str] = field(default_factory=dict)
    equipments_en: dict[str, str] = field(default_factory=dict)

    def __post_init__(self, builder: Optional[TranslatorBuilder] = None):
        if builder is not None:
            self.ships_en = (
                {**self.ships_en, **builder.ships_en}
                if builder.ships_en is not None
                else self.ships_en
            )
            self.equipments_en = (
                {**self.equipments_en, **builder.equipments_en}
                if builder.equipments_en is not None
                else self.equipments_en
            )
        else:
            self.ships_en = dict()
            self.equipments_en = dict()

    def translate_ship(self, name: str, lang: Literal["EN"] = "EN") -> str:
        if lang != "EN" or name == "":
            return ""

        result = self.ships_en.get(name, "")

        if not result:
            if (_r := DATABASE.QueryShipNameEnByKeyFromKc3(name)) is not None:
                result = _r
            else:
                LOGGER.debug(
                    f"fallback kc3 dataset fail to find ship {name!r} english name"
                )

            if (_r := DATABASE.QueryShipByNameJapaneseFromKcWikiEn(name)) is not None:
                result = _r.nameFull
            else:
                LOGGER.warning(
                    f"fallback kcwiki dataset fail to find ship {name!r} english name"
                )
        return result

    def translate_equipment(self, name: str, lang: Literal["EN"] = "EN") -> str:
        if lang != "EN" or name == "":
            return ""

        result = self.equipments_en.get(name, "")

        if not result:
            if (_r := DATABASE.QueryEquipmentNameEnByKeyFromKc3(name)) is not None:
                result = _r
            else:
                LOGGER.debug(
                    f"fallback kc3 dataset fail to find equipment {name!r} english name"
                )

            if (
                _r := DATABASE.QueryEquipmentByNameJapaneseFromKcWikiEn(name)
            ) is not None:
                result = _r.name
            else:
                LOGGER.warning(
                    f"fallback kcwiki dataset fail to find equipment {name!r} english name"
                )

        return result
