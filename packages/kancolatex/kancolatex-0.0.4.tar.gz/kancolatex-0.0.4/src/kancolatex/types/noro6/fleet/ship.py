from __future__ import annotations

import copy
import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Optional
from typing_extensions import Sequence
from typing_extensions import TypedDict

from .... import utils
from ....logger import LOGGER
from ... import const
from ...const import FleetType
from ...const import ShipType
from ..aerial_combat import AntiAirCutIn
from ..aerial_combat import ShootDownInfo
from ..interface import ShipBase
from ..item import Item
from ..item import ItemBonusStatus
from ..item import ItemBuilder
from ..item import bonusData
from ..item import getTotalBonus
from .ship_master import ShipMaster


@dataclass(slots=True)
class ShipBuilder:
    ship: Ship | None = None
    master: Optional[ShipMaster] = None
    items: Optional[list[Item]] = None
    exItem: Optional[Item] = None
    level: Optional[int] = None
    luck: Optional[int] = None
    asw: Optional[int] = None
    antiAir: Optional[int] = None
    hp: Optional[int] = None
    isEscort: Optional[bool] = None
    isActive: Optional[bool] = None
    area: Optional[int] = None
    uniqueId: Optional[int] = None
    releaseExpand: Optional[bool] = None
    noStock: Optional[bool] = None
    isTray: Optional[bool] = None
    spEffectItemId: Optional[int] = None


@dataclass(slots=True)
class ShipDisplayStatus:
    HP: int = 0
    firePower: int = 0
    armor: int = 0
    torpedo: int = 0
    avoid: int = 0
    antiAir: int = 0
    asw: int = 0
    LoS: int = 0
    luck: int = 0
    range: int = 0
    accuracy: int = 0
    bomber: int = 0


@dataclass(slots=True)
class Ship(ShipBase):
    builder: InitVar[ShipBuilder]

    data: ShipMaster = field(default_factory=ShipMaster)
    items: list[Item] = field(default_factory=list)
    exItem: Item = field(default_factory=lambda: Item(ItemBuilder()))
    level: int = 0
    displayStatus: ShipDisplayStatus = field(
        default_factory=lambda: ShipDisplayStatus()
    )
    itemBonusStatus: ItemBonusStatus = field(default_factory=lambda: ItemBonusStatus())
    itemBonuses: list[ItemBonusStatus] = field(default_factory=list)
    hp: int = 0
    luck: int = 0
    baseDayBattleFirePower: float = 0
    supportFirePower: int = 0
    nightBattleFirePower: float = 0
    antiAir: int = 0
    actualArmor: int = 0
    scout: int = 0
    itemsScout: float = 0
    avoid: int = 0
    accuracy: float = 0
    supportAccuracy: int = 0
    asw: int = 0
    improveAsw: int = 0
    itemAsw: int = 0
    enabledTSBK: bool = False
    tp: float = 0
    speed: int = 0
    fuel: int = 0
    ammo: int = 0
    area: int = 0
    uniqueId: int = 0
    hunshinRate: float = 0
    isActive: bool = True
    isEmpty: bool = False
    antiAirBonus: float = 0
    isEscort: bool = False
    hasJet: bool = False
    fullAirPower: int = 0
    supportAirPower: int = 0
    supportAswAirPower: int = 0
    enabledASWSupport: bool = False
    antiAirCutIn: list[AntiAirCutIn] = field(default_factory=list)
    specialKokakuCount: int = 0
    kokakuCount: int = 0
    specialKijuCount: int = 0
    kijuCount: int = 0
    antiAirRadarCount: int = 0
    surfaceRadarCount: int = 0
    koshaCount: int = 0
    sumSPRos: int = 0
    nightContactRate: float = 0
    enabledAircraftNightAttack: bool = False
    nightAttackCrewFireBonus: int = 0
    nightAttackCrewBomberBonus: int = 0
    releaseExpand: bool = False
    noStock: bool = False
    isTray: bool = False
    spEffectItemId: int = 0
    missingAsw: int = 0
    needTSBKLevel: int = 0
    fixDown: float = 0
    rateDown: float = 0
    allPlaneDeathRate: int = 0

    def __post_init__(self, builder: ShipBuilder) -> None:
        if builder.ship is not None:
            self.data = (
                builder.master if builder.master is not None else builder.ship.data
            )
            self.level = (
                builder.level if builder.level is not None else builder.ship.level
            )
            self.luck = builder.luck if builder.luck is not None else builder.ship.luck
            self.asw = builder.asw if builder.asw is not None else builder.ship.asw
            self.antiAir = (
                builder.antiAir if builder.antiAir is not None else builder.ship.antiAir
            )
            self.items = (
                builder.items.copy()
                if builder.items is not None
                else builder.ship.items.copy()
            )
            self.exItem = (
                builder.exItem if builder.exItem is not None else builder.ship.exItem
            )
            self.isActive = (
                builder.isActive
                if builder.isActive is not None
                else builder.ship.isActive
            )
            self.isEscort = (
                builder.isEscort
                if builder.isEscort is not None
                else builder.ship.isEscort
            )
            self.hp = builder.hp if builder.hp is not None else builder.ship.hp
            self.area = builder.area if builder.area is not None else builder.ship.area
            self.uniqueId = (
                builder.uniqueId
                if builder.uniqueId is not None
                else builder.ship.uniqueId
            )
            self.releaseExpand = (
                builder.releaseExpand
                if builder.releaseExpand is not None
                else builder.ship.releaseExpand
            )
            self.noStock = builder.noStock if builder.noStock is not None else False
            self.isTray = (
                builder.isTray if builder.isTray is not None else builder.ship.isTray
            )
            self.spEffectItemId = (
                builder.spEffectItemId
                if builder.spEffectItemId is not None
                else builder.ship.spEffectItemId
            )
        else:
            self.data = builder.master if builder.master is not None else ShipMaster()  # type: ignore
            self.level = builder.level if builder.level is not None else 99
            self.luck = builder.luck if builder.luck is not None else self.data.luck
            self.asw = (
                builder.asw
                if builder.asw is not None
                else Ship.getStatusFromLevel(
                    self.level, self.data.maxAsw, self.data.minAsw
                )
            )
            self.antiAir = (
                builder.antiAir if builder.antiAir is not None else self.data.antiAir
            )
            self.items = builder.items.copy() if builder.items is not None else list()
            self.exItem = (
                builder.exItem if builder.exItem is not None else Item(ItemBuilder())
            )
            self.isActive = builder.isActive if builder.isActive is not None else True
            self.isEscort = builder.isEscort if builder.isEscort is not None else False
            self.hp = builder.hp if builder.hp is not None else self.data.hp
            self.area = builder.area if builder.area is not None else 0
            self.uniqueId = builder.uniqueId if builder.uniqueId is not None else 0
            self.releaseExpand = (
                builder.releaseExpand if builder.releaseExpand is not None else True
            )
            self.noStock = builder.noStock if builder.noStock is not None else False
            self.isTray = builder.isTray if builder.isTray is not None else False
            self.spEffectItemId = (
                builder.spEffectItemId if builder.spEffectItemId is not None else 0
            )

        # 装備数をマスタのスロット数に合わせる
        if len(self.items) < self.data.slotCount:
            # 少ないケース => 追加
            for i in range(len(self.items), self.data.slotCount):
                self.items.append(Item(ItemBuilder(slot=self.data.slots[i])))
        elif len(self.items) > self.data.slotCount:
            # 多いケース => 絞る
            self.items = self.items[: self.data.slotCount]

        # 空の装備の搭載数を戻す
        for i, (fullSlot, item) in enumerate(zip(self.data.slots, self.items)):
            if item.data.id == 0 and fullSlot > 0:
                self.items[i] = Item(ItemBuilder(slot=fullSlot))

        # 異常値によるステータス修正
        if self.asw == 0 and self.data.minAsw and self.data.maxAsw:
            self.asw = Ship.getStatusFromLevel(
                self.level, self.data.maxAsw, self.data.minAsw
            )
        if self.luck == 0 and self.data.luck:
            self.luck = self.data.luck
        if self.hp == 0 and self.data.hp:
            self.hp = self.data.hp

        # レベルによる耐久修正
        if self.level > 99 and self.hp < self.data.hp2:
            self.hp = self.data.hp2
        elif self.level <= 99 and (self.hp == self.data.hp2 or self.hp == 0):
            self.hp = self.data.hp

        self.fullAirPower = 0
        self.supportAirPower = 0
        self.supportAswAirPower = 0
        self.antiAirBonus = 0
        self.itemsScout = 0
        self.itemAsw = 0
        self.hasJet = False
        self.specialKokakuCount = 0
        self.kokakuCount = 0
        self.kijuCount = 0
        self.actualArmor = self.data.armor
        self.specialKijuCount = 0
        self.antiAirRadarCount = 0
        self.surfaceRadarCount = 0
        self.koshaCount = 0
        self.hunshinRate = 0
        self.enabledTSBK = False
        self.enabledASWSupport = False
        self.sumSPRos = 0
        self.nightBattleFirePower = 0
        self.nightAttackCrewFireBonus = 0
        self.nightAttackCrewBomberBonus = 0
        self.accuracy = 0
        self.fuel = max(
            math.floor(self.data.fuel * 0.85) if self.level > 99 else self.data.fuel, 1
        )
        self.ammo = max(
            math.floor(self.data.ammo * 0.85) if self.level > 99 else self.data.ammo, 1
        )

        # 以下、計算により算出するステータス
        # レベルより算出
        self.scout = Ship.getStatusFromLevel(
            self.level, self.data.maxScout, self.data.minScout
        )
        self.avoid = Ship.getStatusFromLevel(
            self.level, self.data.maxAvoid, self.data.minAvoid
        )
        self.improveAsw = max(
            self.asw
            - Ship.getStatusFromLevel(self.level, self.data.maxAsw, self.data.minAsw),
            0,
        )

        # ステータス表示値
        self.displayStatus = ShipDisplayStatus(
            HP=self.hp,
            firePower=self.data.fire,
            armor=self.data.armor,
            torpedo=self.data.torpedo,
            avoid=self.avoid,
            antiAir=self.antiAir,
            asw=self.asw,
            LoS=self.scout,
            luck=self.luck,
            range=max(self.data.range, 1),
            accuracy=0,
            bomber=0,
        )
        self.itemBonusStatus = ItemBonusStatus()

        # 輸送量(艦娘分)
        self.tp = self._getTransportPower()

        # 対潜支援参加可能な艦種であるかどうか
        enabledASWSupport: bool = self.data.type in {
            ShipType.CVL,
            ShipType.AV,
            ShipType.AO,
            ShipType.AO_2,
            ShipType.LHA,
            ShipType.CL,
            ShipType.CT,
        }

        # 夜偵"失敗率"
        nightContactFailureRate: float = 1
        # 装備一覧より取得
        items = (*self.items, self.exItem)
        # 装備ボーナス算出
        self.itemBonuses = Ship.getItemBonus(self.data, items)
        # 海色リボン 白たすき系
        if self.spEffectItemId == 1:
            # 海色リボン
            self.itemBonuses.append(ItemBonusStatus(raig=1, souk=1))
        elif self.spEffectItemId == 2:
            # 白たすき
            self.itemBonuses.append(ItemBonusStatus(houg=2, kaih=2))

        crewTorpedoBonus: int = 0
        crewBomberBonus: int = 0
        crewBonuses = tuple(v for v in self.itemBonuses if v.fromTypeId == 35)
        for bonus in crewBonuses:
            # 搭乗員雷装ボーナスを取得
            if bonus.torpedo and crewTorpedoBonus < bonus.torpedo:
                crewTorpedoBonus = bonus.torpedo
            # 搭乗員爆装ボーナスを取得
            if bonus.bombing and crewBomberBonus < bonus.bombing:
                crewBomberBonus = bonus.torpedo
            # 搭乗員夜襲(爆装)ボーナスを加算
            if bonus.bombing:
                self.nightAttackCrewBomberBonus += bonus.bombing
            # 搭乗員夜襲(火力)ボーナスを加算
            if bonus.firepower:
                self.nightAttackCrewFireBonus += bonus.firepower

        # 雷装ボーナス適用装備(最も雷装 or 爆装が高い
        maximumAttacker = Item(ItemBuilder())

        for item in items:

            # 装備ステータス 単純加算
            self.displayStatus.firePower += item.data.fire
            self.displayStatus.armor += item.data.armor
            self.displayStatus.torpedo += item.data.torpedo
            self.displayStatus.avoid += item.data.avoid
            self.displayStatus.antiAir += item.data.antiAir
            self.displayStatus.LoS += item.data.scout
            self.displayStatus.bomber += item.data.bomber
            self.displayStatus.accuracy += item.data.accuracy
            self.accuracy += item.data.accuracy
            self.supportAccuracy += item.data.accuracy

            # 装備防空ボーナス
            self.antiAirBonus += item.antiAirBonus
            # 装備索敵関係
            self.itemsScout += item.itemScout
            # 対潜値
            self.itemAsw += item.data.asw
            # 輸送量
            self.tp += item.tp
            # 装甲値
            self.actualArmor += item.data.armor

            # 射程(大きくなるなら)
            if item.data.range > self.displayStatus.range:
                self.displayStatus.range = item.data.range

            if (
                item.fullSlot > 0
                and item.data.isPlane
                and not item.data.isRecon
                and not item.data.isABAttacker
            ):
                # 制空値を加算 (搭載数1以上 航空機 偵察機でない 陸攻でない)
                self.fullAirPower += item.fullAirPower
                self.supportAirPower += item.supportAirPower

            self.supportAirPower += item.supportAirPower

            # ジェット機所持
            if not self.hasJet and item.data.isJet:
                self.hasJet = True

            if item.fullSlot > 0 and (
                item.data.apiTypeId == 10 or item.data.apiTypeId == 11
            ):
                # 水偵/水爆の裝備索敵值 * int(sqrt(水偵/水爆の機數)
                self.sumSPRos += item.data.scout * math.floor(math.sqrt(item.fullSlot))

            # 雷装ボーナス
            if item.data.isAttacker:
                item.attackTorpedoBonus = 0
                item.crewTorpedoBonus = crewTorpedoBonus
                item.crewBomberBonus = crewBomberBonus

                temp = max(maximumAttacker.data.torpedo, maximumAttacker.data.bomber)
                value = max(item.data.torpedo, item.data.bomber)
                if temp < value:
                    # 最も雷装 or 爆装の高い機体を一時保持
                    maximumAttacker = item

            if item.data.iconTypeId == 11:
                # 対空電探
                if item.data.antiAir > 1:
                    self.antiAirRadarCount += 1
                # 水上電探
                if item.data.scout > 4:
                    self.surfaceRadarCount += 1
            if item.data.iconTypeId == 16:
                # 特殊高角砲
                if item.data.isSpecial:
                    self.specialKokakuCount += 1
                else:
                    # 高角砲
                    self.kokakuCount += 1
            if item.data.apiTypeId == 21:
                # 特殊機銃
                if item.data.isSpecial:
                    self.specialKijuCount += 1
                else:
                    # 機銃
                    self.kijuCount += 1
            # 高射装置カウント
            if item.data.apiTypeId == 36:
                self.koshaCount += 1

            # 対潜支援参加可装備チェック
            if (
                not self.enabledASWSupport
                and enabledASWSupport
                and item.data.apiTypeId in const.ENABLED_ASW_SUPPORT
            ):
                self.enabledASWSupport = True

            # 夜偵
            if item.fullSlot and item.data.iconTypeId == 50:
                # 夜偵発動率 = (int(sqrt(偵察機索敵值)*sqrt(Lv))) / 25
                nightContactFailureRate -= nightContactFailureRate * min(
                    (
                        math.floor(math.sqrt(item.data.scout) * math.sqrt(self.level))
                        / 25
                    ),
                    1,
                )

            # 夜戦火力
            self.nightBattleFirePower += item.bonusNightFire
            self.accuracy += item.bonusAccuracy

        self.nightContactRate = 1 - nightContactFailureRate

        # 速力計算
        self.speed = self.getShipSpeed()

        if len(self.itemBonuses):
            self.itemBonusStatus = getTotalBonus(self.itemBonuses)
            self.displayStatus.firePower += self.itemBonusStatus.firepower
            self.displayStatus.armor += self.itemBonusStatus.armor
            self.displayStatus.torpedo += self.itemBonusStatus.torpedo
            self.displayStatus.avoid += self.itemBonusStatus.evasion
            self.displayStatus.antiAir += self.itemBonusStatus.antiAir
            self.displayStatus.asw += self.itemBonusStatus.asw
            self.displayStatus.LoS += self.itemBonusStatus.los
            self.displayStatus.range += self.itemBonusStatus.range
            self.displayStatus.bomber += self.itemBonusStatus.bombing
            self.displayStatus.accuracy += self.itemBonusStatus.accuracy
            self.accuracy += self.itemBonusStatus.accuracy

        # 空母夜襲発動判定
        self.enabledAircraftNightAttack = self.data.isCV and (
            self.data.id in {545, 599, 610, 883}
            or any(w.data.id == 258 or w.data.id == 259 for w in items)
        )

        if self.enabledAircraftNightAttack:
            # 空母夜襲火力に置き換え
            self.nightBattleFirePower = self.getAircraftNightAttackPrePower(0)
        else:
            # 夜戦火力加算
            self.nightBattleFirePower += (
                self.displayStatus.firePower + self.displayStatus.torpedo
            )

        # 航空戦雷装ボーナス適用装備抽出 & セット
        if len(self.itemBonuses) and maximumAttacker.data.isAttacker:
            tropBomberTorpedoBonuses: list[int] = []
            seaplaneBomberTorpedoBonuses: list[int] = []

            for bonus in self.itemBonuses:
                if bonus.torpedo and bonus.fromTypeId and bonus.fromTypeId == 8:
                    # 艦攻による雷装ボーナス
                    tropBomberTorpedoBonuses.append(bonus.torpedo)
                elif bonus.torpedo and bonus.fromTypeId and bonus.fromTypeId == 11:
                    # 水上爆撃機による雷装ボーナス
                    seaplaneBomberTorpedoBonuses.append(bonus.torpedo)

            if len(tropBomberTorpedoBonuses):
                # 適用装備の最も低い雷装ボーナスを加算
                maximumAttacker.attackTorpedoBonus += next(
                    iter(sorted(tropBomberTorpedoBonuses))
                )
            if len(seaplaneBomberTorpedoBonuses):
                # 適用装備の最も高い雷装ボーナスを加算
                maximumAttacker.attackTorpedoBonus += next(
                    iter(sorted(seaplaneBomberTorpedoBonuses, reverse=True))
                )

        # 発動可能対空CI取得
        self.antiAirCutIn = ShootDownInfo.getAntiAirCutIn(self)

        # 防空ボーナス 小数切捨て 100倍されていたため戻す
        self.antiAirBonus = math.floor(self.antiAirBonus / 100)

        if self.kijuCount:
            # 噴進率計算
            self.hunshinRate = self._getHunshinRate()

        # 先制対潜の可否を判定
        self.enabledTSBK = self._getEnabledTSBK()

        # 装備もマスタもない場合空として計算対象から省く
        self.isEmpty = self.data.id == 0 and not any(v.data.id > 0 for v in self.items)

        # 昼戦基礎火力算出
        self.baseDayBattleFirePower = Ship.getDayBattleFirePower(
            self, FleetType.Single, False
        )
        self.supportFirePower = self.getSupportFirePower()

    @staticmethod
    def getDayBattleFirePower(ship: Ship, fleetType: int, enemyIsUnion: bool) -> float:
        """昼戦砲撃火力を返却"""

        dayBattleFirePower: float = 0
        correct: int = 0

        if fleetType == FleetType.Carrier:
            # 空母機動
            if ship.isEscort:
                # 随伴 => 敵連合-5 敵通常+10
                correct = -5 if enemyIsUnion else 10
            else:
                # 本隊 => +2
                correct = 2
        elif fleetType == FleetType.Surface:
            # 水上打撃
            if ship.isEscort:
                # 随伴 => -5
                correct = -5
            else:
                # 本隊 => 敵連合+2 敵通常+10
                correct = 2 if enemyIsUnion else 10
        elif fleetType == FleetType.Transport:
            # 輸送護衛
            if ship.isEscort:
                # 随伴 => 敵連合-5 敵通常+10
                correct = -5 if enemyIsUnion else 10
            else:
                # 本隊 => -5
                correct = -5

        items = (*ship.items, ship.exItem)
        sumRemodelBonusFirePower: float = 0
        for item in items:
            sumRemodelBonusFirePower += item.bonusFire

        if ship.data.isCV or (
            ship.data.id in {352, 717}
            and any(
                v.data.isAttacker and v.data.apiTypeId != 11 and not v.data.isAswPlane
                for v in items
            )
        ):
            # 空母系 or (速吸 or 山汐丸 + 艦攻艦爆)
            dayBattleFirePower = (
                math.floor(
                    1.5
                    * (
                        ship.displayStatus.firePower
                        + ship.displayStatus.torpedo
                        + math.floor(1.3 * ship.displayStatus.bomber)
                        + sumRemodelBonusFirePower
                        + correct
                    )
                )
                + 55
            )
        else:
            dayBattleFirePower = (
                ship.displayStatus.firePower + sumRemodelBonusFirePower + correct + 5
            )

        return dayBattleFirePower

    def getSupportFirePower(self) -> int:
        """支援火力を返却"""

        supportFirePower: int = 0
        if self.data.isCV or (
            self.data.id in {717}
            and any(v.data.isAttacker and not v.data.isAswPlane for v in self.items)
        ):
            # 空母系 山汐丸
            supportFirePower = (
                math.floor(
                    1.5
                    * (
                        self.displayStatus.firePower
                        + self.displayStatus.torpedo
                        + math.floor(1.3 * self.displayStatus.bomber)
                        - 1
                    )
                )
                + 55
            )
        else:
            supportFirePower = self.displayStatus.firePower + 4

        return supportFirePower

    @staticmethod
    def getStatusFromLevel(_level: int, _max: int, _min: int) -> int:
        """艦娘Lvにより算出可能なステータスを計算"""

        value: int = 0
        if _level == 99 and _max > 0:
            # Lv99ステ
            value = _max
        elif _max > 0:
            # Lv99以外 算出可能な場合
            value = math.floor((_max - _min) * (_level / 99) + _min)
            LOGGER.debug(
                f"{_level = } {_max = } {_min = } {(_max - _min) * (_level / 99) + _min}"
            )
        return value

    @staticmethod
    def getRequiredLevel(_target: int, _max: int, _min: int) -> int:
        """指定数値に到達するために必要なLevelを算出"""
        if not (_max - _min):
            return 0
        return max(math.ceil((99 * (_target - _min)) / (_max - _min)), 1)

    @staticmethod
    def getAccuracyValue(level: int, luck: int) -> int:
        """命中項を返却"""
        return math.floor(2 * math.sqrt(level) + 1.5 * math.sqrt(luck))

    @staticmethod
    def getRequiredLevelAccuracy(target: int, luck: int) -> int:
        """指定命中項に到達するために必要なLevelを算出"""
        if target - (3 / 2) * math.sqrt(luck) >= 0:
            return math.ceil(((target - (3 / 2) * math.sqrt(luck)) ** 2) / 4)
        return 0

    @staticmethod
    def getRequiredLuckAccuracy(target: int, level: int) -> int:
        """指定命中項に到達するために必要な運を算出"""
        return math.ceil((4 / 9) * (target - (2 * math.sqrt(level))) ** 2)

    @staticmethod
    def getAvoidValue(avoid: int, luck: int) -> int:
        """回避項を返却"""
        baseAvoid = math.floor(avoid + math.sqrt(2 * luck))
        if avoid >= 65:
            return math.floor(55 + 2 * math.sqrt(baseAvoid - 65))
        if avoid >= 45:
            return math.floor(40 + 3 * math.sqrt(baseAvoid - 40))
        return baseAvoid

    @staticmethod
    def getCIValue(level: int, luck: int) -> int:
        """CI項を返却"""
        if luck >= 50:
            return math.floor(65 + math.sqrt(luck - 50) + 0.8 * math.sqrt(level))

        return math.floor(15 + luck + 0.75 * math.sqrt(level))

    @staticmethod
    def getRequiredLevelCI(target: int, luck: int) -> int:
        """指定CI項に到達するために必要なLevelを算出"""
        if luck >= 50:
            if target - (65 + math.sqrt(luck - 50)) >= 0:
                return math.ceil(
                    (25 * (target - (65 + math.sqrt(luck - 50))) ** 2) / 16
                )
            return 0

        if target - (15 + luck) >= 0:
            return math.ceil((16 * (target - (15 + luck)) ** 2) / 9)

        return 0

    @staticmethod
    def getRequiredLuckCI(target: int, level: int) -> int:
        """指定CI項に到達するために必要な運を算出"""
        luck = math.ceil(target - (15 + 0.75 * math.sqrt(level)))
        if luck > 50:
            # 運50を超える場合は別式
            return math.ceil((target - (65 + 0.8 * math.sqrt(level))) ** 2 + 50)
        return luck

    def getShipSpeed(self) -> int:
        """速力を決定"""

        items = (*self.items, self.exItem)
        hasTurbine = any(v.data.id == 33 for v in items)
        boilerCount = len(tuple(v for v in items if v.data.id == 34))
        newModelBoilerCount = len(tuple(v for v in items if v.data.id == 87))
        totalBoilerCount = boilerCount + newModelBoilerCount
        # 改修★+7以上の新型缶個数
        remodeledNewModelBoilerCount = len(
            tuple(v for v in items if v.data.id == 87 and v.remodel >= 7)
        )

        if self.data.speed == 10:
            # 高速
            if self.data.type2 in {22, 81, 43, 33, 31, 9} or self.data.id == 951:
                # 島風型, Ташкент級, 天津風改二, 大鳳型, 翔鶴型, 利根型, 最上型
                if (
                    (hasTurbine and newModelBoilerCount)
                    or (hasTurbine and totalBoilerCount >= 2)
                    or (remodeledNewModelBoilerCount >= 2)
                ):
                    # タービン + 新型缶 または タービン + いずれかの缶x2 または 改修★+7以上の新型缶x2 => 最速
                    return 20
                if (hasTurbine and totalBoilerCount) or remodeledNewModelBoilerCount:
                    # いずれかの缶 または 改修★+7以上の新型缶
                    return 15
            elif self.data.type2 in {41, 17, 25, 6, 65, 37} or self.data.originalId in {
                181,
                404,
                331,
            }:
                # 阿賀野型, 蒼龍型, 飛龍型, 金剛型, Iowa級, 大和型
                # 天津風, 雲龍, 天城
                if hasTurbine and newModelBoilerCount and totalBoilerCount >= 2:
                    # 新型缶 + いずれかの缶 => 最速
                    return 20
                if hasTurbine and totalBoilerCount:
                    # いずれかの缶 => 高速+
                    return 15
            elif self.data.type2 in {3, 87} or self.data.type == ShipType.AV:
                # 加賀型, Samuel, 水母
                if hasTurbine and totalBoilerCount:
                    # いずれかの缶 => 高速+
                    return 15
            else:
                if hasTurbine and (newModelBoilerCount >= 2 or totalBoilerCount >= 2):
                    # 新型缶x2 || いずれかの缶x3 => 最速
                    return 20
                if hasTurbine and totalBoilerCount:
                    # いずれかの缶 => 高速+
                    return 15
        elif self.data.speed == 5:
            # 低速
            if self.data.type2 in {37} or self.data.id == 541 or self.data.id == 573:
                # 大和型, 長門改二, 陸奥改二
                if hasTurbine and newModelBoilerCount and totalBoilerCount >= 3:
                    # タービン + 新型缶含むいずれかの缶x3 => 最速
                    return 20
                if hasTurbine and remodeledNewModelBoilerCount >= 2:
                    # タービン + 改修★7新型缶x2 => 最速
                    return 20
                if hasTurbine and newModelBoilerCount and totalBoilerCount >= 2:
                    # タービン + 新型缶含むいずれかの缶x2 => 高速+
                    return 15
                if hasTurbine and remodeledNewModelBoilerCount:
                    # タービン + 改修★7新型缶 => 高速+
                    return 15
                if hasTurbine and totalBoilerCount:
                    # タービン + いずれかの缶 => 高速
                    return 10
            elif self.data.id == 894 or self.data.id == 899:
                # 鳳翔改二 / 戦
                if hasTurbine and newModelBoilerCount and totalBoilerCount >= 2:
                    # タービン + 新型缶x2 => 最速
                    return 20
                if hasTurbine and newModelBoilerCount:
                    # タービン + 新型缶 => 高速+
                    return 15
                if hasTurbine and totalBoilerCount:
                    # タービン + いずれかの缶 => 高速
                    return 10
                if newModelBoilerCount:
                    # 新型缶 => 高速
                    return 10
            elif self.data.originalId == 561 or self.data.id == 623:
                # Samuel B.Roberts, 夕張改二特
                if hasTurbine and (newModelBoilerCount >= 2 or totalBoilerCount >= 3):
                    # タービン + (新型缶x2 || いずれかの缶x3) => 高速+
                    return 15
                if hasTurbine:
                    # タービン => 高速
                    return 10
            elif self.data.type2 == 109:
                # 潜高型
                if hasTurbine and newModelBoilerCount:
                    # タービン + 新型缶 => 高速+
                    return 15
                if newModelBoilerCount or (hasTurbine or totalBoilerCount):
                    # タービン + いずれかの缶 || 新型缶 => 高速
                    return 10
            elif (
                self.data.type == ShipType.SS
                or self.data.type == ShipType.SSV
                or self.data.type2 in {45, 49, 60}
            ):
                # 潜水艦, 潜水空母, 特種船丙型, 工作艦, 改風早型
                if hasTurbine and totalBoilerCount:
                    # タービン + いずれかの缶 => 高速
                    return 10
            else:
                # その他の低速艦
                if hasTurbine and (newModelBoilerCount >= 2 or totalBoilerCount >= 2):
                    # タービン + (新型缶x2 || いずれかの缶x3) => 高速+
                    return 15

                if hasTurbine and totalBoilerCount:
                    # タービン + いずれかの缶 => 高速
                    return 10

        return self.data.speed

    def getProfCriticalBonus(self) -> float:
        """この艦の熟練クリティカルボーナスを算出"""
        bonus: float = 0
        for i, item in enumerate(self.items):
            # 対象は搭載数が存在する攻撃機か大型飛行艇
            if item.slot > 0 and (item.data.isAttacker or item.data.apiTypeId == 41):
                c = (0, 1, 2, 3, 4, 5, 7, 10)[item.levelAlt]

                if item.data.isAswPlane:
                    # 対潜哨戒機
                    if i == 0:
                        # 隊長機補正
                        bonus += math.floor(math.sqrt(item.level) + c) / 128
                    else:
                        bonus += math.floor(math.sqrt(item.level) + c) / 242
                elif i == 0:
                    # 隊長機補正
                    bonus += math.floor(math.sqrt(item.level) + c) / 100
                else:
                    bonus += math.floor(math.sqrt(item.level) + c) / 200

        # 補正値 = int(√内部熟練度  + C) / (隊長機によって変動 100 ~ 240)
        return 1 + bonus

    @staticmethod
    def getItemBonus(ship: ShipMaster, items: Sequence[Item]) -> list[ItemBonusStatus]:
        """装備ボーナスを取得"""
        if not any(bool(v.data.id) for v in items):
            return []

        sumBonuses: list[ItemBonusStatus] = []

        antiAirRadarCount: int = 0
        surfaceRadarCount: int = 0
        accuracyRadarCount: int = 0

        for item in items:
            # 対空電探カウント
            if item.data.iconTypeId == 11 and item.data.antiAir > 1:
                antiAirRadarCount += 1
            # 水上電探カウント
            if item.data.iconTypeId == 11 and item.data.scout > 4:
                surfaceRadarCount += 1
            # 命中付き電探カウント
            if item.data.iconTypeId == 11 and item.data.accuracy >= 8:
                accuracyRadarCount += 1

        (_id, _type, _type2, _originalId) = (
            ship.id,
            ship.type,
            ship.type2,
            ship.originalId,
        )

        for __debug_i, bonusI in enumerate(bonusData()):
            _types, _ids, _bonuses = (
                bonusI.equipmentTypes,
                bonusI.equipmentIds,
                bonusI.bonuses,
            )
            if (_types is not None or _ids is not None) and _bonuses:
                fitItems: list[Item] = []

                # そもそもの存在チェック
                if _types is not None:
                    fitItems = [v for v in items if v.data.apiTypeId in _types]
                elif _ids is not None:
                    fitItems = [v for v in items if v.data.id in _ids]
                if not fitItems or not len(fitItems):
                    continue

                for bonus in _bonuses:
                    # 未改造判定
                    if bonus.shipIds is not None and not _originalId in bonus.shipIds:
                        continue
                    # 艦型判定
                    if bonus.shipClass is not None and not _type2 in bonus.shipClass:
                        continue
                    # 国籍判定
                    if bonus.shipNationalities is not None and not _type2 in {
                        c
                        for v in bonus.shipNationalities
                        for c in const.CountryTable.get(v, set())
                    }:
                        continue
                    # 艦種判定
                    if bonus.shipTypes is not None and not _type in bonus.shipTypes:
                        continue
                    # 艦id判定
                    if (
                        bonus.shipMasterIds is not None
                        and not _id in bonus.shipMasterIds
                    ):
                        continue
                    # 対空電探判定
                    if bonus.bonusesIfAirRadar is not None and not antiAirRadarCount:
                        continue
                    # 水上電探判定
                    if (
                        bonus.bonusesIfSurfaceRadar is not None
                        and not surfaceRadarCount
                    ):
                        continue
                    # 命中付き電探判定
                    if (
                        bonus.bonusesIfAccuracyRadar is not None
                        and not accuracyRadarCount
                    ):
                        continue

                    # 装備固有id判定
                    if bonus.equipmentRequired is not None:
                        requiredItems = bonus.equipmentRequired
                        requiredRemodel = (
                            bonus.equipmentRequiresLevel
                            if bonus.equipmentRequiresLevel is not None
                            else 0
                        )
                        targetItems = tuple(
                            v for v in items if v.data.id in requiredItems
                        )
                        # 個数判定
                        if (
                            bonus.numberOfEquipmentsRequired
                            and len(targetItems) < bonus.numberOfEquipmentsRequired
                        ):
                            continue
                        elif requiredRemodel and not any(
                            v.remodel >= requiredRemodel for v in targetItems
                        ):
                            continue
                        elif not len(targetItems):
                            continue
                    # 装備種別判定
                    if bonus.equipmentTypesRequired is not None and not any(
                        v.data.apiTypeId in bonus.equipmentTypesRequired for v in items
                    ):
                        continue

                    # 改修判定
                    minRemodel = bonus.equipmentLevel
                    if minRemodel is not None:
                        remodelFits = tuple(
                            v for v in fitItems if v.remodel >= minRemodel
                        )
                        # 合致した装備からさらに改修値で判定
                        if not len(remodelFits):
                            continue

                        # 合致した装備からさらに個数で判定
                        if (
                            bonus.numberOfEquipmentsRequiredAfterOtherFilters
                            and len(remodelFits)
                            < bonus.numberOfEquipmentsRequiredAfterOtherFilters
                        ):
                            continue
                        elif not bonus.numberOfEquipmentsRequiredAfterOtherFilters:
                            # 数制限がない場合はその数だけ回す
                            for remodelFitsB in remodelFits:
                                bonusesCopy = bonus.bonuses.model_copy()
                                bonusesCopy.fromTypeId = remodelFitsB.data.apiTypeId
                                sumBonuses.append(bonusesCopy)
                        else:
                            # ようやくBonusを適用
                            bonusesCopy = bonus.bonuses.model_copy()
                            bonusesCopy.fromTypeId = remodelFits[0].data.apiTypeId
                            sumBonuses.append(bonusesCopy)
                    elif (
                        bonus.numberOfEquipmentsRequiredAfterOtherFilters
                        and len(fitItems)
                        < bonus.numberOfEquipmentsRequiredAfterOtherFilters
                    ):
                        # 合致した装備からさらに個数で判定
                        continue
                    elif not bonus.numberOfEquipmentsRequiredAfterOtherFilters:
                        # 個数制限がない場合はその数だけ回す
                        for fitItemsB in fitItems:
                            bonusesCopy = bonus.bonuses.model_copy()
                            bonusesCopy.fromTypeId = fitItemsB.data.apiTypeId
                            sumBonuses.append(bonusesCopy)
                    else:
                        # ようやくBonusを適用
                        bonusesCopy = bonus.bonuses.model_copy()
                        bonusesCopy.fromTypeId = fitItems[0].data.apiTypeId
                        sumBonuses.append(bonusesCopy)

        return sumBonuses

    def getItemBonusDiff(self, slotIndex: int) -> ItemBonusStatus:
        """
        指定したスロットにある装備特有の装備ボーナスを取得
        => 指定スロットの装備を外した場合との差分から算出する
        """

        # この装備がなかった場合のボーナスと比較した分をこの装備のボーナスとする
        baseItems = [*self.items, self.exItem]
        tempItems = copy.deepcopy(baseItems)
        tempItems[
            (
                len(tempItems) - 1
                if (slotIndex == 0 or slotIndex == const.EXPAND_SLOT_INDEX)
                else slotIndex
            )
        ] = Item(ItemBuilder())

        emptyBonus = Ship.getItemBonus(self.data, tempItems)
        # 未装備時のボーナス合計
        totalEmptyBonus = getTotalBonus(emptyBonus)
        # 装備している現在のボーナス これをベースに、未装備時のボーナスを差っ引いていく
        totalBonus = getTotalBonus(self.itemBonuses)
        # 未装備時と、装備時のボーナスの差分を取る

        totalBonus.firepower -= totalEmptyBonus.firepower
        totalBonus.torpedo -= totalEmptyBonus.torpedo
        totalBonus.antiAir -= totalEmptyBonus.antiAir
        totalBonus.armor -= totalEmptyBonus.armor
        totalBonus.asw -= totalEmptyBonus.asw
        totalBonus.evasion -= totalEmptyBonus.evasion
        totalBonus.accuracy -= totalEmptyBonus.accuracy
        totalBonus.range -= totalEmptyBonus.range
        totalBonus.bombing -= totalEmptyBonus.bombing
        totalBonus.los -= totalEmptyBonus.los

        # 海色リボン 白たすきの分を引く
        if self.spEffectItemId == 1 and totalBonus.torpedo and totalBonus.armor:
            # 海色リボン
            totalBonus.torpedo -= 1
            totalBonus.armor -= 1
        elif self.spEffectItemId == 2 and totalBonus.firepower and totalBonus.evasion:
            # 白たすき
            totalBonus.firepower -= 2
            totalBonus.evasion -= 2

        return totalBonus

    def _getEnabledTSBK(self) -> bool:
        """先制対潜の可否を判定"""
        if self.data.id == 0:
            return False

        if self.data.id in {141, 478, 624, 394, 893, 681, 906, 920} or (
            self.data.type2 == 91 and self.data.id != 941
        ):
            return True

        _type = self.data.type
        items = (*self.items, self.exItem)

        hasSonar = any(v.data.apiTypeId == 14 or v.data.apiTypeId == 40 for v in items)

        if _type == ShipType.DE:
            # 海防艦
            if self.displayStatus.asw >= 75 and self.itemAsw >= 4:
                # => 表示対潜値75 + 装備対潜値合計が4以上
                if self.displayStatus.asw >= 75:
                    return True
                self.missingAsw = 75 - self.displayStatus.asw

            if self.displayStatus.asw >= 60 and hasSonar:
                # => 表示対潜値60 + ソナー有
                if self.displayStatus.asw >= 60:
                    return True
                self.missingAsw = 60 - self.displayStatus.asw

        if self.data.type == 717:
            # 山汐丸改
            if any(v.data.isAttacker for v in items):
                # 攻撃機があるなら => 表示対潜値100 + ソナー + (攻撃機 or 対潜哨戒機 or 回転翼機)
                if hasSonar and any(
                    (v.data.isAttacker and v.data.asw >= 1) or v.data.isAswPlane
                    for v in items
                ):
                    if self.displayStatus.asw >= 100:
                        return True
                    self.missingAsw = 100 - self.displayStatus.asw
            elif hasSonar:
                if self.displayStatus.asw >= 100:
                    return True
                self.missingAsw = 100 - self.displayStatus.asw
        elif _type in {
            ShipType.DD,
            ShipType.CL,
            ShipType.CLT,
            ShipType.CT,
            ShipType.AO,
            ShipType.AO_2,
        }:
            # 駆逐 軽巡 練巡 雷巡 補給
            # => 表示対潜値100 + ソナー
            if hasSonar:
                if self.displayStatus.asw >= 100:
                    return True
            self.missingAsw = 100 - self.displayStatus.asw

        if (
            self.data.type2 == 76 and utils.indexOf(self.data.name, "改") >= 0
        ) or self.data.id == 646:
            # 大鷹型改 改二 or 加賀改二護
            # => 対潜値1以上の艦攻/艦爆 or 対潜哨戒機 or 回転翼機
            return any(
                (v.data.isAttacker and v.data.asw >= 1) or v.data.isAswPlane
                for v in items
            )

        if _type == ShipType.CVL:
            # 軽空母 / 護衛空母
            hasAswPlane = any(v.fullSlot and v.data.isAswPlane for v in items)
            hasEmptyAswPlane = any(v.fullSlot == 0 and v.data.isAswPlane for v in items)
            if hasSonar and (
                hasAswPlane or any(v.data.isAttacker and v.data.asw >= 1 for v in items)
            ):
                # => 表示対潜値100 + ソナー + (対潜値1以上の艦攻/艦爆 or 対潜哨戒機 or 回転翼機)
                if self.displayStatus.asw >= 100:
                    return True
                self.missingAsw = 100 - self.displayStatus.asw
            if (
                hasAswPlane
                or any(v.data.apiTypeId == 8 and v.data.asw >= 7 for v in items)
                or (
                    hasEmptyAswPlane
                    and any(
                        v.data.isAttacker and v.data.asw and v.fullSlot for v in items
                    )
                )
            ):
                # => 表示対潜値65 + (対潜値7以上の艦攻 or 対潜哨戒機 or 回転翼機)
                # または、表示対潜値65 + 搭載数0の対潜哨戒機 or 回転翼機 + 対潜1以上の攻撃機
                if self.displayStatus.asw >= 65:
                    return True
                self.missingAsw = 65 - self.displayStatus.asw
            if (
                hasSonar
                and (
                    hasAswPlane
                    or any(v.data.apiTypeId == 8 and v.data.asw >= 7 for v in items)
                )
                or (
                    hasEmptyAswPlane
                    and any(
                        v.data.isAttacker and v.data.asw and v.fullSlot for v in items
                    )
                )
            ):
                # => 表示対潜値50 + ソナー + (対潜値7以上の艦攻 or 対潜哨戒機 or 回転翼機)
                # 表示対潜値50 + ソナー + 搭載数0の対潜哨戒機 or 回転翼機 + 対潜1以上の攻撃機
                if self.displayStatus.asw >= 50:
                    return True
                self.missingAsw = 50 - self.displayStatus.asw

        if self.data.id == 554:
            # 日向改二
            if any(v.data.id == 326 or v.data.id == 327 for v in items):
                # => S-51J / S-51J改 どっちかが存在
                return True
            # カ号 / オ号改 / オ号改二 の数が2以上
            return (
                len(
                    tuple(
                        v.data.id == 69 or v.data.id == 324 or v.data.id == 325
                        for v in items
                    )
                )
                >= 2
            )
        if self.data.id == 411 or self.data.id == 412:
            # 扶桑型改二
            # => 表示対潜値100 + ソナー + (水上爆撃機 or 爆雷 or 対潜哨戒機 or 回転翼機)
            if hasSonar and any(
                v.data.apiTypeId == 11 or v.data.apiTypeId == 15 or v.data.isAswPlane
                for v in items
            ):
                if self.displayStatus.asw >= 100:
                    return True
                self.missingAsw = 100 - self.displayStatus.asw

        if _type == ShipType.BBV or _type == ShipType.LHA:
            # 陸軍と航空戦艦
            # => 表示対潜値100 + ソナー + (攻撃機 or 対潜哨戒機 or 回転翼機)
            if hasSonar and any(
                (v.data.isAttacker and v.data.asw >= 1) or v.data.isAswPlane
                for v in items
            ):
                if self.displayStatus.asw >= 100:
                    return True
                self.missingAsw = 100 - self.displayStatus.asw
        # 対潜値が問題で先制対潜に失敗しているなら、残りの対潜値から上げるべきレベルを算出
        if self.missingAsw > 0 and self.data.maxAsw:
            targetAsw = (self.asw - self.improveAsw) + self.missingAsw
            self.needTSBKLevel = Ship.getRequiredLevel(
                targetAsw, self.data.maxAsw, self.data.minAsw
            )

        self.missingAsw = max(self.missingAsw, 0)

        return False

    def _getTransportPower(self) -> int:
        """艦種 艦娘毎によるTPを返却"""

        # 艦種固定値
        t = self.data.type
        if t == ShipType.DD:
            return 5

        elif t == ShipType.CL:
            return 2

        elif t == ShipType.CT:
            return 6

        elif t == ShipType.CAV:
            return 4

        elif t == ShipType.BBV:
            return 7

        elif t == ShipType.AO_2 or t == ShipType.AO:
            return 15

        elif t == ShipType.AV:
            return 9

        elif t == ShipType.LHA:
            return 12

        elif t == ShipType.SSV:
            return 1

        elif t == ShipType.AS:
            return 7

        return 0

    def _getHunshinRate(self) -> float:
        rate: float = 0

        # 噴進砲改二チェック
        items = (*self.items, self.exItem)
        hunshinCount = len(tuple(v for v in items if v.data.id == 274))

        # 艦種チェック
        if hunshinCount and self.data.type in {6, 7, 10, 11, 16, 18}:
            # 艦船加重対空値(改式) = int(素対空 / 2 + Σ(装備対空値 * 装備倍率))
            antiAirWeight = self.antiAir + 2 * sum(v.antiAirWeight for v in items)
            rate = (0.9 * min(self.luck, 50) + math.floor(antiAirWeight)) / 281

            # 複数積みボーナス
            if hunshinCount == 2:
                rate += 0.15
            elif hunshinCount >= 3:
                rate += 0.3

            # 伊勢型ボーナス
            if self.data.type2 == 2:
                rate += 0.25

        return 100 * rate

    def getAircraftNightAttackPrePower(
        self, contactBonus: float = 0, isLandBase: bool = False
    ) -> float:
        """空母夜間航空攻撃の基本火力を返却"""

        # 艦娘の素火力 + 熟練甲板ボーナス(火力青字 + 爆装青地)
        power: float = (
            self.data.fire
            + self.nightAttackCrewFireBonus
            + self.nightAttackCrewBomberBonus
        )
        # 雷装ボーナス
        power += self.itemBonusStatus.torpedo

        for item in self.items:
            if not item.data.isNightAircraftItem:
                # 夜間機以外は飛ばし
                continue

            # +（夜間飛行機の火力 + 雷装(対地時無効) + 爆装）
            if isLandBase:
                power += item.data.fire + (
                    0 if item.data.isTorpedoAttacker else item.data.bomber
                )
            else:
                power += item.data.fire + (
                    item.data.torpedo
                    if item.data.isTorpedoAttacker
                    else item.data.bomber
                )

            totalStatus = (
                item.data.fire + item.data.torpedo + item.data.bomber + item.data.asw
            )
            if item.data.iconTypeId == 45 or item.data.iconTypeId == 46:
                # 夜間飛行機搭載補正 = A(3.0) × 搭載数 + B(0.45) × (火力 + 雷装 + 爆装 + 対潜) × √(搭載数) + √(★)
                power += (
                    3 * item.fullSlot
                    + 0.45 * totalStatus * math.sqrt(item.fullSlot)
                    + math.sqrt(item.remodel)
                )
            else:
                # 夜間飛行機搭載補正 = B(0.3) × (火力 + 雷装 + 爆装 + 対潜) × √(搭載数) + √(★)
                power += 0.3 * totalStatus * math.sqrt(item.fullSlot) + math.sqrt(
                    item.remodel
                )

        return power + contactBonus

    def getAswArmorDeBuff(self) -> float:
        """爆雷の装甲減少補正値を返却"""

        items = (*self.items, self.exItem)
        # 爆雷と一部装備
        targets = {226, 227, 377, 378, 439, 472, 488}
        sumCorr: float = 0

        isDE = self.data.type == ShipType.DE
        for item in items:
            if item and item.data.id in targets:
                sumCorr -= math.sqrt(item.data.asw - 2) + (1 if isDE else 0)

        return sumCorr

    def putItem(self, item: Item, slot: int, initLevels: Sequence[_initLevel]) -> Ship:
        items = [*self.items]
        level = 0
        if initLevels:
            # 定情報より初期熟練度を解決
            initData = utils.find(
                initLevels, lambda v, _: v.get("id", 0) == item.data.apiTypeId
            )
            if initData:
                level = initData.get("level", 0)

        if slot < len(items):
            if item.data.apiTypeId == 41 and self.data.type2 == 90:
                # 日進 & 大型飛行艇
                items[slot] = Item(
                    ItemBuilder(
                        item=items[slot],
                        master=item.data,
                        remodel=item.remodel,
                        level=level,
                        slot=1,
                    )
                )
            else:
                # 装備を置き換え
                items[slot] = Item(
                    ItemBuilder(
                        item=items[slot],
                        master=item.data,
                        remodel=item.remodel,
                        level=level,
                    )
                )
            # 装備を変更した艦娘インスタンス再生成
            return Ship(builder=ShipBuilder(ship=self, items=items))
        if slot == const.EXPAND_SLOT_INDEX:
            # 補強増設を変更した艦娘インスタンス再生成
            builder: ShipBuilder = ShipBuilder(
                ship=self,
                exItem=Item(
                    ItemBuilder(
                        item=self.exItem, master=item.data, remodel=item.remodel
                    )
                ),
            )
            return Ship(builder=builder)

        # 搭載失敗
        return self


class _initLevel(TypedDict):
    """putItem _initLevel"""

    id: int
    level: int
