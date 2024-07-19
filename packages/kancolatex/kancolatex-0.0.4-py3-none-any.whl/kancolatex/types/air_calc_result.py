from __future__ import annotations

import math
from dataclasses import dataclass
from dataclasses import field

from .. import utils
from . import const


@dataclass(slots=True)
class AirCalcResult:
    airState: const.AirStatus = field(default_factory=lambda: const.AIR_STATUS[-1])
    airStateText: str = ""
    airStateBarWidth: float = 0
    rates: list[float] = field(default_factory=list)
    supportRates: list[float] = field(default_factory=list)
    loopSumAirPower: int = 0
    loopSumEnemyAirPower: int = 0
    avgAirPower: int = 0
    avgEnemyAirPower: int = 0
    avgEnemySupportAirPower: int = 0
    avgDownSlot: int = 0
    avgUsedSteels: int = 0
    isUnknownEnemyAirPower: bool = False

    @staticmethod
    def formatResult(result: AirCalcResult, maxCount: int) -> None:
        """計算結果をいい感じに整形"""

        # 最も高い制空状態を格納
        state = utils.indexOf(result.rates, max(result.rates))
        airState = utils.find(const.AIR_STATUS, lambda v, _: v.value == state)
        result.airState = airState if airState is not None else const.AIR_STATUS[-1]

        # 平均値にする
        result.avgAirPower = round(result.loopSumAirPower / maxCount)
        result.avgEnemyAirPower = round(result.loopSumEnemyAirPower / maxCount)
        (b0, b1, b2, b3, _) = AirCalcResult._getBorders(result.avgEnemySupportAirPower)

        if b0 <= 0:
            # 敵制空値がない場合は確保固定
            result.airStateBarWidth = 100
        elif result.avgAirPower >= b0:
            result.airStateBarWidth = (result.avgAirPower / b0) * 100 * 0.9
        elif result.avgAirPower >= b1:
            result.airStateBarWidth = (result.avgAirPower / b0) * 100 * 0.9
        elif result.avgAirPower >= b2:
            result.airStateBarWidth = (result.avgAirPower / b1) * 100 * 0.45
        elif result.avgAirPower >= b3:
            result.airStateBarWidth = (result.avgAirPower / b2) * 100 * 0.2
        else:
            result.airStateBarWidth = (result.avgAirPower / b3) * 100 * 0.1

        # 念のため
        result.airStateBarWidth = min(result.airStateBarWidth, 100)
        # レートを百分率表記に変換 あといい感じに切る
        result.rates = [math.floor((100 * v) / maxCount) / 100 for v in result.rates]

    def addRate(self, state: int) -> None:
        """指定した制空状態の結果を1増加させる"""
        self.rates[state] += 1

    def addSupportRates(self, state: int) -> None:
        """指定した制空状態の結果を1増加させる -支援艦隊"""
        self.supportRates[state] += 1

    @staticmethod
    def _getBorders(airPower: int) -> tuple[int, int, int, int, int]:
        return (
            airPower * 3,
            math.ceil(airPower * 1.5),
            math.floor(airPower / 1.5) + 1,
            math.floor(airPower / 3) + 1,
            0,
        )
