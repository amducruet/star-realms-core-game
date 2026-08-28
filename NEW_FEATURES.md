# New Features Implemented

## ✅ Feature 1: Custom Starting Authority

**What it does:**
You can now choose how much Authority (health) players start with!

**Options available:**
- **30** - Quick game (fast-paced)
- **40** - Fast game
- **50** - Standard (default, classic Star Realms)
- **60** - Long game
- **75** - Epic battle
- **100** - Marathon mode

**Where to find it:**
In the game lobby, there's now a new dropdown: **"Starting Authority (Health)"**

**Example:**
- Choose 30 for a quick 5-10 minute game
- Choose 100 for a long epic battle where you build up huge decks

---

## ✅ Feature 2: Maximum 5 Ships In Play

**Rule:**
You can only have **maximum 5 ships** in the "In Play" area per turn.

**How it works:**
- **Ships**: Maximum 5 per turn in "In Play" area
  - These are discarded at end of turn
  - If you try to play a 6th ship, you get an error: "Maximum 5 ships in play"
  
- **Bases**: Unlimited in "Bases" area
  - These stay from previous turns
  - Don't count toward the 5 ship limit
  - Can play bases even if you already have 5 ships

**Example Turn:**
```
Your hand: 4 Scouts, 1 Blob Fighter, 1 Trade Station (Base)

1. Play Scout #1 → In Play (1/5 ships)
2. Play Scout #2 → In Play (2/5 ships)
3. Play Scout #3 → In Play (3/5 ships)
4. Play Scout #4 → In Play (4/5 ships)
5. Play Blob Fighter → In Play (5/5 ships) ✓ LIMIT REACHED
   - Blob Fighter draws a card
6. Try to play drawn card (ship) → ✗ BLOCKED "Maximum 5 ships in play"
7. Play Trade Station (Base) → Bases area ✓ ALLOWED (bases don't count)

Result: 5 ships in play + 1 base
```

**AIBehavior:**
- AIwill automatically stop playing ships after 5
- You'll see: "⚠️ Hit 5 ship limit, stopping card plays"
- AIcontinues with buying cards and attacking

---

## 🎮 Testing The New Features

**Open:** http://localhost:3000

### Test Starting Authority:
1. Create a new game
2. Look for **"Starting Authority (Health)"** dropdown
3. Select "30 (Quick)" or "100 (Marathon)"
4. Start game
5. Check player authority - should match your selection!

### Test 5 Ships Limit:
1. Start a game
2. Play 5 ships from your hand
3. If you drew extra cards (via card effects), try to play a 6th ship
4. You should see error: "Maximum 5 ships in play"
5. But you CAN still play bases!

---

## 📋 What's Next: Card Actions Review

Ready to review the different card actions! Here are the main types:

### 1. **Primary Effects** (Always happen)
- `+X Combat` - Attack damage
- `+X Trade` - Currency to buy cards  
- `+X Authority` - Heal yourself
- `Draw a card` - Draw from your deck

### 2. **Ally Abilities** (Trigger with same-faction cards)
- `⭐ Blob Ally:` - 1+ Blob cards in play
- `⭐⭐ Double Blob Ally:` - 2+ Blob cards in play
- Same for: Trade Federation, Machine Cult, Star Empire

### 3. **Scrap Abilities** (Not implemented yet - Phase 2)
- `🗑️ Scrap: +2 Combat` - Destroy this card for effect
- Need UI button to activate

### 4. **Paid Abilities** (Not implemented yet - Phase 2)
- `💰 Pay 3 Trade: Draw a card`
- Need UI button to activate

### 5. **Optional Effects** (Not implemented yet - Phase 2)
- "You may scrap a card..."
- "You may destroy target base..."
- Need UI for choices

Which card actions would you like to implement next?
