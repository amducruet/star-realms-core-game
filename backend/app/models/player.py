"""
Player models.
"""
from typing import List, Dict
from pydantic import BaseModel, Field
from app.models.card import CardInstance


class Player(BaseModel):
    """Player state."""
    player_id: str
    name: str
    authority: int = 50

    # Card zones
    deck: List[CardInstance] = Field(default_factory=list)
    hand: List[CardInstance] = Field(default_factory=list)
    discard_pile: List[CardInstance] = Field(default_factory=list)
    in_play: List[CardInstance] = Field(default_factory=list)  # Ships played this turn
    bases: List[CardInstance] = Field(default_factory=list)  # Bases that stay in play

    # Turn resources
    combat: int = 0
    trade: int = 0

    # AIflag
    is_ai: bool = False

    # Turn modifiers
    next_acquire_to_top: bool = False      # "put next ship/base on top of deck"
    next_acquire_to_top_type: str = 'any'  # 'ship', 'base', or 'any'
    faction_played_count: Dict[str, int] = Field(default_factory=dict)  # faction -> ships played this turn
    scrapped_this_turn: int = 0

    class Config:
        frozen = False
