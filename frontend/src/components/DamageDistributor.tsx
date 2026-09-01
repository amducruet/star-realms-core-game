/**
 * Damage distribution modal for multiplayer combat.
 */
import { useState, useEffect } from 'react';
import { Player } from '../types/game';
import '../styles/DamageDistributor.css';

interface DamageDistributorProps {
  opponents: Player[];
  availableCombat: number;
  onDistribute: (targets: Array<{ player_id: string; damage: number }>) => void;
  onCancel: () => void;
}

export function DamageDistributor({
  opponents,
  availableCombat,
  onDistribute,
  onCancel,
}: DamageDistributorProps) {
  const [damageAllocation, setDamageAllocation] = useState<Record<string, number>>({});

  // Initialize with 0 damage for each opponent
  useEffect(() => {
    const initial: Record<string, number> = {};
    opponents.forEach((opp) => {
      initial[opp.player_id] = 0;
    });
    setDamageAllocation(initial);
  }, [opponents]);

  const totalAllocated = Object.values(damageAllocation).reduce((sum, val) => sum + val, 0);
  const remaining = availableCombat - totalAllocated;

  const handleDamageChange = (playerId: string, value: string) => {
    const damage = parseInt(value) || 0;
    const clamped = Math.max(0, Math.min(damage, availableCombat));
    setDamageAllocation((prev) => ({
      ...prev,
      [playerId]: clamped,
    }));
  };

  const handleIncrement = (playerId: string) => {
    if (remaining > 0) {
      setDamageAllocation((prev) => ({
        ...prev,
        [playerId]: (prev[playerId] || 0) + 1,
      }));
    }
  };

  const handleDecrement = (playerId: string) => {
    setDamageAllocation((prev) => ({
      ...prev,
      [playerId]: Math.max(0, (prev[playerId] || 0) - 1),
    }));
  };

  const handleMaxOut = (playerId: string) => {
    const currentDamage = damageAllocation[playerId] || 0;
    const canAdd = remaining;
    setDamageAllocation((prev) => ({
      ...prev,
      [playerId]: currentDamage + canAdd,
    }));
  };

  const handleConfirm = () => {
    const targets = opponents
      .map((opp) => ({
        player_id: opp.player_id,
        damage: damageAllocation[opp.player_id] || 0,
      }))
      .filter((t) => t.damage > 0);

    if (targets.length === 0) {
      return;
    }

    onDistribute(targets);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="damage-distributor" onClick={(e) => e.stopPropagation()}>
        <h2>Distribute Damage</h2>
        <div className="combat-info">
          <span className="available">⚔️ Available: {availableCombat}</span>
          <span className="allocated">Allocated: {totalAllocated}</span>
          <span className={`remaining ${remaining === 0 ? 'zero' : ''}`}>
            Remaining: {remaining}
          </span>
        </div>

        <div className="damage-targets">
          {opponents.map((opponent) => {
            const damage = damageAllocation[opponent.player_id] || 0;
            const hasNonOutpostBase = opponent.bases?.some((b) => !b.is_outpost) || false;

            return (
              <div
                key={opponent.player_id}
                className={`target-row ${hasNonOutpostBase ? 'disabled' : ''}`}
              >
                <div className="target-info">
                  <span className="target-name">
                    {opponent.name}
                    {opponent.is_ai&& ' 🤖'}
                  </span>
                  <span className="target-health">❤️ {opponent.authority}</span>
                  {hasNonOutpostBase && <span className="outpost-warning">🛡️ Destroy bases first</span>}
                </div>

                <div className="damage-controls">
                  <button
                    className="btn-control"
                    onClick={() => handleDecrement(opponent.player_id)}
                    disabled={damage === 0 || hasNonOutpostBase}
                  >
                    -
                  </button>
                  <input
                    type="number"
                    min="0"
                    max={availableCombat}
                    value={damage}
                    onChange={(e) => handleDamageChange(opponent.player_id, e.target.value)}
                    disabled={hasNonOutpostBase}
                  />
                  <button
                    className="btn-control"
                    onClick={() => handleIncrement(opponent.player_id)}
                    disabled={remaining === 0 || hasNonOutpostBase}
                  >
                    +
                  </button>
                  <button
                    className="btn-max"
                    onClick={() => handleMaxOut(opponent.player_id)}
                    disabled={remaining === 0 || hasNonOutpostBase}
                  >
                    Max
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="modal-actions">
          <button className="btn-cancel" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="btn-confirm"
            onClick={handleConfirm}
            disabled={totalAllocated === 0}
          >
            Attack ({totalAllocated} damage)
          </button>
        </div>
      </div>
    </div>
  );
}
