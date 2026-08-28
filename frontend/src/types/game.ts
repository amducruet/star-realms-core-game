/**
 * TypeScript type definitions matching backend models.
 */

export interface CardInstance {
  instance_id: string;
  card_id: string;
  name: string;
  type: string;
  faction: string;
  cost: number;
  defense: number | null;
  is_outpost: boolean;
  text: string;
  current_defense: number | null;
}

export interface Player {
  player_id: string;
  name: string;
  authority: number;
  deck: CardInstance[];
  hand: CardInstance[];
  discard_pile: CardInstance[];
  in_play: CardInstance[];
  bases: CardInstance[];
  combat: number;
  trade: number;
  is_ai: boolean;
}

export type GamePhase = 'lobby' | 'playing' | 'ended';
export type TurnPhase = 'main' | 'discard';

export interface GameConfig {
  max_players: number;
  starting_authority: number;
  starting_hand_size: number;
  starting_scouts: number;
  starting_vipers: number;
  trade_row_size: number;
}

export interface GameAction {
  action_id: string;
  action_type: string;
  player_id: string;
  timestamp: number;
  data: Record<string, any>;
}

export interface GameState {
  game_id: string;
  phase: GamePhase;
  turn_phase: TurnPhase;
  config: GameConfig;
  players: Player[];
  current_player_index: number;
  trade_row: CardInstance[];
  trade_deck: CardInstance[];
  explorer_pile: CardInstance[];
  scrap_heap: CardInstance[];
  action_log: GameAction[];
  winner_id: string | null;
  pending_effect: {
    type: 'scrap_card' | 'discard_card' | 'choice' | 'acquire_free_to_top' | 'base_from_discard_to_top' | 'discard_any_number' | 'copy_ship';
    location?: 'hand' | 'discard' | 'hand_or_discard' | 'trade_row';
    target?: 'opponent' | 'self';
    optional: boolean;
    triggered_by?: string;
    options?: any[][];
    labels?: string[];
    card_type?: string;
    max_cost?: number;
    per_discard_effects?: any[];
    on_complete_effects?: any[];
  } | null;
}

export interface WSMessage {
  type: string;
  game?: GameState;
  data?: any;
}
