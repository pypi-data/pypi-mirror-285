from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class FitBonusValue(BaseModel):
    firepower: int = Field(alias="houg", default=0)
    torpedo: int = Field(alias="raig", default=0)
    antiAir: int = Field(alias="tyku", default=0)
    armor: int = Field(alias="souk", default=0)
    evasion: int = Field(alias="kaih", default=0)
    asw: int = Field(alias="tais", default=0)
    los: int = Field(alias="saku", default=0)

    accuracy: int = Field(alias="houm", default=0)
    """Visible acc fit actually doesn't work according to some studies"""

    range: int = Field(alias="leng", default=0)
    bombing: int = Field(alias="baku", default=0)

    fromTypeId: int = Field(init=False, default=0)
    """Special field only use in noro6"""

    def __mul__(self, other: int) -> FitBonusValue:
        return FitBonusValue(
            houg=self.firepower * other,
            raig=self.torpedo * other,
            tyku=self.antiAir * other,
            souk=self.armor * other,
            kaih=self.evasion * other,
            tais=self.asw * other,
            saku=self.los * other,
            houm=self.accuracy * other,
            leng=self.range * other,
            baku=self.bombing * other,
        )

    def __add__(self, other: FitBonusValue) -> FitBonusValue:
        return FitBonusValue(
            houg=self.firepower + other.firepower,
            raig=self.torpedo + other.torpedo,
            tyku=self.antiAir + other.antiAir,
            souk=self.armor + other.armor,
            kaih=self.evasion + other.evasion,
            tais=self.asw + other.asw,
            saku=self.los + other.los,
            houm=self.accuracy + other.accuracy,
            leng=self.range + other.range,
            baku=self.bombing + other.bombing,
        )

    def hasBonus(self) -> bool:
        return any(
            (
                self.firepower,
                self.torpedo,
                self.antiAir,
                self.armor,
                self.evasion,
                self.asw,
                self.los,
                self.accuracy,
                self.range,
                self.bombing,
            )
        )

    def __eq__(self, value: object) -> bool:
        if type(value) is not type(self):
            return False

        return all(
            (
                value.firepower == self.firepower,
                value.torpedo == self.torpedo,
                value.antiAir == self.antiAir,
                value.armor == self.armor,
                value.evasion == self.evasion,
                value.asw == self.asw,
                value.los == self.los,
                value.accuracy == self.accuracy,
                value.range == self.range,
                value.bombing == self.bombing,
            )
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.firepower,
                self.torpedo,
                self.antiAir,
                self.armor,
                self.evasion,
                self.asw,
                self.los,
                self.accuracy,
                self.range,
                self.bombing,
            )
        )
