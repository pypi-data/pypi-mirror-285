from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ... import const
from ...const import EquipmentTypes
from ...equipment_id import EquipmentId
from ..interface import MasterItem


@dataclass(slots=True)
class _Bonuses:
    key: str
    text: str


@dataclass(slots=True)
class ItemMaster:
    id: EquipmentId = 0
    apiTypeId: EquipmentTypes = EquipmentTypes.UNKNOWN
    iconTypeId: int = 0
    name: str = ""
    abbr: str = ""
    fire: int = 0
    torpedo: int = 0
    bomber: int = 0
    antiAir: int = 0
    armor: int = 0
    asw: int = 0
    antiBomber: int = 0
    accuracy: int = 0
    interception: int = 0
    avoid: int = 0
    scout: int = 0
    range: int = 0
    radius: int = 0
    cost: int = 0
    canRemodel: bool = False
    avoidId: int = 0
    grow: int = 0
    sortieAntiAir: float = 0
    defenseAntiAir: int = 0

    isSpecial: bool = False

    isPlane: bool = False
    isFighter: bool = False
    isAswPlane: bool = False
    isAutoGyro: bool = False
    isAttacker: bool = False
    isRecon: bool = False
    isABAttacker: bool = False
    isBakusen: bool = False
    isRocket: bool = False
    isLateModelTorpedo: bool = False
    isShinzan: bool = False
    isJet: bool = False
    enabledAttackLandBase: bool = False
    isStrictDepthCharge: bool = False
    isTorpedoAttacker: bool = False
    isNightAircraftItem: bool = False
    isSPPlane: bool = False
    isEnemyItem: bool = False
    bonuses: list[_Bonuses] = field(default_factory=list)
    airbaseMaxSlot: int = 18

    def __post_init__(self):
        # 特殊機銃(対空9以上) 特殊高角砲(対空8以上)判定
        self.isSpecial = (self.apiTypeId == 21 and self.antiAir >= 9) or (
            self.iconTypeId == 16 and self.antiAir >= 8
        )

        # その他区分解決
        self.isPlane = self.apiTypeId in const.PLANE_TYPES
        self.isFighter = self.apiTypeId in const.FIGHTERS
        self.isAswPlane = self.apiTypeId in const.ASW_PLANES
        self.isAutoGyro = self.apiTypeId is EquipmentTypes.Autogyro
        self.isAttacker = self.apiTypeId in const.ATTACKERS or (
            self.isAswPlane and self.bomber > 0 and not self.isAutoGyro
        )
        self.isRecon = self.apiTypeId in const.RECONNAISSANCES
        self.isABAttacker = self.apiTypeId in const.AB_ATTACKERS
        self.isBakusen = self.id in const.BAKUSEN
        self.isRocket = self.apiTypeId in const.ROCKET
        self.isLateModelTorpedo = self.apiTypeId in const.LATE_MODEL_TORPEDO
        self.isShinzan = self.apiTypeId in const.AB_ATTACKERS_LARGE
        self.isJet = self.apiTypeId is EquipmentTypes.JetBomber
        self.enabledAttackLandBase = self.apiTypeId in const.ENABLED_LAND_BASE_ATTACK
        self.isStrictDepthCharge = self.apiTypeId in const.STRICT_DEPTH_CHARGE
        self.isTorpedoAttacker = self.apiTypeId in {
            EquipmentTypes.CarrierBasedTorpedo,
            EquipmentTypes.LandBasedAttacker,
            EquipmentTypes.HeavyBomber,
        }

        self.isSPPlane = self.apiTypeId in const.SB_PLANE_TYPES
        self.isEnemyItem = self.id > 1500

        if self.isPlane:
            if self.isShinzan:
                self.airbaseMaxSlot = 9
            elif self.isRecon:
                self.airbaseMaxSlot = 4
            else:
                self.airbaseMaxSlot = 18

        # 出撃対空 = 対空値 + 1.5 * 迎撃
        self.sortieAntiAir = self.antiAir + 1.5 * self.interception
        self.defenseAntiAir = self.antiAir + self.interception + 2 * self.antiBomber

        if not self.isSpecial:
            # ロケ戦 対地可能 後期魚雷 対潜+7以上の艦攻
            self.isSpecial = (
                self.isRocket
                or self.enabledAttackLandBase
                or self.isLateModelTorpedo
                or (
                    self.apiTypeId == EquipmentTypes.CarrierBasedTorpedo
                    and self.asw >= 7
                )
            )

        if self.isStrictDepthCharge:
            self.iconTypeId = 1700

        self.bonuses = []
        _bonuses = (
            i
            for i in const.SPECIAL_GROUP
            if (item := i.get("item")) and self.id in item
        )
        for bonus in _bonuses:

            def _findAlready():
                for v in self.bonuses:
                    if (bonusKey := bonus.get("key")) and v.key == bonusKey:
                        return v
                else:
                    return None

            already = _findAlready()

            if already is not None:
                # 既に同じキーのものがあるなら特効文字列を結合
                already.text += bonus.get("text", "")
            else:
                self.bonuses.append(
                    _Bonuses(bonus.get("key", ""), bonus.get("text", ""))
                )

        self.isNightAircraftItem = self.iconTypeId in {45, 46} or self.id in {
            154,
            242,
            243,
            244,
            320,
        }

    @staticmethod
    def from_master_item(item: MasterItem) -> ItemMaster:
        return ItemMaster(
            id=item.get("id", 0),
            apiTypeId=EquipmentTypes(item.get("type", 0)),
            iconTypeId=item.get("itype", 0),
            name=item.get("name", ""),
            abbr=item.get("abbr", ""),
            fire=item.get("fire", 0),
            torpedo=item.get("torpedo", 0),
            bomber=item.get("bomber", 0),
            antiAir=item.get("antiAir", 0),
            armor=item.get("armor", 0),
            asw=item.get("asw", 0),
            antiBomber=item.get("antiBomber", 0),
            accuracy=item.get("accuracy", 0),
            interception=item.get("interception", 0),
            avoid=item.get("avoid2", 0),
            scout=item.get("scout", 0),
            range=item.get("range", 0),
            radius=item.get("radius", 0),
            cost=item.get("cost", 0),
            canRemodel=bool(item.get("canRemodel", False)),
            avoidId=item.get("avoid", 0),
            grow=item.get("grow", 0),
        )
