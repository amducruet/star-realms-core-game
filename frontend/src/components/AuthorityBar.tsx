import { useEffect, useRef, useState } from 'react';
import { Player } from '../types/game';
import { AuthorityIcon, CombatIcon, TradeIcon } from './Icons';
import '../styles/AuthorityBar.css';
import '../styles/animations.css';

interface AuthorityBarProps {
  player: Player;
  maxAuthority: number;
}

export function AuthorityBar({ player, maxAuthority }: AuthorityBarProps) {
  const pct = Math.max(0, Math.min(100, (player.authority / maxAuthority) * 100));
  const barColor = pct > 50 ? '#ef4444' : pct > 25 ? '#f59e0b' : '#dc2626';

  const prevAuthority = useRef(player.authority);
  const prevCombat = useRef(player.combat);
  const prevTrade = useRef(player.trade);

  const [damagedKey, setDamagedKey] = useState(0);
  const [combatKey, setCombatKey] = useState(0);
  const [tradeKey, setTradeKey] = useState(0);

  useEffect(() => {
    if (player.authority < prevAuthority.current) {
      setDamagedKey(k => k + 1);
    }
    prevAuthority.current = player.authority;
  }, [player.authority]);

  useEffect(() => {
    if (player.combat > prevCombat.current) {
      setCombatKey(k => k + 1);
    }
    prevCombat.current = player.combat;
  }, [player.combat]);

  useEffect(() => {
    if (player.trade > prevTrade.current) {
      setTradeKey(k => k + 1);
    }
    prevTrade.current = player.trade;
  }, [player.trade]);

  return (
    <div className={`authority-bar${damagedKey > 0 ? ' authority-bar--damaged' : ''}`} key={`bar-${damagedKey}`}>
      <div className="authority-bar-left">
        <span className="authority-bar-name">{player.name}</span>
        <span className={`authority-bar-value${damagedKey > 0 ? ' authority-damaged' : ''}`} key={`auth-${damagedKey}`}>
          <AuthorityIcon size={18} /> {player.authority} / {maxAuthority}
        </span>
      </div>
      <div className="authority-bar-track">
        <div
          className="authority-bar-fill"
          style={{ width: `${pct}%`, background: barColor }}
        />
      </div>
      <div className="authority-bar-resources">
        <span className="authority-resource authority-resource--combat" key={`combat-${combatKey}`}>
          <CombatIcon size={16} />
          <span className={combatKey > 0 ? 'num-pop-combat' : ''}>{player.combat}</span>
        </span>
        <span className="authority-resource authority-resource--trade" key={`trade-${tradeKey}`}>
          <TradeIcon size={16} />
          <span className={tradeKey > 0 ? 'num-pop-trade' : ''}>{player.trade}</span>
        </span>
      </div>
    </div>
  );
}
