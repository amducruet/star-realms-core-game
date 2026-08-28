import { useEffect, useRef, useState } from 'react';
import '../styles/LaserOverlay.css';

export interface AttackEvent {
  id: string;
  attackerId: string;
  targetId: string;
}

interface Beam {
  id: string;
  x1: number; y1: number;
  x2: number; y2: number;
  length: number;
  color: string;
  strokeWidth: number;
  impactDelay: number;
}

function getCenter(el: Element): { x: number; y: number } {
  const r = el.getBoundingClientRect();
  return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
}

interface LaserOverlayProps {
  attacks: AttackEvent[];
}

export function LaserOverlay({ attacks }: LaserOverlayProps) {
  const [beams, setBeams] = useState<Beam[]>([]);
  const processedIds = useRef(new Set<string>());

  useEffect(() => {
    const newBeams: Beam[] = [];

    for (const attack of attacks) {
      if (processedIds.current.has(attack.id)) continue;
      processedIds.current.add(attack.id);

      const sourceEl =
        document.querySelector<Element>(`[data-fleet="${attack.attackerId}"]`) ??
        document.querySelector<Element>(`[data-inplay="${attack.attackerId}"]`) ??
        document.querySelector<Element>('.combat-opponents-section');
      // Target is either an opponent panel or the human player's mine section
      const targetEl =
        document.querySelector<Element>(`[data-mine="${attack.targetId}"]`) ??
        document.querySelector<Element>(`[data-opponent="${attack.targetId}"]`) ??
        document.querySelector<Element>('.combat-mine-section');

      if (!sourceEl || !targetEl) continue;

      const src = getCenter(sourceEl);
      const tgt = getCenter(targetEl);
      const dx = tgt.x - src.x;
      const dy = tgt.y - src.y;
      const length = Math.sqrt(dx * dx + dy * dy);

      const configs = [
        { jitterSrc: -20, jitterTgt: -10, color: 'orange', width: 4,  delay: 0 },
        { jitterSrc: 0,   jitterTgt: 0,   color: 'red',    width: 8,  delay: 0.04 },
        { jitterSrc: 20,  jitterTgt: 10,  color: 'white',  width: 2,  delay: 0.08 },
      ];

      configs.forEach((cfg, i) => {
        newBeams.push({
          id: `${attack.id}-${i}`,
          x1: src.x + cfg.jitterSrc,
          y1: src.y,
          x2: tgt.x + cfg.jitterTgt,
          y2: tgt.y,
          length,
          color: cfg.color,
          strokeWidth: cfg.width,
          impactDelay: 0.36 + cfg.delay,
        });
      });
    }

    if (newBeams.length > 0) {
      setBeams(prev => [...prev, ...newBeams]);
      setTimeout(() => {
        setBeams(prev => {
          const ids = new Set(newBeams.map(b => b.id));
          return prev.filter(b => !ids.has(b.id));
        });
      }, 1800);
    }
  }, [attacks]);

  if (beams.length === 0) return null;

  return (
    <svg className="laser-overlay">
      <defs>
        <filter id="laser-glow" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="6" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {beams.map((beam) => (
        <g key={beam.id}>
          <line
            className={`laser-beam laser-beam--${beam.color}`}
            x1={beam.x1} y1={beam.y1}
            x2={beam.x2} y2={beam.y2}
            strokeWidth={beam.strokeWidth}
            strokeDasharray={beam.length}
            style={{ '--beam-length': String(beam.length) } as React.CSSProperties}
          />
          <circle
            className="laser-impact"
            cx={beam.x2}
            cy={beam.y2}
            r={0}
            fill={beam.color === 'red' ? 'rgba(255,68,68,0.45)' : 'rgba(255,160,60,0.3)'}
            style={{ animationDelay: `${beam.impactDelay}s` }}
          />
        </g>
      ))}
    </svg>
  );
}
