from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Optional

from ...const import CountryType
from ...const import EquipmentTypes
from ...equipment_id import EquipmentId
from ...ship_id import ShipId
from .fit_bonus_value import FitBonusValue


class FitBonusData(BaseModel):
    shipClass: Optional[list[int]] = Field(alias="shipClass", default=None)

    shipMasterIds: Optional[list[ShipId]] = Field(alias="shipX", default=None)
    """Master id = exact id of the ship"""

    shipIds: Optional[list[ShipId]] = Field(alias="shipS", default=None)
    """Base id of the ship (minimum remodel), bonus applies to all of the ship forms"""

    shipTypes: Optional[list[int]] = Field(alias="shipType", default=None)
    shipNationalities: Optional[list[CountryType]] = Field(
        alias="shipNationality", default=None
    )

    equipmentRequired: Optional[list[EquipmentId]] = Field(
        alias="requires", default=None
    )
    equipmentRequiresLevel: Optional[int] = Field(alias="requiresLevel", default=None)
    """If "EquipmentRequired" is set, equipments requires to be at least this level"""

    numberOfEquipmentsRequired: Optional[int] = Field(alias="requiresNum", default=None)
    """If "EquipmentRequired" is set, you need this number of equipments"""

    equipmentTypesRequired: Optional[list[EquipmentTypes]] = Field(
        alias="requiresType", default=None
    )
    numberOfEquipmentsTypesRequired: Optional[int] = Field(
        alias="requiresNumType", default=None
    )

    equipmentLevel: Optional[int] = Field(alias="level", default=None)
    """Improvement level of the equipment required"""

    numberOfEquipmentsRequiredAfterOtherFilters: Optional[int] = Field(
        alias="num", default=None
    )
    """Number Of Equipments Required after applying the improvement filter"""

    bonuses: FitBonusValue = Field(alias="bonus", default_factory=FitBonusValue)
    """
    Bonuses to apply
    Applied x times, x being the number of equipment matching the conditions of the bonus fit
    If NumberOfEquipmentsRequiredAfterOtherFilters or EquipmentRequired or EquipmentTypesRequired, bonus is applied only once
    """

    bonusesIfSurfaceRadar: Optional[FitBonusValue] = Field(
        alias="bonusSR", default=None
    )
    """Bonuses to apply if ship has a radar with LOS >= 5"""

    bonusesIfAirRadar: Optional[FitBonusValue] = Field(alias="bonusAR", default=None)
    """Bonuses to apply if ship has a radar with AA >= 2"""

    bonusesIfAccuracyRadar: Optional[FitBonusValue] = Field(
        alias="bonusAccR", default=None
    )
    """Bonuses to apply if ship has a radar with ACC >= 8"""
