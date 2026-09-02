/**
 * Player area component showing player state and cards.
 */
import { Player, CardInstance } from '../types/game';
import { Card } from './Card';
import '../styles/PlayerArea.css';

interface PlayerAreaProps {
  player: Player;
  isCurrentPlayer: boolean;
  isOpponent: boolean;
  showHand?: boolean;
  canAttack?: boolean;
  onAttack?: () => void;
  onAttackBase?: (base: CardInstance) => void;
  onPlayCard?: (card: CardInstance) => void;
  onScrapCard?: (card: CardInstance) => void;
}

export function PlayerArea({
  player,
  isCurrentPlayer,
  isOpponent,
  showHand = false,
  canAttack = false,
  onAttack,
  onAttackBase,
  onPlayCard,
  onScrapCard,
}: PlayerAreaProps) {
  return (
    <div className={`player-area ${isCurrentPlayer ? 'active-player' : ''} ${isOpponent ? 'opponent' : 'current'}`}>
      <div className="player-info">
        <div className="player-name">
          {player.name} {player.is_ai&& '🤖'}
          {isCurrentPlayer && <span className="turn-indicator">▶</span>}
        </div>

        <div className="player-stats">
          <span className="authority" title="Authority">
            ❤️ {player.authority}
          </span>
          <span className="combat" title="Combat">
            ⚔️ {player.combat}
          </span>
          <span className="trade" title="Trade">
            💰 {player.trade}
          </span>
          <span className="deck-count" title="Deck">
            🃏 {player.deck.length}
          </span>
          <span className="discard-count" title="Discard">
            🗑️ {player.discard_pile.length}
          </span>
        </div>

        {canAttack && onAttack && (
          <button className="btn-attack" onClick={onAttack}>
            Attack ({player.combat} damage)
          </button>
        )}
      </div>

      {/* Bases */}
      {player.bases.length > 0 && (
        <div className="player-bases">
          <h4>Bases: {isOpponent && player.bases.some(b => !b.is_outpost) && <span className="outpost-warning">⚠️ Destroy bases first!</span>}</h4>
          <div className="card-list-small">
            {player.bases.map((base) => (
              <Card
                key={base.instance_id}
                card={base}
                onClick={isOpponent && canAttack && onAttackBase ? () => onAttackBase(base) : undefined}
                clickable={isOpponent && canAttack && !!onAttackBase}
                showScrapButton={!isOpponent && isCurrentPlayer}
                onScrap={onScrapCard ? () => onScrapCard(base) : undefined}
              />
            ))}
          </div>
        </div>
      )}

      {/* In Play (Ships played this turn) */}
      {player.in_play.length > 0 && !isOpponent && (
        <div className="player-in-play">
          <h4>In Play:</h4>
          <div className="card-list-small">
            {player.in_play.map((card) => (
              <Card
                key={card.instance_id}
                card={card}
                showScrapButton={isCurrentPlayer}
                onScrap={onScrapCard ? () => onScrapCard(card) : undefined}
              />
            ))}
          </div>
        </div>
      )}

      {/* Hand (only show for current player) */}
      {showHand && player.hand.length > 0 && (
        <div className="player-hand">
          <h4>Your Hand:</h4>
          <div className="card-list">
            {player.hand.map((card) => (
              <Card
                key={card.instance_id}
                card={card}
                onClick={() => onPlayCard?.(card)}
                clickable={isCurrentPlayer && !!onPlayCard}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
