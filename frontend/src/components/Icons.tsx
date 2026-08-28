/** SVG icon components replacing emojis throughout the game UI. */

interface IconProps {
  size?: number;
  className?: string;
}

// ── Resource icons ────────────────────────────────────────────────────────────

export function CombatIcon({ size = 16, className }: IconProps) {
  return (
    <img src="/Icons/combat_icon.png" width={size} height={size} className={className} alt="combat" style={{ display: 'inline-block', verticalAlign: 'middle' }} />
  );
}

export function TradeIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="9" fill="#d97706" stroke="#fbbf24" strokeWidth="1.2"/>
      <circle cx="12" cy="12" r="6" fill="#92400e" stroke="#f59e0b" strokeWidth="0.8"/>
      <path d="M12 7v2M12 15v2M9 9.5h3.5a1.5 1.5 0 010 3H9" stroke="#fbbf24" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  );
}

export function AuthorityIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 3L14.5 8.5H21L16 12.5L18 18.5L12 15L6 18.5L8 12.5L3 8.5H9.5L12 3Z"
        fill="#e11d48" stroke="#fda4af" strokeWidth="1.1" strokeLinejoin="round"/>
    </svg>
  );
}

export function ShieldIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 3L20 7V13C20 17.4 16.5 21 12 22C7.5 21 4 17.4 4 13V7L12 3Z"
        fill="#1d4ed8" stroke="#60a5fa" strokeWidth="1.2" strokeLinejoin="round"/>
      <path d="M9 12l2 2 4-4" stroke="#bfdbfe" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function ScrapIcon({ size = 14, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M10 11v6M14 11v6" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
}

export function DeckIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="4" y="8" width="14" height="12" rx="2" fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.2"/>
      <rect x="6" y="5" width="14" height="12" rx="2" fill="#162840" stroke="#2563eb" strokeWidth="1"/>
      <rect x="8" y="3" width="14" height="12" rx="2" fill="#0f2236" stroke="#1d4ed8" strokeWidth="1"/>
    </svg>
  );
}

// ── Faction art (used in card header) ─────────────────────────────────────────

export function BlobArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="12" fill="#14532d" stroke="#4ade80" strokeWidth="1.5"/>
      <circle cx="15" cy="16" r="3" fill="#4ade80" opacity="0.8"/>
      <circle cx="26" cy="16" r="3" fill="#4ade80" opacity="0.8"/>
      <path d="M14 25 Q20 29 26 25" stroke="#4ade80" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
      <circle cx="15" cy="16" r="1.2" fill="#052e16"/>
      <circle cx="26" cy="16" r="1.2" fill="#052e16"/>
      <ellipse cx="20" cy="11" rx="6" ry="4" fill="#166534" stroke="#4ade80" strokeWidth="1"/>
    </svg>
  );
}

export function StarEmpireArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <path d="M20 4L23 14H34L25.5 20L28.5 30L20 24L11.5 30L14.5 20L6 14H17L20 4Z"
        fill="#713f12" stroke="#fbbf24" strokeWidth="1.3" strokeLinejoin="round"/>
      <path d="M20 10L22 16H28L23.5 19.5L25.5 26L20 22L14.5 26L16.5 19.5L12 16H18L20 10Z"
        fill="#fbbf24" opacity="0.6"/>
    </svg>
  );
}

export function TradeFederationArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="13" fill="#0c1445" stroke="#3b82f6" strokeWidth="1.5"/>
      <circle cx="20" cy="20" r="8" fill="#1e3a8a" stroke="#60a5fa" strokeWidth="1"/>
      <path d="M20 13v3M20 24v3M13 20h3M24 20h3" stroke="#93c5fd" strokeWidth="1.5" strokeLinecap="round"/>
      <circle cx="20" cy="20" r="3" fill="#3b82f6" stroke="#bfdbfe" strokeWidth="1"/>
    </svg>
  );
}

export function MachineCultArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="13" fill="#2d0a0a" stroke="#ef4444" strokeWidth="1.5"/>
      <path d="M14 15h12v10H14z" fill="#7f1d1d" stroke="#f87171" strokeWidth="1"/>
      <circle cx="16.5" cy="18" r="2" fill="#ef4444"/>
      <circle cx="23.5" cy="18" r="2" fill="#ef4444"/>
      <path d="M16 23h8" stroke="#f87171" strokeWidth="1.2" strokeLinecap="round"/>
      <path d="M20 15v-3M17 14l-1-2M23 14l1-2" stroke="#ef4444" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

export function UnalignedArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <path d="M20 6L32 20L20 34L8 20L20 6Z" fill="#1f2937" stroke="#6b7280" strokeWidth="1.5" strokeLinejoin="round"/>
      <path d="M20 12L28 20L20 28L12 20L20 12Z" fill="#374151" stroke="#9ca3af" strokeWidth="1"/>
      <circle cx="20" cy="20" r="3" fill="#6b7280"/>
    </svg>
  );
}

// Ship/base shape used in cards without faction art (Explorer)
export function ShipArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <path d="M20 6L30 26H20H10L20 6Z" fill="#1e3a5f" stroke="#60a5fa" strokeWidth="1.3" strokeLinejoin="round"/>
      <path d="M16 22L12 30H28L24 22" fill="#0f2236" stroke="#3b82f6" strokeWidth="1"/>
      <circle cx="20" cy="20" r="3" fill="#3b82f6" opacity="0.7"/>
      <path d="M8 28L12 24M32 28L28 24" stroke="#60a5fa" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

export function BaseArt({ compact }: { compact?: boolean }) {
  const s = compact ? 28 : 40;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
      <polygon points="20,5 35,14 35,26 20,35 5,26 5,14" fill="#1e3a5f" stroke="#60a5fa" strokeWidth="1.5"/>
      <polygon points="20,12 28,17 28,23 20,28 12,23 12,17" fill="#0f2236" stroke="#3b82f6" strokeWidth="1"/>
      <circle cx="20" cy="20" r="4" fill="#1d4ed8" stroke="#93c5fd" strokeWidth="1"/>
    </svg>
  );
}

// Map faction → art component
export function FactionArt({ faction, type, compact }: { faction: string; type: string; compact?: boolean }) {
  if (type === 'Base' || type === 'Outpost') return <BaseArt compact={compact} />;
  switch (faction) {
    case 'Blob': return <BlobArt compact={compact} />;
    case 'Star Empire': return <StarEmpireArt compact={compact} />;
    case 'Trade Federation': return <TradeFederationArt compact={compact} />;
    case 'Machine Cult': return <MachineCultArt compact={compact} />;
    default: return <UnalignedArt compact={compact} />;
  }
}
