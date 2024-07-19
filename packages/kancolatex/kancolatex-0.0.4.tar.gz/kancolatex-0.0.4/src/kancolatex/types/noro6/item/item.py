from __future__ import annotations

import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import MutableSequence
from typing_extensions import Optional
from typing_extensions import Sequence

from ...const import EquipmentTypes
from ..interface import ContactRate
from .item_master import ItemMaster


@dataclass(slots=True)
class ItemBuilder:
    item: Item | None = None
    master: Optional[ItemMaster] = None
    slot: Optional[int] = None
    level: Optional[int] = None
    remodel: Optional[int] = None
    ignoreRemodelBonus: Optional[bool] = None
    noStock: Optional[bool] = None


@dataclass(slots=True)
class Item:
    builder: InitVar[ItemBuilder]

    data: ItemMaster = field(default_factory=ItemMaster)
    level: int = 0
    remodel: int = 0
    fullSlot: int = 0
    bonusFire: float = 0
    bonusNightFire: float = 0
    bonusExpeditionFire: float = 0
    bonusTorpedo: float = 0
    bonusBomber: float = 0
    bonusAntiAir: float = 0
    bonusExpeditionAntiAir: float = 0
    bonusArmor: float = 0
    bonusAccuracy: float = 0
    bonusAsw: float = 0
    bonusExpeditionAsw: float = 0
    bonusScout: float = 0
    bonusExpeditionScout: float = 0
    bonusAirPower: float = 0
    bonusAirWeight: int = 0
    itemScout: float = 0
    antiAirWeight: float = 0
    antiAirBonus: float = 0
    dayBattleFirePower: float = 0
    aircraftDayBattleFirePower: float = 0
    nightBattleFirePower: float = 0
    actualFire: float = 0
    actualAntiAir: float = 0
    actualTorpedo: float = 0
    actualBomber: float = 0
    actualAsw: float = 0
    actualArmor: float = 0
    actualAccuracy: float = 0
    actualScout: float = 0
    actualAvoid: float = 0
    actualRange: float = 0
    actualDefenseAntiAir: float = 0
    fullAirPower: int = 0
    fullDefenseAirPower: int = 0
    supportAirPower: int = 0
    supportAswAirPower: int = 0
    contactSelectRates: Sequence[float] = field(default_factory=list)
    tp: float = 0
    fuel: int = 0
    ammo: int = 0
    steel: int = 0
    bauxite: int = 0
    reconCorr: float = 0
    reconCorrDefense: float = 0
    calculatedAirPower: Sequence[int] = field(default_factory=list)
    calculatedDefenseAirPower: Sequence[int] = field(default_factory=list)
    attackTorpedoBonus: int = 0
    crewTorpedoBonus: int = 0
    crewBomberBonus: int = 0
    airPower: int = 0
    defenseAirPower: int = 0
    slot: int = 0
    slotHistories: Sequence[int] = field(default_factory=list)
    slotResult: int = 0
    deathRate: int = 0
    minSlot: int = 0
    maxSlot: int = 0
    isEscortItem: bool = False
    disabledItem: bool = False
    needRecord: bool = False
    dist: MutableSequence[int] = field(default_factory=list)
    parentIndex: int = -1
    noStock: bool = False

    def __post_init__(self, builder: ItemBuilder) -> None:
        if builder.item is not None:
            # ItemBuilderより生成 Itemインスタンスを引継ぎ
            self.data = (
                builder.master if builder.master is not None else builder.item.data
            )
            self.fullSlot = (
                builder.slot if builder.slot is not None else builder.item.fullSlot
            )
            self.remodel = (
                builder.remodel if builder.remodel is not None else builder.item.remodel
            )
            self.level = (
                builder.level if builder.level is not None else builder.item.level
            )
            self.noStock = builder.noStock if builder.noStock is not None else False
        else:
            self.data = builder.master if builder.master is not None else ItemMaster()
            self.fullSlot = builder.slot if builder.slot is not None else 0
            self.remodel = builder.remodel if builder.remodel is not None else 0
            self.level = builder.level if builder.level is not None else 0
            self.noStock = builder.noStock if builder.noStock is not None else False

        # 現在搭載数の初期化
        self.slot = self.fullSlot

        # 全戦闘終了時のうちの最大搭載数、最小搭載数
        self.minSlot = self.fullSlot
        self.maxSlot = 0 if self.data.isPlane else self.fullSlot

        # 計算により算出するステータス
        self.bonusAirPower = self._getBonusAirPower()
        self.antiAirWeight = self._getAntiAirWeight()
        self.bonusFire = self._getBonusFirePower()
        self.bonusNightFire = self._getBonusNightFirePower()
        self.bonusTorpedo = self._getBonusTorpedo()
        self.bonusBomber = self._getBonusBomber()
        self.bonusArmor = self._getBonusArmor()
        self.bonusAntiAir = self._getBonusAntiAir()
        self.bonusAccuracy = self._getBonusAccuracy()
        self.bonusAsw = self._getBonusAsw()
        self.bonusScout = self._getBonusScout()
        self.antiAirBonus = self._getAntiAirBonus()
        self.tp = self._getTransportPower()
        self.reconCorr = self._getReconCorr()
        self.reconCorrDefense = self._getReconCorrDefense()
        self.contactSelectRates = self._getContactSelectRates()
        self.bonusExpeditionFire = self._getBonusFirePowerForExpedition()
        self.bonusExpeditionAntiAir = self._getBonusAntiAirForExpedition()
        self.bonusExpeditionAsw = self._getBonusAswForExpedition()
        self.bonusExpeditionScout = self._getBonusScoutForExpedition()
        self.supportAswAirPower = 0

        # (装備の素の索敵値 + 改修係数×√★)×装備係数
        self.itemScout = (
            self.data.scout + self.bonusScout
        ) * self._getItemScoutCoefficient()

        if builder.ignoreRemodelBonus:
            # 改修値をステータスに反映しないオプションがある場合
            self.actualFire = self.data.fire
            self.actualTorpedo = self.data.torpedo
            self.actualBomber = self.data.bomber
            self.actualAsw = self.data.asw
            self.actualArmor = self.data.armor
            self.actualRange = self.data.range
            self.actualAccuracy = self.data.accuracy
            self.actualScout = self.data.scout
            self.actualAvoid = self.data.avoid
            self.dayBattleFirePower = self.data.fire
            self.aircraftDayBattleFirePower = self.data.fire
            self.nightBattleFirePower = self.data.fire + self.data.torpedo
        else:
            self.actualFire = self.data.fire + self.bonusFire
            self.actualTorpedo = self.data.torpedo + self.bonusTorpedo
            self.actualBomber = self.data.bomber + self.bonusBomber
            self.actualAsw = self.data.asw + self.bonusAsw
            self.actualArmor = self.data.armor + self.bonusArmor
            self.actualRange = self.data.range
            self.actualAccuracy = self.data.accuracy + self.bonusAccuracy
            self.actualScout = self.data.scout + self.bonusScout
            self.actualAvoid = self.data.avoid
            self.dayBattleFirePower = self.data.fire + self.bonusFire
            self.aircraftDayBattleFirePower = self.data.fire + self.bonusFire
            self.nightBattleFirePower = (
                self.data.fire + self.data.torpedo + self.bonusNightFire
            )

        self.calculatedAirPower = []
        self.calculatedDefenseAirPower = []

        # 航空機の処理
        if self.data.isPlane:
            if not self.data.isSPPlane:
                self.aircraftDayBattleFirePower = (
                    self.dayBattleFirePower
                    + self.data.torpedo
                    + math.floor(1.3 * self.data.bomber)
                ) * 1.5

            # 出撃コスト算出
            self.fuel = self.fullSlot
            self.ammo = math.ceil(self.fullSlot * 0.6)
            self.bauxite = self.data.cost * 4 if self.data.isRecon else 18
            self.steel = (
                round(self.fullSlot * self.data.cost * 0.2) if self.data.isJet else 0
            )

            if self.data.isABAttacker:
                # 陸攻補正
                self.fuel = math.ceil(
                    self.fullSlot * (2 if self.data.isShinzan else 1.5)
                )
                self.ammo = (
                    self.fullSlot * 2
                    if self.data.isShinzan
                    else math.floor(self.fullSlot * 0.7)
                )
                self.bauxite = self.data.cost * self.data.airbaseMaxSlot
            elif self.data.apiTypeId == EquipmentTypes.FlyingBoat:
                # 大型偵察機補正
                self.fuel = self.fullSlot * 3
                self.ammo = self.fullSlot

            if builder.ignoreRemodelBonus:
                # 改修値をステータスに反映しないオプションがある場合
                # 出撃対空値 = 対空値 + 1.5 * 迎撃
                self.actualAntiAir = self.data.sortieAntiAir
                # 防空対空値 = 対空値 + 迎撃 + 2 * 対爆
                self.actualDefenseAntiAir = self.data.defenseAntiAir
                # 制空値更新
                self.fullAirPower = math.floor(
                    self.actualAntiAir * math.sqrt(self.fullSlot)
                )
                self.fullDefenseAirPower = math.floor(
                    self.actualDefenseAntiAir * math.sqrt(self.fullSlot)
                )
            else:
                # 出撃対空値 = 対空値 + 1.5 * 迎撃 + ボーナス対空値(改修値による)
                self.actualAntiAir = self.data.sortieAntiAir + self.bonusAntiAir
                # 防空対空値 = 対空値 + 迎撃 + 2 * 対爆 + ボーナス対空値(改修値による)
                self.actualDefenseAntiAir = self.data.defenseAntiAir + self.bonusAntiAir
                # 制空値更新
                self.fullAirPower = math.floor(
                    self.actualAntiAir * math.sqrt(self.fullSlot) + self.bonusAirPower
                )
                self.fullDefenseAirPower = math.floor(
                    self.actualDefenseAntiAir * math.sqrt(self.fullSlot)
                    + self.bonusAirPower
                )

            self.airPower = self.fullAirPower
            self.defenseAirPower = self.fullDefenseAirPower

            if self.fullSlot > 0 and self.data.isPlane:
                for slot in range(self.fullSlot + 1):
                    self.calculatedAirPower.append(
                        math.floor(
                            self.actualAntiAir * math.sqrt(slot) + self.bonusAirPower
                        )
                    )

                    self.calculatedDefenseAirPower.append(
                        math.floor(
                            self.actualDefenseAntiAir * math.sqrt(slot)
                            + self.bonusAirPower
                        )
                    )

        else:
            # 以下、航空機でないなら関係ない数値たち
            self.actualAntiAir = 0
            self.actualDefenseAntiAir = 0
            self.fuel = 0
            self.ammo = 0
            self.bauxite = 0
            self.steel = 0
            self.fullAirPower = 0
            self.fullDefenseAirPower = 0
            self.airPower = 0
            self.defenseAirPower = 0
            self.supportAirPower = 0

        self.slotHistories = []

    @property
    def levelAlt(self) -> int:
        """熟練度 0 ~ 7表示"""
        from ....services.noro6 import common_calc

        return common_calc.getProfLevel(self.level)

    def updateAirPower(self) -> None:
        """現在制空値を更新 計算用"""
        if self.slot <= 0:
            self.airPower = 0
            self.slot = 0
        else:
            self.airPower = self.calculatedAirPower[self.slot]

    def updateDefenseAirPower(self) -> None:
        """現在防空制空値を更新 計算用"""
        if self.slot <= 0:
            self.defenseAirPower = 0
            self.slot = 0
        else:
            self.defenseAirPower = self.calculatedDefenseAirPower[self.slot]

    def supply(self) -> None:
        """計算で減衰した各種値を戻す 計算用"""
        if self.needRecord:
            self.dist.append(self.slot)
        self.slot = self.fullSlot
        self.airPower = self.fullAirPower
        self.defenseAirPower = self.fullDefenseAirPower

    def _getBonusAirPower(self) -> float:
        """熟練度によるボーナス制空値を返却"""

        if (
            self.data.id == 0
            or self.fullSlot == 0
            or not self.data.isPlane
            or (self.data.isAswPlane and not self.data.isAttacker)
        ):
            return 0

        _type = self.data.apiTypeId
        _sum = 0

        if self.level >= 100:
            if self.data.isFighter or self.data.isAswPlane:
                _sum += 22
            elif _type == EquipmentTypes.SeaplaneBomber:
                _sum += 6
        elif self.level >= 70:
            if self.data.isFighter or self.data.isAswPlane:
                _sum += 14
            elif _type == EquipmentTypes.SeaplaneBomber:
                _sum += 3
        elif self.level >= 55:
            if self.data.isFighter or self.data.isAswPlane:
                _sum += 9
            elif _type == EquipmentTypes.SeaplaneBomber:
                _sum += 1
        elif self.level >= 40:
            if self.data.isFighter or self.data.isAswPlane:
                _sum += 5
            elif _type == EquipmentTypes.SeaplaneBomber:
                _sum += 1
        elif self.level >= 25:
            if self.data.isFighter or self.data.isAswPlane:
                _sum += 2
            elif _type == EquipmentTypes.SeaplaneBomber:
                _sum += 1

        # 内部熟練度ボーナス
        _sum += math.sqrt(self.level / 10)

        if self.data.id == 138:
            _sum += 1 if self.remodel >= 4 and self.fullSlot == 4 else 0

        return _sum

    def _getBonusFirePower(self) -> float:
        """改修値によるボーナス火力を返却"""

        # 大口径主砲
        if self.data.apiTypeId == EquipmentTypes.MainGunLarge:
            return 1.5 * math.sqrt(self.remodel)

        # その他主砲 / 副砲 / 三式弾 / 徹甲弾 / 機銃 / 探照灯 / 高射装置 / 大発 / 水上艦要員 / 航空要員 / 潜水艦魚雷 / 特型内火艇 / 対地装備 / 司令部施設 / 発煙装置
        if self.data.apiTypeId in {
            1,
            2,
            4,
            18,
            19,
            21,
            24,
            29,
            32,
            34,
            35,
            36,
            37,
            39,
            42,
            46,
            54,
        }:
            # 一部副砲
            if self.data.id in {10, 66, 220, 275, 464}:
                return 0.2 * self.remodel

            if self.data.id in {12, 234, 247, 467}:
                return 0.3 * self.remodel

            return math.sqrt(self.remodel)

        # ソナー 爆雷
        if (
            self.data.apiTypeId
            in {
                EquipmentTypes.Sonar,
                EquipmentTypes.DepthCharge,
                EquipmentTypes.SonarLarge,
            }
            and not self.data.isStrictDepthCharge
        ):
            return 0.75 * math.sqrt(self.remodel)

        #  艦攻 艦爆
        if self.data.apiTypeId in {
            EquipmentTypes.CarrierBasedTorpedo,
            EquipmentTypes.CarrierBasedBomber,
        }:
            return 0.2 * self.remodel

        return 0

    def _getBonusNightFirePower(self) -> float:
        """改修値によるボーナス夜戦火力を返却"""

        # 主砲 / 副砲 / 魚雷 / 三式弾 / 徹甲弾 / 特殊潜航艇 / 探照灯 / 高射装置 / 大発 / 水上艦要員 / 航空要員 / 特型内火艇 / 対地装備 / 司令部施設 / 発煙装置
        if self.data.apiTypeId in {
            1,
            2,
            3,
            4,
            5,
            18,
            19,
            22,
            24,
            29,
            34,
            35,
            36,
            37,
            39,
            42,
            46,
            54,
        }:
            if self.data.id in {10, 66, 220, 275, 464}:
                # 一部副砲
                return 0.2 * self.remodel

            if self.data.id in {12, 234, 247, 467}:
                # 一部副砲その2
                return 0.3 * self.remodel

            return math.sqrt(self.remodel)

        if self.data.apiTypeId == EquipmentTypes.SubmarineTorpedo:
            return 0.2 * self.remodel

        return 0

    def _getBonusFirePowerForExpedition(self) -> float:
        """改修値によるボーナス火力(遠征)を返却"""

        # 小口径主砲 副砲 小型電探 対艦強化弾 対空機銃
        if self.data.apiTypeId in {1, 4, 12, 19, 21}:
            return math.floor(10 * 0.5 * math.sqrt(self.remodel)) / 10

        # 中口径主砲 大口径主砲 大型電探
        if self.data.apiTypeId in {2, 3, 13}:
            return math.floor(10 * math.sqrt(self.remodel)) / 10

        # 搭載数0の飛行機 => 打消し
        if self.data.isPlane and self.slot == 0:
            return -self.data.fire

        return 0

    def _getBonusAntiAirForExpedition(self) -> float:
        """改修値によるボーナス対空(遠征)を返却"""

        # 高角砲 対空機銃
        if self.data.iconTypeId == 16 or self.data.apiTypeId == EquipmentTypes.AAGun:
            return math.floor(10 * math.sqrt(self.remodel)) / 10

        # 搭載数0の飛行機 => 打消し
        if self.data.isPlane and self.slot == 0:
            return -self.data.antiAir

        return 0

    def _getBonusAswForExpedition(self) -> float:
        """改修値によるボーナス対潜(遠征)を返却"""

        # ソナー 爆雷投射機 爆雷
        if self.data.apiTypeId in {
            EquipmentTypes.Sonar,
            EquipmentTypes.DepthCharge,
            EquipmentTypes.SonarLarge,
        }:
            return math.floor(10 * math.sqrt(self.remodel)) / 10

        # 搭載数0の飛行機 => 打消し
        if self.data.isPlane and self.slot == 0:
            return -self.data.asw

        return 0

    def _getBonusScoutForExpedition(self) -> float:
        """改修値によるボーナス索敵(遠征)を返却"""

        # 電探
        if self.data.apiTypeId in {
            EquipmentTypes.RadarSmall,
            EquipmentTypes.RadarLarge,
        }:
            return math.floor(10 * math.sqrt(self.remodel)) / 10

        # 搭載数0の飛行機 => 打消し
        if self.data.isPlane and self.slot == 0:
            return -self.data.scout

        return 0

    def _getBonusTorpedo(self) -> float:
        """改修値によるボーナス雷装を返却"""

        # 艦攻
        if self.data.apiTypeId == EquipmentTypes.CarrierBasedTorpedo:
            return 0.2 * self.remodel

        # 陸攻 重爆 not東海系
        if self.data.isABAttacker and self.data.iconTypeId != 47:
            if self.data.id == 484:
                # 四式重爆 飛龍(熟練)+イ号一型甲 誘導弾 だけなぜか0.75 つよい
                return 0.75 * math.sqrt(self.remodel)

            # その他 0.7
            return 0.7 * math.sqrt(self.remodel)

        # 魚雷 / 機銃
        if self.data.apiTypeId in {EquipmentTypes.Torpedo, EquipmentTypes.AAGun}:
            return 1.2 * math.sqrt(self.remodel)

        # 潜水艦魚雷
        if self.data.apiTypeId == EquipmentTypes.SubmarineTorpedo:
            return 0.2 * self.remodel

        return 0

    def _getBonusBomber(self) -> float:
        """改修値によるボーナス爆装を返却"""
        _type = self.data.apiTypeId

        # 艦爆 (爆戦ってついてないやつ)
        if _type == EquipmentTypes.CarrierBasedBomber and not self.data.isBakusen:
            return 0.2 * self.remodel

        # 水爆
        if _type == EquipmentTypes.SeaplaneBomber:
            return 0.2 * self.remodel

        return 0

    def _getBonusAntiAir(self) -> float:
        """改修値によるボーナス対空を返却"""

        # 艦戦 夜戦 水戦
        if self.data.isFighter:
            return 0.2 * self.remodel

        if (
            self.data.apiTypeId == EquipmentTypes.CarrierBasedBomber
            and self.data.isBakusen
        ):
            return 0.25 * self.remodel

        # 陸攻
        if self.data.isABAttacker:
            return 0.5 * math.sqrt(self.remodel)

        # 陸上偵察機 具体的な数値分からないので実測を満たすように仮置き => 内部100で+0 内部120で+1
        if self.data.apiTypeId == EquipmentTypes.LandBasedRecon:
            return 0.2 * self.remodel

        return 0

    def _getBonusAsw(self) -> float:
        """改修値によるボーナス対潜を返却"""

        _type = self.data.apiTypeId
        if _type in {
            EquipmentTypes.Sonar,
            EquipmentTypes.DepthCharge,
            EquipmentTypes.SonarLarge,
        }:
            return (2 / 3) * math.sqrt(self.remodel)

        # 艦攻
        if _type == EquipmentTypes.CarrierBasedTorpedo:
            return 0.2 * self.remodel

        # 艦爆 (爆戦ってついてないやつ)
        if _type == EquipmentTypes.CarrierBasedBomber and not self.data.isBakusen:
            return 0.2 * self.remodel

        # 対潜哨戒機
        if _type == EquipmentTypes.ASPatrol:
            if self.data.asw >= 8:
                return 0.3 * self.remodel

            return 0.2 * self.remodel

        # オートジャイロ
        if _type == EquipmentTypes.Autogyro:
            if self.data.asw >= 10:
                return 0.3 * self.remodel

            return 0.2 * self.remodel

        # 陸攻(対潜哨戒機)
        if self.data.isABAttacker and self.data.iconTypeId == 47:
            return 0.66 * math.sqrt(self.remodel)

        return 0

    def _getBonusAccuracy(self) -> float:
        """改修値によるボーナス命中を返却"""

        # 水上電探
        if (
            self.data.apiTypeId
            in {EquipmentTypes.RadarSmall, EquipmentTypes.RadarLarge}
            and self.data.scout >= 5
        ):
            return 1.7 * math.sqrt(self.remodel)

        # 主砲 副砲 徹甲弾 三式弾 高射装置 探照灯 ソナ－ 上陸用舟艇
        if (
            self.data.apiTypeId
            in {1, 2, 3, 4, 12, 13, 14, 15, 18, 19, 24, 29, 36, 37, 39, 40, 42}
            and not self.data.isStrictDepthCharge
        ):
            return math.sqrt(self.remodel)

        return 0

    def _getBonusArmor(self) -> float:
        """改修値によるボーナス装甲を返却"""

        # 中型バルジ
        if self.data.apiTypeId == EquipmentTypes.ExtraArmorMedium:
            return 0.2 * self.remodel

        # 大型バルジ
        if self.data.apiTypeId == EquipmentTypes.ExtraArmorLarge:
            return 0.3 * self.remodel

        return 0

    def _getBonusScout(self) -> float:
        """改修値によるボーナス索敵を返却"""

        _bonus: float = 0

        if self.data.apiTypeId == EquipmentTypes.RadarSmall:
            # 小型電探
            _bonus = 1.25 * math.sqrt(self.remodel)
        elif self.data.apiTypeId == EquipmentTypes.RadarLarge:
            # 大型電探
            _bonus = 1.4 * math.sqrt(self.remodel)
        elif self.data.isRecon:
            # 偵察機
            _bonus = 1.2 * math.sqrt(self.remodel)
        elif self.data.apiTypeId == EquipmentTypes.SeaplaneBomber:
            # 水上爆撃機
            _bonus = 1.15 * math.sqrt(self.remodel)

        return _bonus

    def _getItemScoutCoefficient(self) -> float:
        """装備索敵係数を返却"""

        _value: float = 0.6

        if self.data.apiTypeId == EquipmentTypes.CarrierBasedTorpedo:
            # 艦上攻撃機
            _value = 0.8
        elif self.data.apiTypeId == EquipmentTypes.CarrierBasedRecon:
            # 艦上偵察機
            _value = 1
        elif self.data.apiTypeId == EquipmentTypes.SeaplaneRecon:
            # 水上偵察機
            _value = 1.2
        elif self.data.apiTypeId == EquipmentTypes.SeaplaneBomber:
            # 水上爆撃機
            _value = 1.1

        return _value

    def _getAntiAirWeight(self) -> float:
        """この装備の加重対空値を返却"""

        _total: float = 0

        # 加重対空値部品 => 装備対空値 * 装備倍率
        if self.data.iconTypeId == 16:
            # 高角砲(緑)
            _total = self.data.antiAir * 2
        elif self.data.apiTypeId == EquipmentTypes.AADirector:
            # 高射装置
            _total = self.data.antiAir * 2
        elif self.data.apiTypeId == EquipmentTypes.AAGun:
            # 機銃
            _total = self.data.antiAir * 3
        elif self.data.iconTypeId == 11:
            # 電探
            _total = self.data.antiAir * 1.5

        # 艦船対空改修補正 = 装備倍率 * √★
        if (
            self.data.iconTypeId == 16
            or self.data.apiTypeId == EquipmentTypes.AADirector
        ) and self.data.antiAir <= 7:
            # 対空値7以下の高角砲 高射装置
            _total += 1 * math.sqrt(self.remodel)
        elif (
            self.data.iconTypeId == 16
            or self.data.apiTypeId == EquipmentTypes.AADirector
        ) and self.data.antiAir > 7:
            # 対空値8以上の高角砲 高射装置
            _total += 1.5 * math.sqrt(self.remodel)
        elif self.data.apiTypeId == EquipmentTypes.AAGun and self.data.antiAir <= 7:
            # 対空値7以下の機銃
            _total += 2 * math.sqrt(self.remodel)
        elif self.data.apiTypeId == EquipmentTypes.AAGun and self.data.antiAir > 7:
            # 対空値8以上の機銃
            _total += 3 * math.sqrt(self.remodel)

        return _total

    def _getAntiAirBonus(self) -> float:
        _total: float = 0
        # 艦隊防空ボーナス
        if self.data.iconTypeId == 16:
            # 高角砲(緑)
            _total = self.data.antiAir * 35
        elif self.data.apiTypeId == EquipmentTypes.AADirector:
            # 高射装置
            _total = self.data.antiAir * 35
        elif self.data.apiTypeId == EquipmentTypes.AAShell:
            # 対空強化弾(三式)
            _total = self.data.antiAir * 60
        elif self.data.iconTypeId == 11:
            # 電探
            _total = self.data.antiAir * 40
        elif self.data.id == 9:
            # 46cm三連装砲
            _total = self.data.antiAir * 25
        else:
            # その他
            _total = self.data.antiAir * 20

        # 艦隊防空装備改修補正 = 装備倍率 * √★
        if (
            self.data.iconTypeId == 16
            or self.data.apiTypeId == EquipmentTypes.AADirector
        ) and self.data.antiAir <= 7:
            # 対空値7以下の高角砲 高射装置
            _total += 200 * math.sqrt(self.remodel)
        elif (
            self.data.iconTypeId == 16
            or self.data.apiTypeId == EquipmentTypes.AADirector
        ) and self.data.antiAir > 7:
            # 対空値8以上の高角砲 高射装置
            _total += 300 * math.sqrt(self.remodel)
        elif self.data.iconTypeId == 11 and self.data.antiAir > 1:
            _total += 150 * math.sqrt(self.remodel)

        return _total

    def _getTransportPower(self) -> float:
        """輸送量を返却"""

        return {
            24: 8,  # 上陸用舟艇
            30: 5,  # 簡易輸送部材
            43: 1,  # おにぎり
            46: 2,  # 特型内火艇
        }.get(self.data.apiTypeId, 0)

    def _getReconCorr(self) -> float:
        """出撃時偵察機補正を返却"""

        # 出撃時補正 陸偵
        if self.data.apiTypeId == EquipmentTypes.LandBasedRecon:
            # 陸上偵察機補正
            return {9: 1.18, 8: 1.15}.get(self.data.scout, 1)

        return 1

    def _getReconCorrDefense(self) -> float:
        """防空時偵察機補正を返却"""

        # 防空時補正
        if self.data.apiTypeId == EquipmentTypes.LandBasedRecon:
            # 陸上偵察機補正
            return 1.24 if self.data.scout == 9 else 1.18

        if self.data.apiTypeId == EquipmentTypes.CarrierBasedRecon:
            # 艦上偵察機補正
            return 1.3 if self.data.scout > 8 else 1.2

        if self.data.isRecon:
            # それ以外の偵察機補正
            if self.data.scout > 8:
                return 1.16
            elif self.data.scout == 8:
                return 1.13
            else:
                return 1.1

        return 1

    def _getContactSelectRates(self) -> tuple[float, float, float]:
        """触接選択率を返却"""

        if self.data.apiTypeId in {8, 9, 10, 41, 49}:
            _remodel = self.remodel
            _scout = self.data.scout

            _id = self.data.id

            if _id == 102:
                # 九八式水上偵察機(夜偵)
                _scout = math.ceil(_scout + 0.1 * _remodel)
            elif _id in {
                25,  # 零式水上偵察機
                138,  # 二式大艇
                163,  # Ro.43水偵
                304,  # S9 Osprey
                370,  # Swordfish Mk.II改(水偵型)
                239,  # 零式水上偵察機11型乙(熟練)
            }:
                _scout = math.ceil(_scout + 0.14 * _remodel)
            elif _id == 59:
                # 零式水上観測機
                _scout = math.ceil(_scout + 0.2 * _remodel)
            elif _id == 61:
                # 二式艦上偵察機
                _scout = math.ceil(_scout + 0.25 * _remodel)
            elif _id == 151:
                # 試製景雲(艦偵型)
                _scout = math.ceil(_scout + 0.4 * _remodel)

            # 触接選択率 => 20 - (2 * 制空定数[3, 2, 1])
            #!: Python min function must have at least 2 argument,
            #!: I have to remove the last 2 min function.
            return (min(_scout / 14, 1), _scout / 16, _scout / 18)

        return (0, 0, 0)

    def _getProfCriticalBonus(self) -> float:
        """熟練クリティカル補正を算出 -現行では基地航空隊用"""

        _bonus: float = 0
        # 搭載数が存在する攻撃機か大型飛行艇、対潜哨戒機 オートジャイロ
        if self.slot > 0 and (
            self.data.isAttacker or self.data.apiTypeId == EquipmentTypes.FlyingBoat
        ):
            # 熟練度定数C
            c = (0, 1, 2, 3, 4, 5, 7, 10)[self.levelAlt]
            _bonus += math.floor(math.sqrt(self.level) + c) / 100
            if self.data.isAswPlane:
                # 対潜哨戒機
                _bonus = math.floor(math.sqrt(self.level) + c) / 128

        # 補正値 = int(√内部熟練度  + C) / 100
        return 1 + _bonus

    @staticmethod
    def getContactRates(
        items: Sequence[Item],
    ) -> tuple[ContactRate, ContactRate, ContactRate]:
        """装備配列より触接情報テーブルを取得"""

        sumContactValue: float = 0
        # 補正率別 触接選択率テーブル[ 0:確保時, 1:優勢時, 2:劣勢時 ]
        contact120: tuple[list[float], list[float], list[float]] = ([], [], [])
        contact117: tuple[list[float], list[float], list[float]] = ([], [], [])
        contact112: tuple[list[float], list[float], list[float]] = ([], [], [])

        for _i, item in enumerate(items):
            if item.data.isRecon:
                sumContactValue += math.floor(
                    item.data.scout * math.sqrt(item.fullSlot)
                )

            # 制空状態3つループ
            for j in range(3):
                if item.data.accuracy >= 3:
                    contact120[j].append(item.contactSelectRates[j])
                elif item.data.accuracy == 2:
                    contact117[j].append(item.contactSelectRates[j])
                else:
                    contact112[j].append(item.contactSelectRates[j])

        # 触接開始率 = int(sum(索敵 * sqrt(搭載)) + 1) / (70 - 15 * c)
        a = math.sqrt(sumContactValue) + 1
        contactStartRate = (
            min(a / 25, 1),
            min(a / 40, 1),
            min(a / 55, 1),
        )

        # 実触接率 = [ 0:確保, 1:優勢, 2:劣勢 ]
        actualContactRate = (
            ContactRate(0, 0, 0, 0, 0),
            ContactRate(0, 0, 0, 0, 0),
            ContactRate(0, 0, 0, 0, 0),
        )
        _sum = 1
        # 制空状態3つループ
        # 開始触接率
        for i, tmpRate in enumerate(contactStartRate):

            # 補正のデカいものから優先的に
            if len(contact120[i]):
                _sum = 1
                # 全て選択されない確率の導出
                for c120j in contact120[i]:
                    # 発動しない率
                    _sum *= 1 - c120j

                # 選択される率
                rate = tmpRate * (1 - _sum)
                actualContactRate[i].contact120 = rate
                tmpRate -= rate

            if len(contact117[i]):
                _sum = 1
                # 全て選択されない確率の導出
                for c117j in contact117[i]:
                    # 発動しない率
                    _sum *= 1 - c117j

                # 選択される率
                rate = tmpRate * (1 - _sum)
                actualContactRate[i].contact117 = rate
                tmpRate -= rate

            if len(contact112[i]):
                _sum = 1
                # 全て選択されない確率の導出
                for c112j in contact112[i]:
                    # 発動しない率
                    _sum *= 1 - c112j

                # 選択される率
                rate = tmpRate * (1 - _sum)
                actualContactRate[i].contact112 = rate
                tmpRate -= rate

        contactTable = (
            ContactRate(0, 0, 0, 0, 0),
            ContactRate(0, 0, 0, 0, 0),
            ContactRate(0, 0, 0, 0, 0),
        )

        # 制空状態3つループ
        for i, rate in enumerate(actualContactRate):
            sumRate = rate.contact120 + rate.contact117 + rate.contact112

            # 開始触接率
            contactTable[i].startRate = 100 * contactStartRate[i]
            # 順に120% 117% 112% の選択率
            contactTable[i].contact120 = 100 * rate.contact120
            contactTable[i].contact117 = 100 * rate.contact117
            contactTable[i].contact112 = 100 * rate.contact112
            # 最終的な合計の触接率
            contactTable[i].sumRate = min(100 * sumRate, 100)

        return contactTable
