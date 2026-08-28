import { Player, CardInstance } from '../types/game';
import { Card } from './Card';
import '../styles/CombatZone.css';

interface CombatZoneProps {
  currentPlayer: Player;
  opponents: Player[];
  isMyTurn: boolean;
  activePlayerIndex: number;
  players: Player[];
  onScrapCard: (card: CardInstance) => void;
  onAttackPlayer: (targetId: string) => void;
  onAttackBase: (targetId: string, base: CardInstance) => void;
  onEndTurn: () => void;
  onDistributeDamage: () => void;
  maxAuthority: number;
}

const OPPONENT_COLORS = ['#22d3ee', '#fb923c', '#a78bfa', '#f472b6', '#34d399'];

export function CombatZone({
  currentPlayer,
  opponents,
  isMyTurn,
  activePlayerIndex,
  players,
  onAttackPlayer,
  onAttackBase,
}: CombatZoneProps) {
  const canAttack = isMyTurn && currentPlayer.combat > 0;

  return (
    <div className="combat-opponents-section">
      <div className="combat-opponents" style={{ gridTemplateColumns: `repeat(${Math.min(opponents.length, 5)}, 1fr)` }}>
        {opponents.map((opp, idx) => {
          const isActive = players[activePlayerIndex]?.player_id === opp.player_id;
          const hasOutpost = opp.bases.some(b => b.is_outpost);
          const accent = OPPONENT_COLORS[idx % OPPONENT_COLORS.length];
          return (
            <div
              key={opp.player_id}
              className={`combat-opponent ${isActive ? 'combat-opponent--active' : ''}`}
              style={{ border: `2px solid ${accent}`, boxShadow: `0 0 10px ${accent}22` }}
              data-opponent={opp.player_id}
              data-inplay={opp.player_id}
            >
              <div className="combat-opponent-header">
                <span className="combat-opponent-name">
                  {isActive && '▶ '}{opp.name}{opp.is_ai&& ' 🤖'}
                </span>
                <div className="combat-opponent-actions">
                  {canAttack && !hasOutpost && (
                    <button className="btn-attack-player" onClick={() => onAttackPlayer(opp.player_id)}>
                      ⚔️ Attack ({currentPlayer.combat})
                    </button>
                  )}
                  {hasOutpost && <span className="outpost-warning">⚠️ Destroy outpost first</span>}
                </div>
              </div>

              {opp.bases.length > 0 && (
                <div className="combat-section">
                  <span className="combat-section-label">Bases</span>
                  <div className="combat-cards">
                    {opp.bases.map(base => (
                      <Card key={base.instance_id} card={base} small onClick={() => canAttack ? onAttackBase(opp.player_id, base) : undefined} clickable={canAttack} />
                    ))}
                  </div>
                </div>
              )}

              {opp.in_play.length > 0 && (
                <div className="combat-section">
                  <span className="combat-section-label">Ships in play</span>
                  <div className="combat-cards" data-fleet={opp.player_id}>
                    {opp.in_play.map(card => <Card key={card.instance_id} card={card} small />)}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
