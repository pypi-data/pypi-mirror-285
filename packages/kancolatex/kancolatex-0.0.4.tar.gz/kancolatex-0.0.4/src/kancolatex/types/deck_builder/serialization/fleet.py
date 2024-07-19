from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from typing_extensions import Optional

from ...const import FleetType
from .ship import DeckBuilderShip


class DeckBuilderFleet(BaseModel):
    name: str
    type: FleetType = Field(alias="t")
    ship1: Optional[DeckBuilderShip] = Field(alias="s1", default=None)
    ship2: Optional[DeckBuilderShip] = Field(alias="s2", default=None)
    ship3: Optional[DeckBuilderShip] = Field(alias="s3", default=None)
    ship4: Optional[DeckBuilderShip] = Field(alias="s4", default=None)
    ship5: Optional[DeckBuilderShip] = Field(alias="s5", default=None)
    ship6: Optional[DeckBuilderShip] = Field(alias="s6", default=None)
    ship7: Optional[DeckBuilderShip] = Field(alias="s7", default=None)

    model_config = ConfigDict(populate_by_name=True)
