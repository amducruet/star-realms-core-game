# Star Realms Implementation Summary

## Phase 1: Core Gameplay ✅

### What's Been Built

#### Backend (Python/FastAPI)
1. **Card Data Import** (`app/data/import_cards.py`)
   - Imports 97 cards from cleaned Excel file
   - Parses Scouts, Vipers, Trade Deck, and Explorer Pile
   - Generates JSON database

2. **Data Models** (`app/models/`)
   - `CardInstance`: Individual card with unique instance ID
   - `Player`: Player state (authority, deck, hand, discard, bases, in-play, combat, trade)
   - `GameState`: Complete game state with turn management
   - `GameAction`: Event system for Phase 2 animations

3. **Game Service** (`app/services/game_service.py`)
   - Game creation and initialization
   - Starting deck distribution (8 Scouts + 2 Vipers per player)
   - Trade row management (5 cards)
   - Card playing and effect resolution
   - Card acquisition (from trade row or explorers)
   - Combat system (attack players and bases)
   - Outpost rules (must destroy before attacking player)
   - Turn management (draw, play, end turn)
   - Win condition checking

4. **AIService** (`app/services/ai_service.py`)
   - Play all cards
   - Buy most expensive affordable card
   - Attack outposts first, then bases, then player
   - Basic decision making

5. **API Routes** (`app/routes/game_routes.py`)
   - POST `/api/games/create` - Create game
   - POST `/api/games/{id}/start` - Start game
   - GET `/api/games/{id}` - Get game state
   - POST `/api/games/{id}/play_card` - Play a card
   - POST `/api/games/{id}/acquire_card` - Buy a card
   - POST `/api/games/{id}/attack_player` - Attack opponent
   - POST `/api/games/{id}/attack_base` - Destroy base
   - POST `/api/games/{id}/end_turn` - End turn
   - WS `/api/ws/{id}` - Real-time updates

6. **WebSocket Manager** (`app/websocket_manager.py`)
   - Manages connections per game
   - Broadcasts game state changes to all players

#### Frontend (React/TypeScript)
1. **Type Definitions** (`src/types/game.ts`)
   - Matches backend models exactly
   - CardInstance, Player, GameState, GameAction

2. **API Service** (`src/services/api.ts`)
   - Type-safe API client
   - All game actions wrapped in async functions

3. **WebSocket Hook** (`src/hooks/useWebSocket.ts`)
   - Auto-connect/disconnect based on game ID
   - Real-time state updates

4. **Components**
   - `Lobby`: Game setup (player name, AIcount)
   - `GameBoard`: Main game UI with all zones
   - `Card`: Card display with faction colors, cost, defense, text
   - `PlayerArea`: Player info, bases, in-play cards, hand

5. **Styling** (Plain CSS)
   - Dark theme with gradient backgrounds
   - Faction colors: Green (Blob), Blue (TF), Red (MC), Yellow (SE)
   - Responsive card layout
   - Hover effects and transitions
   - Clean, readable typography

### Game Flow

1. **Setup**
   - Player enters name and selects AIopponents (1-5)
   - Game creates 8 Scouts + 2 Vipers for each player
   - Shuffles trade deck and deals 5-card trade row
   - Each player draws 5 cards

2. **Turn Sequence**
   - Play cards from hand (click to play)
   - Ships go to "in play" and are discarded at end of turn
   - Bases stay in play permanently
   - Card effects are applied (Combat, Trade, Authority, Draw)
   - Use Trade to acquire cards from trade row or explorers
   - Use Combat to attack opponent or their bases
   - Click "End Turn" to discard everything and draw 5 new cards

3. **Combat Rules**
   - Must destroy all Outposts before attacking player
   - Must destroy all Outposts before attacking non-outpost bases
   - Bases have Defense that must be overcome
   - Any remaining Combat damages player Authority

4. **Win Condition**
   - Reduce opponent's Authority to 0 or below

### What Works
- ✅ Complete game loop
- ✅ Card effects (Combat, Trade, Authority, Draw)
- ✅ Trade row and explorer pile
- ✅ Deck/hand/discard management
- ✅ Base persistence and destruction
- ✅ Outpost rules
- ✅ Turn flow
- ✅ Win detection
- ✅ Real-time updates via WebSocket
- ✅ Basic AIopponent
- ✅ 2-6 player support (1 human + 1-5 AI)

### What's NOT Implemented Yet (Phase 1 Simplifications)
- ❌ Full ally ability parsing (complex text parsing)
- ❌ Scrap abilities
- ❌ "Or" choice abilities
- ❌ Multi-faction cards
- ❌ Paid abilities (e.g., "Pay 3 Trade: Draw a card")
- ❌ Interactive choices (e.g., "scrap a card in hand")
- ❌ AItaking automatic turns
- ❌ Multiplayer lobby (multiple humans)

### Phase 2: Next Steps

1. **Animations**
   - Card play animation (hand → in play)
   - Card acquisition (trade row → discard pile)
   - Draw animation (deck → hand)
   - Damage numbers
   - Base destruction effect
   - Scrap animation

2. **Advanced Card Abilities**
   - Parse ally abilities from text
   - Implement scrap abilities
   - Handle "Or" choices
   - Interactive card effects

3. **Enhanced AI**
   - Automatic AIturns (no user intervention)
   - Better card evaluation
   - Strategy based on deck composition

4. **Multiplayer**
   - Real lobby with multiple humans
   - Spectator mode
   - Game history/replay

5. **Polish**
   - Sound effects
   - Card hover previews
   - Action log/history
   - Better error messages
   - Loading states
   - Reconnection handling

## How to Test Phase 1

1. Start backend: `cd backend && source venv/bin/activate && python main.py`
2. Start frontend: `cd frontend && npm install && npm run dev`
3. Open http://localhost:3000
4. Enter your name, select 1 AIopponent
5. Click "Create Game" then "Start Game!"
6. Play cards by clicking them
7. Buy cards from trade row (if you have enough Trade)
8. Attack opponent (if you have Combat)
9. End turn

## Known Issues / TODOs

1. Card text is displayed but not fully parsed - many abilities won't work yet
2. AIdoesn't take turns automatically - needs integration with turn system
3. No validation for some edge cases (e.g., trying to buy when no trade)
4. Explorer pile always shows first card (should be same card definition with count)
5. No animation delays - everything is instant
6. No undo functionality
7. No save/load game state

## Architecture Decisions

1. **Stable Instance IDs**: Every card instance has a UUID for animation tracking
2. **Server Authority**: All game logic runs on backend, frontend is just a view
3. **Event Log**: GameAction events stored for Phase 2 animation replay
4. **WebSocket Broadcast**: Game state pushed to all players on every action
5. **Simplified Card Parsing**: Phase 1 uses basic text matching, Phase 2 will add full parser
6. **Plain CSS**: No CSS-in-JS or frameworks, easier to customize

## File Count

- Backend: 12 Python files
- Frontend: 14 TypeScript/TSX files + 5 CSS files
- Total: ~2000 lines of code (estimated)
