import { CardInstance } from '../types/game';
import '../styles/CardPicker.css';

interface CardPickerProps {
  title: string;
  subtitle?: string;
  cards: CardInstance[];
  cardOwners?: Record<string, string>; // instance_id -> player name
  onSelect: (card: CardInstance) => void;
  onSkip?: () => void;
  isOptional: boolean;
}

export function CardPicker({ title, subtitle, cards, cardOwners, onSelect, onSkip, isOptional }: CardPickerProps) {
  return (
    <div className="modal-overlay" onClick={isOptional && onSkip ? onSkip : undefined}>
      <div className="card-picker" onClick={(e) => e.stopPropagation()}>
        <h2>{title}</h2>
        {subtitle && <p className="card-picker-subtitle">{subtitle}</p>}

        <div className="card-picker-list">
          {cards.length === 0 ? (
            <div className="card-picker-empty">No cards available</div>
          ) : (
            cards.map((card) => (
              <div
                key={card.instance_id}
                className="card-picker-item"
                onClick={() => onSelect(card)}
              >
                <span className="card-picker-item-name">{card.name}</span>
                <span className="card-picker-item-meta">
                  {cardOwners?.[card.instance_id] && (
                    <span className="card-picker-item-owner">{cardOwners[card.instance_id]} · </span>
                  )}
                  {card.faction} · {card.type} · Cost: {card.cost}
                </span>
                {card.text && (
                  <span className="card-picker-item-text">{card.text.replace(/<[^>]+>/g, ' ').trim()}</span>
                )}
              </div>
            ))
          )}
        </div>

        <div className="card-picker-actions">
          {isOptional && onSkip && (
            <button className="btn-skip" onClick={onSkip}>
              Skip
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
