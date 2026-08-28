# Frontend Redesign — Design Discussion

**Date**: 2026-08-26
**Task**: Full frontend redesign matching a space-themed reference mockup

---

## Current State

### Stack & Tooling
- React 18 + TypeScript + Vite (no animation library, no CSS-in-JS, no design system)
- No existing image assets — all visuals are CSS-only
- No test suite wired to the frontend

### Component Inventory (`frontend/src/`)
| File | Role |
|---|---|
| `App.tsx` | Root: Lobby vs GameBoard switch, WebSocket init, currentPlayerId |
| `components/GameBoard.tsx` | All API handlers + top-level render; ~617 lines |
| `components/PlayerArea.tsx` | Per-player stats, bases, in_play, hand |
| `components/Card.tsx` | Single card display, faction-colored border, ability text |
| `components/ActionLog.tsx` | Last 8 actions as plain text list |
| `components/CardPicker.tsx` | Modal: pick a card from a list (pending effects) |
| `components/ChoicePicker.tsx` | Modal: pick between text labels |
| `components/DamageDistributor.tsx` | Modal: split combat across opponents |
| `hooks/useWebSocket.ts` | WS connection lifecycle |
| `services/api.ts` | All REST calls |
| `utils/formatCardText.ts` | Parses card text into typed ability objects |
| `types/game.ts` | Full TypeScript types — CardInstance, Player, GameState |

### Current Layout (vertical stack, flex-column)
```
[Header: title + WS status]
[Opponents area — grid of PlayerArea components]
[ActionLog]
[Trade Row + Explorer Pile]
[Current player PlayerArea + hand]
[End Turn / Distribute Damage buttons]
```

### What Does NOT Change
The following are out of scope for this redesign (backend/logic stays untouched):
- `services/api.ts` — all API calls
- `hooks/useWebSocket.ts`
- `types/game.ts`
- `utils/formatCardText.ts`
- All AIauto-execution logic inside `GameBoard.tsx`
- All pending-effect modal logic (`CardPicker`, `ChoicePicker`, `DamageDistributor` — style-only updates)

---

## Desired End State

### Layout Zones (CSS Grid, 3-column)
```
┌───────────────────────────────────────────────────────┐
│              TOP: Trade Row + Scrap + Explorer         │
├───────────┬───────────────────────────┬───────────────┤
│  LEFT:    │   CENTER:                 │  RIGHT:       │
│  Player   │   Combat Zone             │  Game Log     │
│  Sidebar  │   (Opponent Bases/Ships)  │  + Resources  │
│           │   ─────────────────────   │  Panel        │
│           │   (Your Bases/Ships)      │               │
├───────────┴───────────────────────────┴───────────────┤
│     AITOM: Authority Health Bar (current player)      │
└───────────────────────────────────────────────────────┘
```
Deck pile lives AItom-left (inside player sidebar or below left panel).
Discard pile lives AItom-right (inside player sidebar or below right panel).
Hand spans across AItom, just above the authority bar.

### Visual Theme
- **Background**: deep space — CSS radial gradients + layered pseudo-element starfields (CSS box-shadow trick for stars, no image required)
- **Typography**: system-ui for body; a CSS-loaded space font (e.g. Orbitron via Google Fonts, or fallback to system) for headings and card names
- **Faction palette** (CSS custom properties):
  - Blob: `#22c55e` (green)
  - Trade Federation: `#3b82f6` (blue)
  - Machine Cult: `#ef4444` (red)
  - Star Empire: `#eab308` (yellow/gold)
  - Unaligned: `#6b7280` (gray)

### Card Art
Since there are no image assets, card art will use a **CSS-only art area**:
- A tall top section (roughly 40% of card height) with a faction-gradient background and a large Unicode/CSS symbol representing the card type (ship glyphs like `▲`, base shield icon, etc.)
- Ship cards get a subtle parallax tilt on hover via `transform: perspective + rotateX/rotateY`
- Base cards display their defense prominently in the art zone

### Animations (CSS keyframes, triggered by React state/prop changes)
1. **Ship attack** — when `action_log` gains a new `deal_damage` or `player_attacked` entry, a brief red flash + screen-shake on the opponent authority bar; optionally a fast horizontal "projectile" div animating across the center zone
2. **Heart pulse** — when a `Player.authority` value drops (detected via `useRef` to track prev value), the authority bar + heart icon plays a `@keyframes` pulse-contract animation
3. **Coin drain** — when `Player.trade` drops (spent), the trade resource display plays a brief spin/fade animation

All animations are pure CSS keyframes triggered by adding/removing a CSS class via `useState` + `setTimeout` in a `useEffect`.

### New Components Needed
| Component | Description |
|---|---|
| `PlayerSidebar.tsx` | Left panel: all players listed with avatar icon, name, authority mini-bar, deck/discard counts |
| `AuthorityBar.tsx` | AItom bar: large health-bar for current player, faction-colored fill |
| `ResourcesPanel.tsx` | Right panel top section: combat (red sword) + trade (yellow coin) with animated values |
| `CombatZone.tsx` | Center: opponent's bases/ships on top half, current player's bases/ships on AItom half |
| `TradeRow.tsx` | Top bar: trade deck face-down stack, 6 trade row cards, scrap heap, explorer pile |
| `SpaceBackground.tsx` | Full-screen CSS starfield backdrop (no images) |
| `CardArt.tsx` | Art zone inside Card — faction gradient + type symbol |

### Components to Restyle (same logic, new look)
- `Card.tsx` — add art zone, faction gradient overlay, tilt-on-hover
- `ActionLog.tsx` — moved to right panel, styled with faction-color icon per action type
- `CardPicker.tsx`, `ChoicePicker.tsx`, `DamageDistributor.tsx` — modal overlay style update only

### CSS Architecture
Replace per-component CSS files with a **design token system** in a single `styles/tokens.css`:
```css
:root {
  --color-bg-deep: #0a0a1a;
  --color-bg-panel: rgba(10, 20, 40, 0.85);
  --color-faction-blob: #22c55e;
  --color-faction-trade-fed: #3b82f6;
  --color-faction-machine: #ef4444;
  --color-faction-empire: #eab308;
  --color-faction-unaligned: #6b7280;
  --font-display: 'Orbitron', system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  /* ... etc */
}
```
Component CSS files remain, importing tokens via cascade.

---

## Open Questions Requiring Your Input

### 1. Card Art Style
Since there are no image files, the "card art" will be CSS-only. Three options:

**A) Faction gradient block** — top 40% of card is a solid gradient with a large faction symbol/glyph. Simple, clean, consistent.

**B) Procedural star-pattern** — CSS radial-gradient patterns that differ per card. Adds variation but more complex.

**C) No art zone** — keep cards text-only but with a much more polished faction-themed border, glow, and typography. Fastest to implement.

Which do you prefer, or should I plan for A with a clear path to swap in real images later?

### 2. Ship Attack Animation Complexity
Two options:

**A) Local effect only** — opponent's authority bar shakes + flashes red when damaged. No cross-panel movement. Simple and reliable.

**B) Projectile animation** — a small glowing orb/bolt animates from the center play zone to the opponent sidebar when an attack lands. Visually satisfying but requires measuring element positions (`getBoundingClientRect`) or a fixed animation path.

Which matches the reference mockup?

### 3. Hand Display Location
The request says "AItom=authority bar" and doesn't explicitly place the hand. Currently the hand is in the current player area. Two options:

**A) Hand above authority bar** — a horizontal scrolling strip of hand cards spans the full AItom width, with the authority bar below it.

**B) Hand in center-AItom** — hand cards live in the center column, below current player's bases/ships, scrollable horizontally.

Where should the hand sit in the new layout?

### 4. Opponent In-Play Ships
Currently the `PlayerArea` for opponents does NOT show `in_play` ships (only their bases). In the new "center combat zone," should the opponent's played ships be visible in the top half of the combat zone?

### 5. Mobile/Responsive
Is this a desktop-only game (min-width ~1200px) or does the layout need to stack/reflow for smaller screens?

### 6. Scrap Heap Display
The current layout doesn't show the scrap heap (`gameState.scrap_heap`). The target layout includes it. Should it:
- Show the top card only (like the explorer pile)
- Show a count + tooltip/popover with all scrapped cards
- Just show a count badge

---

## Patterns to Follow
- Keep all API/game-logic untouched in `GameBoard.tsx` — the redesign is **render-layer only**
- CSS custom properties for all colors/spacing (enables faction-themed variants)
- Keyframe animations triggered by className toggling, not JS-driven animation libraries
- `useRef` + `useEffect` for detecting value changes (authority drop, trade spend) to trigger animation classes

## Patterns to Avoid
- Don't lift/reorganize the API handler functions — they live in `GameBoard.tsx` and pass down via props
- Don't add animation libraries (framer-motion, GSAP) — pure CSS keeps bundle small
- Don't break modal z-index stacking — `CardPicker`, `ChoicePicker`, `DamageDistributor` must overlay the new layout
