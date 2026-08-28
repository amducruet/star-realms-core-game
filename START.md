# Quick Start Guide

## 🚀 Running the Game

### Step 1: Start the Backend

Open a terminal and run:

```bash
cd ~/star-realms-game/backend
source venv/bin/activate
python main.py
```

You should see:
```
🚀 Starting Star Realms Game Server...
📡 API: http://localhost:8000
📚 Docs: http://localhost:8000/docs
🔌 WebSocket: ws://localhost:8000/api/ws/{game_id}
```

### Step 2: Start the Frontend

Open a **second** terminal and run:

```bash
cd ~/star-realms-game/frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Step 3: Play!

Open your browser to **http://localhost:3000**

## 🎮 How to Play

### Game Setup
1. Enter your player name
2. Select number of AIopponents (1-5)
3. Click "Create Game"
4. Click "Start Game!"

### Playing Your Turn
1. **Play Cards** - Click cards in your hand to play them
   - Ships provide Combat/Trade/Authority
   - Bases stay in play permanently
   
2. **Buy Cards** - Click cards in the Trade Row
   - Must have enough Trade (💰)
   - Acquired cards go to your discard pile
   - Explorers always available for 2 Trade

3. **Attack** - Click "Attack" button on opponent
   - Must have Combat (⚔️)
   - Must destroy Outposts first!
   - Reduces opponent's Authority (❤️)

4. **End Turn** - Click "End Turn" button
   - Discards all played cards
   - Draws 5 new cards

### Win Condition
Reduce your opponent's Authority to 0!

## 📊 Game Stats Explained

- ❤️ **Authority** - Your health (starts at 50)
- ⚔️ **Combat** - Attack power (use to damage opponent)
- 💰 **Trade** - Currency (use to buy cards)
- 🃏 **Deck** - Cards left to draw
- 🗑️ **Discard** - Cards already played

## 🎨 Faction Colors

- 🟢 **Green = Blob** - Aggressive, scrapping, high combat
- 🔵 **Blue = Trade Federation** - Authority gain, defensive
- 🔴 **Red = Machine Cult** - Scrapping, deck cycling
- 🟡 **Yellow = Star Empire** - Hand disruption, card draw
- ⚪ **Gray = Unaligned** - Starting cards (Scouts, Vipers, Explorers)

## ⚠️ Known Limitations (Phase 1)

- Card text is shown but most abilities don't work yet (only basic Combat/Trade/Authority/Draw)
- AIdoesn't take turns automatically yet
- No ally abilities implemented
- No scrap abilities
- No "Or" choice abilities
- Only 1 human player supported

These will be added in Phase 2!

## 🔧 Troubleshooting

### Backend won't start
```bash
# Reinstall dependencies
cd ~/star-realms-game/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Reinstall dependencies
cd ~/star-realms-game/frontend
rm -rf node_modules
npm install
```

### Port already in use
- Backend: Edit `main.py` and change `port=8000` to another port
- Frontend: Edit `vite.config.ts` and change `port: 3000` to another port

## 📚 More Info

- See `README.md` for full project documentation
- See `IMPLEMENTATION.md` for technical details
- API docs available at http://localhost:8000/docs when backend is running

## 🎯 Next Steps (Phase 2)

- Implement full card ability parsing
- Add animations for all actions
- Make AItake turns automatically
- Add multiplayer lobby
- Add sound effects
- Improve UI/UX

Enjoy playing Star Realms! 🌟
