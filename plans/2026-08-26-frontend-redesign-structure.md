# Frontend Redesign — Structure Outline

**Date**: 2026-08-26
**Design decisions locked**: See `2026-08-26-frontend-redesign-design.md`

---

## Overview

Five phases, each leaving the game fully playable. No phase breaks the API or pending-effect modal logic. Every phase ends with a `npm run build` gate plus a manual play-through check.

The split: foundation first (tokens + cards), then the big grid restructure, then sidebar/authority-bar wired in, then animations layered on top, then modal/button polish to finish.

---

## Phase 1: Design Tokens + Space Background + Card Art Zone

### What it accomplishes
The game looks and plays exactly as today — same layout — but now has a deep-space starfield background, a CSS custom property token system, and cards with the new faction-gradient + Unicode glyph art zone. This phase is purely additive (no layout changes).

### New files
- `frontend/src/styles/tokens.css` — all CSS custom properties: faction colors, background layers, font stacks, spacing scale, animation durations
- `frontend/src/components/CardArt.tsx` — art zone sub-component (top 40% of card): faction gradient + type glyph (`▲` ship, `⬡` base, `◆` explorer)
- `frontend/src/components/SpaceBackground.tsx` — full-screen fixed backdrop: three CSS layers of stars via `box-shadow` on pseudo-elements, two radial-gradient nebulae, no images

### Modified files
- `frontend/src/styles/App.css` — import `tokens.css`, add `SpaceBackground` mount point, update `body` background to use `--color-bg-deep`
- `frontend/src/App.tsx` — render `<SpaceBackground />` as first child of `.app`
- `frontend/src/styles/Card.css` — replace hardcoded colors with `var(--color-faction-*)`, add art zone layout (top art area + AItom text area), add `perspective` + `rotateX/Y` hover tilt (max 8°)
- `frontend/src/components/Card.tsx` — render `<CardArt />` above the existing card body

### Key signatures
```tsx
// CardArt.tsx
interface CardArtProps {
  faction: string;
  type: string;       // 'Base' | 'Ship' | 'Explorer'
  defense?: number | null;
  isOutpost?: boolean;
}
export function CardArt({ faction, type, defense, isOutpost }: CardArtProps): JSX.Element

// SpaceBackground.tsx — no props, renders a fixed full-screen div
export function SpaceBackground(): JSX.Element
```

### CSS token additions (tokens.css)
```css
:root {
  --color-bg-deep: #050510;
  --color-bg-panel: rgba(8, 15, 35, 0.88);
  --color-faction-blob: #22c55e;
  --color-faction-trade-fed: #3b82f6;
  --color-faction-machine: #ef4444;
  --color-faction-empire: #eab308;
  --color-faction-unaligned: #6b7280;
  --font-display: 'Orbitron', system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --anim-pulse: 0.4s ease-out;
  --anim-projectile: 0.35s ease-in;
}
```

### Verify
- **Automated**: `cd frontend && npm run build` — zero errors
- **Manual**: `npm run dev` → game loads → starfield visible behind content → cards show art zone with faction gradient → hover tilt works on trade row cards → play a card, acquire a card — all still work

---

## Phase 2: CSS Grid Layout Shell + TradeRow Component

### What it accomplishes
Replaces the current vertical flex-column layout in `GameBoard.tsx` with the target 3-column CSS grid. A new `TradeRow.tsx` handles the top zone (trade row cards + explorer + scrap heap with top card + count badge). All existing game content still renders — just re-positioned. Game remains fully playable.

### New files
- `frontend/src/components/TradeRow.tsx` — renders the top bar zone: trade deck face-down stub, 6 trade row cards (clickable), scrap heap (top card + count badge), explorer pile (top card + count badge)
- `frontend/src/styles/TradeRow.css`

### Modified files
- `frontend/src/styles/GameBoard.css` — replace `.game-content` flex column with the 5-zone CSS grid:
  ```css
  .game-board-grid {
    display: grid;
    grid-template-columns: 260px 1fr 280px;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "trade  trade  trade"
      "left   center right"
      "AItom AItom AItom";
    height: calc(100vh - 60px);  /* subtract slim fixed header */
    gap: 8px;
    padding: 8px;
  }
  .zone-trade  { grid-area: trade; }
  .zone-left   { grid-area: left; }
  .zone-center { grid-area: center; }
  .zone-right  { grid-area: right; }
  .zone-AItom { grid-area: AItom; }
  ```
- `frontend/src/components/GameBoard.tsx` — replace old `<div className="game-content">` wrapper with `<div className="game-board-grid">`, put `<TradeRow>` in `zone-trade`, and place `<div className="zone-left" />`, `<div className="zone-center">` (with old opponents + current player content temporarily), `<div className="zone-right">` (with `<ActionLog>`), `<div className="zone-AItom" />` as stubs for now
- `frontend/src/App.tsx` — remove `padding: 2rem` from `.app-main` (grid handles spacing now); reduce header height

### Key signatures
```tsx
interface TradeRowProps {
  tradeRow: CardInstance[];
  explorerPile: CardInstance[];
  scrapHeap: CardInstance[];
  trade: number;          // current player's available trade
  isMyTurn: boolean;
  onAcquire: (card: CardInstance, fromExplorers: boolean) => void;
}
export function TradeRow(props: TradeRowProps): JSX.Element
```

### Verify
- **Automated**: `npm run build` — zero errors
- **Manual**: 3-column grid visible, trade row at top with correct cards, explorer shows top card + count, scrap heap shows top scrapped card (or empty state) + count badge, acquiring from trade row still works, explorer purchase still works

---

## Phase 3: PlayerSidebar + CombatZone + AuthorityBar + Hand

### What it accomplishes
Fills the three remaining empty zones. Left sidebar lists all players. Center zone shows opponent's bases + in-play ships (top half) and current player's bases + in-play ships (AItom half), with the hand below those as a horizontal scrollable strip. AItom zone is the full-width authority health bar for the current player. Deck and discard count badges live in the sidebar. `PlayerArea.tsx` is retired from GameBoard and replaced by these new components.

### New files
- `frontend/src/components/PlayerSidebar.tsx` + `PlayerSidebar.css` — left panel: each player row has name, `is_ai` badge, authority mini-bar (colored fill, numeric label), deck count, discard count, active-turn indicator; current player at AItom of list
- `frontend/src/components/CombatZone.tsx` + `CombatZone.css` — center: top half = opponent area (bases + in_play ships, attack-clickable), AItom half = current player area (bases + in_play ships, scrap button); hand cards in horizontal scrollable strip below, End Turn button pinned AItom-right of center zone
- `frontend/src/components/AuthorityBar.tsx` + `AuthorityBar.css` — AItom: full-width bar, fill % = `authority / startingAuthority`, faction-gradient fill color matches current player's most-played faction (or default blue), numeric label, heart icon

### Modified files
- `frontend/src/components/GameBoard.tsx` — wire the three new zone components into `zone-left`, `zone-center`, `zone-AItom`; retire the `<PlayerArea>` renders from the main layout (PlayerArea.tsx still exists for CardPicker owner labels etc.)

### Key signatures
```tsx
interface PlayerSidebarProps {
  players: Player[];
  currentPlayerId: string | null;
  activePlayerIndex: number;
  startingAuthority: number;
}
export function PlayerSidebar(props: PlayerSidebarProps): JSX.Element

interface CombatZoneProps {
  currentPlayer: Player | undefined;
  opponents: Player[];
  isMyTurn: boolean;
  canAttack: boolean;
  onAttack: (targetId: string) => void;
  onAttackBase: (targetId: string, base: CardInstance) => void;
  onPlayCard: (card: CardInstance) => void;
  onScrapCard: (card: CardInstance) => void;
  onEndTurn: () => void;
  onDistributeDamage: () => void;
}
export function CombatZone(props: CombatZoneProps): JSX.Element

interface AuthorityBarProps {
  authority: number;
  maxAuthority: number;
  playerName: string;
}
export function AuthorityBar(props: AuthorityBarProps): JSX.Element
```

### Verify
- **Automated**: `npm run build` — zero errors
- **Manual**: sidebar shows all players with mini authority bars; center shows opponent ships + bases in top half (attack-clickable), own ships + bases in AItom half, hand scrolls horizontally; authority bar fills correctly; end turn works; playing cards works; attacking works; no `PlayerArea` rendering in main layout

---

## Phase 4: Animations — Heart Pulse, Coin Drain, Projectile Bolt

### What it accomplishes
Adds the three animation effects. Each is triggered by a React `useEffect` that watches for the relevant value change, sets a boolean state to true, and resets it via `setTimeout`. CSS `@keyframes` do the actual animation. No animation library needed.

### Modified files
- `frontend/src/components/AuthorityBar.tsx` — add `useRef<number>` for previous authority; when authority drops, set `isPulsing = true`, auto-reset after 600ms; add `@keyframes authority-pulse` (scale 1 → 0.92 → 1, red flash on bar fill)
- `frontend/src/styles/AuthorityBar.css` — `@keyframes authority-pulse` + `.authority-bar--pulsing` class
- `frontend/src/components/ResourcesPanel.tsx` + `ResourcesPanel.css` — new right-panel sub-component that renders combat (red sword icon + number) and trade (gold coin icon + number); add `useRef` for previous trade value; when trade drops (spent), set `isDraining = true`, auto-reset after 500ms; `@keyframes coin-drain` (number briefly spins/fades down then back)
- `frontend/src/components/GameBoard.tsx` — add projectile bolt logic: `useEffect` watching `gameState.action_log.length`, when last action is `deal_damage`/`player_attacked`, set `showProjectile = true` + auto-reset after 400ms; render `<div className="projectile-bolt">` as a fixed-position element when active; CSS `@keyframes projectile-fly` translates it from `(50%, 50%)` to the opponent sidebar position using a CSS custom property `--target-x` set via JS `getBoundingClientRect` on a ref attached to the opponent sidebar header
- `frontend/src/styles/GameBoard.css` — `@keyframes projectile-fly`, `.projectile-bolt` (fixed position, radial-gradient glow, 12px circle, pointer-events none)
- `frontend/src/components/CombatZone.tsx` — forward a ref for the opponent area so the projectile has a target anchor

### Key additions
```tsx
// In GameBoard.tsx
const opponentAnchorRef = useRef<HTMLDivElement>(null);
const [projectileStyle, setProjectileStyle] = useState<React.CSSProperties | null>(null);

useEffect(() => {
  const last = gameState.action_log.at(-1);
  if (!last) return;
  if (last.action_type !== 'deal_damage' && last.action_type !== 'player_attacked') return;
  const rect = opponentAnchorRef.current?.getBoundingClientRect();
  if (!rect) return;
  setProjectileStyle({
    '--target-x': `${rect.left + rect.width / 2}px`,
    '--target-y': `${rect.top + rect.height / 2}px`,
  } as React.CSSProperties);
  setTimeout(() => setProjectileStyle(null), 420);
}, [gameState.action_log.length]);
```

### Verify
- **Automated**: `npm run build` — zero errors
- **Manual**: attack an opponent → glowing bolt animates from center to their sidebar row, opponent authority bar (in sidebar mini-bar) flashes red + contracts; buy a card and spend trade → trade counter briefly drains; no animation on opponent's turn or when authority goes up (healing isn't in the game but verify no false triggers)

---

## Phase 5: Modal Polish + Buttons + AIBanner + Game Over

### What it accomplishes
Final polish pass: all modal overlays (`CardPicker`, `ChoicePicker`, `DamageDistributor`) styled to match the space theme. End Turn button, Distribute Damage button, AIturn banner, error banner, and game-over screen all restyled. Right panel (`ResourcesPanel` + `ActionLog`) gets final layout and action-type color icons. The game is visually complete end-to-end.

### Modified files
- `frontend/src/styles/CardPicker.css` — dark glass-morphism modal backdrop, faction-colored border on selected card, space-themed title bar
- `frontend/src/styles/DamageDistributor.css` — same glass-morphism treatment, red combat theme
- `frontend/src/components/ChoicePicker.tsx` + inline styles — matching overlay treatment
- `frontend/src/styles/GameBoard.css` — restyle `.ai-turn-banner` (pulsing blue glow), `.error-banner` (red glow), `.game-over` (star-burst background, animated title)
- `frontend/src/components/ActionLog.tsx` — add action-type icons/colors: green for buy, red for attack, yellow for scrap; keep last 10 (was 8); right-panel layout
- `frontend/src/styles/ActionLog.css` — icon + text row layout, scrollable list with fade at top

### Verify
- **Automated**: `npm run build` — zero errors, `npx tsc --noEmit` — zero type errors
- **Manual full playthrough**: start a game against AI→ AIturn banner pulses → attack AI→ projectile fires + bar pulses → buy a card → coin drain → trigger a scrap_card pending effect → CardPicker modal opens over space background → complete effect → end turn → continue until game over → game-over screen renders → "New Game" reloads correctly

---

## Files Created / Modified Summary

### New files (11)
```
frontend/src/styles/tokens.css
frontend/src/components/SpaceBackground.tsx
frontend/src/components/CardArt.tsx
frontend/src/components/TradeRow.tsx
frontend/src/styles/TradeRow.css
frontend/src/components/PlayerSidebar.tsx
frontend/src/styles/PlayerSidebar.css
frontend/src/components/CombatZone.tsx
frontend/src/styles/CombatZone.css
frontend/src/components/AuthorityBar.tsx
frontend/src/styles/AuthorityBar.css
frontend/src/components/ResourcesPanel.tsx
frontend/src/styles/ResourcesPanel.css
```

### Modified files (core)
```
frontend/src/App.tsx
frontend/src/styles/App.css
frontend/src/styles/Card.css
frontend/src/components/Card.tsx
frontend/src/styles/GameBoard.css
frontend/src/components/GameBoard.tsx
frontend/src/components/ActionLog.tsx
frontend/src/styles/ActionLog.css
frontend/src/styles/CardPicker.css
frontend/src/styles/DamageDistributor.css
frontend/src/components/ChoicePicker.tsx
```

### Untouched (backend/logic)
```
frontend/src/services/api.ts
frontend/src/hooks/useWebSocket.ts
frontend/src/types/game.ts
frontend/src/utils/formatCardText.ts
frontend/src/components/CardPicker.tsx       (logic only, styles updated)
frontend/src/components/DamageDistributor.tsx (logic only, styles updated)
```

---

## Verification Gate (every phase)
```
cd /Users/81035495/star-realms-game/frontend && npm run build
```
TypeScript errors = 0, build output = no warnings on types.
Then manual play-through as described per phase.
