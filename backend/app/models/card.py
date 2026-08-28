"""
Card models.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CardDefinition(BaseModel):
    """Card definition from the database."""
    id: str
    name: str
    type: str  # "Ship" or "Base"
    faction: str  # "Blob", "Trade Federation", "Machine Cult", "Star Empire", "Unaligned"
    cost: int
    defense: Optional[int] = None
    is_outpost: bool = False
    text: str
    quantity: int
    role: str  # "Personal Deck", "Explorer Pile", "Trade Deck"


class CardInstance(BaseModel):
    """A specific instance of a card in the game (with unique instance ID)."""
    instance_id: str = Field(..., description="Unique instance ID for animations")
    card_id: str = Field(..., description="Reference to CardDefinition")
    name: str
    type: str
    faction: str
    cost: int
    defense: Optional[int] = None
    is_outpost: bool = False
    text: str

    # Instance-specific state (for bases in play)
    current_defense: Optional[int] = None  # For bases in play

    class Config:
        frozen = False  # Allow modification for current_defense
