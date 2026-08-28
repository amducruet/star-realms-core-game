import { CardInstance } from '../types/game';
import { formatCardText, hasScrapAbility } from '../utils/formatCardText';
import { CombatIcon, TradeIcon, AuthorityIcon, ShieldIcon, ScrapIcon } from './Icons';
import '../styles/Card.css';
import '../styles/animations.css';

interface CardProps {
  card: CardInstance;
  onClick?: () => void;
  clickable?: boolean;
  count?: number;
  showScrapButton?: boolean;
  onScrap?: () => void;
  compact?: boolean;
  small?: boolean;
  enterIndex?: number;
  played?: boolean;
}

const FACTION_COLORS: Record<string, string> = {
  Blob: 'green',
  'Trade Federation': 'blue',
  'Machine Cult': 'red',
  'Star Empire': 'yellow',
  Unaligned: 'gray',
};

function cardImagePath(name: string): string {
  const file = name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  return `/cards/${file}.png`;
}

interface ParsedStats {
  combat: number;
  trade: number;
  authority: number;
  remainder: string;
}

function parseStats(text: string): ParsedStats {
  let s = text;
  let combat = 0, trade = 0, authority = 0;

  const combatM = s.match(/\+\s*(\d+)\s*Combat/i);
  if (combatM) { combat = parseInt(combatM[1]); s = s.replace(combatM[0], ''); }

  const tradeM = s.match(/\+\s*(\d+)\s*Trade/i);
  if (tradeM) { trade = parseInt(tradeM[1]); s = s.replace(tradeM[0], ''); }

  const authM = s.match(/\+\s*(\d+)\s*Authority/i);
  if (authM) { authority = parseInt(authM[1]); s = s.replace(authM[0], ''); }

  const trimmed = s.replace(/^[\s.,;]+/, '').trim();

  // If remainder starts with "or", the stat was a choice — keep whole text as-is
  if (/^or\b/i.test(trimmed)) {
    return { combat: 0, trade: 0, authority: 0, remainder: text };
  }

  const remainder = trimmed.replace(/[\s.,;]+$/, '').trim();
  return { combat, trade, authority, remainder };
}

export function Card({ card, onClick, clickable = false, count, showScrapButton = false, onScrap, compact = false, small = false, enterIndex, played = false }: CardProps) {
  const factionColor = FACTION_COLORS[card.faction] || 'gray';
  const abilities = formatCardText(card.text);
  const canScrap = hasScrapAbility(card.text);
  const imgSrc = cardImagePath(card.name);

  const primaryAbilities = abilities.filter(a => a.type === 'primary');
  const conditionalAbilities = abilities.filter(a => a.type !== 'primary');

  // Aggregate stats across all primary sections
  const stats = primaryAbilities.reduce(
    (acc, a) => {
      const p = parseStats(a.text);
      return {
        combat: acc.combat + p.combat,
        trade: acc.trade + p.trade,
        authority: acc.authority + p.authority,
        remainders: [...acc.remainders, ...(p.remainder ? [p.remainder] : [])],
      };
    },
    { combat: 0, trade: 0, authority: 0, remainders: [] as string[] }
  );

  const hasStats = stats.combat > 0 || stats.trade > 0 || stats.authority > 0;
  const isBase = card.type === 'Base' || card.type === 'Outpost';
  const statsOnly = hasStats && stats.remainders.length === 0 && conditionalAbilities.length === 0;

  const enterClass = enterIndex !== undefined
    ? `card-enter-${Math.min(enterIndex + 1, 6)}`
    : 'card-enter';
  const playedClass = played ? 'card-played' : '';

  return (
    <div
      className={`card card-${factionColor} ${clickable ? 'card-clickable' : ''} ${compact ? 'card-compact' : ''} ${small ? 'card-small' : ''} ${enterClass} ${playedClass}`}
      onClick={clickable ? onClick : undefined}
    >
      {/* Art + name/cost overlay */}
      <div className={`card-art card-art--${factionColor}`}>
        <img
          src={imgSrc}
          alt={card.name}
          className="card-art-img"
          onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
        />
        <div className="card-name-overlay">
          <span className="card-name">{card.name}</span>
          {card.cost > 0 && (
            <span className="card-cost-badge">
              <TradeIcon size={compact ? 9 : 11} />{card.cost}
            </span>
          )}
        </div>
        {card.is_outpost && <span className="card-outpost-badge">OUTPOST</span>}
      </div>

      {/* Info panel: stats | divider | abilities */}
      <div className={`card-info${statsOnly ? ' card-info--stats-only' : ''}${!hasStats && !isBase ? ' card-info--no-stats' : ''}`}>

        {/* Left: stacked stats */}
        <div className="card-stats-col">
          {stats.combat > 0 && (
            <div className="card-stat card-stat--combat">
              <CombatIcon size={compact ? 11 : 13} />
              <span>{stats.combat}</span>
            </div>
          )}
          {stats.trade > 0 && (
            <div className="card-stat card-stat--trade">
              <TradeIcon size={compact ? 11 : 13} />
              <span>{stats.trade}</span>
            </div>
          )}
          {stats.authority > 0 && (
            <div className="card-stat card-stat--authority">
              <AuthorityIcon size={compact ? 11 : 13} />
              <span>{stats.authority}</span>
            </div>
          )}
          {isBase && card.defense != null && (
            <div className="card-stat card-stat--defense">
              <ShieldIcon size={compact ? 11 : 13} />
              <span>{card.current_defense ?? card.defense}</span>
            </div>
          )}
          {!hasStats && !isBase && (
            <div className="card-stat-empty" />
          )}
        </div>

        <div className="card-info-divider" />

        {/* Right: residual text + conditional abilities */}
        <div className="card-abilities">
          {stats.remainders.map((r, i) => (
            <div key={i} className="card-ability card-ability--primary">{r}</div>
          ))}
          {conditionalAbilities.map((a, i) => (
            <div key={i} className={`card-ability card-ability--${a.type}`}>
              {a.label && <span className="card-ability-label">{a.label}</span>}
              <span className="card-ability-text">{a.text}</span>
            </div>
          ))}
        </div>

      </div>

      {count !== undefined && count > 1 && (
        <div className="card-count">×{count}</div>
      )}

      {showScrapButton && canScrap && onScrap && (
        <button
          className="btn-scrap"
          onClick={(e) => { e.stopPropagation(); onScrap(); }}
        >
          <ScrapIcon size={12} /> Scrap
        </button>
      )}
    </div>
  );
}
