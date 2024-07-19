from dataclasses import dataclass

from pydantic import ValidationError
from typing_extensions import cast

from ...logger import LOGGER
from .. import const
from ..const import FleetType
from ..const import FormationType
from ..deck_builder import DeckBuilderData
from ..deck_builder import DeckBuilderEquipment
from ..deck_builder import DeckBuilderFleet
from ..deck_builder import DeckBuilderShip
from .fleet import Fleet
from .fleet import FleetBuilder
from .fleet import FleetInfo
from .fleet import FleetInfoBuilder
from .fleet import Ship
from .fleet import ShipBuilder
from .fleet import ShipMaster
from .item import Item
from .item import ItemBuilder
from .item import ItemMaster


@dataclass(slots=True)
class Convert:
    @classmethod
    def loadDeckBuilderToFleetInfo(cls, text: str) -> FleetInfo | None:
        try:
            deckBuilderData = DeckBuilderData.model_validate_json(text)
        except ValidationError as e:
            LOGGER.fatal(e)
            return None

        # 艦娘情報の取得と生成
        fleets: list[Fleet] = []
        for f in range(1, 5):
            fleet: DeckBuilderFleet | None = getattr(deckBuilderData, f"fleet{f}", None)
            LOGGER.debug(f"{fleet = }")
            if fleet is not None:
                fleet = DeckBuilderFleet.model_validate(fleet)
                ships: list[Ship] = []
                for s in range(1, 8):
                    data: DeckBuilderShip | None = getattr(fleet, f"ship{s}", None)
                    if data is not None and data.id:
                        ships.append(cls.convertDeckToShip(data))
                    elif s <= 6:
                        ships.append(Ship(ShipBuilder()))
                fleets.append(
                    Fleet(FleetBuilder(ships=ships, formation=FormationType.LineAhead))
                )
            else:
                fleets.append(Fleet(FleetBuilder()))

        LOGGER.debug(f"{deckBuilderData.hqLevel = }")
        admiralLevel: int = (
            deckBuilderData.hqLevel if deckBuilderData.hqLevel > 0 else 120
        )
        LOGGER.debug(f"{admiralLevel = }")
        fleetType: FleetType = (
            deckBuilderData.fleet1.type
            if deckBuilderData.fleet1 is not None
            else FleetType.Single
        )
        isUnion: bool = (
            deckBuilderData.fleet1.type
            in {FleetType.Surface, FleetType.Carrier, FleetType.Transport}
            if deckBuilderData.fleet1 is not None
            else False
        )

        return FleetInfo(
            FleetInfoBuilder(
                fleets=fleets,
                admiralLevel=admiralLevel,
                isUnion=isUnion,
                fleetType=fleetType,
            )
        )

    @staticmethod
    def convertDeckToShip(s: DeckBuilderShip) -> Ship:
        from ...database import DATABASE as _db

        """
        デッキビルダー艦娘情報からShipインスタンスの生成を頑張ってみる
        エラー起きてもそのまま投げます
        """
        master: ShipMaster = (
            ShipMaster.from_master_ship(ms)
            if (ms := _db.QueryMasterShipByIdFromNoro6Media(s.id)) is not None
            else ShipMaster()
        )
        shipLv: int = s.level if s.level > 0 else 99
        releaseExpand: bool = s.isExpansionSlotAvailable
        luck: int = s.luck if s.luck > 0 else master.luck
        baseHP: int = master.hp2 if shipLv > 99 else master.hp
        hp: int = s.hp if s.hp > 0 else baseHP
        items: list[Item] = []
        spEffectItemId = (
            s.SpecialEffectItem[0].apiKind
            if s.SpecialEffectItem is not None and len(s.SpecialEffectItem)
            else 0
        )
        exItem = Item(ItemBuilder())

        LOGGER.debug(f"{s = }")

        for i in range(1, master.slotCount + 1):
            _key = f"equipment{i}"
            item = (
                cast(DeckBuilderEquipment, _item)
                if (_item := getattr(s.equipment, _key, None)) is not None
                else DeckBuilderEquipment(id=0, rf=0, mas=0)
            )
            LOGGER.debug(f"{_key = }, {getattr(s.equipment, _key, None) = }")
            itemMaster: ItemMaster = (
                ItemMaster.from_master_item(im)
                if (im := _db.QueryMasterEquipmentByIdFromNoro6Media(item.id))
                is not None
                else ItemMaster()
            )
            # LOGGER.debug(f"{item.id = }, {im = }, {itemMaster = }")
            aircraftLevel: int = const.PROF_LEVEL_BORDER[
                item.aircraftLevel if item.aircraftLevel is not None else 0
            ]
            if itemMaster and itemMaster.apiTypeId == 41 and master.type2 == 90:
                # 日進 & 大型飛行艇
                items.append(
                    Item(
                        ItemBuilder(
                            master=itemMaster,
                            remodel=item.level,
                            level=aircraftLevel,
                            slot=1,
                        )
                    )
                )
            else:
                items.append(
                    Item(
                        ItemBuilder(
                            master=itemMaster,
                            remodel=item.level,
                            level=aircraftLevel,
                            slot=master.slots[i - 1],
                        )
                    )
                )
        # 補強増設 keyがixか、装備スロットインデックス+1を検索
        if (
            s.equipment.equipmentExpansion is not None
            or s.equipment.model_dump().get(f"equipment{master.slotCount+1}", None)
            is not None
        ):
            item: DeckBuilderEquipment = (
                s.equipment.equipmentExpansion
                if s.equipment.equipmentExpansion is not None
                else (
                    cast(DeckBuilderEquipment, _dumpGet)
                    if (
                        _dumpGet := s.equipment.model_dump().get(
                            f"equipment{master.slotCount+1}", None
                        )
                    )
                    is not None
                    else s.equipment.model_dump().get(
                        f"equipment{master.slotCount+1}", None
                    )
                )
            )
            itemMaster: ItemMaster = (
                ItemMaster.from_master_item(im)
                if (im := _db.QueryMasterEquipmentByIdFromNoro6Media(item.id))
                else ItemMaster()
            )
            aircraftLevel: int = const.PROF_LEVEL_BORDER[
                item.aircraftLevel if item.aircraftLevel is not None else 0
            ]
            exItem = Item(
                ItemBuilder(master=itemMaster, remodel=item.level, level=aircraftLevel)
            )

        if s.antiSubmarine > 0:
            # デッキビルダー形式に対潜値が含まれていた場合 => 装備 + 改修 + ボーナス分なので、切り分ける必要がある
            origAsw = Ship.getStatusFromLevel(shipLv, master.maxAsw, master.minAsw)
            # 対潜なしで一度艦娘を生成 => なぜ？ => 対潜改修値を特定するために、改修なしで素朴に生成したときの対潜値を見たい
            ship = Ship(
                ShipBuilder(
                    master=master,
                    level=shipLv,
                    luck=luck,
                    items=items,
                    exItem=exItem,
                    hp=hp,
                    releaseExpand=releaseExpand,
                    spEffectItemId=spEffectItemId,
                )
            )
            # 表示対潜の差分を見る => これが対潜改修分
            increasedAsw = s.antiSubmarine - ship.displayStatus.asw
            if increasedAsw > 0:
                return Ship(ShipBuilder(ship=ship, asw=origAsw + increasedAsw))

            return ship

        return Ship(
            ShipBuilder(
                master=master,
                level=shipLv,
                luck=luck,
                items=items,
                exItem=exItem,
                hp=hp,
                releaseExpand=releaseExpand,
                spEffectItemId=spEffectItemId,
            )
        )
