import math
import random
from dataclasses import dataclass

from typing_extensions import MutableSequence

from ...types import ItemMaster
from ...types.const import AIR_STATE
from ...types.const import PROF_LEVEL_BORDER


def getAirStatusBorder(airPower: int) -> tuple[int, int, int, int]:
    """引数の制空値から各制空状態のボーダー制空値を返却"""
    if airPower == 0:
        return (0, 0, 0, 0)

    return (
        airPower * 3,
        math.ceil(airPower * 1.5),
        math.floor(airPower / 1.5) + 1,
        math.floor(airPower / 3) + 1,
    )


def getStageShootDownValue(state: int, slot: int) -> float:
    """航空戦 stage1 撃墜数を取得 取得後、整数で丸めること"""

    # 制空定数c = 確保から順に 1, 3, 5, 7, 10
    c = (1, 3, 5, 7, 10)[state]
    # A = 0 ~ (制空定数c / 3)の乱数
    a = math.floor(random.random() * (((c / 3) * 1000) + 1)) / 1000
    # slot * (A + 制空定数c / 4) / 10
    return (slot * ((a + c) / 4)) / 10


def getStageShootDownValueEnemy(state: int, slot: int) -> float:
    """航空戦 stage1 撃墜数を取得 敵側式"""

    # 制空定数c = 確保から順に 10, 8, 6, 4, 1
    c = (10, 8, 6, 4, 1)[state]
    # 0 ~ 制空定数c の一様な整数乱数
    x = math.floor(random.random() * (c + 1))
    y = math.floor(random.random() * (c + 1))
    return math.floor((slot * (0.65 * x + 0.35 * y)) / 10)


def getAirState(airPower: int, enemyAirPower: int, hasPlane: bool = True) -> AIR_STATE:
    """彼我の制空値より、制空状態を返却"""

    if enemyAirPower == 0 and airPower == 0:
        return AIR_STATE.KAKUHO if hasPlane else AIR_STATE.NONE

    borders = getAirStatusBorder(enemyAirPower)
    for i, v in enumerate(borders):
        if airPower >= v:
            return AIR_STATE(i) if airPower > 0 else AIR_STATE.SOSHITSU

    return AIR_STATE.SOSHITSU


def getProfLevel(level: int) -> int:
    """熟練度変換 0～120数値を 0～7に"""

    for i, v in enumerate(reversed(PROF_LEVEL_BORDER[:-1])):
        if level >= v:
            return 7 - i

    return 0


def softCap(power: int, cap: int, a5: int = 0, b5: int = 0) -> float:
    """キャップ適用値を返却"""
    return math.floor(
        (cap + math.sqrt(power - cap) if power >= cap else power) * a5 + b5
    )


@dataclass(slots=True)
class _Powers:
    power: int
    rate: float


@dataclass(slots=True)
class _DamageDistribution:
    damage: int
    rate: float


def getDamageDistribution(
    powers: MutableSequence[_Powers],
    armor: int,
    ammoRate: int,
    hp: int,
    isEnemy: bool = False,
) -> list[_DamageDistribution]:
    """ダメージ分布を返却"""

    # 各ダメージ値とその確率のdictionary
    damageDist: list[_DamageDistribution] = []

    # 0～(装甲 - 1)まで
    loopCount = math.floor(armor)
    step = 1 / loopCount

    for i in range(loopCount):
        tempArmor = armor * 0.7 + i + 0.6
        for _k, p in enumerate(powers):
            # 最終ダメージ 0以下は0にする
            damage = (
                math.floor((p.power - tempArmor) * ammoRate)
                if p.power - tempArmor > 0
                else 0
            )
            if damage >= hp and not isEnemy:
                # 味方艦隊 撃沈してしまう時ダメージ置換
                step2 = 1 / hp
                for j in range(hp):
                    # 被ダメージ = [現在HP × 0.5 + 整数乱数(0 ～ 現在HP-1) × 0.3](端数切捨て)
                    damage2 = math.floor(hp * 0.5 + j * 0.3)
                    rate = step * p.rate * step2

                    def _findData():
                        for d in damageDist:
                            if d.damage == damage2:
                                return d
                        else:
                            return None

                    data = _findData()
                    if data is not None:
                        data.rate += rate
                    else:
                        damageDist.append(_DamageDistribution(damage, rate))

    return damageDist


def getGrowSpeedString(item: ItemMaster) -> str:
    "成長定数から所要戦闘回数を返却"

    return {
        2: "100",
        3: "52 ~ 79",
        4: "37 ~ 49",
        5: "28 ~ 43",
        6: "23 ~ 32",
        7: "19 ~ 29",
        8: "16 ~ 24",
        9: "14 ~ 23",
        10: "13 ~ 20",
        11: "12 ~ 19",
        12: "11 ~ 16",
        13: "10 ~ 16",
        14: "9 ~ 14",
        15: "8 ~ 14",
    }.get(item.grow, "?")
