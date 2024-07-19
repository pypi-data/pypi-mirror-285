from __future__ import annotations

from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

from typing_extensions import Optional
from typing_extensions import cast

from ...const import FleetType
from ...const import FormationType
from .fleet import Fleet
from .fleet import FleetBuilder
from .ship import Ship
from .ship import ShipBuilder


@dataclass(slots=True)
class FleetInfoBuilder:
    info: Optional[FleetInfo] = None
    fleets: Optional[list[Fleet]] = None
    isUnion: Optional[bool] = None
    admiralLevel: Optional[int] = None
    mainFleetIndex: Optional[int] = None
    fleetType: Optional[FleetType] = None


@dataclass(slots=True)
class FleetInfo:
    builder: InitVar[FleetInfoBuilder]

    fleets: list[Fleet] = field(default_factory=list)
    isUnion: bool = False
    fleetType: FleetType = FleetType.Single
    admiralLevel: int = 120
    mainFleetIndex: int = 0
    unionFleet: Fleet | None = None
    calculated: bool = False
    ignoreHistory: bool = False

    def __post_init__(self, builder: FleetInfoBuilder):
        if builder.info:
            self.isUnion = (
                builder.isUnion if builder.isUnion is not None else builder.info.isUnion
            )
            self.admiralLevel = (
                builder.admiralLevel
                if builder.admiralLevel is not None
                else builder.info.admiralLevel
            )
            self.mainFleetIndex = (
                builder.mainFleetIndex
                if builder.mainFleetIndex is not None
                else builder.info.mainFleetIndex
            )
            self.fleets = (
                builder.fleets if builder.fleets is not None else builder.info.fleets
            )
            self.fleetType = (
                builder.fleetType
                if builder.fleetType is not None
                else builder.info.fleetType
            )

        else:
            self.isUnion = builder.isUnion if builder.isUnion is not None else False
            self.admiralLevel = (
                builder.admiralLevel if builder.admiralLevel is not None else 120
            )
            self.mainFleetIndex = (
                builder.mainFleetIndex if builder.mainFleetIndex is not None else 0
            )
            self.fleets = builder.fleets if builder.fleets is not None else list()
            self.fleetType = (
                builder.fleetType if builder.fleetType is not None else FleetType.Single
            )

        minFleetCount: int = 4
        fleetCount: int = len(self.fleets)
        if fleetCount < minFleetCount:
            # 第4艦隊までは最低でも作成
            for _ in range(minFleetCount - fleetCount):
                self.fleets.append(Fleet(FleetBuilder()))

        # 艦隊形式がおかしそうなら矯正
        if self.isUnion and not (
            self.fleetType == FleetType.Carrier
            or self.fleetType == FleetType.Surface
            or self.fleetType == FleetType.Transport
        ):
            self.fleetType = FleetType.Surface
        elif not self.isUnion and self.fleetType != FleetType.Single:
            self.fleetType = FleetType.Single

        if self.isUnion and (self.mainFleetIndex == 0 or self.mainFleetIndex == 1):
            # 連合艦隊にチェックが入っている場合連合艦隊オブジェクトを生成
            mains = self.fleets[0].ships
            # 第1艦隊全艦をnot随伴としてインスタンス化
            for i, ship in enumerate(mains):
                mains[i] = Ship(
                    builder=ShipBuilder(ship, isEscort=False, noStock=ship.noStock)
                )

            escorts = self.fleets[1].ships
            # 第2艦隊全艦を随伴としてインスタンス化
            for i, ship in enumerate(escorts):
                escorts[i] = Ship(
                    builder=ShipBuilder(ship, isEscort=True, noStock=ship.noStock)
                )

            self.unionFleet = Fleet(
                FleetBuilder(
                    isUnion=True,
                    ships=[*mains, *escorts],
                    formation=self.fleets[0].formation,
                )
            )

            # 艦隊別の制空値に初期化
            self.unionFleet.airPower = self.fleets[0].fullAirPower
            self.unionFleet.escortAirPower = self.fleets[1].fullAirPower
        elif not self.isUnion:
            # 連合が解除されているので再度インスタンス化
            self.fleets[0] = Fleet(FleetBuilder(fleet=self.fleets[0], isUnion=False))
            self.fleets[1] = Fleet(FleetBuilder(fleet=self.fleets[1], isUnion=False))

    def mainFleet(self) -> Fleet:
        """計算対象の艦隊データを返却"""
        mainFleet = self.fleets[self.mainFleetIndex]
        if self.isUnion and self.mainFleetIndex <= 1:
            mainFleet = cast(Fleet, self.unionFleet)
        return mainFleet

    @staticmethod
    def getInfoWithChangedFormation(
        info: FleetInfo, formation: FormationType
    ) -> FleetInfo:
        """陣形が変更されたFleetInfoを新しく返却"""
        fleets = [
            Fleet(FleetBuilder(fleet=fleet, formation=formation))
            for fleet in info.fleets
        ]

        return FleetInfo(FleetInfoBuilder(info=info, fleets=fleets))
