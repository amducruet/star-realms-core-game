# 🗑️ Scrap Abilities - Now Working!

## What is Scrap?

**Scrap = Permanently remove a card from the game to get a bonus effect**

- Card goes to the **scrap heap** (never comes back)
- It's **optional** - you decide when to activate
- Can scrap **ships in play** or **bases**
- Great for removing weak starter cards or getting emergency effects

---

## 🎮 How to Use Scrap

### Step 1: Play a Card with Scrap Ability
Cards with `🗑️ Scrap:` in their text can be scrapped.

**Example cards:**
- **Explorer** - `{Scrap}: +2 Combat`
- **Scout** - Some versions have scrap abilities
- **Battle Blob** - `{Scrap}: +4 Combat`

### Step 2: See the Scrap Button
When you play a card with scrap ability, a **🗑️ Scrap** button appears on it in the "In Play" or "Bases" area.

### Step 3: Click to Scrap
- Click the **🗑️ Scrap** button
- Card is removed from play/bases
- Goes to scrap heap
- Effect activates immediately!

---

## 📊 Example Gameplay

### Example 1: Explorer
```
1. Buy Explorer from pile (Cost: 2 Trade)
2. Next turn: Draw Explorer
3. Play Explorer → Get +2 Trade (primary ability)
4. Click "🗑️ Scrap" button
5. Get +2 Combat (scrap ability)
6. Explorer removed from game forever
7. You now have 2 Trade + 2 Combat!
```

### Example 2: Thinning Your Deck
```
Turn 1-5: Play your 8 Scouts normally

Turn 6+: 
- Play Scout → +1 Trade
- Click "🗑️ Scrap" (if Scout has scrap ability)
- Get bonus effect
- Scout removed from game
- Your deck is now thinner!
- Future hands will have better cards!
```

### Example 3: Emergency Combat
```
Situation: Need 6 combat to win, but only have 4

Solution:
- Look at your bases
- See "Blob Wheel" with 🗑️ Scrap button
- Click "🗑️ Scrap"
- Get +3 Trade from scrap
- Use that trade to buy a combat card
- Win the game!
```

---

## 🎯 Strategy Tips

### When to Scrap:

**1. Remove Weak Starters**
- Scouts and Vipers are weak
- Scrap them to thin your deck
- Better cards appear more often

**2. Emergency Effects**
- Need combat NOW to win?
- Scrap for instant combat bonus

**3. Convert Resources**
- Have trade but need combat?
- Scrap something for combat

**4. Clean Up Cheap Cards**
- Once you have expensive cards
- Scrap the cheap ones to improve deck quality

### When NOT to Scrap:

**1. Powerful Bases**
- Don't scrap bases that give good effects every turn
- Only scrap if you need the one-time effect NOW

**2. Unique Effects**
- Some cards have special abilities
- Keep them unless you really need the scrap bonus

---

## 🎨 Visual Guide

**Card with Scrap Ability:**
```
┌─────────────────┐
│ Explorer     2💰 │
├─────────────────┤
│ Unaligned       │
│                 │
│ +2 Trade        │
│                 │
│ 🗑️ Scrap:       │
│ +2 Combat       │
│                 │
│  [🗑️ Scrap]     │ ← Click this button!
└─────────────────┘
```

**After Scrapping:**
- Card disappears from "In Play"
- Effect activates (Combat +2)
- Card appears in scrap heap count
- Never comes back to your deck

---

## 🧪 Testing Scrap

**Open:** http://localhost:3000

### Quick Test:
1. Start a new game
2. Look for **Explorer** in trade row or pile
3. Buy it for 2 Trade
4. Next turn, play Explorer
5. See the **🗑️ Scrap** button on it
6. Click the button
7. Watch your combat increase by 2!
8. Card disappears from play

### Cards with Scrap in Your Game:
- **Explorer** (Always available) - `{Scrap}: +2 Combat`
- **Battle Blob** - `{Scrap}: +4 Combat`
- **Ram** - `{Scrap}: +3 Trade`
- **Blob Wheel (Base)** - `{Scrap}: +3 Trade`
- **Stinger** - `{Scrap}: +1 Trade`
- And many more in the trade deck!

---

## ⚙️ Technical Details

**What Happens When You Scrap:**
1. Card removed from "In Play" or "Bases"
2. Scrap effect parsed and executed
3. Card moved to scrap heap
4. Effect applied (Combat, Trade, Authority, Draw, etc.)
5. Action logged: "You scrapped [Card Name]"

**Scrap Heap:**
- Cards in scrap heap are permanently out of the game
- They never shuffle back into your deck
- You can see scrap heap count (future feature)

---

## 🚀 What's Next?

Now that scrap is working, we can implement:

1. **Paid Abilities** - `💰 Pay 3 Trade: Draw a card`
2. **Optional Effects** - "You may scrap a card in hand"
3. **Targeting** - "Target opponent discards a card"
4. **Choice Effects** - "Draw a card OR gain 2 combat"

Which action would you like to implement next?
