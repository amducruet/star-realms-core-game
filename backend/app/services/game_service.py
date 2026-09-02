"""
Game service - handles all game logic and rules.
"""
import json
import random
import time
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.models.card import CardDefinition, CardInstance
from app.models.game import GameState, GamePhase, TurnPhase, GameConfig, GameAction
from app.models.player import Player
from app.services.card_parser import parse_card, EffectType, ParsedCard
from app.services.ai_service import ai_service


class GameService:
    """Service for managing game state and rules."""

    def __init__(self):
        """Initialize game service and load card database."""
        self.games: Dict[str, GameState] = {}
        self.card_db: Dict[str, CardDefinition] = {}
        self._load_cards()

    def _load_cards(self):
        """Load card definitions from JSON."""
        cards_path = Path(__file__).parent.parent / 'data' / 'cards.json'
        with open(cards_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert all cards to CardDefinition objects
        for card_data in data['all_cards']:
            card_def = CardDefinition(**card_data)
            self.card_db[card_def.id] = card_def

    def create_game(self, game_id: str, player_names: List[str], ai_count: int = 0, starting_authority: int = 50) -> GameState:
        """Create a new game."""
        config = GameConfig(starting_authority=starting_authority)

        game = GameState(
            game_id=game_id,
            phase=GamePhase.LOBBY,
            config=config
        )

        # Create human players
        for name in player_names:
            player = Player(
                player_id=str(uuid.uuid4()),
                name=name,
                authority=starting_authority,
                is_ai=False
            )
            game.players.append(player)

        # Create AIplayers
        for i in range(ai_count):
            player = Player(
                player_id=str(uuid.uuid4()),
                name=f"Robot Player {i + 1}",
                authority=starting_authority,
                is_ai=True
            )
            game.players.append(player)

        self.games[game_id] = game
        return game

    def join_game(self, game_id: str, player_name: str) -> tuple:
        """Add a human player to a lobby-phase game. Returns (game, player_id)."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        if game.phase != GamePhase.LOBBY:
            raise ValueError("Game has already started")
        if len(game.players) >= game.config.max_players:
            raise ValueError("Game is full")

        player = Player(
            player_id=str(uuid.uuid4()),
            name=player_name,
            authority=game.config.starting_authority,
            is_ai=False
        )
        game.players.append(player)
        return game, player.player_id

    def start_game(self, game_id: str) -> GameState:
        """Start the game - deal starting decks and draw opening hands."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        if game.phase != GamePhase.LOBBY:
            raise ValueError("Game already started")

        # Initialize trade deck
        self._initialize_trade_deck(game)

        # Initialize explorer pile
        self._initialize_explorer_pile(game)

        # Deal starting decks to each player
        for player in game.players:
            self._deal_starting_deck(player)

        # Draw opening hands
        for player in game.players:
            self._draw_cards(player, game.config.starting_hand_size)

        # Randomize starting player
        game.current_player_index = random.randint(0, len(game.players) - 1)

        game.phase = GamePhase.PLAYING
        game.turn_phase = TurnPhase.MAIN

        return game

    def _initialize_trade_deck(self, game: GameState):
        """Initialize and shuffle the trade deck."""
        trade_cards = []

        for card_def in self.card_db.values():
            if card_def.role == 'Trade Deck':
                # Add the specified quantity of each card
                for _ in range(card_def.quantity):
                    instance = self._create_card_instance(card_def)
                    trade_cards.append(instance)

        # Shuffle
        random.shuffle(trade_cards)
        game.trade_deck = trade_cards

        # Fill initial trade row
        for _ in range(game.config.trade_row_size):
            if game.trade_deck:
                game.trade_row.append(game.trade_deck.pop(0))

    def _initialize_explorer_pile(self, game: GameState):
        """Initialize the explorer pile."""
        for card_def in self.card_db.values():
            if card_def.role == 'Explorer Pile':
                for _ in range(card_def.quantity):
                    instance = self._create_card_instance(card_def)
                    game.explorer_pile.append(instance)

    def _deal_starting_deck(self, player: Player):
        """Deal starting deck to a player (8 Scouts + 2 Vipers)."""
        scouts_needed = 8
        vipers_needed = 2

        for card_def in self.card_db.values():
            if card_def.role == 'Personal Deck':
                if 'Scout' in card_def.name and scouts_needed > 0:
                    for _ in range(scouts_needed):
                        instance = self._create_card_instance(card_def)
                        player.deck.append(instance)
                    scouts_needed = 0

                if 'Viper' in card_def.name and vipers_needed > 0:
                    for _ in range(vipers_needed):
                        instance = self._create_card_instance(card_def)
                        player.deck.append(instance)
                    vipers_needed = 0

        # Shuffle player's deck
        random.shuffle(player.deck)

    def _create_card_instance(self, card_def: CardDefinition) -> CardInstance:
        """Create a card instance from a definition."""
        return CardInstance(
            instance_id=str(uuid.uuid4()),
            card_id=card_def.id,
            name=card_def.name,
            type=card_def.type,
            faction=card_def.faction,
            cost=card_def.cost,
            defense=card_def.defense,
            is_outpost=card_def.is_outpost,
            text=card_def.text,
            current_defense=card_def.defense  # Initialize current defense
        )

    def _draw_cards(self, player: Player, count: int):
        """Draw cards from deck to hand. Reshuffle discard if needed."""
        for _ in range(count):
            if not player.deck:
                # Reshuffle discard pile into deck
                if player.discard_pile:
                    player.deck = player.discard_pile.copy()
                    player.discard_pile.clear()
                    random.shuffle(player.deck)
                else:
                    # No cards left to draw
                    break

            if player.deck:
                card = player.deck.pop(0)
                player.hand.append(card)

    def play_hand_batch(self, game_id: str, player_id: str) -> GameState:
        """Play the hand as an order-independent batch, pausing for decisions."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player or game.current_player.player_id != player_id:
            raise ValueError("Not your turn")
        if game.pending_effect:
            raise ValueError(f"Must resolve pending effect: {game.pending_effect['type']}")

        if not player.bases_settled_this_turn:
            # Existing bases share the human pre-settlement window with hand
            # cards: scrap first, or cash their recurring effects now.
            player.bases_settled_this_turn = True
            self._activate_bases(player, game)

        if game.base_activation:
            self._advance_base_activation(player, game)
            if game.pending_effect or game.base_activation:
                return game

        if not game.play_batch:
            if not player.hand:
                return game
            game.play_batch = {
                'player_id': player_id,
                'card_ids': [card.instance_id for card in player.hand],
                'decisions': {},
                'skipped': [],
                'copies': {},
                'phase': 'copying',
            }

        if game.play_batch.get('player_id') != player_id:
            raise ValueError("Another player's hand batch is active")
        return self._advance_play_batch(game, player)

    def _batch_scrap_effects(self, player: Player, game: GameState, survivor_ids: set) -> list:
        """Return scrap opportunities supplied by cards still surviving the batch."""
        batch_cards = [card for card in player.hand if card.instance_id in survivor_ids]
        effects = []
        for card in batch_cards:
            copied_id = game.play_batch.get('copies', {}).get(card.instance_id)
            copied_card = next((candidate for candidate in batch_cards if candidate.instance_id == copied_id), None)
            ability_card = copied_card or card
            faction = ability_card.faction
            parsed = parse_card(ability_card.text, faction)
            allies = self._count_allies(player, faction)
            for other in batch_cards:
                if other.instance_id != card.instance_id and (
                    self._batch_card_has_faction(other, faction, game.play_batch, batch_cards) or other.name == 'Mech World'
                ):
                    allies += 1
            card_effects = parsed.get_primary_effects() + parsed.get_ally_effects(allies)
            scrap_effects = [effect for effect in card_effects if effect.get('type') == EffectType.SCRAP_CARD]
            for index, effect in enumerate(scrap_effects):
                effects.append((f"{card.instance_id}:{index}", card, effect))
        return effects

    def _batch_card_has_faction(self, card: CardInstance, faction: str, batch: dict, batch_cards: list) -> bool:
        if self._card_has_faction(card, faction):
            return True
        copied_id = batch.get('copies', {}).get(card.instance_id)
        copied = next((candidate for candidate in batch_cards if candidate.instance_id == copied_id), None)
        return bool(copied and copied.faction == faction)

    def _advance_play_batch(self, game: GameState, player: Player) -> GameState:
        batch = game.play_batch
        if not batch:
            return game

        if batch.get('phase') == 'copying':
            batch_cards = [card for card in player.hand if card.instance_id in batch['card_ids']]
            for needle in (card for card in batch_cards if card.name == 'Stealth Needle'):
                if needle.instance_id in batch['copies']:
                    continue
                candidates = [
                    card.instance_id for card in batch_cards
                    if card.instance_id != needle.instance_id and card.type != 'Base' and card.name != 'Stealth Needle'
                ]
                if not candidates:
                    continue
                batch['current_copy_source'] = needle.instance_id
                game.pending_effect = {
                    'type': 'copy_ship',
                    'optional': False,
                    'batch_copy': True,
                    'source_name': needle.name,
                    'eligible_instance_ids': candidates,
                }
                return game
            batch['phase'] = 'scrapping'

        if batch.get('phase') == 'scrapping':
            # Recompute until decisions made by cards that were themselves
            # scrapped have been removed (strict batch semantics).
            while True:
                decisions = batch['decisions']
                targeted_batch_ids = {
                    value['instance_id'] for value in decisions.values()
                    if value.get('location') == 'hand'
                }
                survivor_ids = set(batch['card_ids']) - targeted_batch_ids
                active = {key: (source, effect) for key, source, effect in self._batch_scrap_effects(player, game, survivor_ids)}
                stale = [key for key in decisions if key not in active]
                stale_skips = [key for key in batch['skipped'] if key not in active]
                if not stale and not stale_skips:
                    break
                for key in stale:
                    decisions.pop(key, None)
                batch['skipped'] = [key for key in batch['skipped'] if key in active]

            reserved_ids = {value['instance_id'] for value in batch['decisions'].values()}
            for key, (source, effect) in active.items():
                if key in batch['decisions'] or key in batch['skipped']:
                    continue
                location = effect.get('location', 'hand')
                candidates = []
                if location in ('hand', 'hand_or_discard'):
                    candidates.extend(
                        card.instance_id for card in player.hand
                        if card.instance_id in survivor_ids
                        and card.instance_id != source.instance_id
                        and card.instance_id not in reserved_ids
                    )
                if location in ('discard', 'hand_or_discard'):
                    candidates.extend(card.instance_id for card in player.discard_pile if card.instance_id not in reserved_ids)
                if location == 'trade_row':
                    candidates.extend(card.instance_id for card in game.trade_row if card.instance_id not in reserved_ids)
                if not candidates:
                    batch['skipped'].append(key)
                    continue
                batch['current_effect_key'] = key
                game.pending_effect = {
                    **effect,
                    'type': 'scrap_card',
                    'optional': effect.get('optional', False),
                    'batch_scrap': True,
                    'source_name': source.name,
                    'eligible_instance_ids': candidates,
                }
                return game

            # All surviving scrap sources have decisions. Apply the decisions
            # now, before any normal card abilities are awarded.
            active_keys = set(active)
            for key, decision in list(batch['decisions'].items()):
                if key not in active_keys:
                    continue
                card = self._remove_scrap_target(player, game, decision['instance_id'], decision['location'])
                game.scrap_heap.append(card)
                player.scrapped_this_turn += 1
                if decision['location'] == 'hand':
                    parsed = parse_card(card.text, card.faction)
                    for scrap_effect in parsed.get_scrap_effects():
                        self._execute_effect(player, scrap_effect, game)
                game.action_log.append(GameAction(
                    action_id=str(uuid.uuid4()), action_type="scrap_card", player_id=player.player_id,
                    timestamp=time.time(), data={"instance_id": card.instance_id, "card_name": card.name,
                                                 "from_location": decision['location']}
                ))
            batch['phase'] = 'playing'
            batch.pop('current_effect_key', None)

        # Play surviving original cards. Ordinary pending effects pause here;
        # calling play_hand_batch after they clear resumes this same batch.
        while not game.pending_effect:
            next_card = next((card for card in player.hand if card.instance_id in batch['card_ids']), None)
            if not next_card:
                game.play_batch = None
                # Cards drawn during play form a fresh batch. Human players
                # get a new pre-settlement window in which they may use a
                # printed Scrap ability; Robots continue through their loop.
                return game
            copied_id = batch.get('copies', {}).get(next_card.instance_id)
            copied_card = next((
                card for card in list(player.hand) + list(player.in_play) + list(game.scrap_heap)
                if card.instance_id == copied_id
            ), None)
            if copied_card and copied_card.faction not in ('Unaligned', next_card.faction):
                if copied_card.faction not in next_card.additional_factions:
                    next_card.additional_factions.append(copied_card.faction)
            self.play_card(game.game_id, player.player_id, next_card.instance_id)
            if copied_card:
                player.faction_played_count[copied_card.faction] = player.faction_played_count.get(copied_card.faction, 0) + 1
                self._apply_copied_ship_effects(player, next_card, copied_card, game)
        return game

    def _apply_copied_ship_effects(self, player: Player, needle: CardInstance, copied: CardInstance, game: GameState):
        """Apply the selected ship's abilities as Stealth Needle's abilities."""
        parsed = parse_card(copied.text, copied.faction)
        for effect in parsed.get_primary_effects():
            self._execute_effect(player, effect, game)
        ally_count = self._count_allies(player, copied.faction, exclude_card=needle)
        if game.play_batch:
            targeted = {
                decision['instance_id'] for decision in game.play_batch.get('decisions', {}).values()
                if decision.get('location') == 'hand'
            }
            for card in player.hand:
                if (
                    card.instance_id in game.play_batch.get('card_ids', [])
                    and card.instance_id not in targeted
                    and card.instance_id != needle.instance_id
                    and (self._batch_card_has_faction(card, copied.faction, game.play_batch, list(player.hand))
                         or card.name == 'Mech World')
                ):
                    ally_count += 1
        for effect in parsed.get_ally_effects(ally_count):
            self._execute_effect(player, effect, game)

    def _remove_scrap_target(self, player: Player, game: GameState, instance_id: str, location: str) -> CardInstance:
        zones = {
            'hand': player.hand,
            'discard': player.discard_pile,
            'trade_row': game.trade_row,
        }
        zone = zones.get(location)
        if zone is None:
            raise ValueError(f"Invalid scrap location: {location}")
        card = next((candidate for candidate in zone if candidate.instance_id == instance_id), None)
        if not card:
            raise ValueError(f"Card {instance_id} not found in {location}")
        zone.remove(card)
        if location == 'trade_row' and game.trade_deck:
            game.trade_row.append(game.trade_deck.pop(0))
        return card

    def play_card(self, game_id: str, player_id: str, instance_id: str) -> GameState:
        """Play a card from hand."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        if game.turn_phase != TurnPhase.MAIN:
            raise ValueError("Can only play cards during main phase")

        if game.pending_effect:
            raise ValueError(f"Must resolve pending effect before playing another card: {game.pending_effect['type']}")

        # Find card in hand
        card = None
        for c in player.hand:
            if c.instance_id == instance_id:
                card = c
                break

        if not card:
            raise ValueError(f"Card {instance_id} not in hand")

        # Remove from hand
        player.hand.remove(card)

        # Apply card effects based on type
        if card.type == 'Base':
            player.bases.append(card)
        else:
            player.in_play.append(card)

        # Track faction plays for Blob World / Fleet HQ
        if card.type != 'Base':
            faction = card.faction
            player.faction_played_count[faction] = player.faction_played_count.get(faction, 0) + 1
            # Fleet HQ: +1 combat per ship played
            for base in player.bases:
                if base.name == 'Fleet HQ':
                    player.combat += 1
                    print(f"  ⚡ Fleet HQ: +1 Combat (total {player.combat})")

        # Parse and apply card effects
        self._apply_card_effects(player, card, game=game)

        # Log action for animations (Phase 2)
        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="play_card",
            player_id=player_id,
            timestamp=time.time(),
            data={
                "instance_id": instance_id,
                "card_name": card.name,
                "card_type": card.type
            }
        )
        game.action_log.append(action)

        return game

    def _apply_card_effects(self, player: Player, card: CardInstance, game=None):
        """Apply card effects using the proper parser with ally abilities."""
        parsed_card = parse_card(card.text, card.faction)

        # Primary effects always apply
        for effect in parsed_card.get_primary_effects():
            self._execute_effect(player, effect, game=game)

        # Apply this card's ally ability if allies already in play
        ally_count = self._count_allies(player, card.faction, exclude_card=card)
        ally_effects = parsed_card.get_ally_effects(ally_count)
        if ally_effects:
            print(f"  → {card.name} triggers its own ally ({ally_count} {card.faction} allies in play)")
        for effect in ally_effects:
            self._execute_effect(player, effect, game=game)

        # Retroactively fire ally abilities on previously played cards of the same faction
        # that now have their threshold met by this new card
        for faction in [card.faction, *card.additional_factions]:
            if faction != 'Unaligned':
                self._trigger_retroactive_ally(player, card, game, faction)

    def _trigger_retroactive_ally(self, player: Player, new_card: CardInstance, game=None, faction: Optional[str] = None):
        """
        When a new card is played, check all previously played same-faction cards
        and fire their ally/double-ally abilities if this card pushes them over threshold.
        """
        faction = faction or new_card.faction
        # Total allies NOW (including the new card)
        total = self._count_allies(player, faction, exclude_card=None)
        # Total allies BEFORE this card was added
        total_before = total - 1  # new_card is already in in_play/bases

        for existing_card in list(player.in_play) + list(player.bases):
            if existing_card.instance_id == new_card.instance_id:
                continue
            if not self._card_has_faction(existing_card, faction):
                continue

            # Allies available to existing_card now (total minus itself)
            allies_now = total - 1
            # Allies available to existing_card before new_card was added (minus itself and new_card)
            allies_before = total - 2

            parsed = parse_card(existing_card.text, existing_card.faction)

            # Fire regular ally if threshold just crossed 0→1
            if parsed.ally_ability and allies_before < 1 <= allies_now:
                print(f"  → {existing_card.name} retroactive ally triggered by {new_card.name}")
                for effect in parsed.ally_ability.effects:
                    self._execute_effect(player, effect, game=game)

            # Fire double ally if threshold just crossed 1→2
            if parsed.double_ally_ability and allies_before < 2 <= allies_now:
                print(f"  → {existing_card.name} retroactive double-ally triggered by {new_card.name}")
                for effect in parsed.double_ally_ability.effects:
                    self._execute_effect(player, effect, game=game)

    def _count_allies(self, player: Player, faction: str, exclude_card: Optional[CardInstance] = None) -> int:
        """Count how many OTHER cards of the same faction are in play."""
        if faction == 'Unaligned':
            return 0

        count = 0
        for card in list(player.in_play) + list(player.bases):
            if exclude_card and card.instance_id == exclude_card.instance_id:
                continue
            # Mech World counts as an ally for every faction
            if self._card_has_faction(card, faction) or card.name == 'Mech World':
                count += 1

        return count

    @staticmethod
    def _card_has_faction(card: CardInstance, faction: str) -> bool:
        return card.faction == faction or faction in card.additional_factions

    def _execute_effect(self, player: Player, effect: Dict[str, Any], game=None):
        """Execute a single card effect."""
        effect_type = effect.get('type')

        if effect_type == EffectType.GAIN_COMBAT:
            amount = effect.get('amount', 0)
            player.combat += amount
            print(f"  → Gained {amount} Combat (total: {player.combat})")

        elif effect_type == EffectType.GAIN_TRADE:
            amount = effect.get('amount', 0)
            player.trade += amount
            print(f"  → Gained {amount} Trade (total: {player.trade})")

        elif effect_type == EffectType.GAIN_AUTHORITY:
            amount = effect.get('amount', 0)
            player.authority += amount
            print(f"  → Gained {amount} Authority (total: {player.authority})")

        elif effect_type == EffectType.DRAW_CARDS:
            amount = effect.get('amount', 0)
            self._draw_cards(player, amount)
            print(f"  → Drew {amount} card(s)")

        elif effect_type == EffectType.NEXT_ACQUIRE_TO_TOP:
            player.next_acquire_to_top = True
            player.next_acquire_to_top_type = effect.get('card_type', 'any')
            print(f"  → Next {effect.get('card_type','ship')} acquired will go to top of deck")

        elif effect_type == EffectType.ACQUIRE_FREE_TO_TOP and game is not None:
            card_type = effect.get('card_type', 'ship')
            max_cost = effect.get('max_cost', 999)
            eligible = [
                card for card in game.trade_row
                if card.cost <= max_cost and (
                    (card_type == 'ship' and card.type != 'Base') or
                    (card_type == 'base' and card.type == 'Base') or
                    card_type in ('ship or base', 'any')
                )
            ]
            explorer_eligible = (
                card_type in ('ship', 'ship or base', 'any') and
                bool(game.explorer_pile) and
                game.explorer_pile[0].cost <= max_cost
            )
            if not eligible and not explorer_eligible:
                return
            game.pending_effect = {
                'type': 'acquire_free_to_top',
                'card_type': card_type,
                'max_cost': max_cost,
                'optional': False,
            }
            print(f"  → Pending acquire-free-to-top: {effect.get('card_type')} cost<={effect.get('max_cost',999)}")

        elif effect_type == EffectType.BASE_FROM_DISCARD_TO_TOP and game is not None:
            if not any(card.type == 'Base' for card in player.discard_pile):
                return
            game.pending_effect = {
                'type': 'base_from_discard_to_top',
                'optional': effect.get('optional', False),
            }
            print(f"  → Pending base-from-discard-to-top")

        elif effect_type == EffectType.CONDITIONAL and game is not None:
            condition = effect.get('condition')
            if condition == 'min_bases':
                if len(player.bases) >= effect.get('min_bases', 2):
                    for sub_effect in effect.get('effects', []):
                        self._execute_effect(player, sub_effect, game)
                    print(f"  → Conditional met ({len(player.bases)} bases >= {effect.get('min_bases')})")
                else:
                    print(f"  → Conditional not met ({len(player.bases)} bases < {effect.get('min_bases')})")

        elif effect_type == EffectType.CHOICE and game is not None:
            options = effect.get('options', [])
            if not options:
                return
            game.pending_effect = {
                'type': 'choice',
                'options': options,
                'labels': effect.get('labels', []),
                'optional': effect.get('optional', False),
            }
            print(f"  → Pending choice: {effect.get('labels')}")

        elif effect_type == EffectType.SCRAP_CARD and game is not None:
            if game.play_batch and game.play_batch.get('phase') == 'playing':
                return
            location = effect.get('location', 'hand')
            has_target = (
                (location == 'trade_row' and bool(game.trade_row)) or
                (location in ('hand', 'hand_or_discard') and bool(player.hand)) or
                (location in ('discard', 'hand_or_discard') and bool(player.discard_pile))
            )
            if not has_target:
                return
            game.pending_effect = {
                'type': 'scrap_card',
                'location': location,
                'optional': effect.get('optional', False),
                'gain_cost_as_combat': effect.get('gain_cost_as_combat', False),
                'on_resolve_effects': effect.get('on_resolve_effects', []),
                'for_each_effects': effect.get('for_each_effects', []),
                'max_count': effect.get('max_count', 1),
                'scrapped_count': 0,
            }
            print(f"  → Pending scrap effect: location={effect.get('location', 'hand')}")

        elif effect_type == EffectType.DISCARD_CARD and game is not None:
            target_type = effect.get('target', 'opponent')
            if target_type == 'self':
                has_target = bool(player.hand)
                target_player_id = player.player_id
            else:
                targets = [
                    candidate for candidate in game.players
                    if candidate.player_id != player.player_id and candidate.authority > 0 and candidate.hand
                ]
                has_target = bool(targets)
                # Star Realms is normally two-player. Keeping the selected
                # target on the pending effect also prevents another client
                # from answering this player's discard choice.
                target_player_id = targets[0].player_id if targets else None
            if not has_target:
                return
            game.pending_effect = {
                'type': 'discard_card',
                'target': target_type,
                'target_player_id': target_player_id,
                'amount': effect.get('amount', 1),
                'optional': effect.get('optional', False),
            }
            print(f"  → Pending discard effect: target={effect.get('target', 'opponent')}")

        elif effect_type == EffectType.DESTROY_BASE and game is not None:
            if not any(p.player_id != player.player_id and p.authority > 0 and p.bases for p in game.players):
                return
            game.pending_effect = {
                'type': 'destroy_base',
                'optional': effect.get('optional', False),
            }
            print(f"  → Pending destroy base effect")

        elif effect_type == EffectType.GAIN_COMBAT_PER_SCRAPPED:
            amount = effect.get('amount', 1)
            total = player.scrapped_this_turn + 1  # +1 for the card being scrapped now
            gained = amount * total
            player.combat += gained
            print(f"  → Gained {gained} Combat ({amount} × {total} scrapped this turn)")

        elif effect_type == EffectType.DRAW_PER_FACTION_PLAYED:
            faction = effect.get('faction', '')
            count = player.faction_played_count.get(faction, 0)
            for _ in range(count):
                self._draw_cards(player, 1)
            print(f"  → Drew {count} cards for {count} {faction} cards played")

        elif effect_type == EffectType.DISCARD_ANY_NUMBER and game is not None:
            game.pending_effect = {
                'type': 'discard_any_number',
                'per_discard_effects': effect.get('per_discard_effects', []),
                'on_complete_effects': effect.get('on_complete_effects', []),
                'optional': True,
            }
            print(f"  → Pending discard_any_number effect")

        elif effect_type == EffectType.COPY_SHIP and game is not None:
            if game.play_batch and game.play_batch.get('phase') == 'playing':
                return
            ships = [c for c in player.in_play if c.name != 'Stealth Needle' and c.type != 'Base']
            if ships:
                game.pending_effect = {
                    'type': 'copy_ship',
                    'optional': False,
                }
                print(f"  → Pending copy_ship effect")

    def acquire_card(self, game_id: str, player_id: str, instance_id: str, from_explorers: bool = False) -> GameState:
        """Acquire a card from trade row or explorer pile."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        # Find and remove card from source
        card = None
        if from_explorers:
            if not game.explorer_pile:
                raise ValueError("Explorer pile is empty")
            card = game.explorer_pile.pop(0)
        else:
            for c in game.trade_row:
                if c.instance_id == instance_id:
                    card = c
                    break

            if not card:
                raise ValueError(f"Card {instance_id} not in trade row")

            game.trade_row.remove(card)

        # Check if player can afford it
        if player.trade < card.cost:
            # Put card back
            if from_explorers:
                game.explorer_pile.insert(0, card)
            else:
                game.trade_row.append(card)
            raise ValueError(f"Not enough trade. Need {card.cost}, have {player.trade}")

        # Pay cost
        player.trade -= card.cost

        # Check if next-acquire-to-top modifier applies
        type_matches = (
            player.next_acquire_to_top_type == 'any' or
            (player.next_acquire_to_top_type == 'ship' and card.type != 'Base') or
            (player.next_acquire_to_top_type == 'base' and card.type == 'Base') or
            (player.next_acquire_to_top_type == 'ship_or_base')
        )
        if player.next_acquire_to_top and type_matches:
            player.deck.insert(0, card)
            player.next_acquire_to_top = False
            player.next_acquire_to_top_type = 'any'
            print(f"  → {card.name} placed on top of deck")
        else:
            player.discard_pile.append(card)

        # Refill trade row if not from explorers
        if not from_explorers and game.trade_deck:
            game.trade_row.append(game.trade_deck.pop(0))

        # Log action
        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="acquire_card",
            player_id=player_id,
            timestamp=time.time(),
            data={
                "instance_id": instance_id,
                "card_name": card.name,
                "from_explorers": from_explorers
            }
        )
        game.action_log.append(action)

        return game

    def attack_opponent(self, game_id: str, player_id: str, target_player_id: str, damage: Optional[int] = None) -> GameState:
        """Attack an opponent with combat."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        target = game.get_player(target_player_id)

        if not player or not target:
            raise ValueError("Player not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        # Use all available combat if damage not specified
        if damage is None:
            damage = player.combat

        if damage > player.combat:
            raise ValueError("Not enough combat")

        # Non-outpost bases must be destroyed before attacking the player directly
        # Outposts do not block direct player attacks
        non_outpost_bases = [b for b in target.bases if not b.is_outpost]
        if non_outpost_bases:
            raise ValueError("Must destroy all non-outpost bases before attacking player")

        # Deal damage
        player.combat -= damage
        target.authority -= damage

        # Check for winner — only end game when all opponents are eliminated
        if target.authority <= 0:
            alive_opponents = [p for p in game.players if p.player_id != player_id and p.authority > 0]
            if not alive_opponents:
                game.phase = GamePhase.ENDED
                game.winner_id = player_id

        # Log action
        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="deal_damage",
            player_id=player_id,
            timestamp=time.time(),
            data={
                "target_player_id": target_player_id,
                "damage": damage
            }
        )
        game.action_log.append(action)

        return game

    def distribute_damage(self, game_id: str, player_id: str, targets: list[dict]) -> GameState:
        """Distribute damage among multiple opponents."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError("Player not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        # Calculate total damage to distribute
        total_damage = sum(t.get("damage", 0) for t in targets)

        if total_damage > player.combat:
            raise ValueError(f"Not enough combat. Have {player.combat}, trying to use {total_damage}")

        if total_damage <= 0:
            raise ValueError("Must deal at least 1 damage")

        # Validate all targets and check for outposts
        for target_data in targets:
            target_player_id = target_data.get("player_id")
            damage = target_data.get("damage", 0)

            if damage <= 0:
                continue

            target = game.get_player(target_player_id)
            if not target:
                raise ValueError(f"Target player {target_player_id} not found")

            # Non-outpost bases must be destroyed before dealing direct damage
            non_outpost_bases = [b for b in target.bases if not b.is_outpost]
            if non_outpost_bases:
                raise ValueError(f"{target.name} has bases that must be destroyed first")

        # Apply damage to all targets
        for target_data in targets:
            target_player_id = target_data.get("player_id")
            damage = target_data.get("damage", 0)

            if damage <= 0:
                continue

            target = game.get_player(target_player_id)
            target.authority -= damage

            # Check if this player is eliminated
            if target.authority <= 0:
                # In multiplayer, only end game when all opponents are eliminated
                alive_opponents = [p for p in game.players if p.player_id != player_id and p.authority > 0]
                if not alive_opponents:
                    game.phase = GamePhase.ENDED
                    game.winner_id = player_id

        # Deduct combat
        player.combat -= total_damage

        # Log action
        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="distribute_damage",
            player_id=player_id,
            timestamp=time.time(),
            data={
                "targets": targets,
                "total_damage": total_damage
            }
        )
        game.action_log.append(action)

        return game

    def attack_base(self, game_id: str, player_id: str, target_player_id: str, instance_id: str, damage: int) -> GameState:
        """Attack an opponent's base."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        target = game.get_player(target_player_id)

        if not player or not target:
            raise ValueError("Player not found")

        if damage > player.combat:
            raise ValueError("Not enough combat")

        # Find base
        base = None
        for b in target.bases:
            if b.instance_id == instance_id:
                base = b
                break

        if not base:
            raise ValueError(f"Base {instance_id} not found")

        # Apply damage
        player.combat -= damage
        base.current_defense -= damage

        # Check if base is destroyed
        if base.current_defense <= 0:
            target.bases.remove(base)
            base.current_defense = base.defense
            target.discard_pile.append(base)

            # Log destruction
            action = GameAction(
                action_id=str(uuid.uuid4()),
                action_type="destroy_base",
                player_id=player_id,
                timestamp=time.time(),
                data={
                    "target_player_id": target_player_id,
                    "instance_id": instance_id,
                    "card_name": base.name
                }
            )
            game.action_log.append(action)

        return game

    def scrap_card(self, game_id: str, player_id: str, instance_id: str) -> GameState:
        """Scrap a card (remove from game permanently) and apply its scrap effect."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        # Find card in hand, in play, or bases.
        card = None
        location = None

        for c in player.hand:
            if c.instance_id == instance_id:
                card = c
                location = 'hand'
                break

        if not card:
            for c in player.in_play:
                if c.instance_id == instance_id:
                    card = c
                    location = 'in_play'
                    break

        if not card:
            for c in player.bases:
                if c.instance_id == instance_id:
                    card = c
                    location = 'bases'
                    break

        if not card:
            raise ValueError(f"Card {instance_id} not in hand, play, or bases")

        if location == 'hand' and (game.play_batch or game.pending_effect):
            raise ValueError("Cannot scrap a hand card while its batch is being resolved")
        if location == 'in_play':
            raise ValueError(f"{card.name}'s benefits have already been cashed in")
        if location == 'bases' and player.bases_settled_this_turn:
            raise ValueError(f"{card.name}'s benefits have already been cashed in")

        # Parse card to check for scrap ability
        parsed_card = parse_card(card.text, card.faction)

        if not parsed_card.has_scrap_ability():
            raise ValueError(f"{card.name} has no scrap ability")

        # Remove card from current location
        if location == 'hand':
            player.hand.remove(card)
        elif location == 'in_play':
            player.in_play.remove(card)
        else:
            player.bases.remove(card)

        # Add to scrap heap
        game.scrap_heap.append(card)
        player.scrapped_this_turn += 1

        # Apply scrap effects
        scrap_effects = parsed_card.get_scrap_effects()
        print(f"  🗑️ Scrapping {card.name}")
        for effect in scrap_effects:
            self._execute_effect(player, effect, game=game)

        # Log action
        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="scrap_card",
            player_id=player_id,
            timestamp=time.time(),
            data={
                "instance_id": instance_id,
                "card_name": card.name
            }
        )
        game.action_log.append(action)

        return game

    def end_turn(self, game_id: str, player_id: str) -> GameState:
        """End the current turn."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        # Recover a batch whose last server-side pending effect was resolved
        # automatically (for example, an AI opponent's forced discard).
        if game.play_batch and not game.pending_effect:
            self._advance_play_batch(game, player)

        # A batch must be completed (including optional decisions) before its
        # cards can be discarded at end of turn.
        if game.pending_effect:
            raise ValueError(f"Must resolve pending effect: {game.pending_effect['type']}")
        if game.play_batch:
            raise ValueError("Must finish playing the current hand batch")
        if game.base_activation:
            raise ValueError("Must finish activating your bases")

        # Discard hand and played cards
        for card in list(player.hand) + list(player.in_play) + list(player.bases):
            card.additional_factions.clear()
        player.discard_pile.extend(player.hand)
        player.discard_pile.extend(player.in_play)
        player.hand.clear()
        player.in_play.clear()

        # Reset base defenses (damage doesn't carry over between turns)
        for base in player.bases:
            base.current_defense = base.defense

        # Reset resources
        player.combat = 0
        player.trade = 0
        player.next_acquire_to_top = False
        player.next_acquire_to_top_type = 'any'
        player.faction_played_count = {}
        player.scrapped_this_turn = 0

        # Draw new hand
        self._draw_cards(player, game.config.starting_hand_size)

        # Next player - skip eliminated players in multiplayer
        starting_index = game.current_player_index
        checks = 0
        max_checks = len(game.players)

        while checks < max_checks:
            game.current_player_index = (game.current_player_index + 1) % len(game.players)
            next_player = game.players[game.current_player_index]
            checks += 1

            print(f"🔄 Checking player {game.current_player_index}: {next_player.name} (Authority: {next_player.authority})")

            # If this player is alive, it's their turn
            if next_player.authority > 0:
                print(f"✅ Next turn goes to: {next_player.name}")
                break

            # If we've checked everyone and no one is alive
            if checks >= max_checks:
                print(f"⚠️ No alive players found after checking {checks} players")
                raise ValueError("No alive players found")

        game.turn_phase = TurnPhase.MAIN

        # The next player chooses whether to scrap each existing base before
        # settling its recurring effects with Play Hand.
        game.current_player.bases_settled_this_turn = False

        return game

    def _activate_bases(self, player, game):
        """Start recurring activation of every in-play base."""
        if not player.bases:
            return
        print(f"🏰 Activating {len(player.bases)} base(s) for {player.name}")
        queued_effects = []
        for base in list(player.bases):
            parsed = parse_card(base.text, base.faction)
            for effect in parsed.get_primary_effects():
                queued_effects.append({'base_id': base.instance_id, 'base_name': base.name, 'effect': effect})
            ally_count = self._count_allies(player, base.faction, exclude_card=base)
            for effect in parsed.get_ally_effects(ally_count):
                queued_effects.append({'base_id': base.instance_id, 'base_name': base.name, 'effect': effect})
        if queued_effects:
            game.base_activation = {'player_id': player.player_id, 'effects': queued_effects, 'index': 0}
            self._advance_base_activation(player, game)

    def _advance_base_activation(self, player, game):
        """Run base effects in order, pausing safely for pending decisions."""
        activation = game.base_activation
        if not activation:
            return game
        effects = activation.get('effects', [])
        while activation['index'] < len(effects) and not game.pending_effect:
            entry = effects[activation['index']]
            activation['index'] += 1
            # A base destroyed before its queued activation no longer fires.
            if not any(base.instance_id == entry['base_id'] for base in player.bases):
                continue
            print(f"  🏰 {entry['base_name']} activates")
            self._execute_effect(player, entry['effect'], game)
        if activation['index'] >= len(effects) and not game.pending_effect:
            game.base_activation = None
        return game

    def resolve_scrap(self, game_id: str, player_id: str, instance_id: str, location: str) -> 'GameState':
        """Resolve a pending scrap_card effect by scrapping a card from hand or discard."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        if not game.pending_effect or game.pending_effect.get('type') != 'scrap_card':
            raise ValueError("No pending scrap effect")

        if game.pending_effect.get('batch_scrap'):
            if instance_id not in game.pending_effect.get('eligible_instance_ids', []):
                raise ValueError(f"Card {instance_id} is not eligible for this batch scrap")
            batch = game.play_batch
            if not batch or not batch.get('current_effect_key'):
                raise ValueError("No active batch scrap opportunity")
            batch['decisions'][batch.pop('current_effect_key')] = {
                'instance_id': instance_id,
                'location': location,
            }
            game.pending_effect = None
            return self._advance_play_batch(game, player)

        allowed_location = game.pending_effect.get('location', 'hand')
        if location == 'trade_row' and allowed_location != 'trade_row':
            raise ValueError(f"Cannot scrap from trade row for location: {allowed_location}")
        if location == 'hand' and allowed_location not in ('hand', 'hand_or_discard'):
            raise ValueError(f"Cannot scrap from hand for location: {allowed_location}")
        if location == 'discard' and allowed_location not in ('discard', 'hand_or_discard'):
            raise ValueError(f"Cannot scrap from discard for location: {allowed_location}")

        card = None
        if location == 'trade_row':
            for c in game.trade_row:
                if c.instance_id == instance_id:
                    card = c
                    break
            if card:
                game.trade_row.remove(card)
                # Refill trade row from deck
                if game.trade_deck:
                    game.trade_row.append(game.trade_deck.pop(0))
        elif location == 'hand':
            for c in player.hand:
                if c.instance_id == instance_id:
                    card = c
                    break
            if card:
                player.hand.remove(card)
        elif location == 'discard':
            for c in player.discard_pile:
                if c.instance_id == instance_id:
                    card = c
                    break
            if card:
                player.discard_pile.remove(card)

        if not card:
            raise ValueError(f"Card {instance_id} not found in {location}")

        game.scrap_heap.append(card)
        player.scrapped_this_turn += 1

        # Apply chained effects before clearing pending_effect
        pe = game.pending_effect
        scrapped_count = pe.get('scrapped_count', 0) + 1
        max_count = pe.get('max_count', 1)

        location = pe.get('location', 'hand')
        has_more_targets = (
            (location == 'trade_row' and bool(game.trade_row)) or
            (location in ('hand', 'hand_or_discard') and bool(player.hand)) or
            (location in ('discard', 'hand_or_discard') and bool(player.discard_pile))
        )
        if scrapped_count < max_count and has_more_targets:
            game.pending_effect = {**pe, 'scrapped_count': scrapped_count}
        else:
            game.pending_effect = None

        if pe.get('gain_cost_as_combat'):
            player.combat += card.cost
            print(f"  → Gained {card.cost} Combat from scrapping {card.name} (cost {card.cost})")

        for bonus_effect in pe.get('for_each_effects', []):
            self._execute_effect(player, bonus_effect, game)

        if game.pending_effect is None:
            for bonus_effect in pe.get('on_resolve_effects', []):
                self._execute_effect(player, bonus_effect, game)

        # A card scrapped directly from the hand was never played, so its
        # primary and ally abilities must not fire. It may still use its own
        # explicitly printed Scrap ability (for example, Battle Blob's +4
        # Combat). Apply it after completing the effect that selected the card
        # so any new pending effect it creates is preserved.
        if location == 'hand':
            parsed_card = parse_card(card.text, card.faction)
            for scrap_effect in parsed_card.get_scrap_effects():
                self._execute_effect(player, scrap_effect, game=game)

        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="scrap_card",
            player_id=player_id,
            timestamp=time.time(),
            data={"instance_id": instance_id, "card_name": card.name, "from_location": location}
        )
        game.action_log.append(action)
        return game

    def resolve_discard(self, game_id: str, player_id: str, target_player_id: str, instance_id: str) -> 'GameState':
        """Resolve a pending discard_card effect by choosing a card from target's hand."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if not game.pending_effect or game.pending_effect.get('type') != 'discard_card':
            raise ValueError("No pending discard effect")

        pe_target = game.pending_effect.get('target', 'opponent')
        if pe_target == 'self':
            # Current player discards their own card
            if game.current_player.player_id != player_id:
                raise ValueError("Not your turn")
            target = player
        else:
            # The targeted opponent chooses which card to discard
            expected_target_id = game.pending_effect.get('target_player_id')
            if expected_target_id and target_player_id != expected_target_id:
                raise ValueError("This discard choice belongs to another player")
            if player_id != target_player_id:
                raise ValueError("The targeted player must choose their own discard")
            target = game.get_player(target_player_id)
            if not target:
                raise ValueError(f"Target player {target_player_id} not found")

        card = None
        for c in target.hand:
            if c.instance_id == instance_id:
                card = c
                break

        if not card:
            raise ValueError(f"Card {instance_id} not found in target's hand")

        target.hand.remove(card)
        target.discard_pile.append(card)
        game.pending_effect = None

        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="discard_card",
            player_id=player_id,
            timestamp=time.time(),
            data={"instance_id": instance_id, "card_name": card.name, "target_player_id": target_player_id}
        )
        game.action_log.append(action)
        return game

    def resolve_destroy_base(self, game_id: str, player_id: str, target_player_id: str, instance_id: str) -> 'GameState':
        """Resolve a pending destroy_base effect by destroying a target opponent's base."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        if not game.pending_effect or game.pending_effect.get('type') != 'destroy_base':
            raise ValueError("No pending destroy base effect")

        target = game.get_player(target_player_id)
        if not target or target_player_id == player_id:
            raise ValueError(f"Invalid target player {target_player_id}")

        base = next((b for b in target.bases if b.instance_id == instance_id), None)
        if not base:
            raise ValueError(f"Base {instance_id} not found in target's bases")

        target.bases.remove(base)
        base.current_defense = base.defense
        target.discard_pile.append(base)
        game.pending_effect = None

        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="destroy_base",
            player_id=player_id,
            timestamp=time.time(),
            data={"target_player_id": target_player_id, "instance_id": instance_id, "card_name": base.name}
        )
        game.action_log.append(action)
        return game

    def skip_effect(self, game_id: str, player_id: str) -> 'GameState':
        """Skip an optional pending effect."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        if not game.pending_effect:
            raise ValueError("No pending effect to skip")

        if game.pending_effect.get('batch_scrap'):
            if not game.pending_effect.get('optional', False):
                raise ValueError("Cannot skip a mandatory effect")
            batch = game.play_batch
            if not batch or not batch.get('current_effect_key'):
                raise ValueError("No active batch scrap opportunity")
            batch['skipped'].append(batch.pop('current_effect_key'))
            game.pending_effect = None
            return self._advance_play_batch(game, player)

        if not game.pending_effect.get('optional', False):
            raise ValueError("Cannot skip a mandatory effect")

        game.pending_effect = None
        return game

    def resolve_choice(self, game_id: str, player_id: str, option_index: int) -> GameState:
        """Resolve a pending choice effect by picking option 0 or 1."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")

        if not game.pending_effect or game.pending_effect.get('type') != 'choice':
            raise ValueError("No pending choice effect")

        options = game.pending_effect.get('options', [])
        if option_index < 0 or option_index >= len(options):
            raise ValueError(f"Invalid option index: {option_index}")

        chosen_effects = options[option_index]
        game.pending_effect = None

        for effect in chosen_effects:
            self._execute_effect(player, effect, game)

        label = game.pending_effect  # already cleared, just for logging
        print(f"  → Player chose option {option_index}")
        return game

    def resolve_acquire_free_to_top(self, game_id: str, player_id: str, instance_id: str, from_explorers: bool = False) -> GameState:
        """Resolve acquire-free-to-top: take a card from trade row for free, put on top of deck."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")
        if not game.pending_effect or game.pending_effect.get('type') != 'acquire_free_to_top':
            raise ValueError("No pending acquire-free-to-top effect")

        pe = game.pending_effect
        max_cost = pe.get('max_cost', 999)
        card_type_filter = pe.get('card_type', 'ship')

        card = None
        if from_explorers:
            if game.explorer_pile:
                card = game.explorer_pile.pop(0)
        else:
            for c in game.trade_row:
                if c.instance_id == instance_id:
                    card = c
                    break
            if card:
                game.trade_row.remove(card)
                if game.trade_deck:
                    game.trade_row.append(game.trade_deck.pop(0))

        if not card:
            raise ValueError(f"Card {instance_id} not found in trade row")

        if card.cost > max_cost:
            raise ValueError(f"{card.name} costs {card.cost}, max allowed is {max_cost}")

        type_ok = (
            card_type_filter in ('any', 'ship_or_base', 'ship or base') or
            (card_type_filter == 'ship' and card.type != 'Base') or
            (card_type_filter == 'base' and card.type == 'Base')
        )
        if not type_ok:
            raise ValueError(f"{card.name} is not a valid {card_type_filter}")

        player.deck.insert(0, card)
        game.pending_effect = None

        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="acquire_free_to_top",
            player_id=player_id,
            timestamp=time.time(),
            data={"card_name": card.name, "instance_id": instance_id}
        )
        game.action_log.append(action)
        print(f"  → {card.name} acquired for free, placed on top of deck")
        return game

    def resolve_base_from_discard_to_top(self, game_id: str, player_id: str, instance_id: str) -> GameState:
        """Resolve base-from-discard-to-top: move a base from discard pile to top of deck."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        if game.current_player.player_id != player_id:
            raise ValueError("Not your turn")
        if not game.pending_effect or game.pending_effect.get('type') != 'base_from_discard_to_top':
            raise ValueError("No pending base-from-discard-to-top effect")

        card = None
        for c in player.discard_pile:
            if c.instance_id == instance_id:
                card = c
                break

        if not card:
            raise ValueError(f"Card {instance_id} not found in discard pile")
        if card.type != 'Base':
            raise ValueError(f"{card.name} is not a base")

        player.discard_pile.remove(card)
        player.deck.insert(0, card)
        game.pending_effect = None

        action = GameAction(
            action_id=str(uuid.uuid4()),
            action_type="base_to_top_of_deck",
            player_id=player_id,
            timestamp=time.time(),
            data={"card_name": card.name, "instance_id": instance_id}
        )
        game.action_log.append(action)
        print(f"  → {card.name} moved from discard to top of deck")
        return game

    def resolve_discard_any(self, game_id: str, player_id: str, instance_id: str) -> 'GameState':
        """Discard one card from hand as part of a discard_any_number effect."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        if not game.pending_effect or game.pending_effect.get('type') != 'discard_any_number':
            raise ValueError("No pending discard_any_number effect")

        card = next((c for c in player.hand if c.instance_id == instance_id), None)
        if not card:
            raise ValueError(f"Card {instance_id} not found in hand")

        player.hand.remove(card)
        player.discard_pile.append(card)

        for eff in game.pending_effect.get('per_discard_effects', []):
            self._execute_effect(player, eff, game)

        game.action_log.append(GameAction(
            action_id=str(uuid.uuid4()),
            action_type="discard_card",
            player_id=player_id,
            timestamp=time.time(),
            data={"card_name": card.name, "reason": "discard_any"}
        ))
        return game

    def finish_discard_any(self, game_id: str, player_id: str) -> 'GameState':
        """Finish the discard_any_number effect, applying on_complete_effects."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        if not game.pending_effect or game.pending_effect.get('type') != 'discard_any_number':
            raise ValueError("No pending discard_any_number effect")

        pe = game.pending_effect
        game.pending_effect = None

        for eff in pe.get('on_complete_effects', []):
            self._execute_effect(player, eff, game)

        return game

    def resolve_copy_ship(self, game_id: str, player_id: str, instance_id: str) -> 'GameState':
        """Copy the abilities of a ship played this turn."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")
        player = game.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        if not game.pending_effect or game.pending_effect.get('type') != 'copy_ship':
            raise ValueError("No pending copy_ship effect")

        if game.pending_effect.get('batch_copy'):
            if instance_id not in game.pending_effect.get('eligible_instance_ids', []):
                raise ValueError(f"Ship {instance_id} is not eligible to copy")
            batch = game.play_batch
            if not batch or not batch.get('current_copy_source'):
                raise ValueError("No active batch copy choice")
            batch['copies'][batch.pop('current_copy_source')] = instance_id
            game.pending_effect = None
            return self._advance_play_batch(game, player)

        card = next((c for c in player.in_play if c.instance_id == instance_id), None)
        if not card:
            raise ValueError(f"Card {instance_id} not found in in_play")

        game.pending_effect = None

        parsed = parse_card(card.text, card.faction)
        if parsed and parsed.primary_ability:
            for eff in parsed.primary_ability.effects:
                self._execute_effect(player, eff, game)

        ally_count = self._count_allies(player, card.faction)
        if parsed and ally_count >= 1 and parsed.ally_ability:
            for eff in parsed.ally_ability.effects:
                self._execute_effect(player, eff, game)

        game.action_log.append(GameAction(
            action_id=str(uuid.uuid4()),
            action_type="copy_ship",
            player_id=player_id,
            timestamp=time.time(),
            data={"copied_card": card.name}
        ))
        return game

    def execute_ai_turn(self, game_id: str) -> GameState:
        """Execute AIturn for current player if they are AI."""
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game {game_id} not found")

        current_player = game.players[game.current_player_index]

        if not current_player.is_ai:
            raise ValueError("Current player is not an AI")

        # Use AIservice to execute turn
        game = ai_service.execute_turn(game, self)

        # Update stored game state
        self.games[game_id] = game

        return game

    def get_game(self, game_id: str) -> Optional[GameState]:
        """Get game state."""
        return self.games.get(game_id)


# Global game service instance
game_service = GameService()
