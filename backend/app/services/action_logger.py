"""
Action logger for displaying game events to players.
"""
from typing import List
from app.models.game import GameAction


class ActionLog:
    """Format game actions into readable messages."""

    @staticmethod
    def format_action(action: GameAction, player_name: str) -> str:
        """Format a game action into a readable message."""
        action_type = action.action_type
        data = action.data

        if action_type == "play_card":
            card_name = data.get("card_name", "a card")
            return f"{player_name} played {card_name}"

        elif action_type == "acquire_card":
            card_name = data.get("card_name", "a card")
            from_explorers = data.get("from_explorers", False)
            source = "Explorer pile" if from_explorers else "Trade Row"
            return f"{player_name} bought {card_name} from {source}"

        elif action_type == "deal_damage":
            target = data.get("target_player_id")
            damage = data.get("damage", 0)
            return f"{player_name} dealt {damage} damage to opponent"

        elif action_type == "destroy_base":
            card_name = data.get("card_name", "a base")
            return f"{player_name} destroyed {card_name}"

        return f"{player_name}: {action_type}"

    @staticmethod
    def get_recent_actions(actions: List[GameAction], limit: int = 10) -> List[str]:
        """Get the most recent actions as formatted strings."""
        recent = actions[-limit:] if len(actions) > limit else actions
        messages = []

        for action in recent:
            # We need player name, which we don't have here
            # This will be done in the route
            messages.append(action)

        return messages
