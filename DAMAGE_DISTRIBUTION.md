# Damage Distribution Feature

## Overview
In multiplayer games (3+ players), you can now distribute your combat damage across multiple opponents instead of attacking just one at a time.

## How to Use

### 1. During Your Turn
When you have combat available and there are multiple opponents:
- Look for the **"⚔️ Distribute Damage"** button in the turn actions area
- The button shows how much combat you have available

### 2. Open the Distributor
Click the "Distribute Damage" button to open the damage distribution modal.

### 3. Allocate Damage
For each opponent, you can:
- **Use +/- buttons** to adjust damage by 1
- **Type a number** directly into the input field
- **Click "Max"** to allocate all remaining combat to that opponent
- See their current health (❤️) displayed

### 4. Monitor Your Allocation
The top of the modal shows:
- **Available:** Total combat you started with
- **Allocated:** How much you've assigned so far
- **Remaining:** Combat left to allocate

### 5. Attack
- Click **"Attack (X damage)"** to execute the attack
- Click **"Cancel"** to go back without attacking

## Important Rules

### Outpost Protection
- Opponents with Outposts (🛡️) **cannot** be targeted
- You must destroy all Outposts before attacking that player
- These opponents will be grayed out in the distributor

### Partial Damage
- You don't have to use all your combat
- You can save some combat for attacking bases later
- You can distribute damage unevenly (e.g., 3 to one, 1 to another)

### Minimum Damage
- You must allocate at least 1 damage total
- Individual opponents can receive 0 damage (they'll be skipped)

## Example Scenarios

### Scenario 1: Focused Attack
You have 5 combat, 2 opponents:
- Opponent A: 5 damage
- Opponent B: 0 damage
- Result: Opponent A takes 5 damage, B is unharmed

### Scenario 2: Spread Attack
You have 6 combat, 3 opponents:
- Opponent A: 2 damage
- Opponent B: 2 damage  
- Opponent C: 2 damage
- Result: Each opponent loses 2 authority

### Scenario 3: Strategic Distribution
You have 8 combat, 2 opponents:
- Opponent A (has 3 health): 3 damage → Eliminated!
- Opponent B (has 20 health): 5 damage
- Result: Player A eliminated, Player B weakened

## Technical Details

### Backend
- **Endpoint:** `POST /api/games/{game_id}/distribute_damage`
- **Validation:** Checks total damage ≤ available combat
- **Outpost Check:** Validates no targets have Outposts
- **Win Condition:** Game ends when all opponents reach 0 authority

### Frontend
- **Component:** `DamageDistributor.tsx`
- **Styling:** `DamageDistributor.css`
- **Integration:** Seamlessly works with existing GameBoard

## Benefits

1. **Strategic Depth:** Make tactical decisions about who to eliminate first
2. **Multiplayer Balance:** Don't let one player dominate by focusing fire
3. **Flexibility:** Adapt your attack strategy based on game state
4. **Efficiency:** Distribute damage in one action instead of multiple clicks

## Notes
- This feature only appears in games with 3+ players
- In 2-player games, the standard "Attack" button on the opponent remains
- AIplayers can still only attack one opponent at a time (for now)
