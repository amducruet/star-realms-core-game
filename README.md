# Star Realms Web Game

A multiplayer deck-building card game inspired by Star Realms.

<img width="1724" height="954" alt="UI" src="https://github.com/user-attachments/assets/83c38aa4-71d1-4227-9f92-4be462b9265b" />


## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- WebSockets
- Pydantic

### Frontend
- React 18
- TypeScript
- Plain CSS

## Features

- 1v1 AImode
- 2-6 player multiplayer
- Server-authoritative game logic
- Real-time updates via WebSockets
- Card data imported from Excel


## Running Locally
### Backend
```bash
cd backend
source venv/bin/activate  # Already created
python main.py
```

The backend will start on http://localhost:8000
API docs available at http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend will start on http://localhost:3000

## Quick Start

Open two terminals:

**Terminal 1 (Backend):**
```bash
cd ~/star-realms-game/backend
source venv/bin/activate
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd ~/star-realms-game/frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser!

## Project Structure

```
star-realms-game/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   ├── import_cards.py    # Excel import script
│   │   │   └── cards.json         # Generated card database
│   │   ├── models/
│   │   │   ├── card.py           # Card models
│   │   │   ├── player.py         # Player state
│   │   │   └── game.py           # Game state
│   │   ├── services/
│   │   │   ├── game_service.py   # Game logic and rules
│   │   │   └── ai_service.py     # Simple AIopponent
│   │   ├── routes/
│   │   │   └── game_routes.py    # API endpoints
│   │   └── websocket_manager.py  # WebSocket handling
│   ├── main.py                   # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Lobby.tsx         # Game setup screen
│   │   │   ├── GameBoard.tsx     # Main game UI
│   │   │   ├── Card.tsx          # Card component
│   │   │   └── PlayerArea.tsx    # Player display
│   │   ├── services/
│   │   │   └── api.ts            # Backend API client
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts   # WebSocket hook
│   │   ├── types/
│   │   │   └── game.ts           # TypeScript types
│   │   ├── styles/               # CSS files
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
└── README.md
```

## Game Rules Summary

- Start with 50 Authority (health)
- Starting deck: 8 Scouts (1 Trade) + 2 Vipers (1 Combat)
- Draw 5 cards each turn
- Play all cards in hand
- Use Trade to acquire cards from trade row
- Use Combat to attack opponent
- Discard hand and played cards at end of turn
- First player to reduce opponent to 0 Authority wins
