from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ...const import ShipType
from ..interface import MasterEnemy


@dataclass(slots=True)
class EnemyMaster:
    id: int = 0
    name: str = ""
    type: int = 0
    type2: int = 0
    version: int = 0
    hp: int = 0
    antiAir: int = 0
    armor: int = 0
    slotCount: int = 0
    slots: list[int] = field(default_factory=list)
    items: list[int] = field(default_factory=list)
    speed: int = 0
    isLandBase: bool = False
    isUnknown: bool = False
    isCV: bool = False
    isBB: bool = False

    @staticmethod
    def from_master_enemy(enemy: MasterEnemy) -> EnemyMaster:
        return EnemyMaster(
            id=enemy.get("id", 0),
            name=enemy.get("name", ""),
            type=enemy.get("type", 0),
            hp=enemy.get("hp", 0),
            antiAir=enemy.get("aa", 0),
            slotCount=enemy.get("slot_count", 0),
            speed=enemy.get("speed", 0),
            isUnknown=bool(enemy.get("unknown", False)),
            #
            slots=enemy.get("slots", list()),
            items=enemy.get("items", list()),
            #
            isLandBase=(enemy.get("speed", 0) == 0),
            #
            isCV=(enemy.get("type", 0) in {ShipType.CV, ShipType.CVL, ShipType.CVB}),
            isBB=(
                enemy.get("type", 0)
                in {ShipType.FBB, ShipType.BB, ShipType.BBB, ShipType.BBV}
            ),
        )
