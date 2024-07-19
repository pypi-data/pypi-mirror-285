from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from typing_extensions import Any
from typing_extensions import Optional

from .airbase import DeckBuilderAirBase
from .fleet import DeckBuilderFleet
from .sortie_data import DeckBuilderSortieData


class DeckBuilderData(BaseModel):
    version: int = Field(alias="version", default=4)
    hqLevel: int = Field(alias="hqlv")
    fleet1: Optional[DeckBuilderFleet] = Field(alias="f1", default=None)
    fleet2: Optional[DeckBuilderFleet] = Field(alias="f2", default=None)
    fleet3: Optional[DeckBuilderFleet] = Field(alias="f3", default=None)
    fleet4: Optional[DeckBuilderFleet] = Field(alias="f4", default=None)
    airBase1: Optional[DeckBuilderAirBase] = Field(alias="a1", default=None)
    airBase2: Optional[DeckBuilderAirBase] = Field(alias="a2", default=None)
    airBase3: Optional[DeckBuilderAirBase] = Field(alias="a3", default=None)
    sortie: Optional[DeckBuilderSortieData] = Field(alias="s", default=None)

    """
    * noro6 will export empty object when no ship in that fleet
    """

    @field_validator("fleet1", "fleet2", "fleet3", "fleet4", mode="before")
    def _emptyDictToNone(v: Any):
        if v == {}:
            return None

        return v
