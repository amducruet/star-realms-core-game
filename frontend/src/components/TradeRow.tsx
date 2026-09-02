import { CardInstance, Player } from '../types/game';
import { Card } from './Card';
import '../styles/TradeRow.css';

interface TradeRowProps {
  tradeRow: CardInstance[];
  explorerPile: CardInstance[];
  scrapHeap: CardInstance[];
  currentPlayer: Player | undefined;
  isMyTurn: boolean;
  onAcquire: (card: CardInstance, fromExplorers?: boolean) => void;
  onScrapSelect?: (card: CardInstance) => void;
  eligibleScrapIds?: string[];
}

export function TradeRow({ tradeRow, explorerPile, scrapHeap, currentPlayer, isMyTurn, onAcquire, onScrapSelect, eligibleScrapIds }: TradeRowProps) {
  const canAfford = (cost: number) => isMyTurn && !!currentPlayer && currentPlayer.trade >= cost;
  const eligibleScrapSet = eligibleScrapIds ? new Set(eligibleScrapIds) : null;

  return (
    <div className="trade-row-zone">
      <div className="trade-row-section">
        <span className="trade-zone-label">
          Trade Row
        </span>
        <div className="trade-row-cards">
          {tradeRow.map((card, i) => {
            const scrapEligible = !!onScrapSelect && (!eligibleScrapSet || eligibleScrapSet.has(card.instance_id));
            return (
              <Card
                key={card.instance_id}
                card={card}
                onClick={scrapEligible ? () => onScrapSelect(card) : onScrapSelect ? undefined : () => onAcquire(card)}
                clickable={onScrapSelect ? scrapEligible : canAfford(card.cost)}
                enterIndex={i}
              />
            );
          })}
        </div>
      </div>

      <div className="trade-row-aside">
        <div className="trade-pile">
          <span className="trade-zone-label">Explorer Pile</span>
          {explorerPile.length > 0 ? (
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <Card
                card={explorerPile[0]}
                onClick={() => onAcquire(explorerPile[0], true)}
                clickable={!onScrapSelect && canAfford(2)}
              />
              {explorerPile.length > 1 && <div className="card-count">×{explorerPile.length}</div>}
            </div>
          ) : (
            <div className="pile-empty">Empty</div>
          )}
        </div>

        <div className="trade-pile">
          <span className="trade-zone-label">Scrap Heap</span>
          {scrapHeap.length > 0 ? (
            <div className="scrap-pile-wrap">
              <Card card={scrapHeap[scrapHeap.length - 1]} />
              {scrapHeap.length > 1 && (
                <span className="pile-count">×{scrapHeap.length}</span>
              )}
            </div>
          ) : (
            <div className="pile-empty">Empty</div>
          )}
        </div>
      </div>
    </div>
  );
}
