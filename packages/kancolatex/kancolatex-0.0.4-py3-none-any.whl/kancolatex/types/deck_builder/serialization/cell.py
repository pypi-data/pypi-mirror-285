from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Optional

from ...const import FormationType
from .enemy_fleet import DeckBuilderEnemyFleet


class DeckBuilderCell(BaseModel):
    cellId: int = Field(alias="c")
    playerFormation: FormationType = Field(alias="pf")
    enemyFormation: FormationType = Field(alias="ef")
    fleet1: DeckBuilderEnemyFleet = Field(alias="f1")
    fleet2: Optional[DeckBuilderEnemyFleet] = Field(alias="f2", default=None)
