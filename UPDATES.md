# Game Updates Summary

## Major Features Added

### 1. **SP (Sequence Points) System**
- Players earn SP when they win a sequence
- SP amount is based on string length:
  - **5-9 characters**: 1 SP
  - **10-19 characters**: 2 SP (SP+)
  - **20-39 characters**: 3 SP (SPx)
  - **40+ characters**: 4 SP (SP^)
- SP displays in purple on the main stats bar
- Save/load SP from `equipment.json`

### 2. **Equipment Crafting System**
- Access via **Tools → Equipment Crafting** menu
- Two equipment types:
  - **Gauntlets** (Left Hand) - 5 available
  - **Devices** (Right Hand) - 5 available
- 10 total unique equipment pieces with different crafting costs and effects
- Each item has increasing SP costs ranging from 5 to 70 SP

### 3. **Equipment Types & Effects**

**Gauntlets (Left Hand):**
- Iron Gauntlet (5 SP): Reduce rolls by 2
- Steel Gauntlet (15 SP): Gain 5 bonus rolls
- Silver Gauntlet (25 SP): +15% property accuracy
- Gold Gauntlet (40 SP): +50% SP gained
- Obsidian Gauntlet (60 SP): Double all SP earned

**Devices (Right Hand):**
- Basic Device (5 SP): 1 free reroll per win
- Analysis Device (15 SP): See 1 extra property
- Fortune Device (25 SP): +25% luck in rolls
- Mastery Device (40 SP): Properties reveal 50% faster
- Infinity Device (70 SP): See all target properties

### 4. **Equipment Management**
- **Craft Tab**: View all craftable equipment and their costs
- **Inventory Tab**: See owned equipment with equip status
- **Equip Tab**: Equip gauntlets to left hand and devices to right hand
- Can equip one gauntlet AND one device simultaneously
- Equipment effects stack when both are equipped
- Persistent storage in `equipment.json`

### 5. **UI/Performance Improvements**

**Minigame Optimization:**
- Removed lag by adding `mini_running` flag
- Improved timer logic to prevent cascading callbacks
- Button state properly disabled when time runs out
- Smoother roll detection

**Button Hold Animation Removal:**
- Added `activebackground` and `activeforeground` parameters to all main buttons
- Prevents buttons from turning white when held down
- Maintains original button colors while interacting

### 6. **Visual Updates**
- SP label added to main stats bar (purple color)
- Equipment menu uses tabbed interface:
  - Craft Equipment
  - Inventory
  - Equip
- Gauntlet emoji: 🧤
- Device emoji: 📱
- Victory message now shows SP gained

## Technical Changes

### New Methods
- `_init_equipment_recipes()`: Initialize 10 equipment types with recipes
- `_load_equipment()`: Load equipment from file with SP and equipped items
- `_save_equipment()`: Save equipment state persistently
- `_calculate_sp(string_length)`: Calculate SP based on string length
- `show_equipment_window()`: Main equipment UI with tabs

### Modified Methods
- `__init__()`: Added SP, gauntlet/device variables, equipment loading
- `play_mini_game()`: Optimized for performance with proper timer logic
- `manual_roll()`: Added SP calculation and label update on win
- `quit_game()`: Added equipment save before exit

### Files Created/Modified
- **questionmark.py**: Added 500+ lines for equipment system
- **equipment.json**: New file for persistent equipment storage (auto-created)

## Game Balance Notes

- Achievement requirements already balanced:
  - Speed Demon: Win under 50 rolls
  - Perfectionist: 3 wins in a row
- Equipment costs increase with power level
- Infinity Device (most powerful) requires 70 SP
- All equipment is purchasable with SP earned from winning sequences

## How to Use Equipment

1. **Earn SP**: Win sequences with various string lengths
2. **Open Equipment Menu**: Tools → Equipment Crafting
3. **Craft Equipment**: Switch to "Craft Equipment" tab and click craft buttons
4. **Check Inventory**: View owned equipment in "Inventory" tab
5. **Equip Items**: Switch to "Equip" tab to equip gauntlet and/or device
6. **Play with Effects**: Equipment gives passive effects while equipped

## Version Info
- All features tested and working
- No external dependencies required (matplotlib still optional)
- Windows compatible (tested on Windows)
- Persistent save system in place
