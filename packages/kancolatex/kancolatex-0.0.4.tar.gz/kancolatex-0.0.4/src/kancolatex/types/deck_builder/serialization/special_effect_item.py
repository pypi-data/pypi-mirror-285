from pydantic import BaseModel
from pydantic import Field

from ...const import SpEffectItemKind


class DeckBuilderSpecialEffectItem(BaseModel):

    apiKind: SpEffectItemKind = Field(alias="kind")
    """name change from SpEffectItemKind to apiKind, python linter will happy."""

    firepower: int = Field(alias="fp")
    torpedo: int = Field(alias="tp")
    armor: int = Field(alias="ar")
    evasion: int = Field(alias="ev")
