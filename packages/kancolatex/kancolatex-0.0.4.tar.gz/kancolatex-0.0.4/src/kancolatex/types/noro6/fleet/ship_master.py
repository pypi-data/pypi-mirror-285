from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ...const import ShipType
from ..interface import MasterShip


@dataclass(slots=True)
class ShipMaster:
    id: int = 0
    albumId: int = 0
    name: str = ""
    yomi: str = ""
    type: int = 0
    type2: int = 0
    slotCount: int = 0
    slots: list[int] = field(default_factory=list)
    version: int = 0
    isFinal: bool = False
    originalId: int = 0
    range: int = 0
    hp: int = 0
    hp2: int = 0
    maxHp: int = 0
    fire: int = 0
    torpedo: int = 0
    night: int = 0
    antiAir: int = 0
    armor: int = 0
    luck: int = 0
    maxLuck: int = 0
    minScout: int = 0
    maxScout: int = 0
    minAsw: int = 0
    maxAsw: int = 0
    minAvoid: int = 0
    maxAvoid: int = 0
    speed: int = 5
    beforeId: int = 0
    nextLv: int = 0
    sort: int = 0
    fuel: int = 0
    ammo: int = 0
    blueprints: int = 0
    actionReports: int = 0
    catapults: int = 0
    isCV: bool = False
    isBB: bool = False

    def __post_init__(self):
        self.night = self.fire + self.torpedo
        self.isCV = self.type in {ShipType.CV, ShipType.CVL, ShipType.CVB}
        self.isBB = self.type in {ShipType.FBB, ShipType.BB, ShipType.BBB, ShipType.BBV}

    @staticmethod
    def from_master_ship(ship: MasterShip) -> ShipMaster:
        return ShipMaster(
            id=ship.get("id", 0),
            albumId=ship.get("album", 0),
            name=ship.get("name", ""),
            yomi=ship.get("yomi", 0),
            type=ship.get("type", 0),
            type2=ship.get("type2", 0),
            slotCount=ship.get("s_count", 0),
            version=ship.get("ver", 0),
            isFinal=bool(ship.get("final", False)),
            range=ship.get("range", 0),
            hp=ship.get("hp", 0),
            hp2=ship.get("hp2", 0),
            maxHp=ship.get("max_hp", 0),
            fire=ship.get("fire", 0),
            torpedo=ship.get("torpedo", 0),
            antiAir=ship.get("anti_air", 0),
            armor=ship.get("armor", 0),
            luck=ship.get("luck", 0),
            maxLuck=ship.get("max_luck", 0),
            minScout=ship.get("min_scout", 0),
            maxScout=ship.get("scout", 0),
            minAsw=ship.get("min_asw", 0),
            maxAsw=ship.get("asw", 0),
            minAvoid=ship.get("min_avoid", 0),
            maxAvoid=ship.get("avoid", 0),
            speed=ship.get("speed", 5),
            beforeId=ship.get("before", 0),
            nextLv=ship.get("next_lv", 0),
            sort=ship.get("sort", 0),
            slots=ship.get("slots", list()),
            originalId=ship.get("orig", 0),
            fuel=ship.get("fuel", 0),
            ammo=ship.get("ammo", 0),
            blueprints=ship.get("blueprints", 0),
            actionReports=ship.get("actionReports", 0),
            catapults=ship.get("catapults", 0),
        )
