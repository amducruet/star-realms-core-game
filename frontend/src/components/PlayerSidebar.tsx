import { Player } from '../types/game';
import { AuthorityIcon, CombatIcon, TradeIcon, DeckIcon, ScrapIcon } from './Icons';
import '../styles/PlayerSidebar.css';

interface PlayerSidebarProps {
  players: Player[];
  currentPlayerId: string | null;
  activePlayerIndex: number;
  startingAuthority: number;
}

export function PlayerSidebar({ players, currentPlayerId, activePlayerIndex, startingAuthority }: PlayerSidebarProps) {
  return (
    <div className="player-sidebar">
      <span className="sidebar-label">Players ({players.length})</span>
      {players.map((p, i) => {
        const isActive = i === activePlayerIndex;
        const isMe = p.player_id === currentPlayerId;
        const pct = Math.max(0, Math.min(100, (p.authority / startingAuthority) * 100));
        const barColor = pct > 50 ? '#22c55e' : pct > 25 ? '#f59e0b' : '#ef4444';

        return (
          <div key={p.player_id} className={`sidebar-player ${isActive ? 'sidebar-player--active' : ''} ${isMe ? 'sidebar-player--me' : ''}`}>
            <div className="sidebar-player-header">
              <span className="sidebar-player-name">
                {isActive && <span className="sidebar-turn-arrow">▶</span>}
                {p.name}
                {p.is_ai&& <span className="sidebar-ai-badge">AI</span>}
                {isMe && <span className="sidebar-you-badge">YOU</span>}
              </span>
              <span className="sidebar-authority"><AuthorityIcon size={13} /> {p.authority}</span>
            </div>
            <div className="sidebar-authority-bar">
              <div className="sidebar-authority-fill" style={{ width: `${pct}%`, background: barColor }} />
            </div>
            <div className="sidebar-player-stats">
              <span title="Combat"><CombatIcon size={13} /> {p.combat}</span>
              <span title="Trade"><TradeIcon size={13} /> {p.trade}</span>
              <span title="Deck"><DeckIcon size={13} /> {p.deck.length}</span>
              <span title="Discard"><ScrapIcon size={13} /> {p.discard_pile.length}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
