from typing_extensions import MutableSequence

from ... import FitBonusValue as ItemBonusStatus


def getTotalBonus(bonuses: MutableSequence[ItemBonusStatus]) -> ItemBonusStatus:
    """装備ボーナス配列から合計のボーナスを算出する"""

    bonus = ItemBonusStatus()

    for v in bonuses:
        bonus += v

    return bonus


def bonusData():
    from ....database import DATABASE

    for v in DATABASE.QueryFitBonusAllFromEOEn():
        yield v
