import { Player, CardInstance } from '../types/game';
import { Card } from './Card';
import { AuthorityBar } from './AuthorityBar';
import '../styles/CombatZone.css';
import '../styles/LaserOverlay.css';

interface PlayerMineProps {
  currentPlayer: Player;
  isMyTurn: boolean;
  opponents: Player[];
  maxAuthority: number;
  onScrapCard: (card: CardInstance) => void;
  onPlayHand: () => void;
  canPlayHand: boolean;
  onEndTurn: () => void;
  onDistributeDamage: () => void;
  launching?: boolean;
}

export function PlayerMine({ currentPlayer, isMyTurn, opponents, maxAuthority, onScrapCard, onPlayHand, canPlayHand, onEndTurn, onDistributeDamage, launching = false }: PlayerMineProps) {
  return (
    <div className="combat-mine-section" data-mine={currentPlayer.player_id}>
      <AuthorityBar player={currentPlayer} maxAuthority={maxAuthority} />

      <div className="combat-mine">

        {/* Deck pile */}
        <div className="player-pile">
          <span className="combat-section-label">Deck</span>
          <div className="pile-stack">
            {currentPlayer.deck.length > 2 && <div className="pile-card pile-card--back2" />}
            {currentPlayer.deck.length > 1 && <div className="pile-card pile-card--back1" />}
            {currentPlayer.deck.length > 0
              ? <div className="pile-card pile-card--top">🚀</div>
              : <div className="pile-card pile-card--empty">empty</div>
            }
          </div>
          <span className="pile-count-label">{currentPlayer.deck.length} cards</span>
        </div>

        {/* Center: bases + in-play + hand */}
        <div className="combat-cards-center" data-inplay={currentPlayer.player_id}>
          {currentPlayer.bases.length > 0 && (
            <div className="combat-section">
              <span className="combat-section-label">
                Bases — {currentPlayer.bases_settled_this_turn ? 'Cashed in' : 'Ready'}
              </span>
              <div className="combat-cards">
                {currentPlayer.bases.map(base => (
                  <Card key={base.instance_id} card={base} small played={!!currentPlayer.bases_settled_this_turn} showScrapButton={isMyTurn && !currentPlayer.bases_settled_this_turn} onScrap={() => onScrapCard(base)} />
                ))}
              </div>
            </div>
          )}
          {currentPlayer.in_play.length > 0 && (
            <div className="combat-section combat-section--in-play">
              <span className="combat-section-label">In Play — Cashed in</span>
              <div className={`combat-cards${launching ? ' fleet-launching' : ''}`}>
                {currentPlayer.in_play.map((card, i) => (
                  <Card key={card.instance_id} card={card} small played enterIndex={i} />
                ))}
              </div>
            </div>
          )}
          {currentPlayer.hand.length > 0 && (
            <div className="combat-section combat-section--hand">
              <span className="combat-section-label">Hand — Not played</span>
              <div className="combat-cards">
                {currentPlayer.hand.map((card, i) => (
                  <Card key={card.instance_id} card={card} small showScrapButton={isMyTurn && canPlayHand} onScrap={() => onScrapCard(card)} enterIndex={i} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Discard pile + actions */}
        <div className="player-pile">
          {isMyTurn && (
            <div className="pile-actions">
              {(currentPlayer.hand.length > 0 || (currentPlayer.bases.length > 0 && !currentPlayer.bases_settled_this_turn)) && (
                <button className="btn-play-hand" onClick={onPlayHand} disabled={!canPlayHand}>Play Hand</button>
              )}
              <button className="btn-end-turn" onClick={onEndTurn}>End Turn</button>
              {opponents.length > 1 && currentPlayer.combat > 0 && (
                <button className="btn-distribute-damage" onClick={onDistributeDamage}>
                  ⚔️ Distribute ({currentPlayer.combat})
                </button>
              )}
            </div>
          )}
          <span className="combat-section-label">Discard</span>
          <div className="pile-stack">
            {currentPlayer.discard_pile.length > 1 && <div className="pile-card pile-card--back1" />}
            {currentPlayer.discard_pile.length > 0
              ? <div className="pile-card pile-card--discard"><span>{currentPlayer.discard_pile[currentPlayer.discard_pile.length - 1].name}</span></div>
              : <div className="pile-card pile-card--empty">empty</div>
            }
          </div>
          <span className="pile-count-label">{currentPlayer.discard_pile.length} cards</span>
        </div>

      </div>
    </div>
  );
}
