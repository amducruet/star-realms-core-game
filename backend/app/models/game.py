"""
Game state models.
"""
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.models.player import Player
from app.models.card import CardInstance


class GamePhase(str, Enum):
    """Game phases."""
    LOBBY = "lobby"
    PLAYING = "playing"
    ENDED = "ended"


class TurnPhase(str, Enum):
    """Turn phases."""
    MAIN = "main"  # Play cards, use trade, use combat
    DISCARD = "discard"  # End turn, discard and draw


class GameAction(BaseModel):
    """A game action event for animation system."""
    action_id: str
    action_type: str  # "play_card", "acquire_card", "deal_damage", "draw_card", "discard_card", "scrap_card", "destroy_base"
    player_id: str
    timestamp: float
    data: dict = Field(default_factory=dict)  # Flexible data for different action types


class GameConfig(BaseModel):
    """Game configuration."""
    max_players: int = 6
    starting_authority: int = 50
    starting_hand_size: int = 5
    starting_scouts: int = 8
    starting_vipers: int = 2
    trade_row_size: int = 5


class GameState(BaseModel):
    """Complete game state."""
    game_id: str
    phase: GamePhase = GamePhase.LOBBY
    turn_phase: TurnPhase = TurnPhase.MAIN
    config: GameConfig = Field(default_factory=GameConfig)

    # Players
    players: List[Player] = Field(default_factory=list)
    current_player_index: int = 0

    # Shared zones
    trade_row: List[CardInstance] = Field(default_factory=list)
    trade_deck: List[CardInstance] = Field(default_factory=list)
    explorer_pile: List[CardInstance] = Field(default_factory=list)
    scrap_heap: List[CardInstance] = Field(default_factory=list)

    # Action log for animations (Phase 2)
    action_log: List[GameAction] = Field(default_factory=list)

    # Pending interactive effect waiting for player resolution
    pending_effect: Optional[dict] = None
    # Transient state for two-phase, order-independent hand play.
    play_batch: Optional[dict] = None
    base_activation: Optional[dict] = None

    # Winner
    winner_id: Optional[str] = None

    class Config:
        frozen = False

    @property
    def current_player(self) -> Optional[Player]:
        """Get the current player."""
        if 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None

    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
