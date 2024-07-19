from __future__ import annotations

import math
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Sequence

from .... import utils
from ....logger import LOGGER
from ... import const
from ...air_calc_result import AirCalcResult
from ...const import SUPPORT_TYPE
from ...const import AvoidType
from ...const import Formation
from ...const import FormationType
from ...const import ShipType
from ..aerial_combat import AntiAirCutIn
from ..aerial_combat import ShootDownInfo
from ..interface import ContactRate
from ..item import Item
from .ship import Ship
from .ship import ShipBuilder


@dataclass(slots=True)
class FleetBuilder:
    fleet: Fleet | None = None
    ships: Sequence[Ship] | None = None
    formation: FormationType | None = None
    isUnion: bool | None = None


@dataclass(slots=True)
class Fleet:
    builder: InitVar[FleetBuilder]

    ships: list[Ship] = field(default_factory=list)
    formation: FormationType = field(default=FormationType.LineAhead)
    isUnion: bool = False
    fullAirPower: int = 0
    supportTypes: list[SUPPORT_TYPE] = field(default_factory=list)
    supportAirPower: int = 0
    supportAswAirPower: int = 0
    enabledAswSupport: bool = False
    tp: float = 0
    hasPlane: bool = False
    hasMainPlane: bool = False
    hasJet: bool = False
    fleetAntiAir: float = 0
    allPlanes: list[Item] = field(default_factory=list)
    shootDownList: list[ShootDownInfo] = field(default_factory=list)
    shootDownListAirRaid: list[ShootDownInfo] = field(default_factory=list)
    unionShootDownList: list[ShootDownInfo] = field(default_factory=list)
    unionShootDownListAirRaid: list[ShootDownInfo] = field(default_factory=list)
    allAntiAirCutIn: list[AntiAirCutIn] = field(default_factory=list)
    fleetRosCorr: int = 0
    nightContactRate: float = 0
    fleetSpeed: str = ""
    airPower: int = 0
    results: list[AirCalcResult] = field(default_factory=list)
    mainResult: AirCalcResult = field(default_factory=AirCalcResult)
    escortAirPower: int = 0

    def __post_init__(self, builder: FleetBuilder) -> None:
        # builderよりそのままインスタンスを引継ぎ
        if builder.fleet:
            self.ships = (
                [*builder.ships]
                if builder.ships is not None
                else [*builder.fleet.ships]
            )
            self.isUnion = (
                builder.isUnion
                if builder.isUnion is not None
                else builder.fleet.isUnion
            )
            self.formation = (
                builder.formation
                if builder.formation is not None
                else builder.fleet.formation
            )
        else:
            self.ships = [*builder.ships] if builder.ships is not None else list()
            self.isUnion = builder.isUnion if builder.isUnion is not None else False
            self.formation = (
                builder.formation
                if builder.formation is not None
                else FormationType.LineAhead
            )

            if len(self.ships) == 0:
                # 0隻だった場合は空の艦娘を6隻分つっこむ
                self.ships = [Ship(ShipBuilder()) for _ in range(6)]

        # 計算により算出するステータス
        formation = utils.find(const.FORMATIONS, lambda v, _: v.value == self.formation)
        self.fleetAntiAir = self.getFleetAntiAir(formation)
        self.tp = 0
        self.fullAirPower = 0
        self.supportAirPower = 0
        self.supportAswAirPower = 0
        self.fleetRosCorr = 0
        self.hasJet = False
        self.hasPlane = False
        self.hasMainPlane = False
        self.allPlanes = []

        self.allAntiAirCutIn = []
        enabledShips = [v for v in self.ships if v.isActive and not v.isEmpty]

        sumShipRos: int = 0
        sumSPRos: int = 0
        nightContactFailureRate: float = 1.0
        # TP追加ダブらない用のフラグ もっぱら鬼怒改二用
        hasAdditionalTP: bool = False
        for ship in enabledShips:

            if ship.isActive and not ship.isEmpty:
                self.fullAirPower += ship.fullAirPower
                self.supportAirPower += ship.supportAirPower
                self.supportAswAirPower += ship.supportAswAirPower
                self.tp += ship.tp

                if not hasAdditionalTP and ship.data.id == 487:
                    self.tp += 8
                    hasAdditionalTP = True

                sumShipRos += ship.scout
                sumSPRos += ship.sumSPRos

                # 夜偵発動率計算

                if not self.isUnion or (self.isUnion and ship.isEscort):
                    nightContactFailureRate -= (
                        nightContactFailureRate * ship.nightContactRate
                    )

                self.allAntiAirCutIn = [*self.allAntiAirCutIn, *ship.antiAirCutIn]

                shipPlanes = [
                    v for v in ship.items if v.data.isPlane and v.fullSlot > 0
                ]
                if len(shipPlanes):
                    for _j, planeJ in enumerate(shipPlanes):
                        # 親indexをセットして親を見つけられるようにする
                        planeJ.parentIndex = utils.findIndex(
                            self.ships, lambda v, _: v == ship
                        )
                        # 連合かつ第2艦隊なら艦載機の随伴機フラグを挙げる => そうでないなら随伴機フラグを解除
                        planeJ.isEscortItem = self.isUnion and ship.isEscort

                    self.allPlanes = [*self.allPlanes, *shipPlanes]
                    if not self.hasPlane and utils.find(
                        self.allPlanes, lambda v, _: not v.data.isRecon
                    ):
                        self.hasPlane = True
                    if not self.hasMainPlane and utils.find(
                        self.allPlanes,
                        lambda v, _: not v.data.isRecon and not v.isEscortItem,
                    ):
                        self.hasMainPlane = True

                if not self.hasJet and ship.hasJet:
                    self.hasJet = True

        self.nightContactRate = 1 - nightContactFailureRate

        # 艦隊索敵補正: A = ∑(艦船の素索敵值) + ∑(水偵/水爆の裝備索敵值*int(sqrt(水偵/水爆の機數)))
        # 艦隊索敵補正 = int(sqrt(A) + 0.1 * A)
        rosA = sumShipRos + sumSPRos
        self.fleetRosCorr = math.floor(math.sqrt(rosA) + 0.1 * rosA)

        self.airPower = self.fullAirPower

        speeds = [v.speed for v in enabledShips]
        LOGGER.debug(f"{speeds = }")
        if not len(speeds):
            self.fleetSpeed = ""
        elif all(v >= 20 for v in speeds):
            self.fleetSpeed = "最速"
        elif all(v >= 15 for v in speeds):
            self.fleetSpeed = "高速+"
        elif all(v >= 10 for v in speeds):
            self.fleetSpeed = "高速"
        elif all(v >= 5 for v in speeds):
            self.fleetSpeed = "低速統一"
        else:
            self.fleetSpeed = "低速"

        # 対空砲火情報を更新

        priories = const.ANTI_AIR_CUT_IN_PRIORITIES
        self.allAntiAirCutIn.sort(
            key=lambda v: pos if (pos := utils.indexOf(priories, v.id)) >= 0 else 99
        )

        # 対空砲火情報更新
        self.shootDownList = []
        self.unionShootDownList = []
        self.shootDownListAirRaid = []
        self.unionShootDownListAirRaid = []
        _sum: float = 1
        border: float = 0
        for cutIn in self.allAntiAirCutIn:
            rate = _sum * cutIn.rate
            _sum -= rate
            border += rate

            self.shootDownList.append(
                ShootDownInfo(
                    enabledShips, False, self.isUnion, cutIn, border, formation
                )
            )
            self.unionShootDownList.append(
                ShootDownInfo(enabledShips, False, True, cutIn, border, formation)
            )
            self.shootDownListAirRaid.append(
                ShootDownInfo(
                    enabledShips, False, self.isUnion, cutIn, border, formation, True
                )
            )
            self.unionShootDownListAirRaid.append(
                ShootDownInfo(enabledShips, False, True, cutIn, border, formation, True)
            )

        # 対空CI不発データを挿入
        notCutinData = ShootDownInfo(
            enabledShips, False, self.isUnion, AntiAirCutIn(), 1, formation
        )
        self.shootDownList.append(notCutinData)
        self.unionShootDownList.append(
            ShootDownInfo(enabledShips, False, True, AntiAirCutIn(), 1, formation)
        )
        self.shootDownListAirRaid.append(
            ShootDownInfo(
                enabledShips, False, self.isUnion, AntiAirCutIn(), 1, formation, True
            )
        )
        self.unionShootDownListAirRaid.append(
            ShootDownInfo(enabledShips, False, True, AntiAirCutIn(), 1, formation, True)
        )

        # 画面表示用撃墜数格納
        for i, enabledShipI in enumerate(enabledShips):
            enabledShipI.fixDown = notCutinData.shootDownStatusList[0].fixDownList[i]
            enabledShipI.rateDown = notCutinData.shootDownStatusList[0].rateDownList[i]

        self.supportTypes = self._getSupportTypes()
        self.enabledAswSupport = SUPPORT_TYPE.ANTI_SUBMARINE in self.supportTypes

    def getFleetAntiAir(
        self, formation: Formation | None = None, avoid: AvoidType | None = None
    ) -> float:
        """引数の条件下での艦隊防空値を返却(表示値 実計算では別)"""

        # 各艦の艦隊対空ボーナス合計
        sumAntiAirBonus: float = 0
        ships = [v for v in self.ships if v.isActive and not v.isEmpty]
        for ship in ships:
            # 装備フィットボーナス(対空)
            itemBonusAntiAir = v if (v := ship.itemBonusStatus.antiAir) else 0
            sumAntiAirBonus += ship.antiAirBonus + itemBonusAntiAir

        sumAntiAirBonus = math.floor(sumAntiAirBonus)

        # 艦隊防空 => int(陣形補正 * 各艦の艦隊対空ボーナス合計) / ブラウザ版(1.3)
        fleetAntiAir: float = (
            math.floor(
                sumAntiAirBonus * (formation.correction if formation is not None else 1)
            )
            / 1.3
        )

        if avoid is not None and avoid.c2 != 1.0:
            # 艦隊防空補正 => int(艦隊防空 * 対空射撃回避補正(艦隊防空ボーナス))
            return math.floor(fleetAntiAir * avoid.c2)

        # 最終艦隊防空補正 改式表示値
        return fleetAntiAir

    @staticmethod
    def getScoutScore(
        argShips: Sequence[Ship], admiralLevel: int = 120, cCount: int = 4
    ) -> list[float]:
        """艦娘配列の合計索敵スコアを分岐点係数毎に取得 係数は第3引数の値だけ増やせる"""

        # Σ(√艦娘の素の索敵値) + Σ{(装備の素の索敵値 + 改修係数×√★)×装備係数}×分岐点係数 - ⌈艦隊司令部Lv.×司令部補正係数⌉ + 2×(6 - 分岐点に到達した際の隻数)
        scoutScore: list[float] = []
        block3: float = admiralLevel * 0.4
        ships = tuple(v for v in argShips if v.isActive and not v.isEmpty)

        # 分岐点係数
        for i in range(1, cCount + 1):
            block1: float = 0
            block2: float = 0
            for ship in ships:
                # Σ(√艦娘の素の索敵値 + 装備ボーナス)
                block1 += math.sqrt(ship.scout + (ship.itemBonusStatus.los))
                # Σ{(装備の素の索敵値 + 改修係数×√★)×装備係数}×分岐点係数
                block2 += ship.itemsScout * i
            scoutScore.append(
                block1 + block2 - math.ceil(block3) + (2 * (6 - len(ships)))
            )

        return scoutScore

    def getUnionScoutScore(
        self, admiralLevel: int = 120, cCount: int = 4
    ) -> list[float]:
        """連合艦隊時の索敵を取得 司令部レベルによって変わるため画面側で呼び出す"""

        mainShips = [v for v in self.ships if not v.isEscort]
        mainScouts = Fleet.getScoutScore(mainShips, admiralLevel, cCount)

        escortShips = [v for v in self.ships if v.isEscort]
        subScouts = Fleet.getScoutScore(escortShips, admiralLevel, cCount)

        return [
            mainScout + subScout for mainScout, subScout in zip(mainScouts, subScouts)
        ]

    @staticmethod
    def getSmokeTriggerRate(argShips: Sequence[Ship]) -> tuple[float, float, float]:
        """
        艦娘配列から煙幕発動率取得 仮説1 ゆめみさん
        https://x.com/yukicacoon/status/1739480992090632669
        """

        ships = [v for v in argShips if v.isActive and not v.isEmpty]
        # 発煙搭載数 + 改搭載数*2
        n: int = 0
        # 煙幕の改修値合計
        totalSmokeRemodel: int = 0
        # 煙幕改の改修値合計
        totalSmokeKaiRemodel: int = 0

        for ship in ships:
            for item in ship.items:
                if item.data.id == 500:
                    # 通常煙幕
                    n += 1
                    totalSmokeRemodel += item.remodel
                elif item.data.id == 501:
                    # 煙幕改
                    n += 2
                    totalSmokeKaiRemodel += item.remodel

        # 旗艦の運
        flagshipLuck: int = ships[0].luck
        # Roundup[√(luk)+0.3*煙改修+0.5*煙改改修]
        k: int = math.ceil(
            math.sqrt(flagshipLuck)
            + 0.3 * totalSmokeRemodel
            + 0.5 * totalSmokeKaiRemodel
        )

        # 不発率
        p0 = max(320 - 20 * k - 100 * n, 0)

        if n >= 3:
            p3 = 4.2 * k + 15 * (n - 3)
            p2 = min(30, 100 - p3)
            p1 = max(100 - p2 - p3, 0)
            return (p1, p2, p3)
        if n >= 2:
            p3 = 0
            p2 = (100 - p0) * 0.05 * (k + 2)
            p1 = max(100 - p0 - p2 - p3, 0)
            return (p1, p2, p3)
        if n >= 1:
            p3 = 0
            p2 = 0
            p1 = max(100 - p0, 0)
            return (p1, p2, p3)

        return (0, 0, 0)

    @staticmethod
    def getSmokeTriggerRate2(argShips: Sequence[Ship]) -> tuple[float, float, float]:
        """
        艦娘配列から煙幕発動率取得 仮説2 Xeさん
        https://x.com/Xe_UCH/status/1767407602554855730
        """
        ships = [v for v in argShips if v.isActive and not v.isEmpty]

        # 発煙搭載数 + 改搭載数*2
        smokeA: int = 0
        # 煙幕の改修値合計
        totalSmokeRemodel: int = 0
        # 煙幕改の改修値合計
        totalSmokeKaiRemodel: int = 0

        for ship in ships:
            for item in ship.items:
                if item.data.id == 500:
                    # 通常煙幕
                    smokeA += 1
                    totalSmokeRemodel += item.remodel
                elif item.data.id == 501:
                    # 煙幕改
                    smokeA += 2
                    totalSmokeKaiRemodel += item.remodel

        # 旗艦の運
        flagshipLuck = ships[0].luck
        # 発動判定p0: https://twitter.com/yukicacoon/status/1739480992090632669
        k = math.ceil(
            math.sqrt(flagshipLuck)
            + 0.3 * totalSmokeRemodel
            + 0.5 * totalSmokeKaiRemodel
        )
        # 発動率
        triggerRate = 1 - max(3.2 - 0.2 * k - smokeA, 0)

        if smokeA >= 3:
            triple = min(
                3
                * math.ceil(
                    5 * smokeA
                    + 1.5 * math.sqrt(flagshipLuck)
                    + 0.5 * totalSmokeKaiRemodel
                    + 0.3 * totalSmokeRemodel
                    - 15
                )
                + 1,
                100,
            )
            double = 30 - ((triple - 70) if triple > 70 else 0)
            single = max(100 - triple - double, 0)
            return (single * triggerRate, double * triggerRate, triple * triggerRate)
        if smokeA == 2:
            triple = 0
            double = min(
                3
                * math.ceil(
                    5 * smokeA
                    + 1.5 * math.sqrt(flagshipLuck)
                    + 0.5 * totalSmokeKaiRemodel
                    + 0.3 * totalSmokeRemodel
                    - 5
                )
                + 1,
                100,
            )
            single = max(100 - triple - double, 0)
            return (single * triggerRate, double * triggerRate, triple * triggerRate)
        if smokeA < 1:
            return (0, 0, 0)

        return (max(100 * triggerRate, 0), 0, 0)

    @staticmethod
    def getAerialScoutScore(argShips: Sequence[Ship]) -> float:
        """艦娘配列の合計航空偵察索敵スコア"""

        ships = [v for v in argShips if v.isActive and not v.isEmpty]
        score: float = 0
        for ship in ships:
            items = (*ship.items, ship.exItem)
            for item in items:
                if item.data.apiTypeId == 10 or item.data.apiTypeId == 11:
                    score += item.data.scout * math.sqrt(math.sqrt(item.fullSlot))
                elif item.data.apiTypeId == 41:
                    score += item.data.scout * math.sqrt(item.fullSlot)

        return score

    def getContactRates(
        self, isUnion: bool = False
    ) -> tuple[ContactRate, ContactRate, ContactRate]:
        items = (
            self.allPlanes
            if isUnion
            else [v for v in self.allPlanes if not v.isEscortItem]
        )
        return Item.getContactRates(items)

    def _getSupportTypes(self) -> list[SUPPORT_TYPE]:
        """発生する支援種別を返却"""
        if len(tuple(v for v in self.ships if v.data.type == ShipType.DD)) < 2:
            return [SUPPORT_TYPE.NOT_FOUNDED_DD]

        types = tuple(v.data.type for v in self.ships)
        # 空母系
        countCA = len(
            tuple(
                v
                for v in types
                if v == ShipType.CV or v == ShipType.CVB or v == ShipType.CVL
            )
        )
        # 航空支援系A(水母 揚陸艦)
        aerialACount = len(
            tuple(v for v in types if v == ShipType.AV or v == ShipType.LHA)
        )
        # 航空支援系B(航戦 航巡 補給)
        aerialBCount = len(
            tuple(
                v
                for v in types
                if v == ShipType.BBV
                or v == ShipType.CAV
                or v == ShipType.AO
                or v == ShipType.AO_2
            )
        )
        # 砲撃支援系存在(戦艦 重巡)
        hasFireType = any(
            v
            for v in types
            if v == ShipType.BB
            or v == ShipType.FBB
            or v == ShipType.BBB
            or v == ShipType.CA
        )

        if hasFireType and (countCA + aerialACount < 2):
            # 砲撃支援系存在し、空母系 + 航空支援系Aが2未満
            return [SUPPORT_TYPE.SHELLING]

        # 航空支援判定
        if countCA or aerialACount >= 2 or aerialBCount >= 2:
            supports: list[SUPPORT_TYPE] = []
            # 対潜支援判定 軽空母がいるかつ対潜艦1
            cvlIndex = utils.findIndex(
                self.ships, lambda v, _: v.data.type == ShipType.CVL
            )
            # ↑の軽空母以外で対潜支援参加可能
            if cvlIndex >= 0 and len(
                tuple(
                    v
                    for i, v in enumerate(self.ships)
                    if i != cvlIndex and v.enabledASWSupport
                )
            ):
                supports.append(SUPPORT_TYPE.ANTI_SUBMARINE)
            if (
                cvlIndex >= 0
                and len(tuple(v for v in self.ships if v.data.type == ShipType.DE)) >= 2
            ):
                # 海防艦 * 2でもOK
                supports.append(SUPPORT_TYPE.ANTI_SUBMARINE)

            # 航空支援
            if any(
                v for v in self.allPlanes if v.data.isAttacker and not v.data.isAswPlane
            ):
                supports.append(SUPPORT_TYPE.AIRSTRIKE)

            if len(supports):
                return supports
            return [SUPPORT_TYPE.NONE]

        return [SUPPORT_TYPE.LONG_RANGE_TORPEDO]

    def getSupportTypeName(self) -> str:
        """支援種別名称を返却"""
        supports = const.SUPPORTS
        typeNames = tuple(
            (
                support.text
                if (support := utils.find(supports, lambda w, _: w.value == v))
                is not None
                else "-"
            )
            for v in self.supportTypes
        )
        return "/".join(typeNames)

    def getSupportTypeNames(self) -> tuple[str, ...]:
        supports = const.SUPPORTS
        return tuple(
            (
                support.text
                if (support := utils.find(supports, lambda w, _: w.value == v))
                is not None
                else "-"
            )
            for v in self.supportTypes
        )
