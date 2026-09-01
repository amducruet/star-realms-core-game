"""
Simple AIopponent service.
"""
import random
from typing import Optional, List, Dict, Any
from app.models.game import GameState
from app.models.player import Player


class AIService:
    """Simple AIopponent."""

    def execute_turn(self, game: GameState, game_service) -> GameState:
        """
        Execute complete AIturn for the current player.
        Returns updated game state.
        """
        current_player = game.players[game.current_player_index]

        if not current_player.is_ai:
            raise ValueError("Current player is not an AI")

        print(f"\n🤖 AITurn START: {current_player.name} (Player {game.current_player_index})")
        print(f"   Authority: {current_player.authority}, Hand size: {len(current_player.hand)}")

        # Generate action plan
        actions = self._plan_actions(game, current_player)
        print(f"   Planned {len(actions)} actions")

        # Execute each action
        for i, action in enumerate(actions):
            try:
                print(f"   Action {i+1}/{len(actions)}: {action.get('type')}")
                game = self._execute_action(game, current_player, action, game_service)
                current_player = game.players[game.current_player_index]
            except Exception as e:
                print(f"  ⚠️ AIaction failed: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"🤖 AITurn COMPLETE: Next player is {game.current_player_index}")
        return game

    def _plan_actions(self, game: GameState, ai_player: Player) -> List[Dict[str, Any]]:
        """
        Plan AIactions for this turn.
        Returns list of dicts with action type and parameters.
        """
        return [
            {"type": "play_all_cards"},
            {"type": "buy_cards"},
            {"type": "attack_phase"},
            {"type": "end_turn"},
        ]

    def _execute_action(self, game: GameState, ai_player: Player, action: Dict[str, Any], game_service) -> GameState:
        """Execute a single AIaction."""
        action_type = action.get("type")

        if action_type == "play_all_cards":
            # Loop so draw effects mid-turn get played too
            played = set()
            while True:
                current_player = game.get_player(ai_player.player_id)
                unplayed = [c for c in current_player.hand if c.instance_id not in played]
                if not unplayed:
                    break
                card = unplayed[0]
                played.add(card.instance_id)
                print(f"  🃏 Playing card: {card.name}")
                game = game_service.play_card(game.game_id, ai_player.player_id, card.instance_id)
                game = self._resolve_pending_effect(game, ai_player, game_service)

        elif action_type == "buy_cards":
            # Buy cards until no trade left
            current_player = game.get_player(ai_player.player_id)
            while current_player.trade > 0:
                affordable_cards = []

                # Check trade row
                for card in game.trade_row:
                    if card.cost <= current_player.trade:
                        affordable_cards.append((card, False))

                # Check explorer pile
                if game.explorer_pile and current_player.trade >= 2:
                    affordable_cards.append((game.explorer_pile[0], True))

                if not affordable_cards:
                    break

                # Buy most expensive
                affordable_cards.sort(key=lambda x: x[0].cost, reverse=True)
                best_card, from_explorers = affordable_cards[0]

                print(f"  💰 Buying: {best_card.name} (cost {best_card.cost})")
                game = game_service.acquire_card(
                    game.game_id,
                    ai_player.player_id,
                    best_card.instance_id,
                    from_explorers
                )
                current_player = game.get_player(ai_player.player_id)

        elif action_type == "attack_phase":
            # Attack with all available combat
            current_player = game.get_player(ai_player.player_id)
            # Only target alive opponents
            opponents = [p for p in game.players if p.player_id != ai_player.player_id and p.authority > 0]

            if opponents and current_player.combat > 0:
                # Target opponent with lowest health for potential elimination
                target = min(opponents, key=lambda p: p.authority)

                target_player_id = target.player_id

                # Destroy non-outpost bases first (they block direct attacks)
                non_outpost_bases = [b for b in target.bases if not b.is_outpost]
                for base in non_outpost_bases:
                    current_player = game.get_player(ai_player.player_id)
                    if current_player.combat >= base.current_defense:
                        print(f"  ⚔️ Attacking base: {base.name}")
                        game = game_service.attack_base(
                            game.game_id,
                            ai_player.player_id,
                            target_player_id,
                            base.instance_id,
                            base.current_defense
                        )

                # Attack player directly (outposts don't block this)
                current_player = game.get_player(ai_player.player_id)
                refreshed_target = game.get_player(target_player_id)
                remaining_non_outpost = [b for b in refreshed_target.bases if not b.is_outpost]
                if current_player.combat > 0 and not remaining_non_outpost:
                    print(f"  ⚔️ Attacking {refreshed_target.name} for {current_player.combat} damage")
                    game = game_service.attack_opponent(
                        game.game_id,
                        ai_player.player_id,
                        target_player_id,
                        None
                    )
                else:
                    # Can't reach player — spend remaining combat on outposts if possible
                    current_player = game.get_player(ai_player.player_id)
                    refreshed_target = game.get_player(target_player_id)
                    outposts = [b for b in refreshed_target.bases if b.is_outpost]
                    for outpost in outposts:
                        current_player = game.get_player(ai_player.player_id)
                        if current_player.combat >= outpost.current_defense:
                            print(f"  ⚔️ Attacking outpost: {outpost.name}")
                            game = game_service.attack_base(
                                game.game_id,
                                ai_player.player_id,
                                target_player_id,
                                outpost.instance_id,
                                outpost.current_defense
                            )

        elif action_type == "end_turn":
            print(f"  ✅ Ending turn")
            game = game_service.end_turn(game.game_id, ai_player.player_id)

        return game

    def _resolve_pending_effect(self, game: GameState, ai_player: Player, game_service) -> GameState:
        """Resolve any pending interactive effect for the Robot player."""
        if not game.pending_effect:
            return game

        pe = game.pending_effect
        effect_type = pe.get('type')
        optional = pe.get('optional', False)

        print(f"  🎯 Resolving pending effect: {effect_type} (optional={optional})")

        if effect_type == 'scrap_card':
            location = pe.get('location', 'hand')
            current_player = game.get_player(ai_player.player_id)

            # Gather candidate cards
            candidates = []
            if location == 'trade_row':
                candidates += [(c, 'trade_row') for c in game.trade_row]
            else:
                if location in ('hand', 'hand_or_discard'):
                    candidates += [(c, 'hand') for c in current_player.hand]
                if location in ('discard', 'hand_or_discard'):
                    candidates += [(c, 'discard') for c in current_player.discard_pile]

            if not candidates:
                if optional:
                    return game_service.skip_effect(game.game_id, ai_player.player_id)
                game.pending_effect = None
                return game

            # Trade row: scrap cheapest (removes weak cards for opponent too)
            # Hand/discard: scrap cheapest (deck thinning)
            candidates.sort(key=lambda x: x[0].cost)
            card, loc = candidates[0]
            print(f"  🗑️ AIscrapping {card.name} from {loc}")
            return game_service.resolve_scrap(game.game_id, ai_player.player_id, card.instance_id, loc)

        elif effect_type == 'discard_card':
            pe_target = pe.get('target', 'opponent')

            if pe_target == 'self':
                current_player = game.get_player(ai_player.player_id)
                if not current_player.hand:
                    game.pending_effect = None
                    return game
                # Discard cheapest card
                worst = min(current_player.hand, key=lambda c: c.cost)
                print(f"  🗑️ AIdiscards own card: {worst.name}")
                return game_service.resolve_discard(game.game_id, ai_player.player_id, ai_player.player_id, worst.instance_id)

            opponents = [p for p in game.players if p.player_id != ai_player.player_id]
            target = next((p for p in opponents if p.hand), None)
            if not target:
                if optional:
                    return game_service.skip_effect(game.game_id, ai_player.player_id)
                game.pending_effect = None
                return game

            # Discard the opponent's most expensive card
            best = max(target.hand, key=lambda c: c.cost)
            print(f"  🗑️ AIforcing {target.name} to discard {best.name}")
            return game_service.resolve_discard(game.game_id, ai_player.player_id, target.player_id, best.instance_id)

        elif effect_type == 'choice':
            options = pe.get('options', [])
            labels = pe.get('labels', [])
            # Pick the option with the highest total numeric value
            def score_option(effects):
                score = 0
                for e in effects:
                    t = e.get('type', '')
                    if t == 'gain_combat':
                        score += e.get('amount', 0) * 1.2  # slight combat preference
                    elif t in ('gain_trade', 'gain_authority', 'draw_cards'):
                        score += e.get('amount', 0)
                return score
            best = max(range(len(options)), key=lambda i: score_option(options[i])) if options else 0
            print(f"  🎯 AIchoosing option {best}: {labels[best] if best < len(labels) else best}")
            return game_service.resolve_choice(game.game_id, ai_player.player_id, best)

        elif effect_type == 'acquire_free_to_top':
            max_cost = pe.get('max_cost', 999)
            card_type = pe.get('card_type', 'ship')
            candidates = [
                c for c in game.trade_row
                if c.cost <= max_cost and (
                    card_type == 'ship' and c.type != 'Base' or
                    card_type == 'base' and c.type == 'Base' or
                    card_type in ('ship or base', 'any')
                )
            ]
            if not candidates:
                # Try explorers if ships are allowed
                if card_type in ('ship', 'ship or base', 'any') and game.explorer_pile:
                    first = game.explorer_pile[0]
                    if first.cost <= max_cost:
                        return game_service.resolve_acquire_free_to_top(game.game_id, ai_player.player_id, first.instance_id, from_explorers=True)
                game.pending_effect = None
                return game
            # Pick most expensive
            best = max(candidates, key=lambda c: c.cost)
            print(f"  🆓 AIacquiring {best.name} for free")
            return game_service.resolve_acquire_free_to_top(game.game_id, ai_player.player_id, best.instance_id)

        elif effect_type == 'discard_any_number':
            current_player = game.get_player(ai_player.player_id)
            hand = list(current_player.hand)
            for card in hand:
                game = game_service.resolve_discard_any(game.game_id, ai_player.player_id, card.instance_id)
                current_game = game_service.games.get(game.game_id)
                if not current_game or not current_game.pending_effect:
                    break
                game = current_game
            current_game = game_service.games.get(game.game_id)
            if current_game and current_game.pending_effect and current_game.pending_effect.get('type') == 'discard_any_number':
                game = game_service.finish_discard_any(game.game_id, ai_player.player_id)
            return game

        elif effect_type == 'copy_ship':
            current_player = game.get_player(ai_player.player_id)
            ships = [c for c in current_player.in_play if c.type != 'Base' and c.name != 'Stealth Needle']
            if ships:
                best = max(ships, key=lambda c: c.cost)
                print(f"  🔮 AIcopying ship: {best.name}")
                return game_service.resolve_copy_ship(game.game_id, ai_player.player_id, best.instance_id)
            else:
                game.pending_effect = None
                return game

        elif effect_type == 'base_from_discard_to_top':
            current_player = game.get_player(ai_player.player_id)
            bases_in_discard = [c for c in current_player.discard_pile if c.type == 'Base']
            if not bases_in_discard:
                if optional:
                    return game_service.skip_effect(game.game_id, ai_player.player_id)
                game.pending_effect = None
                return game
            # Pick most expensive base
            best = max(bases_in_discard, key=lambda c: c.cost)
            print(f"  📦 AImoving {best.name} to top of deck")
            return game_service.resolve_base_from_discard_to_top(game.game_id, ai_player.player_id, best.instance_id)

        else:
            # Unknown effect type — skip if optional, clear otherwise
            if optional:
                return game_service.skip_effect(game.game_id, ai_player.player_id)
            game.pending_effect = None
            return game


# Global AIservice instance
ai_service = AIService()
