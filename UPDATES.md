# Questionmark Game - Changelog

## Version 1.1 - Security & Features Update (March 31, 2026)

### 🔒 Security Fixes
- Removed all user data files from GitHub repository
- Updated .gitignore to prevent future data exposure
- Repository now contains only safe, public files

### 🛠️ Developer Console
- **Restricted Access**: Only authorized users can access
- **Admin Management**: "DeMarcusThe2nd" manages permissions via Settings
- **Commands Available**: set_sp, add_wins, reset_stats, unlock_all_achievements, give_equipment, export_data, etc.

### 💰 Enhanced SP System
- **5x More Rewards**: SP amounts increased across all lengths
- **New Amounts**: 4-7 chars = 5 SP, 8-14 = 10 SP+, 15-24 = 15 SPx, 25+ = 20 SP^
- **Consistent**: Manual and auto-roll now give same SP

### ⚙️ Balanced Equipment Costs
- **Updated Prices**: Costs scaled to match new SP economy
- **Range**: 10-50 SP (was 5-70 SP)
- **Premium Currency**: Higher tiers require SP+, SPx, SP^

### 🎯 Daily Challenges (8 total)
- Quick Thinker (3 wins) → +5 SP
- Accuracy Master (5 wins) → +8 SP
- SP+ Collector (3 earned) → +10 SP
- SPx Collector (2 earned) → +15 SP
- SP^ Collector (1 earned) → +25 SP
- Grinding Session (50 rolls) → +12 SP
- Perfect Series (3 in row) → +20 SP
- Long String Master (25+ chars) → +18 SP

---

## Version 1.0 - Initial Release

### 🎮 Core Features
- **SP System**: Earn points for winning sequences (length-based rewards)
- **Equipment Crafting**: 10 items (5 gauntlets, 5 devices) with passive effects
- **Difficulty Levels**: Easy/Normal/Hard with different property requirements
- **Auto-Roll**: Configurable speed (1-50 rolls/second)
- **Mini-Game**: Time-based challenge mode
- **Statistics**: Comprehensive tracking with leaderboard
- **Achievements**: Persistent unlock system

### 🧤 Equipment (10 total)
**Gauntlets**: Iron (15 SP), Steel (5 SP+), Silver (5 SPx), Gold (10 SPx), Obsidian (5 SP^)
**Devices**: Basic (10 SP), Analysis (5 SP+), Fortune (10 SP+), Mastery (5 SPx), Infinity (5 SP^)

### 🎨 UI/UX
- Tabbed equipment interface (Craft/Inventory/Equip)
- Sound effects & visual themes (Dark/Light/Neon)
- Tutorial system for new players
- Persistent save system

### 📊 Technical
- Windows compatible, no external dependencies
- MIT License
- ~500+ lines added for equipment system
- Secure user data isolation

## Quick Start
1. **Play**: Generate strings, match all target properties
2. **Earn SP**: Win sequences to get currency
3. **Craft Equipment**: Buy items in Tools → Equipment Crafting
4. **Equip Items**: Use passive effects to improve gameplay
5. **Complete Challenges**: Daily bonuses for various achievements

## System Requirements
- Python 3.x
- Windows OS
- tkinter (built-in)
- Optional: matplotlib for charts
