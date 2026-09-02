/**
 * Action log component showing recent game actions.
 */
import { GameAction, GameState } from '../types/game';
import '../styles/ActionLog.css';

interface ActionLogProps {
  gameState: GameState;
}

function formatAction(action: GameAction, gameState: GameState): string {
  const player = gameState.players.find((p) => p.player_id === action.player_id);
  const playerName = player?.name || 'Unknown';

  switch (action.action_type) {
    case 'play_card':
      return `${playerName} played ${action.data.card_name}`;

    case 'card_played':
      return `${playerName} played ${action.data.card_name}`;

    case 'acquire_card':
    case 'card_acquired':
      const source = action.data.from_explorers ? 'Explorer pile' : 'Trade Row';
      return `${playerName} bought ${action.data.card_name} from ${source}`;

    case 'deal_damage':
    case 'player_attacked':
      const target = gameState.players.find((p) => p.player_id === action.data.target_player_id);
      return `${playerName} dealt ${action.data.damage} damage to ${target?.name || 'opponent'}`;

    case 'destroy_base':
    case 'base_attacked':
      return `${playerName} destroyed ${action.data.card_name || 'a base'}`;

    case 'discard_card': {
      const target = gameState.players.find(
        (p) => p.player_id === action.data.target_player_id,
      );
      const targetName = target?.name || playerName;
      return `${targetName} discarded ${action.data.card_name || 'a card'}`;
    }

    default:
      return `${playerName}: ${action.action_type}`;
  }
}

export function ActionLog({ gameState }: ActionLogProps) {
  const actions = [...gameState.action_log].reverse();

  return (
    <div className="action-log">
      <div className="action-log-header">Game Log</div>
      <div className="action-list">
        {actions.length === 0 ? (
          <div className="action-empty">No actions yet</div>
        ) : (
          actions.map((action) => (
            <div key={action.action_id} className="action-item">
              {formatAction(action, gameState)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
