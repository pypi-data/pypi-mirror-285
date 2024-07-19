from dataclasses import dataclass

from pydantic import TypeAdapter
from pydantic import ValidationError
from typing_extensions import Generic
from typing_extensions import MutableSequence
from typing_extensions import NotRequired
from typing_extensions import Optional
from typing_extensions import TypeAlias
from typing_extensions import TypedDict
from typing_extensions import TypeVar

from ....logger import LOGGER


class MasterItem(TypedDict):
    id: int
    type: int
    itype: int
    name: str
    abbr: NotRequired[str]
    fire: NotRequired[int]
    antiAir: NotRequired[int]
    torpedo: NotRequired[int]
    bomber: NotRequired[int]
    armor: NotRequired[int]
    asw: NotRequired[int]
    antiBomber: NotRequired[int]
    interception: NotRequired[int]
    scout: NotRequired[int]
    canRemodel: NotRequired[int]
    accuracy: NotRequired[int]
    avoid2: NotRequired[int]
    radius: NotRequired[int]
    cost: NotRequired[int]
    avoid: NotRequired[int]
    range: NotRequired[int]
    grow: NotRequired[int]


class MasterShip(TypedDict):
    id: int
    album: int
    type: int
    name: str
    yomi: str
    s_count: int
    slots: MutableSequence[int]
    final: int
    orig: int
    ver: int
    range: int
    type2: int
    hp: int
    hp2: int
    max_hp: int
    fire: int
    torpedo: int
    anti_air: int
    armor: int
    luck: int
    max_luck: int
    min_scout: int
    scout: int
    min_asw: int
    asw: int
    min_avoid: int
    avoid: int
    speed: int
    before: int
    next_lv: int
    sort: int
    fuel: int
    ammo: int
    blueprints: int
    reports: int
    catapults: int


class MasterEnemy(TypedDict):
    id: int
    type: int
    slot_count: int
    name: str
    slots: MutableSequence[int]
    items: MutableSequence[int]
    hp: int
    aa: int
    armor: int
    speed: int
    unknown: int


class MasterShipType(TypedDict):
    api_id: int
    api_name: str
    api_equip_type: MutableSequence[int]


class MasterEquipmentShip(TypedDict):
    """特定艦娘が装備可能な装備カテゴリ"""

    api_ship_id: int
    api_equip_type: MutableSequence[int]


class _MasterEquipmentExSlot_api_ship_ids(TypedDict):
    api_ship_ids: dict[str, int] | None


class _MasterEquipmentExSlot_api_stypes(TypedDict):
    api_stypes: dict[str, int] | None


class _MasterEquipmentExSlot_api_ctypes(TypedDict):
    api_ctypes: dict[str, int] | None


class _MasterEquipmentExSlot_api_req_level(TypedDict):
    api_req_level: int | None


MasterEquipmentExSlot: TypeAlias = dict[
    str,
    _MasterEquipmentExSlot_api_ship_ids
    | _MasterEquipmentExSlot_api_stypes
    | _MasterEquipmentExSlot_api_ctypes
    | _MasterEquipmentExSlot_api_req_level,
]
"""特定艦娘が補強増設に装備可能な装備id"""


class FormattedMasterEquipmentExSlot(TypedDict):
    api_slotitem_id: int
    api_ship_ids: MutableSequence[int]
    api_stype: MutableSequence[int]
    api_req_level: NotRequired[int]


class MasterWorld(TypedDict):
    world: int
    name: str


class MasterMap(TypedDict):
    area: int
    name: str
    boss: MutableSequence[str]
    has_detail: int
    has_air_raid: int


class MasterCell(TypedDict):
    w: int
    m: int
    i: int
    n: str
    t: int
    r: MutableSequence[int]


class Master(TypedDict):
    api_mst_equip_exslot_ship: MasterEquipmentExSlot
    api_mst_equip_ship: MutableSequence[MasterEquipmentShip]
    api_mst_stype: MutableSequence[MasterShipType]
    worlds: MutableSequence[MasterWorld]
    maps: MutableSequence[MasterMap]
    cells: MutableSequence[MasterCell]
    ships: MutableSequence[MasterShip]
    items: MutableSequence[MasterItem]
    enemies: MutableSequence[MasterEnemy]
    area_count: int


T = TypeVar("T")


@dataclass(slots=True)
class _MasterTypeValidator(Generic[T]):
    _type: type[T]

    def validate(self, v: str | bytes) -> Optional[T]:
        ta = TypeAdapter(self._type)

        try:
            return ta.validate_json(v)
        except ValidationError as e:
            LOGGER.error(e)

        return None


class MasterTypeValidator:
    @staticmethod
    def Master(v: str | bytes) -> Master | None:
        validator = _MasterTypeValidator(Master)
        return validator.validate(v)

    @staticmethod
    def MasterShip(v: str | bytes) -> MasterShip | None:
        validator = _MasterTypeValidator(MasterShip)
        return validator.validate(v)

    @staticmethod
    def MasterItem(v: str | bytes) -> MasterItem | None:
        validator = _MasterTypeValidator(MasterItem)
        return validator.validate(v)
