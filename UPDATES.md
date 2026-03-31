# Questionmark Game - Update History

## Version 1.1 - Major Security & Feature Update (March 31, 2026)

### 🔒 Security & Privacy Overhaul
- **Repository Security**: Removed all sensitive user data files from GitHub
- **Privacy Protection**: Updated .gitignore to prevent accidental commits of user data
- **Data Isolation**: User accounts, passwords, and game progress never exposed publicly
- **Clean History**: Repository now contains only safe, public files

### 🛠️ Developer Console System
- **Restricted Access**: Only authorized users can access the developer console
- **Admin Management**: User "DeMarcusThe2nd" can manage dev console access permissions
- **Settings Integration**: New "Dev Console Access" tab in settings for permission management
- **Command Interface**: Full-featured console with input/output for advanced game manipulation

#### Available Dev Commands:
- `set_sp <amount>` - Set regular SP
- `set_sp_plus <amount>` - Set SP+ currency
- `set_sp_x <amount>` - Set SPx currency
- `set_sp_caret <amount>` - Set SP^ currency
- `add_wins <amount>` - Add wins to counter
- `set_rolls <amount>` - Set total rolls
- `reset_stats` - Reset all stats to zero
- `unlock_all_achievements` - Unlock all achievements
- `give_equipment <name>` - Give specific equipment item
- `clear_inventory` - Clear equipment inventory
- `set_difficulty <easy|normal|hard>` - Change difficulty
- `reload_game` - Reload game state
- `export_data` - Export all user data to JSON file
- `help` - Display available commands

### 💰 Enhanced SP (Sequence Points) System
- **Increased Rewards**: SP rewards multiplied by 5x for better progression
- **New SP Amounts**:
  - **4-7 characters**: 5 SP (was 1)
  - **8-14 characters**: 10 SP+ (was 1)
  - **15-24 characters**: 15 SPx (was 1)
  - **25+ characters**: 20 SP^ (was 1)
- **Consistent Rewards**: Both manual and auto-roll now give identical SP amounts

### ⚙️ Balanced Equipment Crafting System
- **Updated Costs**: Equipment costs scaled to match new SP reward system
- **Balanced Progression**: Equipment costs range from 10-50 SP (previously 5-70 SP)
- **Premium Currency**: Higher-tier items require rarer SP types (SP+, SPx, SP^)

### 🎯 Daily Challenges & Rewards
- **Bonus SP**: Daily challenges provide additional SP rewards
- **Challenge Types**:
  - Quick Thinker: 3 wins (+5 SP bonus)
  - Accuracy Master: 5 wins (+8 SP bonus)
  - SP+ Collector: 3 SP+ earned (+10 SP bonus)
  - SPx Collector: 2 SPx earned (+15 SP bonus)
  - SP^ Collector: 1 SP^ earned (+25 SP bonus)
  - Grinding Session: 50 rolls (+12 SP bonus)
  - Perfect Series: 3 wins in a row (+20 SP bonus)
  - Long String Master: Win with 25+ char string (+18 SP bonus)

### 🏆 Achievement System
- **Persistent Unlocks**: Achievements save across sessions
- **Diverse Goals**: Speed, accuracy, collection, and special achievements
- **Visual Feedback**: Achievement progress tracking

### 📊 Statistics & Leaderboard
- **Comprehensive Stats**: Tracks wins, rolls, streaks, fastest times
- **Property Discovery**: Logs discovered string properties
- **Global Leaderboard**: Shows top players (usernames, wins, titles only)
- **Privacy-Safe**: No sensitive data exposed in leaderboards

### 🎮 Game Features
- **Difficulty Levels**: Easy, Normal, Hard with different property requirements
- **Auto-Roll System**: Configurable speed (1-50 rolls per second)
- **Mini-Game**: Time-based challenge mode
- **Tutorial System**: Interactive guidance for new players
- **Sound Effects**: Optional audio feedback
- **Theme Support**: Dark, Light, and Neon visual themes

---

## Version 1.0 - Initial Release

## Major Features Added

### 1. **SP (Sequence Points) System**
- Players earn SP when they win a sequence
- SP amount is based on string length:
  - **4-7 characters**: 5 SP
  - **8-14 characters**: 10 SP (SP+)
  - **15-24 characters**: 15 SP (SPx)
  - **25+ characters**: 20 SP (SP^)
- SP displays in purple on the main stats bar
- Save/load SP from `equipment.json`

### 2. **Equipment Crafting System**
- Access via **Tools → Equipment Crafting** menu
- Two equipment types:
  - **Gauntlets** (Left Hand) - 5 available
  - **Devices** (Right Hand) - 5 available
- 10 total unique equipment pieces with different crafting costs and effects
- Each item has increasing SP costs ranging from 10 to 50 SP

### 3. **Equipment Types & Effects**

**Gauntlets (Left Hand):**
- Iron Gauntlet (15 SP): Reduce rolls by 1
- Steel Gauntlet (5 SP+): Gain 3 bonus rolls
- Silver Gauntlet (5 SPx): +10% property accuracy
- Gold Gauntlet (10 SPx): +25% SP gained
- Obsidian Gauntlet (5 SP^): Double all SP earned

**Devices (Right Hand):**
- Basic Device (10 SP): 1 free reroll per win
- Analysis Device (5 SP+): See 1 extra property
- Fortune Device (10 SP+): +15% luck in rolls
- Mastery Device (5 SPx): Properties reveal 30% faster
- Infinity Device (5 SP^): See all target properties

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
- Infinity Device (most powerful) requires 50 SP
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
- MIT License
- Repository secured with proper .gitignore
