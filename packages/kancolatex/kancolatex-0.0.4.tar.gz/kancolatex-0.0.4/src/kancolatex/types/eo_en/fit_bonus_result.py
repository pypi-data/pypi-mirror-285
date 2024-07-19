from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ..const import EquipmentTypes
from ..equipment_id import EquipmentId
from .serialization import FitBonusData
from .serialization import FitBonusValue


@dataclass(slots=True)
class FitBonusResult:
    fitBonusData: FitBonusData = field(default_factory=FitBonusData)
    equipmentTypes: list[EquipmentTypes] = field(default_factory=list)
    equipmentIds: list[EquipmentId] = field(default_factory=list)
    fitBonusValue: list[FitBonusValue] = field(default_factory=list)

    @property
    def finalBonus(self) -> FitBonusValue:
        result = FitBonusValue.model_construct()

        for v in self.fitBonusValue:
            result += v

        return result
