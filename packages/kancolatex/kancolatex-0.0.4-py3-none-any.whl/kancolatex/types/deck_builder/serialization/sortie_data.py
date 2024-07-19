from pydantic import BaseModel
from pydantic import Field

from .cell import DeckBuilderCell


class DeckBuilderSortieData(BaseModel):
    mapAreaId: int = Field(alias="a")
    mapInfoId: int = Field(alias="i")
    cells: list[DeckBuilderCell] = Field(alias="c")
