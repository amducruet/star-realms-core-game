# Outpost Attack Fix

## ✅ Problem Fixed

**Issue:** You couldn't attack opponent bases or outposts - there was no way to click on them!

## 🔧 What Was Changed

### 1. Made Opponent Bases Clickable
- Opponent bases now have `onClick` handlers
- When you have combat available, bases glow with a **red border**
- Hover effect shows you can click them

### 2. Added Attack Base Function
- Click on opponent's base to attack it
- Automatically calculates damage (uses enough to destroy, or all your combat)
- Updates game state in real-time

### 3. Visual Outpost Warning
- When opponent has outposts, you'll see:
  - **⚠️ Outposts must be destroyed first!** warning
  - Outposts glow red when clickable
  - Clear indication they must be targeted first

### 4. Proper Attack Flow
- **If opponent has outposts:** You can ONLY attack outposts (not player or other bases)
- **After outposts destroyed:** You can attack player or any remaining bases
- Error message if you try to attack player while outposts exist

## 🎮 How to Attack Bases

### Step 1: Check for Outposts
Look at opponent's "Bases:" section. If there's a **⚠️ warning**, they have outposts.

### Step 2: Attack Outposts First
1. Make sure you have Combat (⚔️)
2. Click on the outpost base (it will have a red border)
3. Game automatically uses enough combat to destroy it
4. Outpost disappears from play

### Step 3: Attack Other Targets
Once all outposts are destroyed:
- Click other bases to destroy them
- OR click "Attack" button to damage the player directly

## 📊 Example Gameplay

```
Turn 1:
- You have 8 Combat
- Opponent has "Ion Station" (Outpost, 5 Defense)
- Click Ion Station → Uses 5 combat → Outpost destroyed ✓
- You have 3 combat left
- Click "Attack" button → Deal 3 damage to opponent

Turn 2:
- You have 6 Combat
- Opponent has "Trade Station" (Base, 4 Defense) - NOT an outpost
- You can attack the player OR the base
- Click Trade Station → Uses 4 combat → Base destroyed ✓
- You have 2 combat left
- Click "Attack" button → Deal 2 damage to opponent
```

## 🎯 Visual Indicators

**When You Have Combat:**
- Opponent bases glow with **red border**
- Hover shows you can click
- Cursor changes to pointer

**Outpost Warning:**
- **⚠️ Outposts must be destroyed first!** appears in red
- Outposts are clearly marked

**After Clicking:**
- Base defense reduces (or base destroyed)
- Your combat reduces
- Action log shows: "You destroyed [Base Name]"

## 🧪 Testing

1. **Start game with AI**
2. **Buy bases** from trade row (look for "Base" type cards)
3. **End your turn** - bases stay in play
4. **Wait for AIto buy bases**
5. **Your next turn** - you'll see their bases
6. **Click opponent bases** to attack them

## ⚠️ Important Rules

1. **Outposts MUST be destroyed first**
   - Can't attack player if they have outposts
   - Can't attack non-outpost bases if they have outposts
   - Game will block you with error message

2. **Combat is consumed**
   - Attacking uses your combat
   - Can attack multiple targets in one turn
   - Combat resets to 0 at end of turn

3. **Bases stay between turns**
   - Your bases stay in play
   - Opponent bases stay in play
   - Only destroyed by combat or card effects

## 🚀 Try It Now

**Open:** http://localhost:3000

1. Create game vs AI
2. Play until someone buys a base
3. Attack it next turn!
