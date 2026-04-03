# 📋 Update Log

---

## 🚀 Version 2.0 — April 3, 2026

### 🎨 Complete UI Revamp
- **Overhauled every single window** in the game with a brand-new dark modern theme
- Introduced the `_init_ui_style` system — a centralized `self._ui` dictionary powering all colors, fonts, and styles across the entire app
- New color palette: deep navy backgrounds (`#0f0f1a`, `#161625`, `#1c1c35`), vibrant accent purple (`#7c4dff`), neon green success (`#00e676`), gold highlights (`#ffd740`), and more
- Built **6 new reusable UI helper methods**:
  - `_styled_toplevel` — consistent styled popup windows
  - `_styled_header` — section headers with icon + subtitle support
  - `_styled_card` — card-style containers with rounded-look borders
  - `_styled_button` — buttons with smooth hover color transitions
  - `_styled_scrollable` — scrollable content areas with themed scrollbars
  - `_lighten_color` — dynamic color lightening for hover effects
- All **20+ sub-windows** converted: Leaderboard, Equipment, Shop, Achievements, Stats, History, Settings, Progression, Tournaments, and more
- All popups, overlays, and in-game notifications updated to match the new theme

### 🧭 Navigation Ribbon
- **Replaced the old 3 dropdown menus** (Game/View/Tools) with a full-width navigation ribbon
- Icon-based buttons organized into **4 logical groups**:
  - **Info** — Leaderboard, Achievements, Stats
  - **Progression** — Progression, Equipment, Shop
  - **Activities** — Tournaments, PvP Arena
  - **System** — History, Settings, Save, Quit
- Smooth hover effects and vertical separators between groups
- Much more accessible and visually appealing than the old cramped menus

### ⚔️ PvP Arena System (~710 lines of new code)
- **Full competitive PvP mode** with ELO-based matchmaking
- **5 unique AI opponents** with distinct personalities and ELO ratings:
  - Shadow Roller, Lucky Larry, The Analyst, Speed Demon, Grand Master
- **Draft & Ban Phase** — strategically ban properties before each duel to reduce pure RNG
- **Best-of-5 Duel Engine** — tactical round-by-round matches
- **5 Tactical Abilities** with cooldowns:
  - Reroll, Property Reveal, Time Freeze, Double Down, Shield
- **ELO Ranking System** with 8 tiers: Bronze → Silver → Gold → Platinum → Diamond → Master → Grandmaster → Legend
- **4-tab PvP window**: Fight, Abilities, Match History, Rankings
- **Full JSON persistence** — PvP data saves/loads per user
- Rewards: SP, XP, and ELO gains/losses after each duel

### 🐛 Bug Fixes
- **Fixed `_styled_header` TypeError** — all 16 call sites were passing the icon argument incorrectly (positional instead of keyword), causing "got multiple values for argument 'subtitle'" errors
- **Fixed Leaderboard showing blank/empty** — the outer frame from `_styled_scrollable` wasn't being `.pack()`ed, so content was invisible
- **Fixed Equipment & Shop windows crashing** — `_styled_card` returns a tuple `(outer, card)` but some calls assigned it to a single variable instead of unpacking
- **Fixed buttons jumping/shifting** when roll properties changed — added fixed `height` to roll result and properties labels, pinned button area to `side=tk.BOTTOM`

### ⚡ Performance Optimization
- **Fixed severe lag when spamming spacebar to roll:**
  - **Non-blocking sound**: `winsound.Beep()` was **blocking the entire GUI thread** for 100ms+ per roll (650ms+ on wins). Now runs in a **background thread** so the UI stays responsive
  - **Roll debounce**: Added a 50ms cooldown — rapid-fire spacebar presses no longer queue up dozens of expensive rolls
  - **Achievement check throttle**: `_check_achievements()` (20+ condition checks + `datetime.now()`) now only runs every **5th roll** instead of every single roll
  - **Celebration animation fix**: Reduced from 10 flashes → 4 flashes, and animations now **cancel any running instance** before starting a new one to prevent stacking

### 🎃 April Fools
- April Fools mode toggled on/off during development; now properly uses date-based detection (activates only on April 1st)

---

*Previous versions did not have an update log.*
