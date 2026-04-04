import random
import string
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import threading
import winsound
import json
import os
import datetime
import hashlib
from datetime import timedelta

# Optional imports
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Background music support
try:
    import vlc  # type: ignore
    VLC_AVAILABLE = True
except (ImportError, Exception):
    VLC_AVAILABLE = False

class AccountManager:
    """Handles user account management"""
    def __init__(self):
        self.accounts_file = "accounts.json"
        self.current_user = None
        self.accounts = self._load_accounts()
    
    def _load_json(self, filename, default=None):
        """Generic JSON loader"""
        if not os.path.exists(filename):
            return default if default is not None else {}
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default if default is not None else {}
    
    def _save_json(self, filename, data):
        """Generic JSON saver"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def _load_accounts(self):
        """Load all accounts from file"""
        return self._load_json(self.accounts_file, {})
    
    def _save_accounts(self):
        """Save all accounts to file"""
        self._save_json(self.accounts_file, self.accounts)
    
    def _hash_password(self, password):
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password):
        """Register a new account"""
        if username in self.accounts:
            return False, "Username already exists"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(password) < 4:
            return False, "Password must be at least 4 characters"
        
        self.accounts[username] = {
            "password_hash": self._hash_password(password),
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_played": None,
            "play_time": 0,
            "title": "Novice"
        }
        self._save_accounts()
        return True, "Account created successfully"
    
    def login(self, username, password):
        """Login to an account"""
        if username not in self.accounts:
            return False, "Account not found"
        
        account = self.accounts[username]
        if account["password_hash"] != self._hash_password(password):
            return False, "Incorrect password"
        
        self.current_user = username
        account["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_accounts()
        return True, "Login successful"
    
    def get_user_data_file(self, username):
        """Get the data file path for a user"""
        return f"user_{username}_data.json"
    
    def get_user_stats_file(self, username):
        """Get the stats file path for a user"""
        return f"user_{username}_stats.json"
    
    def get_user_achievements_file(self, username):
        """Get achievements file path for a user"""
        return f"user_{username}_achievements.json"
    
    def get_user_equipment_file(self, username):
        """Get equipment file path for a user"""
        return f"user_{username}_equipment.json"
    
    def get_user_history_file(self, username):
        """Get history file path for a user"""
        return f"user_{username}_history.json"
    
    def get_user_crafting_file(self, username):
        """Get crafting data file path for a user"""
        return f"user_{username}_crafting.json"
    
    def get_user_pokedex_file(self, username):
        """Get Pokédex data file path for a user"""
        return f"user_{username}_pokedex.json"
    
    def save_remembered_account(self, username, password=None):
        """Save account for auto-login (expires in 30 days)"""
        remembered_file = "remembered_accounts.json"
        expiration = datetime.datetime.now() + timedelta(days=30)
        
        try:
            # Load existing remembered accounts
            if os.path.exists(remembered_file):
                with open(remembered_file, 'r') as f:
                    remembered = json.load(f)
            else:
                remembered = {}
            
            # Get password hash - either from provided password or from account
            if password:
                password_hash = self._hash_password(password)
            else:
                # Get from current account
                if username in self.accounts:
                    password_hash = self.accounts[username]["password_hash"]
                else:
                    return
            
            # Add/update this account
            remembered[username] = {
                "password_hash": password_hash,
                "expires": expiration.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save using helper
            self._save_json(remembered_file, remembered)
        except Exception as e:
            pass
    
    def get_remembered_accounts(self):
        """Get list of non-expired remembered accounts"""
        remembered_file = "remembered_accounts.json"
        remembered = self._load_json(remembered_file, {})
        
        # Filter out expired accounts
        now = datetime.datetime.now()
        valid_accounts = {}
        for username, data in remembered.items():
            expires = datetime.datetime.strptime(data["expires"], "%Y-%m-%d %H:%M:%S")
            if now < expires:
                valid_accounts[username] = data
        
        # Save cleaned list if changed
        if valid_accounts != remembered:
            self._save_json(remembered_file, valid_accounts)
        
        return valid_accounts
    
    def auto_login(self, username):
        """Attempt auto-login with remembered account"""
        remembered = self.get_remembered_accounts()
        if username in remembered:
            # Check if account still exists
            if username in self.accounts:
                account = self.accounts[username]
                stored_hash = remembered[username]["password_hash"]
                # Automatically log in without checking password
                self.current_user = username
                account["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_accounts()
                return True, "Auto-login successful"
        return False, "Auto-login failed"
    
    def forget_remembered_account(self, username):
        """Remove account from remembered list"""
        remembered_file = "remembered_accounts.json"
        if not os.path.exists(remembered_file):
            return
        
        try:
            with open(remembered_file, 'r') as f:
                remembered = json.load(f)
            
            if username in remembered:
                del remembered[username]
                with open(remembered_file, 'w') as f:
                    json.dump(remembered, f, indent=2)
        except Exception as e:
            pass
    
    def get_dev_console_access(self):
        """Get list of users with dev console access"""
        return self._load_json("dev_console_access.json", [])
    
    def save_dev_console_access(self, allowed_users):
        """Save list of users with dev console access"""
        dev_access_file = "dev_console_access.json"
        with open(dev_access_file, 'w') as f:
            json.dump(allowed_users, f, indent=2)
    
    def add_dev_console_access(self, username):
        """Add user to dev console access list"""
        allowed = self.get_dev_console_access()
        if username not in allowed:
            allowed.append(username)
            self.save_dev_console_access(allowed)
            return True
        return False
    
    def remove_dev_console_access(self, username):
        """Remove user from dev console access list"""
        allowed = self.get_dev_console_access()
        if username in allowed:
            allowed.remove(username)
            self.save_dev_console_access(allowed)
            return True
        return False
    
    def has_dev_console_access(self, username):
        """Check if user has dev console access"""
        # DeMarcusThe2nd always has access
        if username == "DeMarcusThe2nd":
            return True
        allowed = self.get_dev_console_access()
        return username in allowed


class RollingGame:
    def __init__(self, username=None):
        # Account system
        self.account_manager = AccountManager()
        self.current_username = username
        
        # Basic game variables
        self.roll_count = 0
        self.rolls_history = []
        self.target_properties = set()
        self.game_won = False
        self.auto_rolling = False
        self.auto_roll_speed = 10  # Rolls per second (1-50)
        self.wins_count = 0
        self.current_theme = "dark"
        self.sound_enabled = True
        self.animations_enabled = True
        self.background_music_enabled = True
        self.show_stats_on_win = True
        self.auto_save_enabled = True
        
        # NEW GAME SYSTEMS FOR ENGAGEMENT
        # Level and XP System
        self.player_level = 1
        self.player_xp = 0
        self.xp_to_level_up = 100
        
        # Rank titles based on level
        self.rank_titles = {
            1: "Novice", 5: "Apprentice", 10: "Adept", 15: "Expert", 20: "Master",
            25: "Grand Master", 30: "Legendary", 40: "Mythic", 50: "Omniscient"
        }
        
        # Skill Tree System
        self.skills = self._init_skill_tree()
        
        # Meta-progression (carries over across sessions)
        self.meta_progression = self._load_meta_progression()
        
        # Daily streaks and engagement hooks
        self.winning_streak = 0
        self.max_winning_streak = 0
        self.session_win_count = 0
        self.total_sp_earned_today = 0
        
        # Load settings from file
        self._load_settings()
        
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        # Load persistent counters from stats
        self.roll_count = self.stats.get("total_rolls", 0)
        self.wins_count = self.stats.get("total_wins", 0)
        self.rolls_history = []  # Initialize empty, will be loaded below
        self.mini_game_best = 0  # Best mini-game score
        
        # Load roll history
        self.rolls_history = self._load_history()
        
        # Daily Challenge System
        self.daily_challenges = self._init_daily_challenges()
        self.challenge_progress = self._load_challenge_progress()
        
        # SP and Equipment System
        self.sp = 0  # Regular SP (5 characters)
        self.sp_plus = 0  # SP+ (10 characters)
        self.sp_x = 0  # SPx (20 characters)
        self.sp_caret = 0  # SP^ (40+ characters)
        self.equipped_gauntlet = None  # Left hand
        self.equipped_device = None  # Right hand
        self.equipment_inventory = self._load_equipment()
        self._init_equipment_recipes()
        
        # Shop/Marketplace System
        self.shop_inventory = []
        self._load_shop_inventory()
        
        # Background music system
        self.music_thread = None
        self.music_playing = False
        self.background_music_file = "Ambatukam Termuwani.mp3"
        
        # April Fools Mode (April 1st only)
        import datetime
        self.is_april_fools = datetime.datetime.now().month == 4 and datetime.datetime.now().day == 1
        
        # Custom Game Modes
        self.current_game_mode = "Classic"
        self.mode_stats = {}
        self._init_game_modes()
        
        # Tournament System
        self.tournament_data = {}
        self._load_tournaments()
        
        # Strategy System
        self._init_strategy_system()
        
        # Engagement System
        self._init_engagement_system()
        
        # Progression System
        self._init_progression_system()
        
        # Easter egg tracking
        self.konami_code_buffer = []
        self.konami_mode_enabled = False
        
        # Daily bonus system
        self.last_login_date = None
        self.daily_bonus_claimed = False
        self._check_daily_bonus()
        
        # Cosmetics system
        self.player_title = "Player"
        self.player_color = "#ffffff"
        
        # Temporary effect variables
        self.temp_luck_boost = 0
        self.temp_xp_boost = 0
        self.temp_effects_timer = 0
        self.temp_sp_multiplier = 0
        self.temp_xp_multiplier = 0
        self.temp_concentration_bonus = 0
        self.temp_precision_bonus = 0
        self.streak_protection_active = False
        self.reward_multiplier_active = 1.0
        self.reroll_charges = 0
        self.property_scanner_active = False
        self.auto_invest_enabled = False
        self.critical_roll_chance = 0.0
        self.seen_tutorials = set()
        
        # ── PvP Arena System ─────────────────────────────────────────────
        self._init_pvp_system()
        
        # ── Crafting Overhaul System ─────────────────────────────────────
        self._init_crafting_system()
        
        # ── Clans/Guilds System ──────────────────────────────────────────
        self._init_clan_system()
        
        # ── String Pokédex System ────────────────────────────────────────
        self._init_pokedex_system()
        
        # Difficulty setting
        self.difficulty = "normal"
        
        # Initialize game
        self._generate_target()
        self.possible_properties = [
            "has_numbers", "has_symbols", "has_uppercase", "has_lowercase", "is_long",
            "has_spaces", "has_operators", "has_multiple_words", "has_repeats",
            "starts_with_letter", "ends_with_symbol", "has_punctuation", "has_vowels",
            "is_very_long", "has_consecutive_letters"
        ]
        
        # Check for remembered account BEFORE creating any windows
        remembered = self.account_manager.get_remembered_accounts()
        if remembered and self.current_username is None:
            for username in remembered:
                if self.account_manager.auto_login(username):
                    self.current_username = username
                    break
        
        # If no user, show login screen FIRST (as standalone window)
        if self.current_username is None:
            self.show_login_screen_standalone()
        else:
            # User exists (auto-login), create game window and start
            self._create_game_window()
            self._complete_startup()
    
    
    def _init_equipment_recipes(self):
        """Initialize equipment crafting recipes"""
        self.equipment_recipes = {
            # April Fools special items
            "rubber_chicken": {"type": "gauntlet", "cost": {"sp": 0}, "effect": "honk", "desc": "🐔 HONK HONK (Free April Fools)"},
            "magic_8_ball": {"type": "device", "cost": {"sp": 0}, "effect": "???", "desc": "🎱 Outlook hazy (Free April Fools)"},
            # Special items
            "thors_hammer": {"type": "gauntlet", "cost": {"sp": 0}, "effect": "auto_roll_67", "desc": "⚡ Thor's Hammer (Free - Auto rolls)"},
            "infinity_gauntlet": {"type": "gauntlet", "cost": {"sp": 0}, "effect": "infinity", "desc": "💎 Infinity Gauntlet (Free - Doubles SP)"},
            "67_gauntlet": {"type": "gauntlet", "cost": {"sp": 67}, "effect": "lucky_67", "desc": "67️⃣ The Number 67"},
            "67_division": {"type": "device", "cost": {"sp": 0}, "effect": "math", "desc": "➗ 67/67 (Free)"},
            "sqrt_squared": {"type": "device", "cost": {"sp": 0}, "effect": "math", "desc": "🔢 (√3)² (Free)"},
            "67_plus_71": {"type": "gauntlet", "cost": {"sp": 138}, "effect": "math", "desc": "➕ 67+71=138"},
            "67_minus_65": {"type": "device", "cost": {"sp": 2}, "effect": "math", "desc": "➖ 67-65=2"},
            "iron_gauntlet": {"type": "gauntlet", "cost": {"sp": 15}, "effect": "roll_count - 1", "desc": "Reduce rolls by 1"},
            "steel_gauntlet": {"type": "gauntlet", "cost": {"sp_plus": 5}, "effect": "win_bonus + 3", "desc": "Gain 3 bonus rolls"},
            "silver_gauntlet": {"type": "gauntlet", "cost": {"sp_x": 5}, "effect": "accuracy + 10%", "desc": "+10% property accuracy"},
            "gold_gauntlet": {"type": "gauntlet", "cost": {"sp_x": 10}, "effect": "sp_gain + 25%", "desc": "+25% SP gained"},
            "obsidian_gauntlet": {"type": "gauntlet", "cost": {"sp_caret": 5}, "effect": "double_sp", "desc": "Double all SP earned"},
            "basic_device": {"type": "device", "cost": {"sp": 10}, "effect": "reroll_free", "desc": "1 free reroll per win"},
            "analysis_device": {"type": "device", "cost": {"sp_plus": 5}, "effect": "see_extra_prop", "desc": "See 1 extra property"},
            "fortune_device": {"type": "device", "cost": {"sp_plus": 10}, "effect": "luck_boost", "desc": "+15% luck in rolls"},
            "mastery_device": {"type": "device", "cost": {"sp_x": 5}, "effect": "fast_analysis", "desc": "Properties reveal 30% faster"},
            "infinity_device": {"type": "device", "cost": {"sp_caret": 5}, "effect": "perfect_vision", "desc": "See all target properties"}
        }
    
    # ===== GENERIC JSON HELPERS =====
    def _load_json(self, filename, default=None):
        """Generic JSON loader with error handling"""
        if not os.path.exists(filename):
            return default if default is not None else {}
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return default if default is not None else {}
    
    def _save_json(self, filename, data):
        """Generic JSON saver with error handling"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            return False
    
    def _play_sound(self, beeps):
        """Generic sound player - beeps is list of (frequency, duration, delay) tuples.
        Runs in a background thread so the GUI never freezes."""
        if not self.sound_enabled:
            return
        import threading
        def _worker():
            try:
                for freq, duration, *delay in beeps:
                    winsound.Beep(freq, duration)
                    if delay:
                        time.sleep(delay[0])
            except Exception:
                pass
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
    
    def _check_and_unlock_achievement(self, achievement_id, condition, display_name):
        """Check and unlock an achievement; records timestamp and awards SP reward."""
        ach = self.achievements.get(achievement_id)
        if ach and condition and not ach.get("unlocked", False):
            ach["unlocked"] = True
            ach["unlock_time"] = datetime.datetime.now().isoformat()
            reward = ach.get("reward", 0)
            if reward:
                self.sp += reward
                try:
                    self._update_sp_label()
                except Exception:
                    pass
            return display_name
        return None
    
    def _load_settings(self):
        """Load game settings from file"""
        settings = self._load_json("game_settings.json", {})
        self.sound_enabled = settings.get("sound_enabled", True)
        self.animations_enabled = settings.get("animations_enabled", True)
        self.background_music_enabled = settings.get("background_music_enabled", True)
        self.show_stats_on_win = settings.get("show_stats_on_win", True)
        self.auto_save_enabled = settings.get("auto_save_enabled", True)
        self.current_theme = settings.get("current_theme", "dark")
    
    def _save_settings(self):
        """Save game settings to file"""
        settings = {
            "sound_enabled": self.sound_enabled,
            "animations_enabled": self.animations_enabled,
            "background_music_enabled": self.background_music_enabled,
            "show_stats_on_win": self.show_stats_on_win,
            "auto_save_enabled": self.auto_save_enabled,
            "current_theme": self.current_theme
        }
        self._save_json("game_settings.json", settings)
    
    def _init_skill_tree(self):
        """Initialize skill tree with learnable skills"""
        return {
            "sp_mastery_1": {"name": "SP Mastery I", "cost": 50, "desc": "+10% SP gain", "learned": False, "effect": 0.1},
            "sp_mastery_2": {"name": "SP Mastery II", "cost": 100, "desc": "+15% SP gain", "learned": False, "effect": 0.15},
            "fortune": {"name": "Fortune", "cost": 75, "desc": "+5% win chance", "learned": False, "effect": 0.05},
            "quick_learner": {"name": "Quick Learner", "cost": 60, "desc": "+20% XP gain", "learned": False, "effect": 0.2},
            "lucky_break": {"name": "Lucky Break", "cost": 150, "desc": "5% chance to skip rolls", "learned": False, "effect": 0.05},
            "perseverance": {"name": "Perseverance", "cost": 100, "desc": "+25% streak bonuses", "learned": False, "effect": 0.25},
        }
    
    def _load_meta_progression(self):
        """Load meta progression data (carries across sessions)"""
        if not self.current_username:
            return {}
        meta_file = f"user_{self.current_username}_meta.json"
        return self._load_json(meta_file, {
            "total_wins_all_time": 0,
            "total_sp_earned_all_time": 0,
            "level": 1,
            "xp": 0
        })
    
    def _save_meta_progression(self):
        """Save meta progression data"""
        if not self.current_username:
            return
        meta_file = f"user_{self.current_username}_meta.json"
        meta_data = {
            "total_wins_all_time": self.meta_progression.get("total_wins_all_time", 0) + self.session_win_count,
            "total_sp_earned_all_time": self.meta_progression.get("total_sp_earned_all_time", 0) + self.total_sp_earned_today,
            "level": self.player_level,
            "xp": self.player_xp
        }
        self._save_json(meta_file, meta_data)
    
    def _add_xp(self, amount):
        """Add XP and handle leveling"""
        xp_boost = 1.0 + (self.meta_progression.get("level", 1) * 0.02)  # Skill tree bonus
        total_xp = int(amount * xp_boost)
        self.player_xp += total_xp
        
        # Check for level ups
        while self.player_xp >= self.xp_to_level_up:
            self.player_xp -= self.xp_to_level_up
            self._level_up()
        
        # Always refresh the unlock progress bar after XP changes
        try:
            self._update_unlock_progress_bar()
        except Exception:
            pass
    
    def _level_up(self):
        """Handle level up with gradual mechanic introductions"""
        self.player_level += 1
        self.xp_to_level_up = int(100 * (1.1 ** self.player_level))  # Exponential scaling
        self._play_achievement_sound()
        
        # Check for new mechanic unlocks at this level
        self._check_mechanic_unlocks()
        
        # Apply per-level passive upgrades that change gameplay
        self._apply_level_milestone_rewards()
        
        # Update the unlock progress bar if it exists
        if hasattr(self, 'unlock_progress_label'):
            self._update_unlock_progress_bar()
        
        return f"LEVEL UP: {self.player_level}!"
    
    def _update_winning_streak(self, won):
        """Track winning streaks for multiplier"""
        if won:
            self.winning_streak += 1
            self.session_win_count += 1
            self.max_winning_streak = max(self.max_winning_streak, self.winning_streak)
        else:
            self.winning_streak = 0
    
    def _get_streak_multiplier(self):
        """Get SP multiplier based on streak"""
        base = 1.0
        if self.winning_streak >= 3:
            base += 0.1
        if self.winning_streak >= 5:
            base += 0.15
        if self.winning_streak >= 10:
            base += 0.25
        return base
    
    def _apply_skill_bonuses(self, sp_earned):
        """Apply bonuses from learned skills"""
        bonus_sp = sp_earned
        
        # SP Mastery skills
        if self.skills["sp_mastery_1"]["learned"]:
            bonus_sp += sp_earned * 0.10
        if self.skills["sp_mastery_2"]["learned"]:
            bonus_sp += sp_earned * 0.15
        
        return int(bonus_sp)
    
    def _update_label(self, label, text, fg=None, font=None):
        """Helper to update label with text, color, and font"""
        config = {"text": text}
        if fg:
            config["fg"] = fg
        if font:
            config["font"] = font
        label.config(**config)
    
    def _update_temp_effect(self, attr_name, timer_name='temp_effects_timer'):
        """Helper to decrement and clear temporary effects"""
        if hasattr(self, attr_name) and getattr(self, attr_name) > 0:
            setattr(self, timer_name, getattr(self, timer_name) - 1)
            if getattr(self, timer_name) <= 0:
                setattr(self, attr_name, 0)
    
    def _init_daily_challenges(self):
        """Initialize daily challenges system"""
        return {
            "challenge_1": {"name": "Quick Thinker", "desc": "Win 3 sequences", "target": 3, "reward_sp": 5, "icon": "⚡"},
            "challenge_2": {"name": "Accuracy Master", "desc": "Win 5 sequences", "target": 5, "reward_sp": 8, "icon": "●"},
            "challenge_3": {"name": "SP+ Collector", "desc": "Earn 3 SP+", "target": 3, "reward_sp": 10, "icon": "⬆"},
            "challenge_4": {"name": "SPx Collector", "desc": "Earn 2 SPx", "target": 2, "reward_sp": 15, "icon": "■"},
            "challenge_5": {"name": "SP^ Collector", "desc": "Earn 1 SP^", "target": 1, "reward_sp": 25, "icon": "▲"},
            "challenge_6": {"name": "Grinding Session", "desc": "Roll 50 times", "target": 50, "reward_sp": 12, "icon": "🔄"},
            "challenge_7": {"name": "Perfect Series", "desc": "Win 3 in a row", "target": 3, "reward_sp": 20, "icon": "🔥"},
            "challenge_8": {"name": "Long String Master", "desc": "Win with 25+ char string", "target": 1, "reward_sp": 18, "icon": "📝"}
        }
    
    def _load_challenge_progress(self):
        """Load daily challenge progress"""
        if not self.current_username:
            return {}
        challenge_file = self.account_manager.get_user_data_file(self.current_username)
        data = self._load_json(challenge_file, {})
        return data.get("challenges", {})
    
    def _save_challenge_progress(self):
        """Save daily challenge progress"""
        if not self.current_username:
            return
        challenge_file = self.account_manager.get_user_data_file(self.current_username)
        challenge_data = {"challenges": self.challenge_progress}
        self._save_json(challenge_file, challenge_data)
    
    def _update_challenges(self, sp_type, string_length):
        """Update daily challenge progress and return rewards"""
        rewards = []
        
        # Challenge 1: Win sequences (Quick Thinker - 3 wins)
        self.challenge_progress["challenge_1"] = self.challenge_progress.get("challenge_1", 0) + 1
        if self.challenge_progress["challenge_1"] == 3 and not hasattr(self, '_challenge_1_completed'):
            self._challenge_1_completed = True
            self.sp += 5  # Award 5 SP
            rewards.append("Quick Thinker: +5 SP")
        
        # Challenge 2: Win sequences (Accuracy Master - 5 wins)
        self.challenge_progress["challenge_2"] = self.challenge_progress.get("challenge_2", 0) + 1
        if self.challenge_progress["challenge_2"] == 5 and not hasattr(self, '_challenge_2_completed'):
            self._challenge_2_completed = True
            self.sp += 8  # Award 8 SP
            rewards.append("Accuracy Master: +8 SP")
        
        # Challenge 3-5: SP type collectors
        if sp_type == "sp_plus":
            self.challenge_progress["challenge_3"] = self.challenge_progress.get("challenge_3", 0) + 1
            if self.challenge_progress["challenge_3"] == 3 and not hasattr(self, '_challenge_3_completed'):
                self._challenge_3_completed = True
                self.sp += 10  # Award 10 SP
                rewards.append("SP+ Collector: +10 SP")
        elif sp_type == "sp_x":
            self.challenge_progress["challenge_4"] = self.challenge_progress.get("challenge_4", 0) + 1
            if self.challenge_progress["challenge_4"] == 2 and not hasattr(self, '_challenge_4_completed'):
                self._challenge_4_completed = True
                self.sp += 15  # Award 15 SP
                rewards.append("SPx Collector: +15 SP")
        elif sp_type == "sp_caret":
            self.challenge_progress["challenge_5"] = self.challenge_progress.get("challenge_5", 0) + 1
            if self.challenge_progress["challenge_5"] == 1 and not hasattr(self, '_challenge_5_completed'):
                self._challenge_5_completed = True
                self.sp += 25  # Award 25 SP
                rewards.append("SP^ Collector: +25 SP")
        
        # Challenge 6: Rolling
        self.challenge_progress["challenge_6"] = self.challenge_progress.get("challenge_6", 0) + 1
        if self.challenge_progress["challenge_6"] == 50 and not hasattr(self, '_challenge_6_completed'):
            self._challenge_6_completed = True
            self.sp += 12  # Award 12 SP
            rewards.append("Grinding Session: +12 SP")
        
        # Challenge 7: Perfect Series (3 wins in a row)
        if self.stats.get('current_streak', 0) >= 3 and not hasattr(self, '_challenge_7_completed'):
            self._challenge_7_completed = True
            self.sp += 20  # Award 20 SP
            rewards.append("Perfect Series: +20 SP")
        
        # Update SP label if rewards were given
        if rewards:
            self._update_sp_label()
        
        return "\n".join(rewards) if rewards else ""
    
    def _get_player_title(self):
        """Get player title based on achievements"""
        if self.wins_count >= 100:
            return "Legend"
        elif self.wins_count >= 50:
            return "Master"
        elif self.wins_count >= 25:
            return "Expert"
        elif self.wins_count >= 10:
            return "Veteran"
        elif self.wins_count >= 5:
            return "Adept"
        return "Novice"
    
    def _load_equipment(self):
        """Load equipment inventory from file (per-user)"""
        eq_file = self.account_manager.get_user_equipment_file(self.current_username) if self.current_username else "equipment.json"
        default = {"sp": 0, "sp_plus": 0, "sp_x": 0, "sp_caret": 0, "owned": [], "equipped": {"gauntlet": None, "device": None}}
        data = self._load_json(eq_file, default)
        # Extract and set instance variables
        self.sp = data.get("sp", 0)
        self.sp_plus = data.get("sp_plus", 0)
        self.sp_x = data.get("sp_x", 0)
        self.sp_caret = data.get("sp_caret", 0)
        self.equipped_gauntlet = data.get("equipped", {}).get("gauntlet")
        self.equipped_device = data.get("equipped", {}).get("device")
        return data
    
    def _save_equipment(self):
        """Save equipment inventory to file (per-user)"""
        eq_file = self.account_manager.get_user_equipment_file(self.current_username) if self.current_username else "equipment.json"
        eq_data = {
            "sp": self.sp,
            "sp_plus": self.sp_plus,
            "sp_x": self.sp_x,
            "sp_caret": self.sp_caret,
            "owned": list(set(self.equipment_inventory.get("owned", []))),
            "equipped": {"gauntlet": self.equipped_gauntlet, "device": self.equipped_device}
        }
        self._save_json(eq_file, eq_data)
    
    # ===== CRAFTING OVERHAUL SYSTEM =====
    
    def _init_crafting_system(self):
        """Initialize the advanced crafting system with property-combo recipes"""
        craft_file = self.account_manager.get_user_crafting_file(self.current_username) if self.current_username else "crafting.json"
        saved = self._load_json(craft_file, {})
        
        self.discovered_combos = set()
        for combo in saved.get("discovered_combos", []):
            self.discovered_combos.add(frozenset(combo))
        self.crafted_items = saved.get("crafted_items", [])
        self.crafting_xp = saved.get("crafting_xp", 0)
        self.crafting_level = saved.get("crafting_level", 1)
        
        # Property-combo crafting recipes
        self.crafting_recipes = {
            # ── Tier 1: 2-property combos (Common) ──
            "ember_gauntlet": {
                "name": "🔥 Ember Gauntlet", "tier": 1, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_uppercase"]),
                "cost": {"sp": 25}, "crafting_level": 1,
                "effect": {"sp_bonus": 0.10},
                "desc": "+10% SP gain from wins",
            },
            "frost_lens": {
                "name": "❄️ Frost Lens", "tier": 1, "type": "device",
                "combo": frozenset(["has_lowercase", "has_vowels"]),
                "cost": {"sp": 25}, "crafting_level": 1,
                "effect": {"xp_bonus": 0.10},
                "desc": "+10% XP gain from wins",
            },
            "iron_bracer": {
                "name": "🛡️ Iron Bracer", "tier": 1, "type": "gauntlet",
                "combo": frozenset(["has_symbols", "has_punctuation"]),
                "cost": {"sp": 30}, "crafting_level": 1,
                "effect": {"streak_shield": 0.15},
                "desc": "15% chance to protect win streak",
            },
            "scout_monocle": {
                "name": "🔍 Scout Monocle", "tier": 1, "type": "device",
                "combo": frozenset(["starts_with_letter", "ends_with_symbol"]),
                "cost": {"sp": 30}, "crafting_level": 1,
                "effect": {"reveal_property": 1},
                "desc": "Reveals 1 extra target property hint",
            },
            "swift_gloves": {
                "name": "⚡ Swift Gloves", "tier": 1, "type": "gauntlet",
                "combo": frozenset(["is_long", "has_spaces"]),
                "cost": {"sp": 20}, "crafting_level": 1,
                "effect": {"roll_speed": 0.10},
                "desc": "+10% auto-roll speed",
            },
            # ── Tier 2: 3-property combos (Uncommon) ──
            "storm_caller": {
                "name": "⛈️ Storm Caller", "tier": 2, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_uppercase", "has_symbols"]),
                "cost": {"sp": 50, "sp_plus": 3}, "crafting_level": 3,
                "effect": {"sp_bonus": 0.20, "critical_chance": 0.02},
                "desc": "+20% SP, +2% critical roll chance",
            },
            "crystal_scanner": {
                "name": "🔮 Crystal Scanner", "tier": 2, "type": "device",
                "combo": frozenset(["has_vowels", "has_consecutive_letters", "starts_with_letter"]),
                "cost": {"sp": 50, "sp_plus": 3}, "crafting_level": 3,
                "effect": {"reveal_property": 2, "xp_bonus": 0.10},
                "desc": "Reveals 2 extra properties, +10% XP",
            },
            "void_wrap": {
                "name": "🌑 Void Wrap", "tier": 2, "type": "gauntlet",
                "combo": frozenset(["has_repeats", "has_operators", "has_numbers"]),
                "cost": {"sp": 60, "sp_plus": 5}, "crafting_level": 4,
                "effect": {"sp_bonus": 0.15, "streak_shield": 0.25},
                "desc": "+15% SP, 25% streak protection",
            },
            "oracle_device": {
                "name": "🌟 Oracle Device", "tier": 2, "type": "device",
                "combo": frozenset(["has_multiple_words", "has_spaces", "is_long"]),
                "cost": {"sp": 55, "sp_plus": 4}, "crafting_level": 3,
                "effect": {"xp_bonus": 0.25, "luck": 0.05},
                "desc": "+25% XP, +5% luck boost",
            },
            "thunder_fist": {
                "name": "🥊 Thunder Fist", "tier": 2, "type": "gauntlet",
                "combo": frozenset(["has_uppercase", "has_lowercase", "has_punctuation"]),
                "cost": {"sp": 45, "sp_plus": 3}, "crafting_level": 3,
                "effect": {"sp_bonus": 0.18, "reroll_gen": 0.05},
                "desc": "+18% SP, 5% chance for free reroll",
            },
            # ── Tier 3: 4-property combos (Rare) ──
            "dragon_claw": {
                "name": "🐉 Dragon Claw", "tier": 3, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_symbols", "has_uppercase", "is_long"]),
                "cost": {"sp": 100, "sp_plus": 10, "sp_x": 3}, "crafting_level": 6,
                "effect": {"sp_bonus": 0.35, "critical_chance": 0.05},
                "desc": "+35% SP, +5% critical chance",
            },
            "astral_projector": {
                "name": "🌌 Astral Projector", "tier": 3, "type": "device",
                "combo": frozenset(["has_vowels", "has_consecutive_letters", "has_lowercase", "starts_with_letter"]),
                "cost": {"sp": 100, "sp_plus": 10, "sp_x": 3}, "crafting_level": 6,
                "effect": {"xp_bonus": 0.40, "reveal_property": 3},
                "desc": "+40% XP, reveals 3 extra properties",
            },
            "shadow_gauntlet": {
                "name": "🌘 Shadow Gauntlet", "tier": 3, "type": "gauntlet",
                "combo": frozenset(["has_repeats", "has_operators", "has_punctuation", "has_symbols"]),
                "cost": {"sp": 120, "sp_plus": 8, "sp_x": 4}, "crafting_level": 7,
                "effect": {"sp_bonus": 0.30, "streak_shield": 0.40, "luck": 0.05},
                "desc": "+30% SP, 40% streak protect, +5% luck",
            },
            "phoenix_eye": {
                "name": "🔥 Phoenix Eye", "tier": 3, "type": "device",
                "combo": frozenset(["has_numbers", "has_uppercase", "has_multiple_words", "has_spaces"]),
                "cost": {"sp": 110, "sp_plus": 10, "sp_x": 2}, "crafting_level": 6,
                "effect": {"xp_bonus": 0.30, "sp_bonus": 0.15, "critical_chance": 0.03},
                "desc": "+30% XP, +15% SP, +3% critical",
            },
            # ── Tier 4: 5-property combos (Epic) ──
            "titan_grip": {
                "name": "💎 Titan Grip", "tier": 4, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_symbols", "has_uppercase", "has_lowercase", "is_long"]),
                "cost": {"sp": 200, "sp_plus": 20, "sp_x": 8, "sp_caret": 2}, "crafting_level": 9,
                "effect": {"sp_bonus": 0.50, "critical_chance": 0.08, "streak_shield": 0.30},
                "desc": "+50% SP, +8% crit, 30% streak shield",
            },
            "cosmos_engine": {
                "name": "🌠 Cosmos Engine", "tier": 4, "type": "device",
                "combo": frozenset(["has_vowels", "has_consecutive_letters", "has_multiple_words", "has_spaces", "starts_with_letter"]),
                "cost": {"sp": 200, "sp_plus": 20, "sp_x": 8, "sp_caret": 2}, "crafting_level": 9,
                "effect": {"xp_bonus": 0.60, "reveal_property": 4, "luck": 0.10},
                "desc": "+60% XP, reveals 4 props, +10% luck",
            },
            # ── Tier 5: 6+ property combos (Legendary) ──
            "infinity_forge": {
                "name": "♾️ Infinity Forge", "tier": 5, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_symbols", "has_uppercase", "has_lowercase", "is_long", "has_repeats"]),
                "cost": {"sp": 500, "sp_plus": 50, "sp_x": 15, "sp_caret": 5}, "crafting_level": 12,
                "effect": {"sp_bonus": 0.75, "critical_chance": 0.12, "streak_shield": 0.50, "luck": 0.10},
                "desc": "+75% SP, +12% crit, 50% shield, +10% luck",
            },
            "omniscient_core": {
                "name": "🧿 Omniscient Core", "tier": 5, "type": "device",
                "combo": frozenset(["has_vowels", "has_consecutive_letters", "has_multiple_words", "is_very_long", "has_spaces", "starts_with_letter"]),
                "cost": {"sp": 500, "sp_plus": 50, "sp_x": 15, "sp_caret": 5}, "crafting_level": 12,
                "effect": {"xp_bonus": 1.00, "reveal_property": 5, "luck": 0.15, "critical_chance": 0.05},
                "desc": "+100% XP, reveals 5 props, +15% luck, +5% crit",
            },
            "world_ender": {
                "name": "💀 World Ender", "tier": 5, "type": "gauntlet",
                "combo": frozenset(["has_numbers", "has_symbols", "has_operators", "has_uppercase", "has_lowercase", "is_long", "has_punctuation"]),
                "cost": {"sp": 750, "sp_plus": 75, "sp_x": 25, "sp_caret": 8}, "crafting_level": 15,
                "effect": {"sp_bonus": 1.00, "critical_chance": 0.15, "streak_shield": 0.60, "luck": 0.15, "reroll_gen": 0.10},
                "desc": "+100% SP, +15% crit, 60% shield, +15% luck",
            },
        }
        
        # Tier descriptions and colors
        self.crafting_tiers = {
            1: {"name": "Common", "color": "#b0bec5", "icon": "⚪"},
            2: {"name": "Uncommon", "color": "#66bb6a", "icon": "🟢"},
            3: {"name": "Rare", "color": "#42a5f5", "icon": "🔵"},
            4: {"name": "Epic", "color": "#ab47bc", "icon": "🟣"},
            5: {"name": "Legendary", "color": "#ffa726", "icon": "🟠"},
        }
    
    def _save_crafting_data(self):
        """Save crafting system data"""
        craft_file = self.account_manager.get_user_crafting_file(self.current_username) if self.current_username else "crafting.json"
        data = {
            "discovered_combos": [list(c) for c in self.discovered_combos],
            "crafted_items": self.crafted_items,
            "crafting_xp": self.crafting_xp,
            "crafting_level": self.crafting_level,
        }
        self._save_json(craft_file, data)
    
    def _check_crafting_discoveries(self, properties):
        """Check if current winning roll's properties unlock any new crafting combos"""
        from itertools import combinations
        props_list = list(properties)
        new_discoveries = 0
        for size in range(2, min(len(props_list) + 1, 8)):
            for combo in combinations(props_list, size):
                fs = frozenset(combo)
                if fs not in self.discovered_combos:
                    for recipe_id, recipe in self.crafting_recipes.items():
                        if recipe["combo"] == fs:
                            self.discovered_combos.add(fs)
                            new_discoveries += 1
                            self.crafting_xp += recipe["tier"] * 15
                            xp_needed = self.crafting_level * 50
                            while self.crafting_xp >= xp_needed:
                                self.crafting_xp -= xp_needed
                                self.crafting_level += 1
                                xp_needed = self.crafting_level * 50
                            break
        if new_discoveries > 0:
            self._save_crafting_data()
            try:
                self.root.after(500, lambda n=new_discoveries: messagebox.showinfo(
                    "🔨 New Recipe Discovered!",
                    f"You discovered {n} new crafting recipe{'s' if n > 1 else ''}!\n\n"
                    f"Open the Crafting Bench to see what you can forge!"
                ))
            except:
                pass
        return new_discoveries
    
    def _craft_item(self, item_id):
        """Craft an item from the advanced crafting bench"""
        if item_id not in self.crafting_recipes:
            return False, "Recipe not found"
        recipe = self.crafting_recipes[item_id]
        
        if recipe["combo"] not in self.discovered_combos:
            return False, "Recipe not yet discovered"
        if self.crafting_level < recipe["crafting_level"]:
            return False, f"Requires Crafting Level {recipe['crafting_level']} (yours: {self.crafting_level})"
        if item_id in self.crafted_items:
            return False, "Already crafted this item"
        
        cost = recipe["cost"]
        if cost.get("sp", 0) > self.sp:
            return False, f"Need {cost['sp']} SP (have {self.sp})"
        if cost.get("sp_plus", 0) > self.sp_plus:
            return False, f"Need {cost['sp_plus']} SP+ (have {self.sp_plus})"
        if cost.get("sp_x", 0) > self.sp_x:
            return False, f"Need {cost['sp_x']} SPx (have {self.sp_x})"
        if cost.get("sp_caret", 0) > self.sp_caret:
            return False, f"Need {cost['sp_caret']} SP^ (have {self.sp_caret})"
        
        self.sp -= cost.get("sp", 0)
        self.sp_plus -= cost.get("sp_plus", 0)
        self.sp_x -= cost.get("sp_x", 0)
        self.sp_caret -= cost.get("sp_caret", 0)
        self.crafted_items.append(item_id)
        self.crafting_xp += recipe["tier"] * 25
        xp_needed = self.crafting_level * 50
        while self.crafting_xp >= xp_needed:
            self.crafting_xp -= xp_needed
            self.crafting_level += 1
            xp_needed = self.crafting_level * 50
        
        self._save_crafting_data()
        self._save_equipment()
        self._update_sp_label()
        return True, f"Crafted {recipe['name']}!"
    
    def _get_crafting_bonuses(self):
        """Calculate total bonuses from all crafted items"""
        bonuses = {"sp_bonus": 0.0, "xp_bonus": 0.0, "critical_chance": 0.0,
                   "streak_shield": 0.0, "luck": 0.0, "reveal_property": 0,
                   "roll_speed": 0.0, "reroll_gen": 0.0}
        for item_id in self.crafted_items:
            if item_id in self.crafting_recipes:
                recipe = self.crafting_recipes[item_id]
                for key, value in recipe["effect"].items():
                    bonuses[key] = bonuses.get(key, 0) + value
        return bonuses
    
    # ===== CLANS / GUILDS SYSTEM =====
    
    def _init_clan_system(self):
        """Initialize the Clans/Guilds system"""
        self.clans_data = self._load_json("clans.json", {"clans": {}})
        
        self.player_clan = None
        if self.current_username:
            for clan_name, clan_info in self.clans_data.get("clans", {}).items():
                if self.current_username in clan_info.get("members", []):
                    self.player_clan = clan_name
                    break
        
        self.clan_perks = {
            2: {"name": "Fellowship", "desc": "+5% XP for all members", "effect": {"xp_bonus": 0.05}},
            4: {"name": "Shared Fortune", "desc": "+5% SP for all members", "effect": {"sp_bonus": 0.05}},
            6: {"name": "Lucky Clovers", "desc": "+2% critical chance", "effect": {"critical_chance": 0.02}},
            8: {"name": "Iron Will", "desc": "15% streak protection", "effect": {"streak_shield": 0.15}},
            10: {"name": "Golden Touch", "desc": "+10% SP for all members", "effect": {"sp_bonus": 0.10}},
            12: {"name": "Wisdom", "desc": "+10% XP for all members", "effect": {"xp_bonus": 0.10}},
            15: {"name": "Legendary Bond", "desc": "+5% critical, +5% luck", "effect": {"critical_chance": 0.05, "luck": 0.05}},
            20: {"name": "Transcendence", "desc": "+25% all gains", "effect": {"sp_bonus": 0.25, "xp_bonus": 0.25}},
        }
    
    def _save_clan_data(self):
        """Save global clan data"""
        self._save_json("clans.json", self.clans_data)
    
    def _get_clan_level(self, clan_name):
        """Calculate clan level from XP"""
        clan = self.clans_data.get("clans", {}).get(clan_name, {})
        xp = clan.get("total_xp", 0)
        level = 1
        xp_needed = 100
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = level * 100
        return level, xp, level * 100
    
    def _get_clan_perks(self, clan_name):
        """Get active perks for a clan based on its level"""
        level, _, _ = self._get_clan_level(clan_name)
        active_perks = {}
        for perk_level, perk_data in self.clan_perks.items():
            if level >= perk_level:
                for key, value in perk_data["effect"].items():
                    active_perks[key] = active_perks.get(key, 0) + value
        return active_perks
    
    def _contribute_clan_xp(self, sp_gained):
        """Contribute XP to the player's clan after a win"""
        if not self.player_clan:
            return
        clans = self.clans_data.get("clans", {})
        if self.player_clan not in clans:
            return
        clan = clans[self.player_clan]
        contribution = max(1, sp_gained // 2)
        clan["total_xp"] = clan.get("total_xp", 0) + contribution
        if "contributions" not in clan:
            clan["contributions"] = {}
        clan["contributions"][self.current_username] = clan["contributions"].get(self.current_username, 0) + contribution
        clan["total_wins"] = clan.get("total_wins", 0) + 1
        self._save_clan_data()
    
    def _get_clan_bonuses(self):
        """Get total bonuses from clan perks"""
        if not self.player_clan:
            return {}
        return self._get_clan_perks(self.player_clan)
    
    def _create_clan(self, clan_name):
        """Create a new clan"""
        if not self.current_username:
            return False, "Must be logged in"
        if self.player_clan:
            return False, "Already in a clan — leave first"
        clan_name = clan_name.strip()
        if not clan_name or len(clan_name) < 3 or len(clan_name) > 20:
            return False, "Clan name must be 3-20 characters"
        if clan_name in self.clans_data.get("clans", {}):
            return False, "Clan name already taken"
        
        self.clans_data.setdefault("clans", {})[clan_name] = {
            "leader": self.current_username,
            "members": [self.current_username],
            "total_xp": 0,
            "total_wins": 0,
            "contributions": {self.current_username: 0},
            "created": __import__("datetime").datetime.now().isoformat(),
            "motto": "A new clan rises!",
        }
        self.player_clan = clan_name
        self._save_clan_data()
        return True, f"Clan '{clan_name}' created!"
    
    def _join_clan(self, clan_name):
        """Join an existing clan"""
        if not self.current_username:
            return False, "Must be logged in"
        if self.player_clan:
            return False, "Already in a clan — leave first"
        if clan_name not in self.clans_data.get("clans", {}):
            return False, "Clan not found"
        
        clan = self.clans_data["clans"][clan_name]
        if len(clan.get("members", [])) >= 20:
            return False, "Clan is full (max 20 members)"
        if self.current_username in clan.get("members", []):
            return False, "Already a member"
        
        clan.setdefault("members", []).append(self.current_username)
        clan.setdefault("contributions", {})[self.current_username] = 0
        self.player_clan = clan_name
        self._save_clan_data()
        return True, f"Joined '{clan_name}'!"
    
    def _leave_clan(self):
        """Leave current clan"""
        if not self.player_clan:
            return False, "Not in a clan"
        clan = self.clans_data.get("clans", {}).get(self.player_clan, {})
        if clan.get("leader") == self.current_username:
            members = [m for m in clan.get("members", []) if m != self.current_username]
            if members:
                clan["leader"] = members[0]
                clan["members"] = members
            else:
                del self.clans_data["clans"][self.player_clan]
        else:
            clan["members"] = [m for m in clan.get("members", []) if m != self.current_username]
        
        old_name = self.player_clan
        self.player_clan = None
        self._save_clan_data()
        return True, f"Left '{old_name}'"
    
    # ===== STRING POKÉDEX SYSTEM =====
    
    def _init_pokedex_system(self):
        """Initialize the String Pokédex collection system"""
        pdx_file = self.account_manager.get_user_pokedex_file(self.current_username) if self.current_username else "pokedex.json"
        saved = self._load_json(pdx_file, {})
        
        self.pokedex_entries = saved.get("entries", [])
        self.pokedex_total_caught = saved.get("total_caught", 0)
        self.pokedex_unique_combos = set()
        for combo in saved.get("unique_combos", []):
            self.pokedex_unique_combos.add(frozenset(combo))
        
        self.rarity_tiers = {
            1: {"name": "Common", "color": "#b0bec5", "icon": "⬜", "stars": "★"},
            2: {"name": "Common", "color": "#b0bec5", "icon": "⬜", "stars": "★★"},
            3: {"name": "Uncommon", "color": "#66bb6a", "icon": "🟩", "stars": "★★★"},
            4: {"name": "Rare", "color": "#42a5f5", "icon": "🟦", "stars": "★★★★"},
            5: {"name": "Epic", "color": "#ab47bc", "icon": "🟪", "stars": "★★★★★"},
            6: {"name": "Legendary", "color": "#ffa726", "icon": "🟧", "stars": "★★★★★★"},
        }
    
    def _save_pokedex(self):
        """Save Pokédex data"""
        pdx_file = self.account_manager.get_user_pokedex_file(self.current_username) if self.current_username else "pokedex.json"
        data = {
            "entries": self.pokedex_entries[-500:],
            "total_caught": self.pokedex_total_caught,
            "unique_combos": [list(c) for c in self.pokedex_unique_combos],
        }
        self._save_json(pdx_file, data)
    
    def _record_pokedex_entry(self, string, properties):
        """Record a winning string in the Pokédex"""
        import datetime as _dt
        prop_count = len(properties)
        rarity_level = min(prop_count, 6) if prop_count >= 1 else 1
        rarity_key = max(1, rarity_level)
        rarity = self.rarity_tiers.get(rarity_key, self.rarity_tiers[1])
        
        if prop_count >= 7:
            rarity_name = "Mythic"
            rarity_color = "#ff4081"
            rarity_icon = "💜"
            rarity_stars = "★★★★★★★"
        else:
            rarity_name = rarity["name"]
            rarity_color = rarity["color"]
            rarity_icon = rarity["icon"]
            rarity_stars = rarity["stars"]
        
        combo_key = frozenset(properties)
        is_new_combo = combo_key not in self.pokedex_unique_combos
        if is_new_combo:
            self.pokedex_unique_combos.add(combo_key)
        
        entry = {
            "id": self.pokedex_total_caught + 1,
            "string": string,
            "properties": sorted(list(properties)),
            "property_count": prop_count,
            "rarity": rarity_name,
            "rarity_color": rarity_color,
            "rarity_icon": rarity_icon,
            "stars": rarity_stars,
            "is_new_combo": is_new_combo,
            "timestamp": _dt.datetime.now().isoformat(),
        }
        
        self.pokedex_entries.append(entry)
        self.pokedex_total_caught += 1
        if len(self.pokedex_entries) > 500:
            self.pokedex_entries = self.pokedex_entries[-500:]
        
        self._save_pokedex()
        return entry
    
    def _get_pokedex_stats(self):
        """Get Pokédex collection statistics"""
        rarity_counts = {"Common": 0, "Uncommon": 0, "Rare": 0, "Epic": 0, "Legendary": 0, "Mythic": 0}
        for entry in self.pokedex_entries:
            r = entry.get("rarity", "Common")
            rarity_counts[r] = rarity_counts.get(r, 0) + 1
        
        total_possible_combos = 0
        for size in range(1, 8):
            from math import comb
            total_possible_combos += comb(15, size)
        
        return {
            "total_caught": self.pokedex_total_caught,
            "entries_stored": len(self.pokedex_entries),
            "unique_combos": len(self.pokedex_unique_combos),
            "total_possible_combos": total_possible_combos,
            "rarity_counts": rarity_counts,
        }
    
    # ===== SHOP/MARKETPLACE SYSTEM =====
    
    def _load_shop_inventory(self):
        """Load shop inventory from file"""
        default_inventory = {
            "items": [
                {"name": "SP Pack (100)", "type": "sp", "cost": 50, "amount": 100, "description": "100 SP for crafting"},
                {"name": "SP+ Pack (5)", "type": "sp_plus", "cost": 75, "amount": 5, "description": "5 SP+ for advanced crafting"},
                {"name": "SPx Pack (2)", "type": "sp_x", "cost": 100, "amount": 2, "description": "2 SPx for rare crafting"},
                {"name": "SP^ Pack (1)", "type": "sp_caret", "cost": 150, "amount": 1, "description": "1 SP^ for legendary crafting"},
                {"name": "Lucky Charm", "type": "consumable", "cost": 25, "effect": "luck_boost", "description": "Temporarily boost luck by 10%"},
                {"name": "XP Booster", "type": "consumable", "cost": 30, "effect": "xp_boost", "description": "Double XP gain for 10 rolls"}
            ],
            "refresh_time": datetime.datetime.now().isoformat()
        }
        data = self._load_json("shop_inventory.json", default_inventory)
        self.shop_inventory = data.get("items", default_inventory["items"])
        self.shop_refresh_time = data.get("refresh_time", datetime.datetime.now().isoformat())
        return data
    
    def _save_shop_inventory(self):
        """Save shop inventory to file"""
        shop_data = {"items": self.shop_inventory, "refresh_time": self.shop_refresh_time}
        self._save_json("shop_inventory.json", shop_data)
    
    def purchase_item(self, item_name):
        """Purchase an item from the shop"""
        item = None
        for shop_item in self.shop_inventory:
            if shop_item["name"] == item_name:
                item = shop_item
                break
        
        if not item:
            return False, "Item not found in shop"
        
        cost = item["cost"]
        if self.sp < cost:
            return False, "Not enough SP"
        
        # Deduct cost
        self.sp -= cost
        
        # Apply item effect
        item_type = item["type"]
        if item_type == "sp":
            self.sp += item["amount"]
        elif item_type == "sp_plus":
            self.sp_plus += item["amount"]
        elif item_type == "sp_x":
            self.sp_x += item["amount"]
        elif item_type == "sp_caret":
            self.sp_caret += item["amount"]
        elif item_type == "consumable":
            effect = item["effect"]
            if effect == "luck_boost":
                self.temp_luck_boost = self.temp_luck_boost or 0 + 0.1
                self.temp_effects_timer = 10  # 10 rolls
            elif effect == "xp_boost":
                self.temp_xp_boost = self.temp_xp_boost or 0 + 1.0  # 2x XP
                self.temp_effects_timer = 10  # 10 rolls
        
        self._save_equipment()
        self._update_sp_label()
        return True, f"Successfully purchased {item_name}!"
    
    def refresh_shop(self):
        """Refresh shop inventory (costs SP)"""
        refresh_cost = 20
        if self.sp < refresh_cost:
            return False, "Not enough SP to refresh shop"
        
        self.sp -= refresh_cost
        # Generate new random inventory
        base_items = [
            {"name": "SP Pack (100)", "type": "sp", "cost": 50, "amount": 100},
            {"name": "SP Pack (200)", "type": "sp", "cost": 90, "amount": 200},
            {"name": "SP+ Pack (5)", "type": "sp_plus", "cost": 75, "amount": 5},
            {"name": "SPx Pack (2)", "type": "sp_x", "cost": 100, "amount": 2},
            {"name": "SP^ Pack (1)", "type": "sp_caret", "cost": 150, "amount": 1},
            {"name": "Lucky Charm", "type": "consumable", "cost": 25, "effect": "luck_boost"},
            {"name": "XP Booster", "type": "consumable", "cost": 30, "effect": "xp_boost"},
            {"name": "Mega Lucky Charm", "type": "consumable", "cost": 50, "effect": "mega_luck_boost"},
            {"name": "Super XP Booster", "type": "consumable", "cost": 60, "effect": "super_xp_boost"}
        ]
        
        # Select 6 random items
        self.shop_inventory = random.sample(base_items, 6)
        self.shop_refresh_time = datetime.datetime.now().isoformat()
        self._save_shop_inventory()
        self._update_sp_label()
        return True, "Shop refreshed!"
    
    # ===== CUSTOM GAME MODES SYSTEM =====
    
    def _init_game_modes(self):
        """Initialize custom game modes"""
        self.game_modes = {
            "Classic": {
                "description": "Standard Questionmark gameplay",
                "rules": ["standard_scoring"],
                "unlocked": True
            },
            "Speed Run": {
                "description": "Race against time - 30 seconds per roll",
                "rules": ["time_limit", "speed_bonus"],
                "unlocked": True
            },
            "Perfect Mode": {
                "description": "Only perfect matches count",
                "rules": ["perfect_only", "high_risk"],
                "unlocked": self.wins_count >= 10
            },
            "Combo Master": {
                "description": "Build combos for massive points",
                "rules": ["combo_system", "chain_bonus"],
                "unlocked": self.wins_count >= 25
            },
            "Zen Mode": {
                "description": "No time pressure, focus on accuracy",
                "rules": ["no_timer", "accuracy_focus"],
                "unlocked": self.wins_count >= 5
            },
            "Nightmare": {
                "description": "Extreme difficulty with random effects",
                "rules": ["random_effects", "extreme_difficulty"],
                "unlocked": self.wins_count >= 50
            }
        }
        self.current_game_mode = "Classic"
        self.mode_stats = {}
    
    def switch_game_mode(self, mode_name):
        """Switch to a different game mode"""
        if mode_name not in self.game_modes:
            return False, "Game mode not found"
        
        mode = self.game_modes[mode_name]
        if not mode["unlocked"]:
            return False, "Game mode not unlocked yet"
        
        self.current_game_mode = mode_name
        self.mode_stats[mode_name] = self.mode_stats.get(mode_name, {"plays": 0, "wins": 0, "best_score": 0})
        return True, f"Switched to {mode_name} mode!"
    
    def get_mode_rules(self):
        """Get rules for current game mode"""
        if self.current_game_mode not in self.game_modes:
            return []
        return self.game_modes[self.current_game_mode]["rules"]
    
    def apply_mode_bonuses(self, score, time_taken=None):
        """Apply game mode specific bonuses to score"""
        mode = self.current_game_mode
        rules = self.get_mode_rules()
        bonus_multiplier = 1.0
        
        if "speed_bonus" in rules and time_taken and time_taken < 10:
            bonus_multiplier *= 1.5  # 50% bonus for fast rolls
        if "combo_system" in rules:
            current_combo = getattr(self, 'current_combo', 0)
            bonus_multiplier *= (1 + current_combo * 0.1)  # 10% per combo
        if "high_risk" in rules:
            bonus_multiplier *= 2.0  # Double points for high risk
        if "accuracy_focus" in rules:
            bonus_multiplier *= 1.2  # 20% bonus for accuracy
        
        return int(score * bonus_multiplier)
    
    # ===== STRATEGY SYSTEM =====
    
    def _init_strategy_system(self):
        """Initialize strategy system with player choices"""
        # Talent tree - players spec into different builds
        self.talent_tree = {
            "precision": {
                "name": "Precision Mastery",
                "levels": [
                    {"level": 1, "cost": 20, "desc": "+10% property detection", "bonus": 0.1},
                    {"level": 2, "cost": 40, "desc": "+20% property detection", "bonus": 0.2},
                    {"level": 3, "cost": 80, "desc": "+35% property detection", "bonus": 0.35},
                ],
                "current_level": 0,
                "unlocked": True,
                "category": "detection"
            },
            "efficiency": {
                "name": "Efficiency Expert",
                "levels": [
                    {"level": 1, "cost": 25, "desc": "+5% SP gain", "bonus": 0.05},
                    {"level": 2, "cost": 50, "desc": "+12% SP gain", "bonus": 0.12},
                    {"level": 3, "cost": 100, "desc": "+25% SP gain", "bonus": 0.25},
                ],
                "current_level": 0,
                "unlocked": True,
                "category": "rewards"
            },
            "fortune": {
                "name": "Fortune Seeker",
                "levels": [
                    {"level": 1, "cost": 30, "desc": "+3% property match chance", "bonus": 0.03},
                    {"level": 2, "cost": 60, "desc": "+7% property match chance", "bonus": 0.07},
                    {"level": 3, "cost": 120, "desc": "+15% property match chance", "bonus": 0.15},
                ],
                "current_level": 0,
                "unlocked": self.wins_count >= 5,
                "category": "luck"
            },
            "endurance": {
                "name": "Streak Specialist",
                "levels": [
                    {"level": 1, "cost": 35, "desc": "+20% streak bonuses", "bonus": 0.2},
                    {"level": 2, "cost": 70, "desc": "+50% streak bonuses", "bonus": 0.5},
                    {"level": 3, "cost": 140, "desc": "+100% streak bonuses", "bonus": 1.0},
                ],
                "current_level": 0,
                "unlocked": self.wins_count >= 10,
                "category": "momentum"
            },
        }
        
        # Pre-roll strategy choices
        self.roll_strategies = {
            "safe": {
                "name": "Safe Strategy",
                "desc": "Guaranteed SP gain, predictable properties",
                "sp_multiplier": 1.0,
                "property_variety": "low",
                "difficulty": "easy",
                "win_bonus": 0,
                "cost": 0
            },
            "balanced": {
                "name": "Balanced Strategy",
                "desc": "Moderate SP gain, mixed properties",
                "sp_multiplier": 1.3,
                "property_variety": "medium",
                "difficulty": "medium",
                "win_bonus": 10,
                "cost": 5
            },
            "risky": {
                "name": "Risky Strategy",
                "desc": "High SP potential, chaotic properties",
                "sp_multiplier": 1.8,
                "property_variety": "high",
                "difficulty": "hard",
                "win_bonus": 30,
                "cost": 15
            },
            "aggressive": {
                "name": "Aggressive Strategy",
                "desc": "Maximum SP, extreme properties",
                "sp_multiplier": 2.5,
                "property_variety": "extreme",
                "difficulty": "nightmare",
                "win_bonus": 75,
                "cost": 40
            },
        }
        
        self.current_roll_strategy = "safe"
        
        # Active effects players can enable per session
        self.active_effects = {
            "focus_mode": {
                "name": "🎯 Focus Mode",
                "desc": "Predict properties better, cost 10 SP/session",
                "enabled": False,
                "cost_per_session": 10,
                "property_detection_bonus": 0.25,
                "sp_cost_per_roll": 0,
                "effect": "detection"
            },
            "luck_cascade": {
                "name": "✨ Luck Cascade",
                "desc": "Winning streaks grant better properties, cost 15 SP/session",
                "enabled": False,
                "cost_per_session": 15,
                "streak_multiplier": 1.5,
                "sp_cost_per_roll": 0,
                "effect": "momentum"
            },
            "sharpness": {
                "name": "⚡ Sharpness",
                "desc": "Fewer distracting properties, cost 12 SP/session",
                "enabled": False,
                "cost_per_session": 12,
                "property_reduction": 0.2,  # Reduce property count by 20%
                "sp_cost_per_roll": 0,
                "effect": "clarity"
            },
            "empowerment": {
                "name": "💪 Empowerment",
                "desc": "Win bonuses doubled, cost 20 SP/session",
                "enabled": False,
                "cost_per_session": 20,
                "win_bonus_multiplier": 2.0,
                "sp_cost_per_roll": 0,
                "effect": "rewards"
            }
        }
        
        # Load strategy data if it exists
        self._load_strategy_data()
    
    def _load_strategy_data(self):
        """Load talent tree and strategy data from file"""
        if not self.current_username:
            return
        strategy_file = f"user_{self.current_username}_strategy.json"
        if os.path.exists(strategy_file):
            data = self._load_json(strategy_file, {})
            if "talent_tree" in data:
                for branch, levels in data["talent_tree"].items():
                    if branch in self.talent_tree:
                        self.talent_tree[branch]["current_level"] = levels.get("current_level", 0)
            if "active_effects" in data:
                for effect, enabled in data["active_effects"].items():
                    if effect in self.active_effects:
                        self.active_effects[effect]["enabled"] = enabled
            if "current_strategy" in data:
                self.current_roll_strategy = data["current_strategy"]
    
    def _save_strategy_data(self):
        """Save talent tree and strategy data to file"""
        if not self.current_username:
            return
        strategy_file = f"user_{self.current_username}_strategy.json"
        talent_tree_data = {branch: {"current_level": data["current_level"]} 
                           for branch, data in self.talent_tree.items()}
        active_effects_data = {effect: data["enabled"] for effect, data in self.active_effects.items()}
        
        data = {
            "talent_tree": talent_tree_data,
            "active_effects": active_effects_data,
            "current_strategy": self.current_roll_strategy
        }
        self._save_json(strategy_file, data)
    
    def unlock_talent(self, talent_name):
        """Unlock next level of a talent (costs SP)"""
        if talent_name not in self.talent_tree:
            return False, "Talent not found"
        
        talent = self.talent_tree[talent_name]
        current_level = talent["current_level"]
        
        if current_level >= len(talent["levels"]):
            return False, "Talent already maxed out"
        
        if not talent["unlocked"]:
            return False, "Talent not unlocked yet"
        
        next_level_data = talent["levels"][current_level]
        required_sp = next_level_data["cost"]
        
        # Check if player has enough SP
        if self.sp < required_sp:
            return False, f"Need {required_sp} SP (have {self.sp})"
        
        # Deduct SP and level up talent
        self.sp -= required_sp
        talent["current_level"] += 1
        self._save_strategy_data()
        
        return True, f"✓ {talent['name']} upgraded to level {talent['current_level']}!"
    
    def get_talent_bonuses(self):
        """Calculate total bonuses from talent tree"""
        bonuses = {
            "sp_multiplier": 1.0,
            "property_detection": 0.0,
            "luck_bonus": 0.0,
            "streak_bonus": 1.0,
        }
        
        # Precision tree
        if self.talent_tree["precision"]["current_level"] > 0:
            level_data = self.talent_tree["precision"]["levels"][self.talent_tree["precision"]["current_level"] - 1]
            bonuses["property_detection"] += level_data["bonus"]
        
        # Efficiency tree
        if self.talent_tree["efficiency"]["current_level"] > 0:
            level_data = self.talent_tree["efficiency"]["levels"][self.talent_tree["efficiency"]["current_level"] - 1]
            bonuses["sp_multiplier"] *= (1 + level_data["bonus"])
        
        # Fortune tree
        if self.talent_tree["fortune"]["current_level"] > 0:
            level_data = self.talent_tree["fortune"]["levels"][self.talent_tree["fortune"]["current_level"] - 1]
            bonuses["luck_bonus"] += level_data["bonus"]
        
        # Endurance tree
        if self.talent_tree["endurance"]["current_level"] > 0:
            level_data = self.talent_tree["endurance"]["levels"][self.talent_tree["endurance"]["current_level"] - 1]
            bonuses["streak_bonus"] *= (1 + level_data["bonus"])
        
        return bonuses
    
    def toggle_active_effect(self, effect_name):
        """Toggle an active effect on/off"""
        if effect_name not in self.active_effects:
            return False, "Effect not found"
        
        effect = self.active_effects[effect_name]
        new_state = not effect["enabled"]
        
        if new_state:
            # Check if player has enough SP to activate
            if self.sp < effect["cost_per_session"]:
                return False, f"Need {effect['cost_per_session']} SP to activate (have {self.sp})"
            
            # Deduct SP for session
            self.sp -= effect["cost_per_session"]
            effect["enabled"] = True
            self._save_strategy_data()
            return True, f"✓ {effect['name']} activated!"
        else:
            effect["enabled"] = False
            self._save_strategy_data()
            return True, f"✓ {effect['name']} deactivated"
    
    def set_roll_strategy(self, strategy_name):
        """Change the roll strategy for next roll"""
        if strategy_name not in self.roll_strategies:
            return False, "Strategy not found"
        
        strategy = self.roll_strategies[strategy_name]
        
        # Check cost
        if strategy["cost"] > 0 and self.sp < strategy["cost"]:
            return False, f"Need {strategy['cost']} SP (have {self.sp})"
        
        # Deduct cost
        if strategy["cost"] > 0:
            self.sp -= strategy["cost"]
        
        self.current_roll_strategy = strategy_name
        self._save_strategy_data()
        return True, f"Strategy set to: {strategy['name']}"
    
    def apply_roll_strategy(self, base_sp_value):
        """Apply current strategy multiplier to SP gain"""
        strategy = self.roll_strategies[self.current_roll_strategy]
        sp_multiplier = strategy["sp_multiplier"]
        
        # Apply talent bonuses
        talent_bonuses = self.get_talent_bonuses()
        sp_multiplier *= talent_bonuses["sp_multiplier"]
        
        # Apply active effects bonuses
        if self.active_effects["empowerment"]["enabled"]:
            sp_multiplier *= self.active_effects["empowerment"]["win_bonus_multiplier"]
        
        return int(base_sp_value * sp_multiplier)
    
    def get_strategy_info(self):
        """Get formatted info about current strategy setup"""
        current_strategy = self.roll_strategies[self.current_roll_strategy]
        talent_bonuses = self.get_talent_bonuses()
        
        info = f"""
╔═══ STRATEGY SETUP ═══╗
Strategy: {current_strategy['name']}
  {current_strategy['desc']}
  
Active Effects: {sum(1 for e in self.active_effects.values() if e['enabled'])}/4
  
Talent Bonuses:
  • SP Multiplier: {talent_bonuses['sp_multiplier']:.1%}
  • Property Detection: +{talent_bonuses['property_detection']:.1%}
  • Luck Bonus: +{talent_bonuses['luck_bonus']:.1%}
  • Streak Bonus: {talent_bonuses['streak_bonus']:.1%}
╚════════════════════╝
"""
        return info
    
    # ===== ENGAGEMENT SYSTEM =====
    
    def _init_engagement_system(self):
        """Initialize active engagement and skill-based progression"""
        # Combo system - reward chaining wins with specific actions
        self.current_combo = 0
        self.max_combo_session = 0
        self.combo_multiplier = 1.0
        
        # Momentum system - win rate determines progression speed
        self.session_start_time = None
        self.session_wins = 0
        self.session_rolls = 0
        self.win_rate_bonus = 1.0
        
        # Critical moments - random events during rolls
        self.pending_critical_moment = None
        self.critical_moment_rewards = {}
        
        # Skill challenges - daily timed challenges
        self.active_skill_challenge = None
        self.skill_challenge_progress = self._load_json(f"user_{self.current_username}_challenges.json", {
            "daily_challenges_completed": 0,
            "challenge_streaks": 0,
            "best_challenge_time": float('inf')
        })
        self.daily_challenges_available = [
            {"id": 1, "name": "Speed Demon", "desc": "Win 3 rolls in under 60 seconds", "target": 3, "time_limit": 60, "reward_xp": 100, "reward_sp": 50},
            {"id": 2, "name": "Precision Master", "desc": "Win 5 rolls with all properties matched", "target": 5, "time_limit": float('inf'), "reward_xp": 150, "reward_sp": 75},
            {"id": 3, "name": "Streak King", "desc": "Achieve 10-win streak in one session", "target": 10, "time_limit": float('inf'), "reward_xp": 200, "reward_sp": 100},
        ]
        
        # Decision prompts - offer choices between rolls
        self.pending_decision = None
        self.decision_history = []
        
        # Mastery tracking - playstyle consistency rewards
        self.playstyle_consistency = {
            "precision_focused": 0,      # Win with high property match
            "speed_focused": 0,           # Fast wins
            "consistency_focused": 0,     # Long streaks
            "risk_focused": 0,            # Using risky strategies
        }
        
        self._load_engagement_data()
    
    def _load_engagement_data(self):
        """Load engagement system data"""
        if not self.current_username:
            return
        engagement_file = f"user_{self.current_username}_engagement.json"
        if os.path.exists(engagement_file):
            data = self._load_json(engagement_file, {})
            self.playstyle_consistency = data.get("playstyle_consistency", self.playstyle_consistency)
            self.skill_challenge_progress = data.get("skill_challenges", self.skill_challenge_progress)
    
    def _save_engagement_data(self):
        """Save engagement system data"""
        if not self.current_username:
            return
        engagement_file = f"user_{self.current_username}_engagement.json"
        data = {
            "playstyle_consistency": self.playstyle_consistency,
            "skill_challenges": self.skill_challenge_progress
        }
        self._save_json(engagement_file, data)
    
    def update_combo(self, win_achieved, strategy_used=None):
        """Update combo system based on win/loss"""
        if win_achieved:
            self.current_combo += 1
            self.max_combo_session = max(self.max_combo_session, self.current_combo)
            
            # Update playstyle consistency
            if strategy_used == "risky" or strategy_used == "aggressive":
                self.playstyle_consistency["risk_focused"] += 1
            if self.current_combo >= 3:
                self.playstyle_consistency["consistency_focused"] += 1
            
            # Combo bonus multiplier (1.0 → 2.0 at 10 combo)
            self.combo_multiplier = 1.0 + (min(self.current_combo, 10) * 0.1)
            
            return self.combo_multiplier
        else:
            # Reset combo on loss
            bonus_multiplier = self.combo_multiplier
            self.current_combo = 0
            self.combo_multiplier = 1.0
            return bonus_multiplier  # Return final multiplier before reset
    
    def calculate_win_rate_bonus(self):
        """Calculate progression speed multiplier based on win rate"""
        if self.session_rolls == 0:
            return 1.0
        
        win_rate = self.session_wins / self.session_rolls
        
        # Rewards consistency: 50% win rate = 1.0x, 75% = 1.5x, 90% = 2.0x
        if win_rate >= 0.9:
            return 2.0
        elif win_rate >= 0.75:
            return 1.5
        elif win_rate >= 0.5:
            return 1.0 + (win_rate - 0.5) * 2  # 0.5→1.0, 1.0→1.0, 1.5→1.5
        else:
            return 1.0 - (0.5 - win_rate)  # Below 50% gets penalty
    
    def check_critical_moment(self):
        """Randomly trigger a critical moment event during rolls"""
        import random
        
        # 10% chance per roll when on a winning streak
        if self.current_combo >= 2 and random.random() < 0.1:
            critical_type = random.choice([
                "property_clue",      # Reveal one property early
                "sp_multiplier",      # 2x SP if you win
                "combo_extension",    # Win grants +2 combo instead of +1
                "skill_check",        # Quick reaction test for bonus
            ])
            
            self.pending_critical_moment = {
                "type": critical_type,
                "triggered": False,
                "completed": False,
                "reward": self._get_critical_moment_reward(critical_type)
            }
            return self.pending_critical_moment
        
        return None
    
    def _get_critical_moment_reward(self, moment_type):
        """Get reward for critical moment"""
        rewards = {
            "property_clue": {"xp": 50, "sp": 25, "desc": "Property hint revealed!"},
            "sp_multiplier": {"xp": 75, "sp": 50, "desc": "2x SP bonus on next win!"},
            "combo_extension": {"xp": 100, "sp": 0, "desc": "+1 to combo on win!"},
            "skill_check": {"xp": 150, "sp": 75, "desc": "Reaction test active!"},
        }
        return rewards.get(moment_type, {"xp": 50, "sp": 25, "desc": "Bonus activated!"})
    
    def complete_critical_moment(self, success=True):
        """Complete a critical moment event"""
        if not self.pending_critical_moment:
            return 0, 0
        
        if not success:
            self.pending_critical_moment = None
            return 0, 0
        
        reward = self.pending_critical_moment["reward"]
        self.pending_critical_moment = None
        
        return reward.get("xp", 0), reward.get("sp", 0)
    
    def create_skill_challenge(self):
        """Create a random skill challenge for this session"""
        import random
        challenge = random.choice(self.daily_challenges_available)
        self.active_skill_challenge = {
            "id": challenge["id"],
            "name": challenge["name"],
            "desc": challenge["desc"],
            "target": challenge["target"],
            "current": 0,
            "time_limit": challenge["time_limit"],
            "start_time": datetime.datetime.now(),
            "reward_xp": challenge["reward_xp"],
            "reward_sp": challenge["reward_sp"],
            "completed": False
        }
        return self.active_skill_challenge
    
    def update_skill_challenge(self, win_achieved=False):
        """Update skill challenge progress"""
        if not self.active_skill_challenge or self.active_skill_challenge["completed"]:
            return None
        
        # Check time limit
        if self.active_skill_challenge["time_limit"] != float('inf'):
            elapsed = (datetime.datetime.now() - self.active_skill_challenge["start_time"]).total_seconds()
            if elapsed > self.active_skill_challenge["time_limit"]:
                self.active_skill_challenge["completed"] = False
                return None  # Time expired
        
        # Update progress
        if win_achieved:
            self.active_skill_challenge["current"] += 1
            
            if self.active_skill_challenge["current"] >= self.active_skill_challenge["target"]:
                self.active_skill_challenge["completed"] = True
                self.skill_challenge_progress["daily_challenges_completed"] += 1
                self.skill_challenge_progress["challenge_streaks"] += 1
                
                reward = {
                    "xp": self.active_skill_challenge["reward_xp"],
                    "sp": self.active_skill_challenge["reward_sp"],
                    "name": self.active_skill_challenge["name"]
                }
                
                self._save_engagement_data()
                return reward
        
        return None
    
    def create_decision_prompt(self):
        """Create a binary decision prompt between rolls"""
        import random
        
        decisions = [
            {
                "id": "safe_vs_risky",
                "prompt": "Risk Assessment",
                "options": [
                    {"text": "Play it safe", "bonus": 10, "risk": 0},
                    {"text": "Take a risk", "bonus": 50, "risk": 0.3}
                ]
            },
            {
                "id": "combo_vs_reset",
                "prompt": "Strategy Change",
                "options": [
                    {"text": "Maintain combo", "bonus": 0, "risk": 0},
                    {"text": "New strategy", "bonus": 25, "risk": 0.2}
                ]
            },
            {
                "id": "sp_vs_xp",
                "prompt": "Reward Focus",
                "options": [
                    {"text": "Maximize SP", "bonus": 0, "risk": 0.1},
                    {"text": "Maximize XP", "bonus": 0, "risk": 0}
                ]
            },
        ]
        
        decision = random.choice(decisions)
        self.pending_decision = {
            "id": decision["id"],
            "prompt": decision["prompt"],
            "options": decision["options"],
            "chosen": None,
            "time_created": datetime.datetime.now()
        }
        return self.pending_decision
    
    def resolve_decision(self, option_index):
        """Resolve a decision prompt"""
        if not self.pending_decision or option_index >= len(self.pending_decision["options"]):
            return None
        
        option = self.pending_decision["options"][option_index]
        self.pending_decision["chosen"] = option_index
        
        # Add to history for mastery tracking
        self.decision_history.append({
            "decision": self.pending_decision["id"],
            "choice": option_index,
            "timestamp": datetime.datetime.now()
        })
        
        result = {
            "bonus_sp": option.get("bonus", 0),
            "risk": option.get("risk", 0),
            "text": option["text"]
        }
        
        self.pending_decision = None
        return result
    
    def calculate_skill_based_xp(self, base_xp, win_rate_bonus=1.0, combo_bonus=1.0, challenge_bonus=1.0):
        """Calculate XP with skill-based multipliers instead of just SP-based"""
        # Base XP multiplied by win rate, combo streak, and challenge completion
        skill_multiplier = win_rate_bonus * combo_bonus * challenge_bonus
        
        return int(base_xp * skill_multiplier)
    
    def get_engagement_status(self):
        """Get formatted engagement system status"""
        win_rate = (self.session_wins / self.session_rolls * 100) if self.session_rolls > 0 else 0
        status = f"""
╔════ ENGAGEMENT STATUS ════╗
Session Stats:
  • Combo: {self.current_combo} (Max: {self.max_combo_session})
  • Combo Multiplier: {self.combo_multiplier:.2f}x
  • Win Rate: {win_rate:.1f}% ({self.session_wins}W/{self.session_rolls}R)
  • Momentum Bonus: {self.win_rate_bonus:.2f}x
  
Active Challenge: {self.active_skill_challenge['name'] if self.active_skill_challenge else 'None'}
Critical Moment: {self.pending_critical_moment['type'] if self.pending_critical_moment else 'None'}
Pending Decision: {self.pending_decision['prompt'] if self.pending_decision else 'None'}

Playstyle Mastery:
  • Risk-Focused: {self.playstyle_consistency['risk_focused']}
  • Consistency: {self.playstyle_consistency['consistency_focused']}
  • Speed: {self.playstyle_consistency['speed_focused']}
  • Precision: {self.playstyle_consistency['precision_focused']}
╚══════════════════════════╝
"""
        return status
    
    # ===== PROGRESSION SYSTEM =====
    
    def _init_progression_system(self):
        """Initialize comprehensive progression system with quests, achievements, and meaningful unlocks"""
        
        # ===== QUEST SYSTEM =====
        # Dynamic quests that guide player progression
        self.active_quests = {}
        self.completed_quests = set()
        self.quest_progress = {}
        
        # Quest templates with scaling difficulty
        self.quest_templates = {
            "daily_wins": {
                "name": "Daily Victor",
                "description": "Win {target} rolls today",
                "type": "daily",
                "tiers": [
                    {"target": 5, "reward_xp": 50, "reward_sp": 25, "reward_title": "Winner"},
                    {"target": 10, "reward_xp": 100, "reward_sp": 50, "reward_title": "Champion"},
                    {"target": 20, "reward_xp": 200, "reward_sp": 100, "reward_title": "Master"}
                ]
            },
            "streak_challenge": {
                "name": "Streak Seeker",
                "description": "Achieve a {target}-win streak",
                "type": "session",
                "tiers": [
                    {"target": 3, "reward_xp": 30, "reward_sp": 15, "reward_title": "Consistent"},
                    {"target": 5, "reward_xp": 75, "reward_sp": 40, "reward_title": "Unstoppable"},
                    {"target": 10, "reward_xp": 150, "reward_sp": 80, "reward_title": "Legendary"}
                ]
            },
            "property_mastery": {
                "name": "Property Expert",
                "description": "Discover {target} different properties",
                "type": "progressive",
                "tiers": [
                    {"target": 10, "reward_xp": 60, "reward_sp": 30, "reward_title": "Observer"},
                    {"target": 25, "reward_xp": 120, "reward_sp": 60, "reward_title": "Analyst"},
                    {"target": 50, "reward_xp": 250, "reward_sp": 125, "reward_title": "Scholar"}
                ]
            },
            "sp_accumulator": {
                "name": "Wealth Builder",
                "description": "Earn {target} SP in a single session",
                "type": "session",
                "tiers": [
                    {"target": 50, "reward_xp": 40, "reward_sp": 20, "reward_title": "Saver"},
                    {"target": 150, "reward_xp": 90, "reward_sp": 45, "reward_title": "Earner"},
                    {"target": 300, "reward_xp": 180, "reward_sp": 90, "reward_title": "Tycoon"}
                ]
            },
            "precision_quest": {
                "name": "Precision Strike",
                "description": "Win {target} rolls with perfect property matches",
                "type": "session",
                "tiers": [
                    {"target": 2, "reward_xp": 80, "reward_sp": 40, "reward_title": "Precise"},
                    {"target": 5, "reward_xp": 160, "reward_sp": 80, "reward_title": "Surgical"},
                    {"target": 10, "reward_xp": 300, "reward_sp": 150, "reward_title": "Perfect"}
                ]
            }
        }
        
        # ===== ACHIEVEMENT SYSTEM =====
        # Progressive achievements with meaningful rewards
        self.progression_achievements = {
            # Basic progression achievements
            "first_win": {
                "name": "First Victory",
                "description": "Win your first roll",
                "icon": "🏆",
                "requirement": lambda: self.meta_progression.get("total_wins_all_time", 0) >= 1,
                "reward": {"xp": 25, "sp": 10, "title": "Victor"},
                "progress": 0,
                "completed": False,
                "category": "beginner"
            },
            "level_up": {
                "name": "Growing Stronger",
                "description": "Reach level {target}",
                "icon": "⬆️",
                "tiers": [5, 10, 15, 25, 50],
                "current_tier": 0,
                "reward_per_tier": {"xp": 100, "sp": 50},
                "progress": lambda: self.player_level,
                "completed": False,
                "category": "progression"
            },
            "wealth_accumulator": {
                "name": "Fortune Builder",
                "description": "Accumulate {target} total SP",
                "icon": "💰",
                "tiers": [1000, 5000, 10000, 25000, 50000],
                "current_tier": 0,
                "reward_per_tier": {"xp": 150, "sp": 75},
                "progress": lambda: self.meta_progression.get("total_sp_earned_all_time", 0),
                "completed": False,
                "category": "wealth"
            },
            "streak_master": {
                "name": "Combo King",
                "description": "Achieve a {target}-win streak",
                "icon": "🔥",
                "tiers": [5, 10, 20, 50, 100],
                "current_tier": 0,
                "reward_per_tier": {"xp": 200, "sp": 100},
                "progress": lambda: self.max_winning_streak,
                "completed": False,
                "category": "skill"
            },
            "property_hunter": {
                "name": "Property Scholar",
                "description": "Discover {target} unique properties",
                "icon": "🔍",
                "tiers": [25, 50, 100, 200, 500],
                "current_tier": 0,
                "reward_per_tier": {"xp": 125, "sp": 60},
                "progress": lambda: len(self.stats.get('property_discoveries', {})),
                "completed": False,
                "category": "exploration"
            },
            "session_grinder": {
                "name": "Dedicated Player",
                "description": "Play for {target} hours total",
                "icon": "⏰",
                "tiers": [10, 50, 100, 250, 500],
                "current_tier": 0,
                "reward_per_tier": {"xp": 300, "sp": 150},
                "progress": lambda: self.meta_progression.get("total_play_time_hours", 0),
                "completed": False,
                "category": "dedication"
            }
        }
        
        # ===== RNG INFLUENCE SYSTEM =====
        # Ways for players to control or influence random outcomes
        self.rng_influence = {
            "luck_tokens": {
                "name": "Luck Tokens",
                "description": "Spend tokens to influence roll outcomes",
                "current_tokens": 0,
                "max_tokens": 10,
                "abilities": {
                    "favorable_roll": {
                        "name": "Favorable Roll",
                        "cost": 2,
                        "description": "+25% win chance for next roll",
                        "effect": {"win_chance_bonus": 0.25, "duration": 1}
                    },
                    "property_hint": {
                        "name": "Property Hint",
                        "cost": 1,
                        "description": "Reveal one target property early",
                        "effect": {"reveal_property": True}
                    },
                    "streak_protection": {
                        "name": "Streak Protection",
                        "cost": 3,
                        "description": "Prevent streak loss on next loss",
                        "effect": {"streak_protection": True, "duration": 1}
                    },
                    "double_reward": {
                        "name": "Double Reward",
                        "cost": 5,
                        "description": "Double SP/XP from next win",
                        "effect": {"reward_multiplier": 2.0, "duration": 1}
                    }
                }
            },
            "karma_system": {
                "name": "Karma Balance",
                "description": "Your actions affect future luck",
                "karma_level": 0,  # -100 to +100
                "effects": {
                    "lucky_streak": "Win streaks build faster",
                    "unlucky_streak": "Losses hurt more",
                    "neutral": "Balanced outcomes"
                }
            },
            "ritual_system": {
                "name": "Lucky Rituals",
                "description": "Perform rituals to influence RNG",
                "available_rituals": {
                    "focus_ritual": {
                        "name": "Focus Ritual",
                        "description": "Meditate for better concentration",
                        "duration": 30,  # seconds
                        "effect": {"concentration_bonus": 0.15},
                        "unlocked": True
                    },
                    "luck_ritual": {
                        "name": "Luck Ritual",
                        "description": "Ancient luck-drawing ceremony",
                        "duration": 60,
                        "effect": {"luck_bonus": 0.1},
                        "unlocked": False
                    },
                    "precision_ritual": {
                        "name": "Precision Ritual",
                        "description": "Heighten senses for perfect timing",
                        "duration": 45,
                        "effect": {"precision_bonus": 0.2},
                        "unlocked": False
                    }
                },
                "active_ritual": None,
                "ritual_end_time": None
            }
        }
        
        # ===== GRADUAL MECHANIC UNLOCKS =====
        # Systems unlock progressively based on player progress
        self.mechanic_unlocks = {
            "basic_progression": {
                "name": "Basic Progression",
                "description": "Level up and earn XP/SP",
                "unlocked": True,
                "unlock_requirement": lambda: True
            },
            "strategy_system": {
                "name": "Strategy System",
                "description": "Choose different strategies for rolls",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 3
            },
            "equipment_basics": {
                "name": "Basic Equipment",
                "description": "Upgrade your gear for bonuses",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 5
            },
            "quest_system": {
                "name": "Quest System",
                "description": "Complete quests for rewards",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 7
            },
            "rng_influence": {
                "name": "RNG Influence",
                "description": "Control aspects of randomness",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 10
            },
            "advanced_equipment": {
                "name": "Advanced Equipment",
                "description": "Unlock powerful equipment slots",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 15
            },
            "investment_system": {
                "name": "Investment System",
                "description": "Invest SP for passive income",
                "unlocked": False,
                "unlock_requirement": lambda: self.meta_progression.get("total_sp_earned_all_time", 0) >= 1000
            },
            "prestige_system": {
                "name": "Prestige System",
                "description": "Reset for permanent bonuses",
                "unlocked": False,
                "unlock_requirement": lambda: self.player_level >= 25
            },
            "master_mechanics": {
                "name": "Master Mechanics",
                "description": "Ultimate progression systems",
                "unlocked": False,
                "unlock_requirement": lambda: self.meta_progression.get("total_wins_all_time", 0) >= 1000
            }
        }
        
        # ===== SYSTEM INTERACTIONS =====
        # How different systems affect each other
        self.system_interactions = {
            "strategy_equipment": "Equipment bonuses stack with strategy multipliers",
            "quests_achievements": "Completing quests unlocks achievement tiers",
            "karma_rituals": "Karma affects ritual effectiveness",
            "level_mechanics": "Higher levels unlock more powerful mechanics",
            "streak_influence": "Win streaks generate luck tokens",
            "investment_quests": "Investment income helps complete wealth quests"
        }
        
        # Load progression data
        self._load_progression_data()
        
        # Generate initial quests
        self._generate_daily_quests()
        
        # Check for new unlocks
        self._check_mechanic_unlocks()
        self._check_achievement_progress()
        
        # ===== SPECIALIZATION TREES =====
        # Player chooses how to specialize, affecting gameplay style
        self.specialization_trees = {
            "efficiency_specialist": {
                "name": "Efficiency Specialist",
                "description": "Maximize output per action through optimization",
                "icon": "⚡",
                "passive_bonuses": {
                    "sp_efficiency": 0.15,  # +15% SP from all sources
                    "xp_efficiency": 0.10,  # +10% XP gain
                    "resource_double_chance": 0.05  # 5% chance for double rewards
                },
                "active_abilities": {
                    "resource_boost": {
                        "name": "Resource Surge",
                        "description": "Double all rewards for next 5 wins",
                        "cooldown": 300,  # 5 minutes
                        "effect": {"reward_multiplier": 2.0, "duration_wins": 5}
                    },
                    "efficiency_burst": {
                        "name": "Efficiency Burst",
                        "description": "50% bonus to all gains for 30 seconds",
                        "cooldown": 600,  # 10 minutes
                        "effect": {"all_bonus": 0.5, "duration_seconds": 30}
                    }
                },
                "unlocked": False,
                "unlock_cost": 2000
            },
            "precision_master": {
                "name": "Precision Master",
                "description": "Excel at perfect matches and property detection",
                "icon": "🎯",
                "passive_bonuses": {
                    "property_detection": 0.25,  # +25% detection accuracy
                    "perfect_match_bonus": 0.30,  # +30% SP on perfect matches
                    "timing_windows": True  # Access to timing mechanics
                },
                "active_abilities": {
                    "perfect_prediction": {
                        "name": "Perfect Prediction",
                        "description": "Guaranteed to see one target property",
                        "cooldown": 180,  # 3 minutes
                        "effect": {"reveal_random_property": True}
                    },
                    "precision_strike": {
                        "name": "Precision Strike",
                        "description": "Next roll has +50% chance for perfect match",
                        "cooldown": 480,  # 8 minutes
                        "effect": {"perfect_match_chance": 0.5}
                    }
                },
                "unlocked": False,
                "unlock_cost": 2500
            },
            "luck_weaver": {
                "name": "Luck Weaver",
                "description": "Bend probability and manipulate chance",
                "icon": "✨",
                "passive_bonuses": {
                    "base_luck": 0.08,  # +8% base win chance
                    "lucky_event_freq": 0.20,  # +20% lucky event frequency
                    "karma_generation": 0.15  # +15% karma from actions
                },
                "active_abilities": {
                    "luck_surge": {
                        "name": "Luck Surge",
                        "description": "Massive luck boost for 10 rolls",
                        "cooldown": 900,  # 15 minutes
                        "effect": {"luck_multiplier": 2.0, "duration_rolls": 10}
                    },
                    "probability_shift": {
                        "name": "Probability Shift",
                        "description": "Force favorable outcome for next roll",
                        "cooldown": 1200,  # 20 minutes
                        "effect": {"guaranteed_win": True}
                    }
                },
                "unlocked": False,
                "unlock_cost": 3000
            },
            "streak_warrior": {
                "name": "Streak Warrior",
                "description": "Build unstoppable momentum through consistency",
                "icon": "🔥",
                "passive_bonuses": {
                    "streak_bonus": 0.25,  # +25% streak multipliers
                    "streak_protection": True,  # Reduced streak loss
                    "combo_scaling": 0.20  # +20% combo effectiveness
                },
                "active_abilities": {
                    "streak_shield": {
                        "name": "Streak Shield",
                        "description": "Immune to streak loss for 3 rolls",
                        "cooldown": 240,  # 4 minutes
                        "effect": {"streak_protection": True, "duration_rolls": 3}
                    },
                    "momentum_burst": {
                        "name": "Momentum Burst",
                        "description": "Instantly gain 5 combo points",
                        "cooldown": 720,  # 12 minutes
                        "effect": {"combo_boost": 5}
                    }
                },
                "unlocked": False,
                "unlock_cost": 2200
            }
        }
        
        # Current specialization (None = not chosen yet)
        self.current_specialization = None
        
        # ===== EQUIPMENT SYSTEM =====
        # Persistent upgrades that enhance capabilities
        self.equipment_system = {
            "slots": {
                "primary_weapon": {
                    "name": "Primary Weapon",
                    "description": "Main tool for generating results",
                    "level": 0,
                    "max_level": 20,
                    "effects": {
                        "sp_per_roll": lambda lvl: lvl * 1,
                        "win_chance": lambda lvl: lvl * 0.005
                    },
                    "upgrade_cost": lambda lvl: 100 * (lvl + 1) ** 2
                },
                "luck_charm": {
                    "name": "Luck Charm",
                    "description": "Enhances fortunate outcomes",
                    "level": 0,
                    "max_level": 15,
                    "effects": {
                        "lucky_event_freq": lambda lvl: lvl * 0.02,
                        "karma_generation": lambda lvl: lvl * 0.01
                    },
                    "upgrade_cost": lambda lvl: 150 * (lvl + 1) ** 2
                },
                "precision_lens": {
                    "name": "Precision Lens",
                    "description": "Improves property detection and analysis",
                    "level": 0,
                    "max_level": 15,
                    "effects": {
                        "property_detection": lambda lvl: lvl * 0.015,
                        "analysis_speed": lambda lvl: lvl * 0.1
                    },
                    "upgrade_cost": lambda lvl: 200 * (lvl + 1) ** 2
                },
                "streak_booster": {
                    "name": "Streak Booster",
                    "description": "Enhances momentum and consistency",
                    "level": 0,
                    "max_level": 15,
                    "effects": {
                        "streak_bonus": lambda lvl: lvl * 0.02,
                        "combo_scaling": lambda lvl: lvl * 0.015
                    },
                    "upgrade_cost": lambda lvl: 180 * (lvl + 1) ** 2
                },
                "efficiency_core": {
                    "name": "Efficiency Core",
                    "description": "Optimizes resource generation",
                    "level": 0,
                    "max_level": 10,
                    "effects": {
                        "xp_efficiency": lambda lvl: lvl * 0.025,
                        "sp_efficiency": lambda lvl: lvl * 0.02
                    },
                    "upgrade_cost": lambda lvl: 300 * (lvl + 1) ** 2
                }
            },
            "total_equipment_power": 0
        }
        
        # ===== INVESTMENT SYSTEM =====
        # Passive income generation
        self.investment_system = {
            "portfolios": {
                "conservative_bonds": {
                    "name": "Conservative Bonds",
                    "description": "Stable, low-risk returns",
                    "base_return_rate": 0.02,  # 2% per hour
                    "risk_level": "low",
                    "min_investment": 500,
                    "max_investment": 50000,
                    "current_investment": 0,
                    "total_earned": 0
                },
                "growth_fund": {
                    "name": "Growth Fund",
                    "description": "Moderate risk, higher returns",
                    "base_return_rate": 0.05,  # 5% per hour
                    "risk_level": "medium",
                    "min_investment": 2000,
                    "max_investment": 100000,
                    "current_investment": 0,
                    "total_earned": 0
                },
                "speculative_ventures": {
                    "name": "Speculative Ventures",
                    "description": "High risk, high reward",
                    "base_return_rate": 0.15,  # 15% per hour base
                    "risk_level": "high",
                    "min_investment": 5000,
                    "max_investment": 250000,
                    "current_investment": 0,
                    "total_earned": 0
                }
            },
            "last_collection_time": None,
            "total_invested": 0,
            "total_earned_all_time": 0
        }
        
        # ===== PRESTIGE SYSTEM =====
        # Endgame progression through resets
        self.prestige_system = {
            "current_level": 0,
            "prestige_points": 0,
            "total_prestiges": 0,
            "permanent_bonuses": {
                "sp_multiplier": 0,  # +1% per prestige level
                "xp_multiplier": 0,  # +1% per prestige level
                "luck_bonus": 0,     # +0.5% per prestige level
                "starting_sp": 0     # +10 SP per prestige level
            },
            "available_upgrades": {
                "enhanced_sp": {
                    "name": "Enhanced SP Generation",
                    "description": "+2% SP multiplier per prestige level",
                    "cost": 5,
                    "purchased": False
                },
                "xp_accelerator": {
                    "name": "XP Accelerator",
                    "description": "+2% XP multiplier per prestige level",
                    "cost": 5,
                    "purchased": False
                },
                "legendary_strategies": {
                    "name": "Legendary Strategies",
                    "description": "Unlocks prestige-only strategies",
                    "cost": 15,
                    "purchased": False
                },
                "master_abilities": {
                    "name": "Master Abilities",
                    "description": "Unlocks ultimate specialization abilities",
                    "cost": 25,
                    "purchased": False
                }
            }
        }
        
        # Load progression data
        self._load_progression_data()
        
        # Generate initial quests
        self._generate_daily_quests()
        
        # Check for new unlocks
        self._check_mechanic_unlocks()
        self._check_achievement_progress()
    
    def _load_progression_data(self):
        """Load progression system data"""
        if not self.current_username:
            return
            
        progression_file = f"user_{self.current_username}_progression.json"
        data = self._load_json(progression_file, {})
        
        # Load quests
        self.active_quests = data.get("active_quests", {})
        self.completed_quests = set(data.get("completed_quests", []))
        self.quest_progress = data.get("quest_progress", {})
        
        # Load achievements
        achievements_data = data.get("achievements", {})
        for key, achievement in self.progression_achievements.items():
            achievement["progress"] = achievements_data.get(f"{key}_progress", 0)
            achievement["completed"] = achievements_data.get(f"{key}_completed", False)
            if "tiers" in achievement:
                achievement["current_tier"] = achievements_data.get(f"{key}_tier", 0)
        
        # Load RNG influence
        rng_data = data.get("rng_influence", {})
        self.rng_influence["luck_tokens"]["current_tokens"] = rng_data.get("luck_tokens", 0)
        self.rng_influence["karma_system"]["karma_level"] = rng_data.get("karma_level", 0)
        ritual_data = rng_data.get("rituals", {})
        for ritual_key in self.rng_influence["ritual_system"]["available_rituals"]:
            if ritual_key in ritual_data:
                self.rng_influence["ritual_system"]["available_rituals"][ritual_key]["unlocked"] = ritual_data[ritual_key].get("unlocked", False)
        self.rng_influence["ritual_system"]["active_ritual"] = rng_data.get("active_ritual", None)
        self.rng_influence["ritual_system"]["ritual_end_time"] = rng_data.get("ritual_end_time", None)
        
        # Load mechanic unlocks
        unlocks_data = data.get("mechanic_unlocks", {})
        for key, mechanic in self.mechanic_unlocks.items():
            mechanic["unlocked"] = unlocks_data.get(key, False)
        
        # Load specialization
        self.current_specialization = data.get("current_specialization", None)
        spec_data = data.get("specialization_trees", {})
        for key, spec in self.specialization_trees.items():
            spec["unlocked"] = spec_data.get(f"{key}_unlocked", False)
        
        # Load equipment
        equip_data = data.get("equipment_system", {})
        for slot_key, slot in self.equipment_system["slots"].items():
            slot["level"] = equip_data.get(f"{slot_key}_level", 0)
        self.equipment_system["total_equipment_power"] = equip_data.get("total_power", 0)
        
        # Load investment system
        invest_data = data.get("investment_system", {})
        for portfolio_key, portfolio in self.investment_system["portfolios"].items():
            portfolio["current_investment"] = invest_data.get(f"{portfolio_key}_investment", 0)
            portfolio["total_earned"] = invest_data.get(f"{portfolio_key}_earned", 0)
        self.investment_system["last_collection_time"] = invest_data.get("last_collection", None)
        self.investment_system["total_invested"] = invest_data.get("total_invested", 0)
        self.investment_system["total_earned_all_time"] = invest_data.get("total_earned", 0)
        
        # Load prestige system
        prestige_data = data.get("prestige_system", {})
        self.prestige_system["current_level"] = prestige_data.get("level", 0)
        self.prestige_system["prestige_points"] = prestige_data.get("points", 0)
        self.prestige_system["total_prestiges"] = prestige_data.get("total", 0)
        bonuses_data = prestige_data.get("bonuses", {})
        for bonus_key in self.prestige_system["permanent_bonuses"]:
            self.prestige_system["permanent_bonuses"][bonus_key] = bonuses_data.get(bonus_key, 0)
        upgrades_data = prestige_data.get("upgrades", {})
        for upgrade_key in self.prestige_system["available_upgrades"]:
            self.prestige_system["available_upgrades"][upgrade_key]["purchased"] = upgrades_data.get(f"{upgrade_key}_purchased", False)
    
    def _save_progression_data(self):
        """Save progression system data"""
        if not self.current_username:
            return
            
        progression_file = f"user_{self.current_username}_progression.json"
        achievements_data = {}
        for key, achievement in self.progression_achievements.items():
            achievements_data[key] = {
                "progress": achievement["progress"],
                "completed": achievement["completed"],
                "tier": achievement.get("current_tier", 0)
            }

        data = {
            "active_quests": self.active_quests,
            "completed_quests": list(self.completed_quests),
            "quest_progress": self.quest_progress,
            "achievements": achievements_data,
            "rng_influence": {
                "luck_tokens": self.rng_influence["luck_tokens"]["current_tokens"],
                "karma_level": self.rng_influence["karma_system"]["karma_level"],
                "rituals": {
                    ritual_key: {"unlocked": ritual["unlocked"]}
                    for ritual_key, ritual in self.rng_influence["ritual_system"]["available_rituals"].items()
                },
                "active_ritual": self.rng_influence["ritual_system"]["active_ritual"],
                "ritual_end_time": self.rng_influence["ritual_system"]["ritual_end_time"]
            },
            "mechanic_unlocks": {k: v["unlocked"] for k, v in self.mechanic_unlocks.items()},
            "current_specialization": self.current_specialization,
            "specialization_trees": {
                f"{key}_unlocked": spec["unlocked"]
                for key, spec in self.specialization_trees.items()
            },
            "equipment_system": {
                **{f"{slot_key}_level": slot["level"] for slot_key, slot in self.equipment_system["slots"].items()},
                "total_power": self.equipment_system["total_equipment_power"]
            },
            "investment_system": {
                **{f"{portfolio_key}_investment": portfolio["current_investment"] for portfolio_key, portfolio in self.investment_system["portfolios"].items()},
                **{f"{portfolio_key}_earned": portfolio["total_earned"] for portfolio_key, portfolio in self.investment_system["portfolios"].items()},
                "last_collection": self.investment_system["last_collection_time"],
                "total_invested": self.investment_system["total_invested"],
                "total_earned": self.investment_system["total_earned_all_time"]
            },
            "prestige_system": {
                "level": self.prestige_system["current_level"],
                "points": self.prestige_system["prestige_points"],
                "total": self.prestige_system["total_prestiges"],
                "bonuses": self.prestige_system["permanent_bonuses"],
                "upgrades": {
                    f"{upgrade_key}_purchased": upgrade["purchased"]
                    for upgrade_key, upgrade in self.prestige_system["available_upgrades"].items()
                }
            }
        }
        self._save_json(progression_file, data)
    
    def _check_milestone_unlocks(self):
        """Check and trigger milestone unlocks"""
        new_unlocks = []
        
        for key, milestone in self.milestone_unlocks.items():
            if not milestone["unlocked"] and milestone["requirement"]():
                milestone["unlocked"] = True
                new_unlocks.append(milestone)
                
                # Enable the unlocked mechanics
                for unlock in milestone["unlocks"]:
                    if unlock in self.unlocked_mechanics:
                        self.unlocked_mechanics[unlock]["enabled"] = True
        
        if new_unlocks:
            self._save_progression_data()
            self._show_milestone_unlock_popup(new_unlocks)
    
    def _show_milestone_unlock_popup(self, unlocks):
        """Show popup for new milestone unlocks"""
        if not unlocks:
            return
            
        unlock_text = "\n\n".join([
            f"🎉 {unlock['name']}\n{unlock['description']}\nReward: {unlock['reward']}"
            for unlock in unlocks
        ])
        
        messagebox.showinfo("Milestone Unlocked!", 
                          f"Congratulations! You've unlocked:\n\n{unlock_text}")
    
    # ===== QUEST SYSTEM METHODS =====
    
    def _generate_daily_quests(self):
        """Generate daily quests for the player"""
        import random
        
        # Clear old daily quests
        self.active_quests = {k: v for k, v in self.active_quests.items() if v.get("type") != "daily"}
        
        # Generate 3 random daily quests
        available_templates = list(self.quest_templates.keys())
        selected_templates = random.sample(available_templates, min(3, len(available_templates)))
        
        for template_key in selected_templates:
            template = self.quest_templates[template_key]
            quest_id = f"daily_{template_key}_{random.randint(1000, 9999)}"
            
            # Choose appropriate tier based on player level
            tier_index = min(self.player_level // 10, len(template["tiers"]) - 1)
            tier = template["tiers"][tier_index]
            
            self.active_quests[quest_id] = {
                "template": template_key,
                "name": template["name"],
                "description": template["description"].format(target=tier["target"]),
                "type": "daily",
                "target": tier["target"],
                "current": 0,
                "reward_xp": tier["reward_xp"],
                "reward_sp": tier["reward_sp"],
                "reward_title": tier["reward_title"],
                "generated_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
    
    def _update_quest_progress(self, quest_type, amount=1):
        """Update progress for quests of a specific type"""
        for quest_id, quest in self.active_quests.items():
            if quest["type"] == quest_type:
                quest["current"] = min(quest["current"] + amount, quest["target"])
                
                # Check if quest completed
                if quest["current"] >= quest["target"] and quest_id not in self.completed_quests:
                    self._complete_quest(quest_id)
    
    def _complete_quest(self, quest_id):
        """Complete a quest and give rewards"""
        if quest_id in self.completed_quests:
            return
            
        quest = self.active_quests[quest_id]
        self.completed_quests.add(quest_id)
        
        # Give rewards
        self._add_xp(quest["reward_xp"])
        self.sp += quest["reward_sp"]
        
        # Update player title if better
        if quest.get("reward_title"):
            # Could implement title system here
            pass
        
        # Show completion message
        messagebox.showinfo("Quest Completed!", 
                          f"🎉 {quest['name']} Complete!\n\n"
                          f"Rewards: {quest['reward_xp']} XP, {quest['reward_sp']} SP")
        
        # Save progress
        self._save_progression_data()
    
    # ===== ACHIEVEMENT SYSTEM METHODS =====
    
    def _check_achievement_progress(self):
        """Check and update achievement progress"""
        new_completions = []
        
        for key, achievement in self.progression_achievements.items():
            old_completed = achievement["completed"]
            
            # Update progress
            if callable(achievement["progress"]):
                achievement["progress"] = achievement["progress"]()
            
            # Check tiered achievements
            if "tiers" in achievement:
                current_tier = 0
                for i, tier_target in enumerate(achievement["tiers"]):
                    if achievement["progress"] >= tier_target:
                        current_tier = i + 1
                
                if current_tier > achievement.get("current_tier", 0):
                    achievement["current_tier"] = current_tier
                    if not old_completed:
                        achievement["completed"] = True
                        new_completions.append(achievement)
                        
                        # Give tier rewards
                        reward_data = achievement["reward_per_tier"]
                        reward_xp = reward_data.get("xp", 0) if isinstance(reward_data, dict) else reward_data[0]
                        reward_sp = reward_data.get("sp", 0) if isinstance(reward_data, dict) else reward_data[1]
                        self._add_xp(reward_xp * current_tier)
                        self.sp += reward_sp * current_tier
            else:
                # Single achievements
                if not achievement["completed"] and achievement["progress"] >= achievement["requirement"]():
                    achievement["completed"] = True
                    new_completions.append(achievement)
                    
                    # Give rewards
                    if "reward" in achievement:
                        reward = achievement["reward"]
                        if "xp" in reward:
                            self._add_xp(reward["xp"])
                        if "sp" in reward:
                            self.sp += reward["sp"]
                        if "title" in reward:
                            # Could set player title
                            pass
        
        # Show completion messages (only if GUI is ready)
        if new_completions and hasattr(self, 'root') and self.root.winfo_exists():
            completion_text = "\n\n".join([
                f"{ach['icon']} {ach['name']}\n{ach.get('description', '')}"
                for ach in new_completions
            ])
            try:
                messagebox.showinfo("Achievement Unlocked!", 
                                  f"Congratulations!\n\n{completion_text}")
            except Exception:
                pass
            
            self._save_progression_data()
    
    # ===== RNG INFLUENCE METHODS =====
    
    def _update_karma(self, action_type, outcome_quality):
        """Update karma based on player actions and outcomes"""
        karma_change = 0
        
        if action_type == "win":
            karma_change = 2 if outcome_quality == "good" else 1
        elif action_type == "loss":
            karma_change = -1 if outcome_quality == "bad" else -2
        elif action_type == "lucky_event":
            karma_change = 3
        elif action_type == "ritual_performed":
            karma_change = 5
        
        # Apply specialization bonus
        if self.current_specialization == "luck_weaver":
            karma_change = int(karma_change * 1.15)
        
        self.rng_influence["karma_system"]["karma_level"] += karma_change
        
        # Clamp karma between -100 and 100
        self.rng_influence["karma_system"]["karma_level"] = max(-100, min(100, self.rng_influence["karma_system"]["karma_level"]))
    
    def _generate_luck_tokens(self, reason):
        """Generate luck tokens based on various actions"""
        tokens_gained = 0
        
        if reason == "win_streak":
            tokens_gained = min(self.winning_streak, 5)  # Max 5 tokens per streak
        elif reason == "perfect_win":
            tokens_gained = 3
        elif reason == "quest_complete":
            tokens_gained = 2
        elif reason == "achievement_unlock":
            tokens_gained = 5
        
        self.rng_influence["luck_tokens"]["current_tokens"] += tokens_gained
        
        # Cap at max tokens
        max_tokens = self.rng_influence["luck_tokens"]["max_tokens"]
        self.rng_influence["luck_tokens"]["current_tokens"] = min(self.rng_influence["luck_tokens"]["current_tokens"], max_tokens)
    
    def _use_luck_token(self, ability_key):
        """Use a luck token ability"""
        if self.rng_influence["luck_tokens"]["current_tokens"] < self.rng_influence["luck_tokens"]["abilities"][ability_key]["cost"]:
            return False
        
        # Deduct tokens
        self.rng_influence["luck_tokens"]["current_tokens"] -= self.rng_influence["luck_tokens"]["abilities"][ability_key]["cost"]
        
        # Apply effect
        effect = self.rng_influence["luck_tokens"]["abilities"][ability_key]["effect"]
        
        if "win_chance_bonus" in effect:
            # Store temporary bonus for next roll
            self.temp_luck_boost += effect["win_chance_bonus"]
        elif "reveal_property" in effect:
            # Reveal a random target property
            if self.target_properties:
                revealed_prop = random.choice(list(self.target_properties))
                messagebox.showinfo("Property Revealed", f"Target property: {revealed_prop}")
        elif "streak_protection" in effect:
            # Protect streak from loss
            self.streak_protection_active = True
        elif "reward_multiplier" in effect:
            # Double next reward
            self.reward_multiplier_active = effect["reward_multiplier"]
        
        self._save_progression_data()
        return True
    
    def _perform_ritual(self, ritual_key):
        """Perform a luck ritual"""
        import time
        
        ritual = self.rng_influence["ritual_system"]["available_rituals"][ritual_key]
        
        if not ritual["unlocked"]:
            return False
        
        # Check if another ritual is active
        if self.rng_influence["ritual_system"]["active_ritual"]:
            messagebox.showerror("Ritual Active", "Another ritual is already active!")
            return False
        
        # Start ritual
        self.rng_influence["ritual_system"]["active_ritual"] = ritual_key
        self.rng_influence["ritual_system"]["ritual_end_time"] = time.time() + ritual["duration"]
        
        # Apply immediate effects
        effect = ritual["effect"]
        if "concentration_bonus" in effect:
            self.temp_concentration_bonus = effect["concentration_bonus"]
        elif "luck_bonus" in effect:
            self.temp_luck_boost += effect["luck_bonus"]
        elif "precision_bonus" in effect:
            self.temp_precision_bonus = effect["precision_bonus"]
        
        messagebox.showinfo("Ritual Started", f"Performing {ritual['name']} for {ritual['duration']} seconds...")
        
        self._save_progression_data()
        return True
    
    def _update_rituals(self):
        """Update active rituals and remove expired ones"""
        import time
        
        if self.rng_influence["ritual_system"]["active_ritual"]:
            if time.time() >= self.rng_influence["ritual_system"]["ritual_end_time"]:
                # Ritual expired
                ritual_key = self.rng_influence["ritual_system"]["active_ritual"]
                ritual = self.rng_influence["ritual_system"]["available_rituals"][ritual_key]
                
                # Remove effects
                effect = ritual["effect"]
                if "concentration_bonus" in effect:
                    self.temp_concentration_bonus = 0
                elif "luck_bonus" in effect:
                    self.temp_luck_boost = max(0, self.temp_luck_boost - effect["luck_bonus"])
                elif "precision_bonus" in effect:
                    self.temp_precision_bonus = 0
                
                self.rng_influence["ritual_system"]["active_ritual"] = None
                self.rng_influence["ritual_system"]["ritual_end_time"] = None
                
                messagebox.showinfo("Ritual Complete", f"{ritual['name']} has ended.")
                
                self._save_progression_data()
    
    # ===== MECHANIC UNLOCK METHODS =====
    
    def _check_mechanic_unlocks(self):
        """Check and unlock new mechanics based on progress"""
        new_unlocks = []
        
        for key, mechanic in self.mechanic_unlocks.items():
            if not mechanic["unlocked"] and mechanic["unlock_requirement"]():
                mechanic["unlocked"] = True
                new_unlocks.append((key, mechanic))
                
                # Special handling for certain unlocks
                if key == "strategy_system":
                    pass  # Already handled in strategy system
                elif key == "quest_system":
                    self._generate_daily_quests()
                elif key == "rng_influence":
                    self.rng_influence["ritual_system"]["available_rituals"]["luck_ritual"]["unlocked"] = True
                elif key == "equipment_basics":
                    # Give starter equipment
                    self.equipment_system["slots"]["primary_weapon"]["level"] = max(
                        self.equipment_system["slots"]["primary_weapon"]["level"], 1)
                elif key == "advanced_equipment":
                    self.rng_influence["ritual_system"]["available_rituals"]["precision_ritual"]["unlocked"] = True
                elif key == "investment_system":
                    self.auto_invest_enabled = True
                elif key == "prestige_system":
                    pass  # Just unlocks the prestige UI
                elif key == "master_mechanics":
                    self.critical_roll_chance = 0.05  # 5% crit chance
        
        if new_unlocks:
            for key, unlock in new_unlocks:
                self._show_mechanic_tutorial(key, unlock)
            self._save_progression_data()
    
    def _show_mechanic_tutorial(self, mechanic_key, mechanic):
        """Show a rich guided tutorial window when a new mechanic unlocks"""
        if mechanic_key in self.seen_tutorials:
            return
        self.seen_tutorials.add(mechanic_key)
        
        # Tutorial content for each mechanic
        tutorials = {
            "basic_progression": {
                "title": "🎮 Welcome to Progression!",
                "body": (
                    "You've unlocked the PROGRESSION SYSTEM!\n\n"
                    "• Every roll earns XP towards your next level\n"
                    "• Winning gives bonus XP and SP rewards\n"
                    "• Win streaks multiply your SP earnings\n"
                    "• Higher levels unlock powerful new mechanics\n\n"
                    "Keep rolling to level up and unlock new abilities!"
                ),
                "tip": "💡 TIP: Win streaks of 3+ give SP multipliers!"
            },
            "strategy_system": {
                "title": "🧠 Strategy System Unlocked! (Level 3)",
                "body": (
                    "You can now choose ROLL STRATEGIES!\n\n"
                    "• Open the Strategy Panel from the Tools menu\n"
                    "• Different strategies change how rolls are evaluated\n"
                    "• Some strategies favor speed, others favor precision\n"
                    "• Strategies interact with your equipment and specialization\n\n"
                    "NEW ABILITY: You gain 1 REROLL charge every 10 rolls!\n"
                    "Use rerolls to retry unfavorable outcomes."
                ),
                "tip": "💡 TIP: Match your strategy to your current quest goals!"
            },
            "equipment_basics": {
                "title": "⚔️ Equipment System Unlocked! (Level 5)",
                "body": (
                    "You can now UPGRADE EQUIPMENT for permanent bonuses!\n\n"
                    "• Open Equipment Crafting from the Tools menu\n"
                    "• 5 equipment slots: Weapon, Luck Charm, Precision Lens, Streak Booster, Core\n"
                    "• Each upgrade costs SP but provides lasting benefits\n"
                    "• Equipment bonuses stack with strategy and specialization\n\n"
                    "NEW ABILITY: Your Primary Weapon now gives +1 SP per roll!\n"
                    "Upgrade it to increase this bonus."
                ),
                "tip": "💡 TIP: Upgrade Luck Charm early for better win chances!"
            },
            "quest_system": {
                "title": "📜 Quest System Unlocked! (Level 7)",
                "body": (
                    "Daily QUESTS are now available!\n\n"
                    "• Open Progression from the Tools menu to see active quests\n"
                    "• Quests give XP, SP, and unlock special titles\n"
                    "• Quest difficulty scales with your level\n"
                    "• Completing quests generates Luck Tokens\n"
                    "• Quest progress feeds into achievement tracking\n\n"
                    "NEW ABILITY: Property Scanner — once per session,\n"
                    "reveal ALL target properties for your current sequence!"
                ),
                "tip": "💡 TIP: Focus on streak quests for maximum reward efficiency!"
            },
            "rng_influence": {
                "title": "🎲 RNG Influence Unlocked! (Level 10)",
                "body": (
                    "You can now INFLUENCE random outcomes!\n\n"
                    "• LUCK TOKENS: Spend to boost win chance, reveal properties,\n"
                    "  protect streaks, or double rewards\n"
                    "• KARMA SYSTEM: Good play builds karma for better luck\n"
                    "• LUCKY RITUALS: Perform rituals for timed bonuses\n\n"
                    "NEW ABILITY: Streak Shield — losing a roll no longer\n"
                    "resets your streak if you have Luck Tokens!"
                ),
                "tip": "💡 TIP: Save Double Reward tokens for high-SP wins!"
            },
            "advanced_equipment": {
                "title": "🛡️ Advanced Equipment Unlocked! (Level 15)",
                "body": (
                    "Powerful new equipment upgrades are available!\n\n"
                    "• Equipment can now reach higher upgrade levels\n"
                    "• Precision Ritual unlocked for better property detection\n"
                    "• Equipment synergizes with your specialization\n\n"
                    "NEW ABILITY: Critical Rolls — every roll has a chance\n"
                    "to be a CRITICAL, giving 3× SP and XP!"
                ),
                "tip": "💡 TIP: High-level Precision Lens makes critical rolls more common!"
            },
            "investment_system": {
                "title": "💰 Investment System Unlocked!",
                "body": (
                    "You can now INVEST SP for passive income!\n\n"
                    "• Open Progression → Investments tab\n"
                    "• 3 portfolios: Conservative (safe), Growth (moderate), Speculative (risky)\n"
                    "• Returns accumulate over real time\n"
                    "• Auto-Invest: A portion of SP earned is automatically invested\n\n"
                    "NEW ABILITY: Every win now auto-invests 5% of SP earned\n"
                    "into your highest-return portfolio!"
                ),
                "tip": "💡 TIP: Diversify investments to balance risk and reward!"
            },
            "prestige_system": {
                "title": "⭐ Prestige System Unlocked! (Level 25)",
                "body": (
                    "The ultimate endgame mechanic: PRESTIGE!\n\n"
                    "• Reset your level, SP, and equipment for Prestige Points\n"
                    "• Prestige Points buy PERMANENT bonuses that persist forever\n"
                    "• Each prestige makes you stronger than before\n"
                    "• Unlock prestige-exclusive upgrades and strategies\n\n"
                    "NEW ABILITY: Prestige Aura — permanently increases\n"
                    "all SP/XP gains by 1% per prestige level!"
                ),
                "tip": "💡 TIP: Max your equipment before prestiging for more points!"
            },
            "master_mechanics": {
                "title": "🏆 Master Mechanics Unlocked! (1000 Wins)",
                "body": (
                    "You've reached MASTERY! The ultimate mechanics are yours!\n\n"
                    "• CRITICAL ROLLS: 5% base chance for 3× rewards\n"
                    "• MASTERY BONUS: +25% to all SP and XP gains\n"
                    "• ULTIMATE RITUALS: Access to the most powerful rituals\n"
                    "• LEGACY TITLES: Exclusive titles for master players\n\n"
                    "Your legacy will be remembered forever.\n"
                    "You've mastered the art of the roll!"
                ),
                "tip": "💡 TIP: Combine critical rolls with Double Reward for insane SP!"
            }
        }
        
        tutorial = tutorials.get(mechanic_key, {
            "title": f"🔓 {mechanic['name']} Unlocked!",
            "body": f"{mechanic['description']}\n\nExplore the Tools menu to access this new feature!",
            "tip": "💡 TIP: Check the Progression panel for details!"
        })
        
        # Show a rich tutorial window
        tut_win = tk.Toplevel(self.root)
        tut_win.title(tutorial["title"])
        tut_win.geometry("520x420")
        tut_win.configure(bg="#1a1a2e")
        tut_win.resizable(False, False)
        tut_win.transient(self.root)
        tut_win.grab_set()
        
        # Header
        header = tk.Label(tut_win, text=tutorial["title"],
                         font=("Segoe UI", 16, "bold"), bg="#1a1a2e", fg="#e94560")
        header.pack(pady=(15, 5))
        
        # Separator
        sep = tk.Frame(tut_win, height=2, bg="#e94560")
        sep.pack(fill=tk.X, padx=30, pady=5)
        
        # Body
        body = tk.Label(tut_win, text=tutorial["body"],
                       font=("Segoe UI", 10), bg="#1a1a2e", fg="#ffffff",
                       justify=tk.LEFT, wraplength=460)
        body.pack(padx=30, pady=10, anchor=tk.W)
        
        # Tip box
        tip_frame = tk.Frame(tut_win, bg="#16213e", padx=10, pady=8)
        tip_frame.pack(fill=tk.X, padx=30, pady=5)
        
        tip_label = tk.Label(tip_frame, text=tutorial["tip"],
                            font=("Segoe UI", 9, "italic"), bg="#16213e", fg="#ffd700",
                            wraplength=440, justify=tk.LEFT)
        tip_label.pack()
        
        # OK button
        ok_btn = tk.Button(tut_win, text="Got it! Let's go! 🚀",
                          font=("Segoe UI", 11, "bold"), bg="#e94560", fg="#ffffff",
                          padx=20, pady=8, command=tut_win.destroy,
                          activebackground="#c81e45", activeforeground="#ffffff")
        ok_btn.pack(pady=15)
        
        # Play achievement sound
        try:
            self._play_achievement_sound()
        except Exception:
            pass
    
    def _apply_level_milestone_rewards(self):
        """Apply concrete gameplay changes at specific level milestones"""
        level = self.player_level
        
        # Level 2: First taste of power — small permanent luck boost
        if level == 2:
            self.temp_luck_boost += 0.02
        
        # Level 3: Reroll charges start generating
        if level >= 3 and level % 3 == 0:
            self.reroll_charges = min(self.reroll_charges + 1, 5)
        
        # Level 5: Equipment SP bonus kicks in
        if level == 5:
            pass  # Handled by equipment unlock
        
        # Level 8: Enhanced streak protection
        if level == 8:
            self.streak_protection_active = True
        
        # Level 10: Karma bonus on level up
        if level >= 10:
            self._update_karma("lucky_event", "good")
        
        # Level 12: Extra luck token capacity
        if level == 12:
            self.rng_influence["luck_tokens"]["max_tokens"] = 15
        
        # Level 15: Critical roll chance begins
        if level == 15:
            self.critical_roll_chance = 0.03  # 3%
        
        # Level 20: Enhanced critical chance
        if level == 20:
            self.critical_roll_chance = 0.05  # 5%
            self.rng_influence["luck_tokens"]["max_tokens"] = 20
        
        # Level 25: Prestige unlocks — mark the occasion
        if level == 25:
            self.critical_roll_chance = 0.07  # 7%
        
        # Every 5 levels: Free luck tokens
        if level % 5 == 0:
            tokens = level // 5
            self.rng_influence["luck_tokens"]["current_tokens"] = min(
                self.rng_influence["luck_tokens"]["current_tokens"] + tokens,
                self.rng_influence["luck_tokens"]["max_tokens"]
            )
        
        # Every 10 levels: Permanent SP bonus
        if level % 10 == 0:
            bonus_sp = level * 5
            self.sp += bonus_sp
    
    def _get_next_unlock_info(self):
        """Get info about the next mechanic unlock milestone"""
        unlock_levels = {
            "strategy_system": 3,
            "equipment_basics": 5,
            "quest_system": 7,
            "rng_influence": 10,
            "advanced_equipment": 15,
            "prestige_system": 25
        }
        
        for key, required_level in sorted(unlock_levels.items(), key=lambda x: x[1]):
            if not self.mechanic_unlocks.get(key, {}).get("unlocked", False):
                mechanic = self.mechanic_unlocks.get(key, {})
                return {
                    "name": mechanic.get("name", key),
                    "level": required_level,
                    "levels_away": required_level - self.player_level,
                    "description": mechanic.get("description", "")
                }
        
        # All level-based unlocks achieved
        # Check wins-based unlock
        if not self.mechanic_unlocks.get("master_mechanics", {}).get("unlocked", False):
            wins = self.meta_progression.get("total_wins_all_time", 0)
            return {
                "name": "Master Mechanics",
                "level": None,
                "levels_away": None,
                "wins_needed": 1000 - wins,
                "description": "Ultimate progression systems"
            }
        
        return None  # Everything unlocked
    
    def _update_unlock_progress_bar(self):
        """Update the unlock progress bar in the main GUI"""
        # Update level display
        if hasattr(self, 'level_display_label'):
            self.level_display_label.config(
                text=f"⭐ Level {self.player_level}  |  XP: {self.player_xp}/{self.xp_to_level_up}")
        
        # Update reroll charges display
        if hasattr(self, 'reroll_display_label'):
            self.reroll_display_label.config(text=f"🔄 Rerolls: {self.reroll_charges}")
        
        # Update luck tokens display
        if hasattr(self, 'tokens_display_label'):
            try:
                tokens = self.rng_influence["luck_tokens"]["current_tokens"]
            except (AttributeError, KeyError, TypeError):
                tokens = 0
            self.tokens_display_label.config(text=f"🍀 Tokens: {tokens}")
        
        # Show/hide reroll button based on level
        if hasattr(self, 'reroll_button'):
            unlocked = self.mechanic_unlocks.get("strategy_guide", {}).get("unlocked", False)
            if unlocked:
                self.reroll_button.grid()
            else:
                self.reroll_button.grid_remove()
        
        # Show/hide scanner button based on quest unlock
        if hasattr(self, 'scanner_button'):
            unlocked = self.mechanic_unlocks.get("quest_system", {}).get("unlocked", False)
            if unlocked:
                self.scanner_button.grid()
            else:
                self.scanner_button.grid_remove()
        
        if not hasattr(self, 'unlock_progress_label'):
            return
        
        next_unlock = self._get_next_unlock_info()
        if next_unlock is None:
            self.unlock_progress_label.config(
                text="🏆 ALL MECHANICS UNLOCKED!", fg="#ffd700")
            if hasattr(self, 'unlock_bar_canvas'):
                self.unlock_bar_canvas.delete("all")
                self.unlock_bar_canvas.create_rectangle(0, 0, 200, 12, fill="#ffd700", outline="")
            return
        
        if next_unlock.get("level"):
            levels_away = next_unlock["levels_away"]
            req_level = next_unlock["level"]
            # Progress from previous unlock to this one
            prev_milestones = [3, 5, 7, 10, 15, 25]
            prev_level = 1
            for m in prev_milestones:
                if m < req_level:
                    prev_level = m
                else:
                    break
            
            progress = (self.player_level - prev_level) / max(1, req_level - prev_level)
            progress = max(0, min(1, progress))
            
            self.unlock_progress_label.config(
                text=f"Next: {next_unlock['name']} (Lv.{req_level}, {levels_away} away)",
                fg="#00ccff")
        else:
            wins_needed = next_unlock.get("wins_needed", 0)
            total_wins = self.meta_progression.get("total_wins_all_time", 0)
            progress = total_wins / 1000.0
            progress = max(0, min(1, progress))
            
            self.unlock_progress_label.config(
                text=f"Next: {next_unlock['name']} ({wins_needed} wins away)",
                fg="#00ccff")
        
        if hasattr(self, 'unlock_bar_canvas'):
            self.unlock_bar_canvas.delete("all")
            bar_width = 200
            bar_height = 12
            # Background
            self.unlock_bar_canvas.create_rectangle(0, 0, bar_width, bar_height, 
                                                     fill="#333333", outline="#555555")
            # Fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                # Gradient-like color from red to green
                if progress < 0.5:
                    color = self._ui["warning"]
                elif progress < 0.8:
                    color = self._ui["gold"]
                else:
                    color = self._ui["success"]
                self.unlock_bar_canvas.create_rectangle(0, 0, fill_width, bar_height,
                                                         fill=color, outline="")
    
    def use_reroll(self):
        """Use a reroll charge to reroll the current result"""
        if self.reroll_charges <= 0:
            messagebox.showwarning("No Rerolls", "You don't have any reroll charges!\nEarn them by leveling up (1 every 3 levels).")
            return False
        
        self.reroll_charges -= 1
        # Perform a new roll without incrementing roll count
        s = self._generate_random_string()
        properties = self._analyze_string(s)
        self._update_display(s, properties)
        
        # Check if this reroll won
        won = properties == self.target_properties
        if won:
            messagebox.showinfo("Reroll Success!", f"🎉 Your reroll was a winner!\nRerolls remaining: {self.reroll_charges}")
        else:
            matches = len(properties & self.target_properties)
            total = len(self.target_properties)
            messagebox.showinfo("Rerolled!", f"New result: {matches}/{total} matches\nRerolls remaining: {self.reroll_charges}")
        
        return won
    
    def use_property_scanner(self):
        """Reveal all target properties for the current sequence"""
        if not self.mechanic_unlocks.get("quest_system", {}).get("unlocked", False):
            messagebox.showwarning("Locked", "Unlock the Quest System (Level 7) to use the Property Scanner!")
            return
        
        if self.property_scanner_active:
            messagebox.showwarning("Already Used", "You've already used the Property Scanner this session!")
            return
        
        self.property_scanner_active = True
        props_list = "\n".join([f"  • {self._property_name_display(p)}" for p in sorted(self.target_properties)])
        messagebox.showinfo("🔍 Property Scanner", 
                          f"TARGET PROPERTIES REVEALED:\n\n{props_list}\n\n"
                          f"(Scanner can be used once per session)")
    
    # ===== SPECIALIZATION METHODS =====
    
    def _unlock_specialization(self, spec_key):
        """Unlock a specialization tree"""
        spec = self.specialization_trees[spec_key]
        
        if spec["unlocked"]:
            messagebox.showerror("Already Unlocked", "This specialization is already unlocked!")
            return False
        
        if self.sp < spec["unlock_cost"]:
            messagebox.showerror("Insufficient SP", f"You need {spec['unlock_cost']} SP to unlock this specialization!")
            return False
        
        # Unlock it
        self.sp -= spec["unlock_cost"]
        spec["unlocked"] = True
        
        # Set as current if none selected
        if not self.current_specialization:
            self.current_specialization = spec_key
        
        messagebox.showinfo("Specialization Unlocked!", 
                          f"🎯 {spec['name']} unlocked!\n\n{spec['description']}")
        
        self._save_progression_data()
        self._update_display()
        return True
    
    def _switch_specialization(self, spec_key):
        """Switch to a different specialization"""
        if spec_key not in self.specialization_trees or not self.specialization_trees[spec_key]["unlocked"]:
            return False
        
        self.current_specialization = spec_key
        self._save_progression_data()
        
        spec = self.specialization_trees[spec_key]
        messagebox.showinfo("Specialization Changed", f"Now using: {spec['name']}")
        return True
    
    # ===== EQUIPMENT METHODS =====
    
    def _upgrade_equipment_slot(self, slot_key):
        """Upgrade an equipment slot"""
        slot = self.equipment_system["slots"][slot_key]
        
        if slot["level"] >= slot["max_level"]:
            messagebox.showerror("Max Level", "This equipment is already at maximum level!")
            return False
        
        upgrade_cost = slot["upgrade_cost"](slot["level"])
        
        if self.sp < upgrade_cost:
            messagebox.showerror("Insufficient SP", f"You need {upgrade_cost} SP to upgrade this equipment!")
            return False
        
        # Upgrade it
        self.sp -= upgrade_cost
        slot["level"] += 1
        
        # Recalculate total equipment power
        self.equipment_system["total_equipment_power"] = sum(
            slot["level"] for slot in self.equipment_system["slots"].values()
        )
        
        messagebox.showinfo("Equipment Upgraded!", 
                          f"{slot['name']} upgraded to level {slot['level']}!")
        
        self._save_progression_data()
        self._update_display()
        return True
    
    # ===== INVESTMENT METHODS =====
    
    def _invest_in_portfolio(self, portfolio_key, amount):
        """Invest SP in a portfolio"""
        portfolio = self.investment_system["portfolios"][portfolio_key]
        
        if amount < portfolio["min_investment"]:
            messagebox.showerror("Minimum Investment", f"Minimum investment is {portfolio['min_investment']} SP!")
            return False
        
        if amount > portfolio["max_investment"]:
            messagebox.showerror("Maximum Investment", f"Maximum investment is {portfolio['max_investment']} SP!")
            return False
        
        if self.sp < amount:
            messagebox.showerror("Insufficient SP", f"You need {amount} SP to make this investment!")
            return False
        
        # Make investment
        self.sp -= amount
        portfolio["current_investment"] += amount
        self.investment_system["total_invested"] += amount
        
        messagebox.showinfo("Investment Made!", 
                          f"Invested {amount} SP in {portfolio['name']}!")
        
        self._save_progression_data()
        self._update_display()
        return True
    
    def _collect_investment_returns(self):
        """Collect returns from all investments"""
        import time
        
        now = time.time()
        total_collected = 0
        
        for portfolio in self.investment_system["portfolios"].values():
            if portfolio["current_investment"] > 0:
                # Calculate time passed since last collection
                time_passed_hours = 1  # Default 1 hour for first collection
                if self.investment_system["last_collection_time"]:
                    time_passed_hours = (now - self.investment_system["last_collection_time"]) / 3600
                
                # Calculate returns based on risk level
                base_return = portfolio["base_return_rate"] * portfolio["current_investment"] * time_passed_hours
                
                # Apply risk modifier (simulated volatility)
                import random
                risk_modifier = 1.0
                if portfolio["risk_level"] == "medium":
                    risk_modifier = random.uniform(0.8, 1.3)
                elif portfolio["risk_level"] == "high":
                    risk_modifier = random.uniform(0.5, 2.0)
                
                actual_return = int(base_return * risk_modifier)
                
                if actual_return > 0:
                    portfolio["total_earned"] += actual_return
                    self.investment_system["total_earned_all_time"] += actual_return
                    total_collected += actual_return
        
        if total_collected > 0:
            self.sp += total_collected
            self.investment_system["last_collection_time"] = now
            
            messagebox.showinfo("Returns Collected!", 
                              f"Collected {total_collected} SP from investments!")
            
            self._save_progression_data()
            self._update_display()
        else:
            messagebox.showinfo("No Returns", "No investment returns available yet.")
    
    # ===== PRESTIGE METHODS =====
    
    def _perform_prestige_reset(self):
        """Perform a prestige reset"""
        if not messagebox.askyesno("Confirm Prestige", 
                                 "Prestige will reset your progress but grant permanent bonuses.\n\nContinue?"):
            return False
        
        # Calculate prestige points based on achievements
        prestige_points = 0
        prestige_points += self.player_level // 5  # 1 point per 5 levels
        prestige_points += len(self.completed_quests) // 10  # 1 point per 10 quests
        prestige_points += sum(1 for ach in self.achievements.values() if ach["completed"])  # 1 point per achievement
        
        # Reset progress
        self.player_level = 1
        self.player_xp = 0
        self.sp = 10  # Small starting bonus
        self.winning_streak = 0
        self.max_winning_streak = 0
        
        # Reset equipment (keep some progress)
        for slot in self.equipment_system["slots"].values():
            slot["level"] = max(1, slot["level"] // 2)  # Keep half levels
        
        # Reset specializations (but keep unlocked)
        self.current_specialization = None
        
        # Grant prestige level and points
        self.prestige_system["current_level"] += 1
        self.prestige_system["prestige_points"] += prestige_points
        self.prestige_system["total_prestiges"] += 1
        
        messagebox.showinfo("Prestige Complete!", 
                          f"Prestige Level {self.prestige_system['current_level']} achieved!\n"
                          f"Gained {prestige_points} prestige points!\n\n"
                          f"All progress reset with permanent bonuses.")
        
        self._save_progression_data()
        self._update_display()
        return True
    
    def _purchase_prestige_upgrade(self, upgrade_key):
        """Purchase a prestige upgrade"""
        upgrade = self.prestige_system["available_upgrades"][upgrade_key]
        
        if upgrade["purchased"]:
            messagebox.showerror("Already Purchased", "This upgrade is already purchased!")
            return False
        
        if self.prestige_system["prestige_points"] < upgrade["cost"]:
            messagebox.showerror("Insufficient Points", f"You need {upgrade['cost']} prestige points!")
            return False
        
        # Purchase upgrade
        self.prestige_system["prestige_points"] -= upgrade["cost"]
        upgrade["purchased"] = True
        
        messagebox.showinfo("Upgrade Purchased!", f"Purchased: {upgrade['name']}")
        
        self._save_progression_data()
        return True
    
    # ===== INTEGRATION METHODS =====
    
    def _apply_progression_bonuses_to_roll(self):
        """Apply all progression bonuses to a roll"""
        # Specialization bonuses
        if self.current_specialization:
            spec = self.specialization_trees[self.current_specialization]
            
            # Apply passive bonuses
            for bonus_key, bonus_value in spec["passive_bonuses"].items():
                if bonus_key == "sp_efficiency":
                    # Applied in SP calculation
                    pass
                elif bonus_key == "xp_efficiency":
                    # Applied in XP calculation
                    pass
                elif bonus_key == "property_detection":
                    # Applied in property analysis
                    pass
                elif bonus_key == "base_luck":
                    self.temp_luck_boost += bonus_value
                elif bonus_key == "lucky_event_freq":
                    # Applied in lucky event generation
                    pass
        
        # Equipment bonuses
        for slot_key, slot in self.equipment_system["slots"].items():
            if slot["level"] > 0:
                effects = slot["effects"]
                for effect_key, effect_func in effects.items():
                    effect_value = effect_func(slot["level"])
                    
                    if effect_key == "sp_per_roll":
                        # Add to SP gain
                        pass  # Handled in SP calculation
                    elif effect_key == "win_chance":
                        self.temp_luck_boost += effect_value
                    elif effect_key == "property_detection":
                        # Applied in property analysis
                        pass
        
        # Prestige bonuses
        prestige_level = self.prestige_system["current_level"]
        if prestige_level > 0:
            # Permanent multipliers
            self.temp_sp_multiplier += prestige_level * 0.01  # +1% SP per level
            self.temp_xp_multiplier += prestige_level * 0.01  # +1% XP per level
            self.temp_luck_boost += prestige_level * 0.005    # +0.5% luck per level
        
        # Karma effects
        karma_level = self.rng_influence["karma_system"]["karma_level"]
        if karma_level > 20:
            self.temp_luck_boost += 0.05  # Good karma bonus
        elif karma_level < -20:
            self.temp_luck_boost -= 0.05  # Bad karma penalty
    
    def _update_progression_after_roll(self, won, sp_gained, xp_gained):
        """Update progression systems after a roll"""
        # Update quest progress
        if won:
            self._update_quest_progress("daily_wins")
            self._update_quest_progress("streak_challenge", 1 if self.winning_streak > 0 else 0)
            
            # Generate luck tokens for streaks
            if self.winning_streak >= 3:
                self._generate_luck_tokens("win_streak")
            
            # Update karma
            outcome_quality = "good" if sp_gained >= 15 else "normal"
            self._update_karma("win", outcome_quality)
        else:
            # Update karma for loss
            self._update_karma("loss", "normal")
        
        # Check property discoveries for quests
        current_properties = len(self.stats.get('property_discoveries', {}))
        if current_properties > self.quest_progress.get("property_count", 0):
            self._update_quest_progress("property_mastery", 
                                      current_properties - self.quest_progress.get("property_count", 0))
            self.quest_progress["property_count"] = current_properties
        
        # Update SP accumulation quest
        session_sp = self.quest_progress.get("session_sp", 0) + sp_gained
        self.quest_progress["session_sp"] = session_sp
        
        # Check SP accumulation quests
        for quest_id, quest in self.active_quests.items():
            if quest["template"] == "sp_accumulator" and quest["current"] < quest["target"]:
                quest["current"] = min(session_sp, quest["target"])
                if quest["current"] >= quest["target"]:
                    self._complete_quest(quest_id)
        
        # Update achievements
        self._check_achievement_progress()
        
        # Update rituals
        self._update_rituals()
        
        # Save progress
        self._save_progression_data()

    def show_progression_window(self):
        """Show the comprehensive progression system window"""
        ui = self._ui
        progression_win = self._styled_toplevel("🎯 Advanced Progression System", 1000, 800)
        self._styled_header(progression_win, "Advanced Progression", "Track your journey", icon="🎯")
        
        # Current status bar
        status_frame = tk.Frame(progression_win, bg=ui["bg_card"], relief=tk.FLAT, bd=0)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_text = f"Level {self.player_level} | {self.player_xp}/{self.xp_to_level_up} XP | {self.sp} SP"
        if self.current_specialization:
            spec = self.specialization_trees[self.current_specialization]
            status_text += f" | {spec['icon']} {spec['name']}"
        
        status_label = tk.Label(status_frame, text=status_text, 
                              bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 11, "bold"))
        status_label.pack(pady=5)
        
        # Notebook for tabs
        notebook = ttk.Notebook(progression_win, style="Modern.TNotebook")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        def _scrollable_tab(tab_text, create_fn):
            """Helper to add a notebook tab with scrollable content"""
            container = tk.Frame(notebook, bg=ui["bg_primary"])
            notebook.add(container, text=tab_text)
            so, si = self._styled_scrollable(container, bg=ui["bg_primary"])
            so.pack(fill=tk.BOTH, expand=True)
            create_fn(si)
        
        # Overview tab
        _scrollable_tab("Overview", self._create_overview_tab)
        
        # Quests tab
        if self.mechanic_unlocks["quest_system"]["unlocked"]:
            _scrollable_tab("Quests", self._create_quests_tab)
        
        # Achievements tab
        achievements_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(achievements_frame, text="Achievements")
        self._create_achievements_tab(achievements_frame)
        
        # Specializations tab
        if self.mechanic_unlocks["equipment_basics"]["unlocked"]:
            _scrollable_tab("Specializations", self._create_specializations_tab)
        
        # Equipment tab
        if self.mechanic_unlocks["equipment_basics"]["unlocked"]:
            _scrollable_tab("Equipment", self._create_equipment_tab)
        
        # RNG Influence tab
        if self.mechanic_unlocks["rng_influence"]["unlocked"]:
            _scrollable_tab("RNG Control", self._create_rng_tab)
        
        # Investments tab
        if self.mechanic_unlocks["investment_system"]["unlocked"]:
            _scrollable_tab("Investments", self._create_investments_tab)
        
        # Prestige tab
        if self.mechanic_unlocks["prestige_system"]["unlocked"]:
            _scrollable_tab("Prestige", self._create_prestige_tab)
    
    def _create_overview_tab(self, parent):
        """Create overview tab with key stats and progress"""
        ui = self._ui
        # Main stats
        stats_frame = tk.LabelFrame(parent, text="Player Stats", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                  font=("Arial", 12, "bold"))
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        stats_text = f"""
Level: {self.player_level} ({self.player_xp}/{self.xp_to_level_up} XP)
SP: {self.sp}
Total Wins: {self.meta_progression.get('total_wins_all_time', 0)}
Total SP Earned: {self.meta_progression.get('total_sp_earned_all_time', 0)}
Max Win Streak: {self.max_winning_streak}
Properties Discovered: {len(self.stats.get('property_discoveries', {}))}
"""
        
        if self.current_specialization:
            spec = self.specialization_trees[self.current_specialization]
            stats_text += f"Specialization: {spec['icon']} {spec['name']}\n"
        
        if self.prestige_system["current_level"] > 0:
            stats_text += f"Prestige Level: {self.prestige_system['current_level']}\n"
        
        stats_label = tk.Label(stats_frame, text=stats_text, bg=ui["bg_primary"], fg=ui["text_primary"], 
                             font=("Courier", 10), justify="left")
        stats_label.pack(pady=5)
        
        # Active effects
        effects_frame = tk.LabelFrame(parent, text="Active Effects", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                    font=("Arial", 12, "bold"))
        effects_frame.pack(fill="x", padx=10, pady=5)
        
        effects_text = "No active effects"
        active_effects = []
        
        if self.current_specialization:
            active_effects.append(f"Specialization: {self.specialization_trees[self.current_specialization]['name']}")
        
        if self.rng_influence["ritual_system"]["active_ritual"]:
            ritual_key = self.rng_influence["ritual_system"]["active_ritual"]
            ritual = self.rng_influence["ritual_system"]["available_rituals"][ritual_key]
            active_effects.append(f"Ritual: {ritual['name']}")
        
        if self.temp_luck_boost > 0:
            active_effects.append(f"Luck Boost: +{self.temp_luck_boost:.1%}")
        
        if active_effects:
            effects_text = "\n".join(active_effects)
        
        effects_label = tk.Label(effects_frame, text=effects_text, bg=ui["bg_primary"], fg=ui["gold"], 
                               font=("Arial", 10))
        effects_label.pack(pady=5)
        
        # Progress indicators
        progress_frame = tk.LabelFrame(parent, text="Progress Indicators", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                     font=("Arial", 12, "bold"))
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        # Next level progress
        level_progress = self.player_xp / self.xp_to_level_up if self.xp_to_level_up > 0 else 1
        self._create_progress_bar(progress_frame, "Level Progress", level_progress, 
                                f"{self.player_xp}/{self.xp_to_level_up} XP")
        
        # Achievement progress
        total_achievements = len(self.achievements)
        completed_achievements = sum(1 for ach in self.achievements.values() if ach["completed"])
        ach_progress = completed_achievements / total_achievements if total_achievements > 0 else 0
        self._create_progress_bar(progress_frame, "Achievements", ach_progress, 
                                f"{completed_achievements}/{total_achievements}")
        
        # Quest progress
        total_quests = len(self.active_quests)
        completed_session_quests = sum(1 for qid in self.active_quests.keys() if qid in self.completed_quests)
        quest_progress = completed_session_quests / total_quests if total_quests > 0 else 0
        self._create_progress_bar(progress_frame, "Active Quests", quest_progress, 
                                f"{completed_session_quests}/{total_quests} completed")
    
    def _create_progress_bar(self, parent, label, progress, text):
        """Create a progress bar with label"""
        ui = self._ui
        frame = tk.Frame(parent, bg=ui["bg_primary"])
        frame.pack(fill="x", padx=5, pady=2)
        
        label = tk.Label(frame, text=f"{label}: {text}", bg=ui["bg_primary"], fg=ui["text_primary"], 
                        font=("Arial", 9))
        label.pack(anchor="w")
        
        # Simple progress bar using frame
        bar_frame = tk.Frame(frame, bg=ui["border_light"], height=10)
        bar_frame.pack(fill="x", pady=1)
        
        fill_width = int(progress * 200)  # Assume 200px width
        if fill_width > 0:
            fill_frame = tk.Frame(bar_frame, bg=ui["success"], width=fill_width, height=8)
            fill_frame.pack(side="left")
    
    def _create_quests_tab(self, parent):
        """Create quests tab"""
        ui = self._ui
        # Active quests
        active_frame = tk.LabelFrame(parent, text="Active Quests", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                   font=("Arial", 12, "bold"))
        active_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        if not self.active_quests:
            no_quests_label = tk.Label(active_frame, text="No active quests", 
                                     bg=ui["bg_primary"], fg=ui["text_muted"], font=("Arial", 10))
            no_quests_label.pack(pady=20)
        else:
            for quest_id, quest in self.active_quests.items():
                quest_frame = tk.Frame(active_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
                quest_frame.pack(fill="x", padx=5, pady=3)
                
                # Quest header
                header_text = f"{quest['name']} ({quest['type'].title()})"
                if quest_id in self.completed_quests:
                    header_text += " ✓ COMPLETED"
                
                header_label = tk.Label(quest_frame, text=header_text, 
                                      bg=ui["success"] if quest_id in self.completed_quests else ui["text_muted"], 
                                      fg=ui["text_primary"], font=("Arial", 10, "bold"))
                header_label.pack(fill="x", padx=5, pady=2)
                
                # Description and progress
                desc_text = f"{quest['description']}\nProgress: {quest['current']}/{quest['target']}"
                desc_label = tk.Label(quest_frame, text=desc_text, 
                                    bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 9))
                desc_label.pack(anchor="w", padx=5, pady=2)
                
                # Rewards
                reward_text = f"Rewards: {quest['reward_xp']} XP, {quest['reward_sp']} SP"
                if quest.get('reward_title'):
                    reward_text += f", Title: {quest['reward_title']}"
                
                reward_label = tk.Label(quest_frame, text=reward_text, 
                                      bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 8))
                reward_label.pack(anchor="w", padx=5, pady=2)
        
        # Generate new quests button
        button_frame = tk.Frame(parent, bg=ui["bg_primary"])
        button_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = tk.Button(button_frame, text="Generate New Daily Quests", 
                              command=self._generate_daily_quests,
                              bg=ui["info"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
        refresh_btn.pack()
    
    def _create_achievements_tab(self, parent):
        """Create achievements tab"""
        ui = self._ui
        canvas = tk.Canvas(parent, bg=ui["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ui["bg_primary"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _mw(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        
        row = 0
        for key, achievement in self.progression_achievements.items():
            # Achievement frame
            ach_frame = tk.Frame(scrollable_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=2)
            ach_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            
            # Status and icon
            status_color = ui["success"] if achievement["completed"] else ui["text_muted"]
            status_text = f"{achievement['icon']} {'✓' if achievement['completed'] else '○'}"
            
            status_label = tk.Label(ach_frame, text=status_text, bg=status_color, fg=ui["text_primary"], 
                                  font=("Arial", 12, "bold"), width=3)
            status_label.pack(side="left", padx=5, pady=5)
            
            # Content frame
            content_frame = tk.Frame(ach_frame, bg=ui["bg_card"])
            content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            # Name
            name_label = tk.Label(content_frame, text=achievement["name"], 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 11, "bold"))
            name_label.pack(anchor="w")
            
            # Description and progress
            if "tiers" in achievement:
                current_tier = achievement.get("current_tier", 0)
                max_tier = len(achievement["tiers"])
                desc_text = f"{achievement['description']}\nTier: {current_tier}/{max_tier}"
                if current_tier < max_tier:
                    next_target = achievement["tiers"][current_tier]
                    desc_text += f" (Next: {next_target})"
            else:
                desc_text = achievement["description"]
            
            desc_label = tk.Label(content_frame, text=desc_text, 
                                bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 9), wraplength=400, justify="left")
            desc_label.pack(anchor="w", pady=2)
            
            # Progress bar for tiered achievements
            if "tiers" in achievement:
                progress_frame = tk.Frame(content_frame, bg=ui["border_light"], height=8)
                progress_frame.pack(fill="x", pady=2)
                
                current_tier = achievement.get("current_tier", 0)
                progress_ratio = current_tier / len(achievement["tiers"]) if achievement["tiers"] else 0
                fill_width = int(progress_ratio * 300)
                
                if fill_width > 0:
                    fill_frame = tk.Frame(progress_frame, bg=ui["success"], width=fill_width, height=6)
                    fill_frame.pack(side="left")
            
            row += 1
        
        scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def _create_specializations_tab(self, parent):
        """Create specializations tab"""
        ui = self._ui
        # Current specialization
        current_frame = tk.LabelFrame(parent, text="Current Specialization", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                    font=("Arial", 12, "bold"))
        current_frame.pack(fill="x", padx=10, pady=5)
        
        if self.current_specialization:
            spec = self.specialization_trees[self.current_specialization]
            current_text = f"{spec['icon']} {spec['name']}\n{spec['description']}\n\nPassive Bonuses:"
            
            for bonus_key, bonus_value in spec["passive_bonuses"].items():
                bonus_name = bonus_key.replace("_", " ").title()
                if "percent" in bonus_name.lower():
                    current_text += f"\n• {bonus_name}: {bonus_value:.1%}"
                else:
                    current_text += f"\n• {bonus_name}: +{bonus_value}"
            
            current_label = tk.Label(current_frame, text=current_text, bg=ui["bg_primary"], fg=ui["text_primary"], 
                                   font=("Arial", 10), justify="left")
            current_label.pack(pady=5)
        else:
            current_label = tk.Label(current_frame, text="No specialization selected", 
                                   bg=ui["bg_primary"], fg=ui["text_muted"], font=("Arial", 10))
            current_label.pack(pady=5)
        
        # Available specializations
        available_frame = tk.LabelFrame(parent, text="Available Specializations", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                      font=("Arial", 12, "bold"))
        available_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        for spec_key, spec in self.specialization_trees.items():
            spec_frame = tk.Frame(available_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=2)
            spec_frame.pack(fill="x", padx=5, pady=5)
            
            # Header with status
            status_text = "✓ UNLOCKED" if spec["unlocked"] else f"🔒 {spec['unlock_cost']} SP"
            header_label = tk.Label(spec_frame, text=f"{spec['icon']} {spec['name']}", 
                                  bg=ui["success"] if spec["unlocked"] else ui["text_muted"], 
                                  fg=ui["text_primary"], font=("Arial", 11, "bold"))
            header_label.pack(fill="x", padx=5, pady=2)
            
            # Description
            desc_label = tk.Label(spec_frame, text=spec["description"], 
                                bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 9))
            desc_label.pack(anchor="w", padx=5, pady=2)
            
            # Buttons
            button_frame = tk.Frame(spec_frame, bg=ui["bg_card"])
            button_frame.pack(fill="x", padx=5, pady=5)
            
            if not spec["unlocked"]:
                unlock_btn = tk.Button(button_frame, text=f"Unlock ({spec['unlock_cost']} SP)", 
                                     command=lambda s=spec_key: self._unlock_specialization(s),
                                     bg=ui["warning"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                unlock_btn.pack(side="left", padx=5)
            else:
                if self.current_specialization != spec_key:
                    select_btn = tk.Button(button_frame, text="Select", 
                                         command=lambda s=spec_key: self._switch_specialization(s),
                                         bg=ui["info"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                    select_btn.pack(side="left", padx=5)
                else:
                    active_label = tk.Label(button_frame, text="ACTIVE", 
                                          bg=ui["success"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                    active_label.pack(side="left", padx=5)
    
    def _create_equipment_tab(self, parent):
        """Create equipment tab"""
        ui = self._ui
        for slot_key, slot in self.equipment_system["slots"].items():
            slot_frame = tk.LabelFrame(parent, text=f"{slot['name']} (Level {slot['level']}/{slot['max_level']})", 
                                     bg=ui["bg_primary"], fg=ui["text_primary"], font=("Arial", 12, "bold"))
            slot_frame.pack(fill="x", padx=10, pady=5)
            
            # Description
            desc_label = tk.Label(slot_frame, text=slot["description"], 
                                bg=ui["bg_primary"], fg=ui["text_secondary"], font=("Arial", 9))
            desc_label.pack(anchor="w", padx=5, pady=2)
            
            # Current effects
            effects_text = "Current Effects:"
            for effect_key, effect_func in slot["effects"].items():
                effect_value = effect_func(slot["level"])
                effect_name = effect_key.replace("_", " ").title()
                effects_text += f"\n• {effect_name}: +{effect_value}"
            
            effects_label = tk.Label(slot_frame, text=effects_text, 
                                   bg=ui["bg_primary"], fg=ui["text_primary"], font=("Arial", 9), justify="left")
            effects_label.pack(anchor="w", padx=5, pady=5)
            
            # Upgrade button
            if slot["level"] < slot["max_level"]:
                upgrade_cost = slot["upgrade_cost"](slot["level"])
                upgrade_btn = tk.Button(slot_frame, text=f"Upgrade ({upgrade_cost} SP)", 
                                      command=lambda s=slot_key: self._upgrade_equipment_slot(s),
                                      bg=ui["success"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
                upgrade_btn.pack(pady=5)
            else:
                max_label = tk.Label(slot_frame, text="MAX LEVEL", 
                                   bg=ui["bg_primary"], fg=ui["gold"], font=("Arial", 10, "bold"))
                max_label.pack(pady=5)
        
        # Total power
        power_frame = tk.Frame(parent, bg=ui["bg_card"], relief=tk.RAISED, bd=2)
        power_frame.pack(fill="x", padx=10, pady=10)
        
        power_text = f"Total Equipment Power: {self.equipment_system['total_equipment_power']}"
        power_label = tk.Label(power_frame, text=power_text, 
                             bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 12, "bold"))
        power_label.pack(pady=10)
    
    def _create_rng_tab(self, parent):
        """Create RNG influence tab"""
        ui = self._ui
        # Luck tokens
        tokens_frame = tk.LabelFrame(parent, text="Luck Tokens", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                   font=("Arial", 12, "bold"))
        tokens_frame.pack(fill="x", padx=10, pady=5)
        
        tokens_text = f"Current Tokens: {self.rng_influence['luck_tokens']['current_tokens']}/{self.rng_influence['luck_tokens']['max_tokens']}"
        tokens_label = tk.Label(tokens_frame, text=tokens_text, 
                              bg=ui["bg_primary"], fg=ui["gold"], font=("Arial", 11, "bold"))
        tokens_label.pack(pady=5)
        
        # Token abilities
        for ability_key, ability in self.rng_influence["luck_tokens"]["abilities"].items():
            ability_frame = tk.Frame(tokens_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            ability_frame.pack(fill="x", padx=5, pady=2)
            
            # Ability info
            info_text = f"{ability['name']}\n{ability['description']}\nCost: {ability['cost']} tokens"
            info_label = tk.Label(ability_frame, text=info_text, 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 9), justify="left")
            info_label.pack(side="left", padx=5, pady=5)
            
            # Use button
            if self.rng_influence["luck_tokens"]["current_tokens"] >= ability["cost"]:
                use_btn = tk.Button(ability_frame, text="Use", 
                                  command=lambda a=ability_key: self._use_luck_token(a),
                                  bg=ui["success"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                use_btn.pack(side="right", padx=5, pady=5)
        
        # Karma system
        karma_frame = tk.LabelFrame(parent, text="Karma Balance", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                  font=("Arial", 12, "bold"))
        karma_frame.pack(fill="x", padx=10, pady=5)
        
        karma_level = self.rng_influence["karma_system"]["karma_level"]
        karma_color = ui["success"] if karma_level > 0 else ui["danger"] if karma_level < 0 else ui["text_primary"]
        karma_text = f"Karma Level: {karma_level}"
        
        if karma_level > 20:
            karma_text += " (Lucky Streak)"
        elif karma_level > 0:
            karma_text += " (Good Karma)"
        elif karma_level == 0:
            karma_text += " (Neutral)"
        elif karma_level > -20:
            karma_text += " (Bad Karma)"
        else:
            karma_text += " (Unlucky Streak)"
        
        karma_label = tk.Label(karma_frame, text=karma_text, 
                             bg=ui["bg_primary"], fg=karma_color, font=("Arial", 11, "bold"))
        karma_label.pack(pady=5)
        
        # Rituals
        rituals_frame = tk.LabelFrame(parent, text="Lucky Rituals", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                    font=("Arial", 12, "bold"))
        rituals_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        for ritual_key, ritual in self.rng_influence["ritual_system"]["available_rituals"].items():
            ritual_frame = tk.Frame(rituals_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            ritual_frame.pack(fill="x", padx=5, pady=3)
            
            # Status
            status_text = "✓ UNLOCKED" if ritual["unlocked"] else "🔒 LOCKED"
            status_label = tk.Label(ritual_frame, text=status_text, 
                                  bg=ui["success"] if ritual["unlocked"] else ui["text_muted"], 
                                  fg=ui["text_primary"], font=("Arial", 9, "bold"))
            status_label.pack(side="left", padx=5, pady=5)
            
            # Info
            info_frame = tk.Frame(ritual_frame, bg=ui["bg_card"])
            info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            name_label = tk.Label(info_frame, text=ritual["name"], 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
            name_label.pack(anchor="w")
            
            desc_label = tk.Label(info_frame, text=f"{ritual['description']} ({ritual['duration']}s)", 
                                bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 8))
            desc_label.pack(anchor="w")
            
            # Perform button
            if ritual["unlocked"] and not self.rng_influence["ritual_system"]["active_ritual"]:
                perform_btn = tk.Button(ritual_frame, text="Perform", 
                                      command=lambda r=ritual_key: self._perform_ritual(r),
                                      bg=ui["warning"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                perform_btn.pack(side="right", padx=5, pady=5)
            elif self.rng_influence["ritual_system"]["active_ritual"] == ritual_key:
                active_label = tk.Label(ritual_frame, text="ACTIVE", 
                                      bg=ui["success"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                active_label.pack(side="right", padx=5, pady=5)
    
    def _create_investments_tab(self, parent):
        """Create investments tab"""
        ui = self._ui
        # Portfolio investments
        for portfolio_key, portfolio in self.investment_system["portfolios"].items():
            port_frame = tk.LabelFrame(parent, text=f"{portfolio['name']}", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                     font=("Arial", 12, "bold"))
            port_frame.pack(fill="x", padx=10, pady=5)
            
            # Description and risk
            desc_text = f"{portfolio['description']}\nRisk Level: {portfolio['risk_level'].title()}\n"
            desc_text += f"Return Rate: {portfolio['base_return_rate']:.1%} per hour\n"
            desc_text += f"Current Investment: {portfolio['current_investment']} SP\n"
            desc_text += f"Total Earned: {portfolio['total_earned']} SP"
            
            desc_label = tk.Label(port_frame, text=desc_text, 
                                bg=ui["bg_primary"], fg=ui["text_secondary"], font=("Arial", 9), justify="left")
            desc_label.pack(anchor="w", padx=5, pady=5)
            
            # Invest button
            if portfolio["current_investment"] < portfolio["max_investment"]:
                invest_frame = tk.Frame(port_frame, bg=ui["bg_primary"])
                invest_frame.pack(fill="x", padx=5, pady=5)
                
                amount_var = tk.StringVar(value=str(portfolio["min_investment"]))
                amount_entry = tk.Entry(invest_frame, textvariable=amount_var, width=10)
                amount_entry.pack(side="left", padx=5)
                
                invest_btn = tk.Button(invest_frame, text="Invest", 
                                     command=lambda p=portfolio_key, v=amount_var: 
                                         self._invest_in_portfolio(p, int(v.get()) if v.get().isdigit() else 0),
                                     bg=ui["success"], fg=ui["text_primary"], font=("Arial", 9, "bold"))
                invest_btn.pack(side="left", padx=5)
        
        # Collection
        collect_frame = tk.Frame(parent, bg=ui["bg_card"], relief=tk.RAISED, bd=2)
        collect_frame.pack(fill="x", padx=10, pady=10)
        
        collect_text = f"Total Invested: {self.investment_system['total_invested']} SP\n"
        collect_text += f"Total Earned: {self.investment_system['total_earned_all_time']} SP"
        
        collect_label = tk.Label(collect_frame, text=collect_text, 
                               bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10))
        collect_label.pack(pady=5)
        
        collect_btn = tk.Button(collect_frame, text="Collect Investment Returns", 
                              command=self._collect_investment_returns,
                              bg=ui["info"], fg=ui["text_primary"], font=("Arial", 11, "bold"))
        collect_btn.pack(pady=5)
    
    def _create_prestige_tab(self, parent):
        """Create prestige tab"""
        ui = self._ui
        # Prestige info
        info_frame = tk.LabelFrame(parent, text="Prestige Status", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                 font=("Arial", 12, "bold"))
        info_frame.pack(fill="x", padx=10, pady=5)
        
        prestige_text = f"Prestige Level: {self.prestige_system['current_level']}\n"
        prestige_text += f"Prestige Points: {self.prestige_system['prestige_points']}\n"
        prestige_text += f"Total Prestiges: {self.prestige_system['total_prestiges']}\n\n"
        prestige_text += "Permanent Bonuses:\n"
        
        for bonus_key, bonus_value in self.prestige_system["permanent_bonuses"].items():
            bonus_name = bonus_key.replace("_", " ").title()
            prestige_text += f"• {bonus_name}: +{bonus_value}%\n"
        
        info_label = tk.Label(info_frame, text=prestige_text, 
                            bg=ui["bg_primary"], fg=ui["text_primary"], font=("Arial", 10), justify="left")
        info_label.pack(pady=5)
        
        # Prestige requirements
        req_frame = tk.LabelFrame(parent, text="Prestige Requirements", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                font=("Arial", 12, "bold"))
        req_frame.pack(fill="x", padx=10, pady=5)
        
        total_wins = self.meta_progression.get("total_wins_all_time", 0)
        can_prestige = total_wins >= 1000
        
        req_text = f"Total Wins: {total_wins}/1000 {'✓' if can_prestige else '✗'}\n"
        req_text += f"Level: {self.player_level}/25 {'✓' if self.player_level >= 25 else '✗'}"
        
        req_label = tk.Label(req_frame, text=req_text, 
                           bg=ui["bg_primary"], fg=ui["success"] if can_prestige else ui["danger"], 
                           font=("Arial", 10))
        req_label.pack(pady=5)
        
        if can_prestige:
            prestige_btn = tk.Button(req_frame, text="PRESTIGE RESET", 
                                   command=self._perform_prestige_reset,
                                   bg=ui["warning"], fg=ui["text_primary"], font=("Arial", 12, "bold"))
            prestige_btn.pack(pady=10)
        
        # Prestige upgrades
        upgrades_frame = tk.LabelFrame(parent, text="Prestige Upgrades", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                     font=("Arial", 12, "bold"))
        upgrades_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        for upgrade_key, upgrade in self.prestige_system["available_upgrades"].items():
            upgrade_frame = tk.Frame(upgrades_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            upgrade_frame.pack(fill="x", padx=5, pady=3)
            
            # Status
            status_text = "✓ PURCHASED" if upgrade["purchased"] else f"Cost: {upgrade['cost']} PP"
            status_label = tk.Label(upgrade_frame, text=status_text, 
                                  bg=ui["success"] if upgrade["purchased"] else ui["text_muted"], 
                                  fg=ui["text_primary"], font=("Arial", 9, "bold"))
            status_label.pack(side="left", padx=5, pady=5)
            
            # Info
            info_frame = tk.Frame(upgrade_frame, bg=ui["bg_card"])
            info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            name_label = tk.Label(info_frame, text=upgrade["name"], 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
            name_label.pack(anchor="w")
            
            desc_label = tk.Label(info_frame, text=upgrade["description"], 
                                bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 8))
            desc_label.pack(anchor="w")
            
            # Purchase button
            if not upgrade["purchased"] and self.prestige_system["prestige_points"] >= upgrade["cost"]:
                buy_btn = tk.Button(upgrade_frame, text="Purchase", 
                                  command=lambda u=upgrade_key: self._purchase_prestige_upgrade(u),
                                  bg=ui["success"], fg=ui["text_primary"], font=("Arial", 8, "bold"))
                buy_btn.pack(side="right", padx=5, pady=5)
        """Create milestones tab content"""
        canvas = tk.Canvas(parent, bg=ui["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ui["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _mw_ms(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_ms))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_ms))
        
        row = 0
        for key, milestone in self.milestone_unlocks.items():
            # Milestone frame
            milestone_frame = tk.Frame(scrollable_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=2)
            milestone_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            
            # Status indicator
            status_color = ui["success"] if milestone["unlocked"] else ui["danger"]
            status_text = "✓ UNLOCKED" if milestone["unlocked"] else "🔒 LOCKED"
            
            status_label = tk.Label(milestone_frame, text=status_text, 
                                  bg=status_color, fg=ui["text_primary"], font=("Arial", 10, "bold"))
            status_label.pack(anchor="w", padx=5, pady=2)
            
            # Name
            name_label = tk.Label(milestone_frame, text=milestone["name"], 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 12, "bold"))
            name_label.pack(anchor="w", padx=5)
            
            # Description
            desc_label = tk.Label(milestone_frame, text=milestone["description"], 
                                bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 9), wraplength=400, justify="left")
            desc_label.pack(anchor="w", padx=5, pady=2)
            
            # Reward
            reward_label = tk.Label(milestone_frame, text=f"Reward: {milestone['reward']}", 
                                  bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 9, "italic"))
            reward_label.pack(anchor="w", padx=5, pady=2)
            
            row += 1
        
        # Configure grid weights
        scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def _create_upgrades_tab(self, parent):
        """Create upgrades tab content"""
        ui = self._ui
        for path_key, path in self.upgrade_paths.items():
            # Path frame
            path_frame = tk.LabelFrame(parent, text=path["name"], bg=ui["bg_primary"], fg=ui["text_primary"], 
                                     font=("Arial", 12, "bold"))
            path_frame.pack(fill="x", padx=10, pady=5)
            
            # Description
            desc_label = tk.Label(path_frame, text=path["description"], 
                                bg=ui["bg_primary"], fg=ui["text_secondary"], font=("Arial", 9))
            desc_label.pack(anchor="w", padx=5, pady=2)
            
            # Progress
            progress_label = tk.Label(path_frame, text=f"Progress: {path['current_progress']}/3 upgrades unlocked", 
                                    bg=ui["bg_primary"], fg=ui["gold"], font=("Arial", 9, "bold"))
            progress_label.pack(anchor="w", padx=5, pady=2)
            
            # Upgrades
            for upgrade_key, upgrade in path["upgrades"].items():
                upgrade_frame = tk.Frame(path_frame, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
                upgrade_frame.pack(fill="x", padx=5, pady=2)
                
                # Status and name
                status_color = ui["success"] if upgrade["unlocked"] else ui["text_muted"]
                status_text = "✓" if upgrade["unlocked"] else "○"
                
                name_label = tk.Label(upgrade_frame, text=f"{status_text} {upgrade['name']}", 
                                    bg=status_color, fg=ui["text_primary"], font=("Arial", 10, "bold"))
                name_label.pack(side="left", padx=5, pady=2)
                
                # Cost
                cost_label = tk.Label(upgrade_frame, text=f"Cost: {upgrade['cost']} SP", 
                                    bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 9))
                cost_label.pack(side="right", padx=5, pady=2)
                
                # Description
                desc_label = tk.Label(upgrade_frame, text=upgrade["description"], 
                                    bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 8), wraplength=300, justify="left")
                desc_label.pack(side="left", padx=10, pady=2)
                
                # Purchase button (if not unlocked and can afford)
                if not upgrade["unlocked"] and self.sp >= upgrade["cost"]:
                    buy_btn = tk.Button(upgrade_frame, text="Purchase", 
                                      command=lambda u=upgrade, p=path_key: self._purchase_upgrade(p, u["name"]),
                                      bg=ui["success"], fg=ui["text_primary"], font=("Arial", 8, "bold"))
                    buy_btn.pack(side="right", padx=5, pady=2)
    
    def _purchase_upgrade(self, path_key, upgrade_name):
        """Purchase an upgrade"""
        path = self.upgrade_paths[path_key]
        for upgrade_key, upgrade in path["upgrades"].items():
            if upgrade["name"] == upgrade_name and not upgrade["unlocked"] and self.sp >= upgrade["cost"]:
                self.sp -= upgrade["cost"]
                upgrade["unlocked"] = True
                path["current_progress"] += 1
                self._save_progression_data()
                self._update_display()
                messagebox.showinfo("Upgrade Purchased!", f"Successfully purchased {upgrade['name']}!")
                self.show_progression_window()  # Refresh window
                return
        
        messagebox.showerror("Purchase Failed", "Unable to purchase upgrade.")
    
    def _create_mechanics_tab(self, parent):
        """Create new mechanics tab content"""
        ui = self._ui
        for key, mechanic in self.unlocked_mechanics.items():
            if mechanic["enabled"]:
                # Mechanic frame
                mech_frame = tk.LabelFrame(parent, text=f"✓ {mechanic['name']}", 
                                         bg=ui["bg_primary"], fg=ui["success"], font=("Arial", 12, "bold"))
                mech_frame.pack(fill="x", padx=10, pady=5)
                
                # Description
                desc_label = tk.Label(mech_frame, text=mechanic["description"], 
                                    bg=ui["bg_primary"], fg=ui["text_secondary"], font=("Arial", 9))
                desc_label.pack(anchor="w", padx=5, pady=2)
                
                # Specific mechanic content
                if key == "auto_roll":
                    self._create_auto_roll_content(mech_frame)
                elif key == "equipment_system":
                    self._create_equipment_content(mech_frame)
                elif key == "investment_system":
                    self._create_investment_content(mech_frame)
                elif key == "prestige_system":
                    self._create_prestige_content(mech_frame)
            else:
                # Locked mechanic
                locked_frame = tk.LabelFrame(parent, text=f"🔒 {mechanic['name']}", 
                                           bg=ui["bg_primary"], fg=ui["text_muted"], font=("Arial", 12, "bold"))
                locked_frame.pack(fill="x", padx=10, pady=5)
                
                desc_label = tk.Label(locked_frame, text=mechanic["description"], 
                                    bg=ui["bg_primary"], fg=ui["text_muted"], font=("Arial", 9))
                desc_label.pack(anchor="w", padx=5, pady=2)
                
                req_label = tk.Label(locked_frame, text="Complete milestones to unlock", 
                                   bg=ui["bg_primary"], fg=ui["text_muted"], font=("Arial", 8, "italic"))
                req_label.pack(anchor="w", padx=5, pady=2)
    
    def _create_auto_roll_content(self, parent):
        """Create auto-roll mechanic controls"""
        ui = self._ui
        controls_frame = tk.Frame(parent, bg=ui["bg_primary"])
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Auto-roll options
        options = [
            ("Auto-roll on win", "auto_roll_on_win"),
            ("Auto-roll on loss", "auto_roll_on_loss"), 
            ("Auto-roll timer", "auto_roll_timer"),
            ("Smart auto-roll", "smart_auto_roll")
        ]
        
        for text, key in options:
            var = tk.BooleanVar(value=self.unlocked_mechanics["auto_roll"]["mechanics"][key])
            chk = tk.Checkbutton(controls_frame, text=text, variable=var, 
                               bg=ui["bg_primary"], fg=ui["text_primary"], selectcolor=ui["success"],
                               command=lambda k=key, v=var: self._toggle_auto_roll_option(k, v.get()))
            chk.pack(anchor="w", pady=1)
    
    def _toggle_auto_roll_option(self, option_key, enabled):
        """Toggle an auto-roll option"""
        self.unlocked_mechanics["auto_roll"]["mechanics"][option_key] = enabled
        self._save_progression_data()
    
    def _create_equipment_content(self, parent):
        """Create equipment system content"""
        ui = self._ui
        for slot_key, slot in self.unlocked_mechanics["equipment_system"]["equipment_slots"].items():
            slot_frame = tk.Frame(parent, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            slot_frame.pack(fill="x", padx=5, pady=2)
            
            # Slot info
            info_label = tk.Label(slot_frame, text=f"{slot['name']} (Level {slot['level']}/{slot['max_level']})", 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
            info_label.pack(side="left", padx=5, pady=2)
            
            # Upgrade cost
            upgrade_cost = 100 * (slot["level"] + 1) ** 2  # Exponential scaling
            cost_label = tk.Label(slot_frame, text=f"Upgrade: {upgrade_cost} SP", 
                                bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 9))
            cost_label.pack(side="right", padx=5, pady=2)
            
            # Upgrade button
            if slot["level"] < slot["max_level"] and self.sp >= upgrade_cost:
                upgrade_btn = tk.Button(slot_frame, text="Upgrade", 
                                      command=lambda s=slot_key: self._upgrade_equipment(s),
                                      bg=ui["success"], fg=ui["text_primary"], font=("Arial", 8, "bold"))
                upgrade_btn.pack(side="right", padx=5, pady=2)
    
    def _upgrade_equipment(self, slot_key):
        """Upgrade equipment slot"""
        slot = self.unlocked_mechanics["equipment_system"]["equipment_slots"][slot_key]
        upgrade_cost = 100 * (slot["level"] + 1) ** 2
        
        if slot["level"] < slot["max_level"] and self.sp >= upgrade_cost:
            self.sp -= upgrade_cost
            slot["level"] += 1
            self._save_progression_data()
            self._update_display()
            messagebox.showinfo("Equipment Upgraded!", f"{slot['name']} upgraded to level {slot['level']}!")
            self.show_progression_window()  # Refresh window
    
    def _create_investment_content(self, parent):
        """Create investment system content"""
        ui = self._ui
        # Current investments
        for inv_key, investment in self.unlocked_mechanics["investment_system"]["investments"].items():
            inv_frame = tk.Frame(parent, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            inv_frame.pack(fill="x", padx=5, pady=2)
            
            # Investment info
            info_text = f"{investment['name']} (Owned: {investment['owned']}) - {investment['income_per_hour']} SP/hour"
            info_label = tk.Label(inv_frame, text=info_text, 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10))
            info_label.pack(side="left", padx=5, pady=2)
            
            # Buy button
            if self.sp >= investment["cost"]:
                buy_btn = tk.Button(inv_frame, text=f"Buy ({investment['cost']} SP)", 
                                  command=lambda i=inv_key: self._buy_investment(i),
                                  bg=ui["success"], fg=ui["text_primary"], font=("Arial", 8, "bold"))
                buy_btn.pack(side="right", padx=5, pady=2)
        
        # Collection button
        collect_btn = tk.Button(parent, text="Collect Investment Income", 
                              command=self._collect_investment_income,
                              bg=ui["info"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
        collect_btn.pack(pady=10)
    
    def _buy_investment(self, investment_key):
        """Buy an investment"""
        investment = self.unlocked_mechanics["investment_system"]["investments"][investment_key]
        
        if self.sp >= investment["cost"]:
            self.sp -= investment["cost"]
            investment["owned"] += 1
            self.unlocked_mechanics["investment_system"]["total_invested"] += investment["cost"]
            self._save_progression_data()
            self._update_display()
            messagebox.showinfo("Investment Purchased!", f"Bought 1 {investment['name']}!")
            self.show_progression_window()  # Refresh window
    
    def _collect_investment_income(self):
        """Collect income from investments"""
        import datetime
        
        now = datetime.datetime.now()
        last_collection = self.unlocked_mechanics["investment_system"]["last_collection"]
        
        if last_collection:
            last_time = datetime.datetime.fromisoformat(last_collection)
            hours_passed = (now - last_time).total_seconds() / 3600
        else:
            hours_passed = 1  # First collection
        
        total_income = 0
        for investment in self.unlocked_mechanics["investment_system"]["investments"].values():
            total_income += investment["owned"] * investment["income_per_hour"] * hours_passed
        
        if total_income > 0:
            self.sp += int(total_income)
            self.unlocked_mechanics["investment_system"]["last_collection"] = now.isoformat()
            self._save_progression_data()
            self._update_display()
            messagebox.showinfo("Income Collected!", f"Collected {int(total_income)} SP from investments!")
    
    def _create_prestige_content(self, parent):
        """Create prestige system content"""
        ui = self._ui
        # Prestige info
        prestige_info = f"Prestige Level: {self.unlocked_mechanics['prestige_system']['prestige_level']}\n"
        prestige_info += f"Prestige Points: {self.unlocked_mechanics['prestige_system']['prestige_points']}"
        
        info_label = tk.Label(parent, text=prestige_info, bg=ui["bg_primary"], fg=ui["gold"], 
                            font=("Arial", 11, "bold"))
        info_label.pack(pady=5)
        
        # Prestige button (if eligible)
        total_wins = self.meta_progression.get("total_wins_all_time", 0)
        if total_wins >= 100:  # Can prestige
            prestige_btn = tk.Button(parent, text="Prestige Reset", 
                                   command=self._perform_prestige,
                                   bg=ui["warning"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
            prestige_btn.pack(pady=5)
        
        # Available upgrades
        upgrades_label = tk.Label(parent, text="Available Upgrades:", bg=ui["bg_primary"], fg=ui["text_primary"], 
                                font=("Arial", 10, "bold"))
        upgrades_label.pack(anchor="w", padx=5, pady=5)
        
        for upgrade_key, upgrade in self.unlocked_mechanics["prestige_system"]["available_upgrades"].items():
            upgrade_frame = tk.Frame(parent, bg=ui["bg_card"], relief=tk.RAISED, bd=1)
            upgrade_frame.pack(fill="x", padx=5, pady=2)
            
            # Upgrade info
            name_label = tk.Label(upgrade_frame, text=upgrade["name"], 
                                bg=ui["bg_card"], fg=ui["text_primary"], font=("Arial", 10, "bold"))
            name_label.pack(side="left", padx=5, pady=2)
            
            # Cost and effect
            cost_label = tk.Label(upgrade_frame, text=f"Cost: {upgrade['cost']} PP", 
                                bg=ui["bg_card"], fg=ui["gold"], font=("Arial", 9))
            cost_label.pack(side="right", padx=5, pady=2)
            
            effect_label = tk.Label(upgrade_frame, text=upgrade["effect"], 
                                  bg=ui["bg_card"], fg=ui["text_secondary"], font=("Arial", 8))
            effect_label.pack(side="left", padx=10, pady=2)
            
            # Purchase button
            pp = self.unlocked_mechanics["prestige_system"]["prestige_points"]
            if pp >= upgrade["cost"]:
                buy_btn = tk.Button(upgrade_frame, text="Purchase", 
                                  command=lambda u=upgrade_key: self._purchase_prestige_upgrade(u),
                                  bg=ui["success"], fg=ui["text_primary"], font=("Arial", 8, "bold"))
                buy_btn.pack(side="right", padx=5, pady=2)
    
    def _perform_prestige(self):
        """Perform prestige reset"""
        if not messagebox.askyesno("Confirm Prestige", 
                                 "Prestige will reset your level, XP, and SP, but grant prestige points and permanent bonuses.\n\nContinue?"):
            return
        
        # Calculate prestige points (based on total wins)
        total_wins = self.meta_progression.get("total_wins_all_time", 0)
        prestige_points = min(total_wins // 10, 50)  # Max 50 PP
        
        # Reset progress
        self.player_level = 1
        self.player_xp = 0
        self.sp = 0
        self.winning_streak = 0
        self.max_winning_streak = 0
        
        # Reset skill tree (but keep meta progression)
        for skill in self.skills.values():
            skill["learned"] = False
        
        # Reset talent tree
        for talent in self.talent_tree.values():
            talent["current_level"] = 0
        
        # Grant prestige points
        self.unlocked_mechanics["prestige_system"]["prestige_level"] += 1
        self.unlocked_mechanics["prestige_system"]["prestige_points"] += prestige_points
        
        self._save_progression_data()
        self._update_display()
        
        messagebox.showinfo("Prestige Complete!", 
                          f"Prestige level {self.unlocked_mechanics['prestige_system']['prestige_level']} achieved!\n"
                          f"Gained {prestige_points} prestige points!")
    
    def _purchase_prestige_upgrade(self, upgrade_key):
        """Purchase a prestige upgrade"""
        upgrade = self.unlocked_mechanics["prestige_system"]["available_upgrades"][upgrade_key]
        pp = self.unlocked_mechanics["prestige_system"]["prestige_points"]
        
        if pp >= upgrade["cost"]:
            self.unlocked_mechanics["prestige_system"]["prestige_points"] -= upgrade["cost"]
            # Mark as purchased (could add to a purchased list, but for now just remove cost)
            upgrade["cost"] = 999999  # Make it unpurchasable again
            self._save_progression_data()
            messagebox.showinfo("Prestige Upgrade Purchased!", f"Purchased {upgrade['name']}!")
            self.show_progression_window()  # Refresh window
    
    def _create_progress_tab(self, parent):
        """Create progress statistics tab"""
        stats_text = f"""
Player Level: {self.player_level}
XP Progress: {self.player_xp}/{self.xp_to_level_up}
Total Wins: {self.meta_progression.get('total_wins_all_time', 0)}
Total SP Earned: {self.meta_progression.get('total_sp_earned_all_time', 0)}
Max Win Streak: {self.max_winning_streak}

Milestones Unlocked: {sum(1 for m in self.milestone_unlocks.values() if m['unlocked'])}/{len(self.milestone_unlocks)}
Upgrades Purchased: {sum(sum(1 for u in p['upgrades'].values() if u['unlocked']) for p in self.upgrade_paths.values())}
New Mechanics Unlocked: {sum(1 for m in self.unlocked_mechanics.values() if m['enabled'])}

Current Rank: {self.rank_titles.get(self.player_level, 'Unknown')}
"""
        
        ui = self._ui
        stats_label = tk.Label(parent, text=stats_text, bg=ui["bg_primary"], fg=ui["text_primary"], 
                             font=ui["font_mono"], justify="left")
        stats_label.pack(anchor="w", padx=10, pady=10)
    
    def _apply_progression_bonuses(self, sp_gained, sp_type):
        """Apply bonuses from progression system"""
        original_sp = sp_gained
        
        # Equipment bonuses
        if self.unlocked_mechanics["equipment_system"]["enabled"]:
            equipment = self.unlocked_mechanics["equipment_system"]["equipment_slots"]
            
            # Roll booster: +SP per roll
            roll_booster_level = equipment["roll_booster"]["level"]
            if roll_booster_level > 0:
                sp_gained += roll_booster_level * 2
            
            # Luck charm: bonus for high-value SP types
            luck_charm_level = equipment["luck_charm"]["level"]
            if luck_charm_level > 0 and sp_type in ["sp_x", "sp_caret"]:
                sp_gained += luck_charm_level
            
            # XP amplifier: indirectly affects SP through level bonuses
            xp_amp_level = equipment["xp_amplifier"]["level"]
            if xp_amp_level > 0:
                sp_gained = int(sp_gained * (1 + xp_amp_level * 0.05))
            
            # Streak keeper: bonus during streaks
            streak_keeper_level = equipment["streak_keeper"]["level"]
            if streak_keeper_level > 0 and self.winning_streak >= 3:
                sp_gained += streak_keeper_level * self.winning_streak
        
        # Upgrade path bonuses
        for path_key, path in self.upgrade_paths.items():
            for upgrade_key, upgrade in path["upgrades"].items():
                if upgrade["unlocked"]:
                    effect = upgrade["effect"]
                    
                    # Efficiency path
                    if "sp_multiplier" in effect:
                        sp_gained = int(sp_gained * (1 + effect["sp_multiplier"]))
                    if "xp_multiplier" in effect:
                        # XP multiplier indirectly affects future SP through levels
                        pass
                    if "double_resource_chance" in effect:
                        import random
                        if random.random() < effect["double_resource_chance"]:
                            sp_gained *= 2
                    
                    # Skill path
                    if "property_detection_bonus" in effect:
                        # This would affect win rate, indirectly affecting SP
                        pass
                    if "timing_bonus_enabled" in effect:
                        # Timing bonuses would be applied elsewhere
                        pass
                    if "prediction_accuracy" in effect:
                        # Prediction would help win rate
                        pass
                    
                    # Luck path
                    if "base_win_chance" in effect:
                        # This affects win rate, indirectly SP
                        pass
                    if "lucky_event_freq" in effect:
                        # Lucky events would trigger bonuses
                        pass
                    if "favorable_outcome_charges" in effect:
                        # Special ability for guaranteed good outcomes
                        pass
                    if "chaos_control_enabled" in effect:
                        # Ability to convert bad rolls to good
                        pass
        
        # Prestige bonuses
        if self.unlocked_mechanics["prestige_system"]["enabled"]:
            prestige_level = self.unlocked_mechanics["prestige_system"]["prestige_level"]
            # Permanent SP boost per prestige level
            sp_gained = int(sp_gained * (1 + prestige_level * 0.01))
        
        return max(1, sp_gained)  # Ensure at least 1 SP

    # ===== TOURNAMENT SYSTEM =====

    
    def _load_tournaments(self):
        """Load tournament data"""
        default_tournament = {
            "active_tournaments": [],
            "completed_tournaments": [],
            "player_rankings": {},
            "season_rewards": []
        }
        data = self._load_json("tournaments.json", default_tournament)
        self.tournament_data = data
        return data
    
    def _save_tournaments(self):
        """Save tournament data"""
        self._save_json("tournaments.json", self.tournament_data)
    
    def create_tournament(self, name, entry_fee=50, max_players=16, duration_days=7):
        """Create a new tournament"""
        tournament = {
            "id": f"tournament_{len(self.tournament_data['active_tournaments'])}",
            "name": name,
            "entry_fee": entry_fee,
            "max_players": max_players,
            "duration_days": duration_days,
            "start_time": datetime.datetime.now().isoformat(),
            "participants": [],
            "matches": [],
            "status": "recruiting",
            "prizes": {
                "1st": entry_fee * max_players * 0.5,  # 50% of total pot
                "2nd": entry_fee * max_players * 0.3,  # 30% of total pot
                "3rd": entry_fee * max_players * 0.2   # 20% of total pot
            }
        }
        self.tournament_data["active_tournaments"].append(tournament)
        self._save_tournaments()
        return tournament["id"]
    
    def join_tournament(self, tournament_id):
        """Join a tournament"""
        tournament = None
        for t in self.tournament_data["active_tournaments"]:
            if t["id"] == tournament_id:
                tournament = t
                break
        
        if not tournament:
            return False, "Tournament not found"
        
        if len(tournament["participants"]) >= tournament["max_players"]:
            return False, "Tournament is full"
        
        if tournament["status"] != "recruiting":
            return False, "Tournament is no longer accepting participants"
        
        if self.sp < tournament["entry_fee"]:
            return False, "Not enough SP for entry fee"
        
        # Check if already joined
        for p in tournament["participants"]:
            if p["username"] == self.current_username:
                return False, "Already joined this tournament"
        
        # Deduct entry fee and join
        self.sp -= tournament["entry_fee"]
        tournament["participants"].append({
            "username": self.current_username,
            "score": 0,
            "wins": 0,
            "losses": 0,
            "current_round": 0
        })
        
        self._save_tournaments()
        self._update_sp_label()
        return True, f"Joined {tournament['name']}!"
    
    def submit_tournament_score(self, tournament_id, score):
        """Submit a score for tournament ranking"""
        tournament = None
        for t in self.tournament_data["active_tournaments"]:
            if t["id"] == tournament_id:
                tournament = t
                break
        
        if not tournament:
            return False, "Tournament not found"
        
        # Find participant
        participant = None
        for p in tournament["participants"]:
            if p["username"] == self.current_username:
                participant = p
                break
        
        if not participant:
            return False, "Not participating in this tournament"
        
        participant["score"] += score
        self._save_tournaments()
        return True, f"Score submitted: +{score} points"
    
    def get_tournament_rankings(self, tournament_id):
        """Get current tournament rankings"""
        tournament = None
        for t in self.tournament_data["active_tournaments"]:
            if t["id"] == tournament_id:
                tournament = t
                break
        
        if not tournament:
            return []
        
        # Sort participants by score
        sorted_participants = sorted(tournament["participants"], 
                                   key=lambda x: (x["score"], x["wins"]), 
                                   reverse=True)
        return sorted_participants
    
    def end_tournament(self, tournament_id):
        """End a tournament and distribute prizes"""
        tournament = None
        idx = -1
        for i, t in enumerate(self.tournament_data["active_tournaments"]):
            if t["id"] == tournament_id:
                tournament = t
                idx = i
                break
        
        if not tournament:
            return False, "Tournament not found"
        
        rankings = self.get_tournament_rankings(tournament_id)
        if len(rankings) < 3:
            return False, "Not enough participants to end tournament"
        
        # Distribute prizes
        prizes = tournament["prizes"]
        for i, participant in enumerate(rankings[:3]):
            prize_sp = 0
            if i == 0:
                prize_sp = prizes["1st"]
            elif i == 1:
                prize_sp = prizes["2nd"]
            elif i == 2:
                prize_sp = prizes["3rd"]
            
            # Award SP to winner (would need to load their account)
            # For now, just record the reward
            participant["prize"] = prize_sp
        
        # Move to completed tournaments
        tournament["status"] = "completed"
        tournament["final_rankings"] = rankings
        self.tournament_data["completed_tournaments"].append(tournament)
        del self.tournament_data["active_tournaments"][idx]
        
        self._save_tournaments()
        return True, f"Tournament {tournament['name']} completed!"
    
    # ===== ANALYTICS DASHBOARD =====
    
    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            return "Matplotlib not available for analytics"
        
        # Create analytics window
        ui = self._ui
        analytics_window = self._styled_toplevel("📊 Analytics Dashboard", 1000, 700)
        self._styled_header(analytics_window, "Analytics Dashboard", "Detailed performance metrics", icon="📊")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6))
        fig.patch.set_facecolor(ui["bg_primary"])
        
        # Win/Loss ratio over time
        if hasattr(self, 'game_history') and self.game_history:
            wins_over_time = []
            losses_over_time = []
            win_count = 0
            loss_count = 0
            
            for game in self.game_history[-50:]:  # Last 50 games
                if game.get('result') == 'win':
                    win_count += 1
                else:
                    loss_count += 1
                wins_over_time.append(win_count)
                losses_over_time.append(loss_count)
            
            ax1.plot(wins_over_time, label='Wins', color=self._ui['success'])
            ax1.plot(losses_over_time, label='Losses', color=self._ui['danger'])
            ax1.set_title('Win/Loss Progress', color=self._ui['text_primary'])
            ax1.set_facecolor(self._ui['bg_primary'])
            ax1.legend()
            ax1.tick_params(colors=self._ui['text_secondary'])
        
        # SP progression
        if hasattr(self, 'sp_history') and self.sp_history:
            ax2.plot(self.sp_history[-50:], color=self._ui['gold'])
            ax2.set_title('SP Progression', color=self._ui['text_primary'])
            ax2.set_facecolor(self._ui['bg_primary'])
            ax2.tick_params(colors=self._ui['text_secondary'])
        
        # Equipment usage stats
        equipment_stats = {
            'SP': self.sp,
            'SP+': self.sp_plus,
            'SPx': self.sp_x,
            'SP^': self.sp_caret
        }
        ax3.bar(equipment_stats.keys(), equipment_stats.values(), color=[self._ui['success'], self._ui['gold'], self._ui['warning'], self._ui['danger']])
        ax3.set_title('Equipment Inventory', color=self._ui['text_primary'])
        ax3.set_facecolor(self._ui['bg_primary'])
        ax3.tick_params(colors=self._ui['text_secondary'])
        
        # Achievement progress
        achievements = self._get_achievement_progress()
        achievement_names = list(achievements.keys())[:5]  # Top 5
        achievement_values = [achievements[name] for name in achievement_names]
        ax4.barh(achievement_names, achievement_values, color=self._ui['info'])
        ax4.set_title('Achievement Progress', color=self._ui['text_primary'])
        ax4.set_facecolor(self._ui['bg_primary'])
        ax4.tick_params(colors=self._ui['text_secondary'])
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=analytics_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add close button
        close_btn = tk.Button(analytics_window, text="Close", command=analytics_window.destroy,
                             bg=self._ui["bg_hover"], fg=self._ui["text_primary"], font=self._ui["font_body"])
        close_btn.pack(pady=10)
        
        return "Analytics dashboard opened"
    
    def _get_achievement_progress(self):
        """Get achievement progress for analytics"""
        achievements = {}
        
        # Basic achievements
        achievements["First Win"] = 100 if self.wins_count > 0 else 0
        achievements["10 Wins"] = min(self.wins_count / 10 * 100, 100)
        achievements["50 Wins"] = min(self.wins_count / 50 * 100, 100)
        achievements["100 Wins"] = min(self.wins_count / 100 * 100, 100)
        
        # SP achievements
        total_sp = self.sp + self.sp_plus * 10 + self.sp_x * 50 + self.sp_caret * 100
        achievements["SP Collector"] = min(total_sp / 1000 * 100, 100)
        
        # Equipment achievements
        achievements["Equipment Master"] = 100 if len(self.equipment_inventory.get("owned", [])) >= 5 else len(self.equipment_inventory.get("owned", [])) / 5 * 100
        
        # Challenge achievements
        challenge_completion = sum(1 for c in self.challenge_progress.values() if c > 0)
        achievements["Challenge Seeker"] = min(challenge_completion / 7 * 100, 100)
        
        return achievements
    
    def export_game_data(self):
        """Export all game data for backup/analysis"""
        export_data = {
            "username": self.current_username,
            "stats": self.stats,
            "equipment": {
                "sp": self.sp,
                "sp_plus": self.sp_plus,
                "sp_x": self.sp_x,
                "sp_caret": self.sp_caret,
                "inventory": self.equipment_inventory,
                "equipped": {"gauntlet": self.equipped_gauntlet, "device": self.equipped_device}
            },
            "achievements": self.achievements,
            "game_history": self.game_history[-100:] if hasattr(self, 'game_history') else [],  # Last 100 games
            "challenge_progress": self.challenge_progress,
            "tournaments": self.tournament_data if hasattr(self, 'tournament_data') else {},
            "export_date": datetime.datetime.now().isoformat()
        }
        
        filename = f"questionmark_backup_{self.current_username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            return f"Data exported to {filename}"
        except Exception as e:
            return f"Export failed: {str(e)}"
    
    def _generate_target(self):
        """Generate balanced target properties based on player progress"""
        possible_properties = [
            "has_numbers",      # Very common
            "has_symbols",      # Common
            "has_uppercase",    # Very common
            "has_lowercase",    # Very common
            "is_long",          # Moderately common
            "has_spaces",       # Uncommon
            "has_operators",    # Rare
            "has_multiple_words", # Uncommon
            "has_repeats",      # Moderately common
            "starts_with_letter", # Common
            "ends_with_symbol", # Rare
            "has_punctuation",  # Uncommon
            "has_vowels",       # Very common
            "is_very_long",     # Rare
            "has_consecutive_letters" # Moderately common
        ]

        # Balance difficulty based on player wins and current difficulty
        base_difficulty = {
            "easy": 1,
            "normal": 2,
            "hard": 3
        }

        # Scale up difficulty as player progresses
        progress_bonus = min(self.wins_count // 10, 2)  # +1 difficulty every 10 wins, max +2

        effective_difficulty = base_difficulty[self.difficulty] + progress_bonus

        # Select properties with weighted probabilities for better balance
        property_weights = {
            "has_numbers": 0.8,      # Very likely
            "has_symbols": 0.6,      # Likely
            "has_uppercase": 0.9,    # Very likely
            "has_lowercase": 0.9,    # Very likely
            "is_long": 0.5,          # Moderately likely
            "has_spaces": 0.3,       # Unlikely
            "has_operators": 0.2,    # Rare
            "has_multiple_words": 0.3, # Unlikely
            "has_repeats": 0.4,      # Moderately unlikely
            "starts_with_letter": 0.7, # Likely
            "ends_with_symbol": 0.2, # Rare
            "has_punctuation": 0.3,  # Unlikely
            "has_vowels": 0.8,       # Very likely
            "is_very_long": 0.1,     # Very rare
            "has_consecutive_letters": 0.4 # Moderately unlikely
        }
        # Select properties based on weights and difficulty
        selected_properties = []
        available_props = list(possible_properties)

        for _ in range(effective_difficulty):
            if not available_props:
                break

            # Weight the selection
            weights = [property_weights.get(prop, 0.5) for prop in available_props]
            total_weight = sum(weights)
            if total_weight == 0:
                selected_prop = random.choice(available_props)
            else:
                r = random.uniform(0, total_weight)
                cumulative = 0
                for i, prop in enumerate(available_props):
                    cumulative += weights[i]
                    if r <= cumulative:
                        selected_prop = prop
                        break
                else:
                    selected_prop = available_props[-1]

            selected_properties.append(selected_prop)
            available_props.remove(selected_prop)

        self.target_properties = set(selected_properties)
        
        # April Fools: Sometimes make targets impossible
        if self.is_april_fools and random.random() < 0.1:
            self.target_properties.add("purple_text")  # This property doesn't exist!
    
    def show_login_screen_standalone(self):
        """Show account login/register screen as standalone window (appears FIRST)"""
        login_window = tk.Tk()
        login_window.title("🎮 QUESTIONMARK - LOGIN")
        login_window.geometry("500x600")
        login_window.configure(bg="#0f0f1a")
        login_window.resizable(False, False)
        login_window.attributes("-topmost", True)
        
        # Center window on screen
        login_window.update_idletasks()
        x = (login_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (login_window.winfo_screenheight() // 2) - (600 // 2)
        login_window.geometry(f"+{x}+{y}")
        
        # Create a scrollable container for the login form
        canvas = tk.Canvas(login_window, bg="#0f0f1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(login_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0f0f1a")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _mw_login(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_login))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_login))
        
        # Title
        title_label = tk.Label(scrollable_frame, text="🎮 QUESTIONMARK", font=("Segoe UI", 22, "bold"),
                              bg="#0f0f1a", fg="#b388ff", pady=15)
        title_label.pack()
        
        # Remembered accounts section (if any exist)
        remembered = self.account_manager.get_remembered_accounts()
        if remembered:
            rem_label = tk.Label(scrollable_frame, text="⚡ QUICK LOGIN:", bg="#0f0f1a", fg="#ffab00", 
                                font=("Segoe UI", 11, "bold"))
            rem_label.pack(pady=(15, 8))
            
            for username in remembered:
                def make_quick_login(u=username):
                    def quick_login_cmd():
                        if self.account_manager.auto_login(u):
                            self.current_username = u
                            login_window.destroy()
                            self._create_game_window()
                            self._complete_startup()
                        else:
                            messagebox.showerror("Error", f"Could not auto-login as {u}")
                    return quick_login_cmd
                
                quick_btn = tk.Button(scrollable_frame, text=f"👤 {username}", command=make_quick_login(username),
                                     bg="#1c1c35", fg="#00e676", font=("Segoe UI", 10, "bold"),
                                     padx=15, pady=8, width=40, relief=tk.RAISED, bd=2)
                quick_btn.pack(pady=3)
            
            separator = tk.Label(scrollable_frame, text="━" * 50, bg="#0f0f1a", fg="#5f6368", 
                                font=("Segoe UI", 8))
            separator.pack(pady=15)
        
        # Manual login section
        manual_label = tk.Label(scrollable_frame, text="📝 MANUAL LOGIN:", bg="#0f0f1a", fg="#ffab00", 
                               font=("Segoe UI", 11, "bold"))
        manual_label.pack(pady=(10, 15))
        
        # Username frame
        uname_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        uname_frame.pack(pady=8, fill=tk.X, padx=20)
        tk.Label(uname_frame, text="Username:", bg="#0f0f1a", fg="#e8eaed", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        username_entry = tk.Entry(uname_frame, width=30, font=("Segoe UI", 10), bg="#12121f", fg="#00e676")
        username_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Password frame
        pwd_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        pwd_frame.pack(pady=8, fill=tk.X, padx=20)
        tk.Label(pwd_frame, text="Password:", bg="#0f0f1a", fg="#e8eaed", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        password_entry = tk.Entry(pwd_frame, width=30, font=("Segoe UI", 10), show="•", bg="#12121f", fg="#00e676")
        password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        status_label = tk.Label(scrollable_frame, text="", bg="#0f0f1a", fg="#ffab00", font=("Segoe UI", 9))
        status_label.pack(pady=5)
        
        # Remember me checkbox
        remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(scrollable_frame, text="💾 Remember me for 30 days", variable=remember_var,
                                       bg="#0f0f1a", fg="#e8eaed", selectcolor="#12121f", font=("Segoe UI", 9))
        remember_check.pack(pady=8)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                self._update_label(status_label, "❌ Please enter username and password", "#ff1744")
                return
            success, msg = self.account_manager.login(username, password)
            if success:
                self.current_username = username
                # Save remembered account if checked
                if remember_var.get():
                    self.account_manager.save_remembered_account(username, password)
                login_window.destroy()
                self._create_game_window()
                self._complete_startup()
            else:
                self._update_label(status_label, f"❌ {msg}", "#ff1744")
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                self._update_label(status_label, "❌ Please enter username and password", "#ff1744")
                return
            success, msg = self.account_manager.register(username, password)
            if success:
                self._update_label(status_label, "✅ Account created! Now login", "#00e676")
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            else:
                self._update_label(status_label, f"❌ {msg}", "#ff1744")
        
        def guest_login():
            self.current_username = "Guest"
            login_window.destroy()
            self._create_game_window()
            self._complete_startup()
        
        # Button frame
        btn_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(btn_frame, text="🔓 LOGIN", command=login, bg="#00c853", fg="#000000",
                             font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(btn_frame, text="✏️ REGISTER", command=register, bg="#0091ea", fg="#000000",
                                font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        guest_btn = tk.Button(btn_frame, text="👻 GUEST", command=guest_login,
                             bg="#2a2a4a", fg="#ffffff", font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        guest_btn.pack(side=tk.LEFT, padx=5)
        
        # Focus on username entry
        username_entry.focus()
        
        # Run login window mainloop
        login_window.mainloop()
    
    def show_login_screen(self):
        """Show account login/register screen as in-game overlay"""
        # Create overlay and content frame
        content_frame, login_window, overlay = self._create_overlay_window("🎮 QUESTIONMARK - LOGIN", width=500, height=580)
        
        # Create a scrollable container for the login form
        canvas = tk.Canvas(content_frame, bg="#0f0f1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0f0f1a")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _mw_login2(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_login2))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw_login2))
        
        # Remembered accounts section (if any exist)
        remembered = self.account_manager.get_remembered_accounts()
        if remembered:
            rem_label = tk.Label(scrollable_frame, text="⚡ QUICK LOGIN:", bg="#0f0f1a", fg="#ffab00", 
                                font=("Segoe UI", 11, "bold"))
            rem_label.pack(pady=(15, 8))
            
            for username in remembered:
                def make_quick_login(u=username):
                    def quick_login_cmd():
                        if self.account_manager.auto_login(u):
                            self.current_username = u
                            self._close_overlay_window(login_window, overlay)
                            self._complete_startup()
                        else:
                            self._show_popup_error("Error", f"Could not auto-login as {u}")
                    return quick_login_cmd
                
                quick_btn = tk.Button(scrollable_frame, text=f"👤 {username}", command=make_quick_login(username),
                                     bg="#1c1c35", fg="#00e676", font=("Segoe UI", 10, "bold"),
                                     padx=15, pady=8, width=35, relief=tk.RAISED, bd=2)
                quick_btn.pack(pady=3)
            
            separator = tk.Label(scrollable_frame, text="━" * 40, bg="#0f0f1a", fg="#5f6368", 
                                font=("Segoe UI", 8))
            separator.pack(pady=15)
        
        # Manual login section
        manual_label = tk.Label(scrollable_frame, text="📝 MANUAL LOGIN:", bg="#0f0f1a", fg="#ffab00", 
                               font=("Segoe UI", 11, "bold"))
        manual_label.pack(pady=(10, 15))
        
        # Username frame
        uname_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        uname_frame.pack(pady=8, fill=tk.X, padx=15)
        tk.Label(uname_frame, text="Username:", bg="#0f0f1a", fg="#e8eaed", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        username_entry = tk.Entry(uname_frame, width=30, font=("Segoe UI", 10), bg="#12121f", fg="#00e676")
        username_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Password frame
        pwd_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        pwd_frame.pack(pady=8, fill=tk.X, padx=15)
        tk.Label(pwd_frame, text="Password:", bg="#0f0f1a", fg="#e8eaed", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        password_entry = tk.Entry(pwd_frame, width=30, font=("Segoe UI", 10), show="•", bg="#12121f", fg="#00e676")
        password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        status_label = tk.Label(scrollable_frame, text="", bg="#0f0f1a", fg="#ffab00", font=("Segoe UI", 9))
        status_label.pack(pady=5)
        
        # Remember me checkbox
        remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(scrollable_frame, text="💾 Remember me for 30 days", variable=remember_var,
                                       bg="#0f0f1a", fg="#e8eaed", selectcolor="#12121f", font=("Segoe UI", 9))
        remember_check.pack(pady=8)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                self._update_label(status_label, "❌ Please enter username and password", "#ff1744")
                return
            success, msg = self.account_manager.login(username, password)
            if success:
                self.current_username = username
                # Save remembered account if checked
                if remember_var.get():
                    self.account_manager.save_remembered_account(username, password)
                self._close_overlay_window(login_window, overlay)
                self._complete_startup()
            else:
                self._update_label(status_label, f"❌ {msg}", "#ff1744")
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                self._update_label(status_label, "❌ Please enter username and password", "#ff1744")
                return
            success, msg = self.account_manager.register(username, password)
            if success:
                self._update_label(status_label, "✅ Account created! Now login", "#00e676")
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            else:
                self._update_label(status_label, f"❌ {msg}", "#ff1744")
        
        def guest_login():
            self.current_username = "Guest"
            self._close_overlay_window(login_window, overlay)
            self._complete_startup()
        
        # Button frame
        btn_frame = tk.Frame(scrollable_frame, bg="#0f0f1a")
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(btn_frame, text="🔓 LOGIN", command=login, bg="#00c853", fg="#000000",
                             font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(btn_frame, text="✏️ REGISTER", command=register, bg="#0091ea", fg="#000000",
                                font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        guest_btn = tk.Button(btn_frame, text="👻 GUEST", command=guest_login,
                             bg="#2a2a4a", fg="#e8eaed", font=("Segoe UI", 11, "bold"), padx=18, pady=10, width=10)
        guest_btn.pack(side=tk.LEFT, padx=5)
        
        # Focus on username entry
        username_entry.focus()

    
    def _complete_startup(self):
        """Complete the startup after successful login"""
        # Reload stats for the logged-in user
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        self.roll_count = self.stats.get("total_rolls", 0)
        self.wins_count = self.stats.get("total_wins", 0)
        self.rolls_history = self._load_history()
        self.equipment_inventory = self._load_equipment()
        self._load_user_tournament_scores()
        
        self._setup_gui()
        try:
            self._play_startup_sound()
        except Exception as e:
            pass  # Silently ignore sound errors
        
        # Update labels with loaded stats
        if hasattr(self, 'roll_label'):
            self.roll_label.config(text=str(self.roll_count))
        if hasattr(self, 'wins_label'):
            self.wins_label.config(text=str(self.wins_count))
        self._update_sp_label()
        
        # Start the event loop
        self.root.mainloop()
    
    def _create_game_window(self):
        """Create the main game window (called after successful login)"""
        self.root = tk.Tk()
        
        # ── Initialize UI Style System ─────────────────────────────────
        self._init_ui_style()
        
        if self.is_april_fools:
            april_titles = [
                "Questionmark - April Fools Edition 🤡",
                "QuestionMARK - It's a MARK 📍",
                "Questionmark - This is Fine 🔥",
                "Questionmark - Trust Me Bro 😎",
            ]
            self.root.title(random.choice(april_titles))
        else:
            self.root.title("Questionmark")
        
        self.root.geometry("960x800")
        self.root.configure(bg=self._ui["bg_primary"])
        self.root.minsize(900, 700)
    
    # ── UI STYLE SYSTEM ──────────────────────────────────────────────────
    def _init_ui_style(self):
        """Initialize the unified UI color & font system"""
        self._ui = {
            # Core palette
            "bg_primary":   "#0f0f1a",     # Deep space blue-black
            "bg_secondary": "#161625",     # Card backgrounds
            "bg_card":      "#1c1c35",     # Elevated card surfaces
            "bg_input":     "#12121f",     # Input fields
            "bg_hover":     "#252545",     # Hover state
            
            # Accent colors
            "accent":       "#7c4dff",     # Primary accent — vivid purple
            "accent_light": "#b388ff",     # Light accent
            "accent_glow":  "#651fff",     # Glow effects
            "success":      "#00e676",     # Green — wins, positive
            "warning":      "#ffab00",     # Amber — caution
            "danger":       "#ff1744",     # Red — errors, quit
            "info":         "#00b0ff",     # Cyan — informational
            "gold":         "#ffd740",     # Gold — rewards, premium
            "xp_color":     "#69f0ae",     # XP green
            "sp_color":     "#ea80fc",     # SP pink-purple
            
            # Text colors
            "text_primary":   "#e8eaed",   # Primary text
            "text_secondary": "#9aa0a6",   # Dimmed text
            "text_muted":     "#5f6368",   # Very dim text
            "text_bright":    "#ffffff",    # Bright white
            
            # Borders
            "border":       "#2a2a4a",     # Subtle borders
            "border_light": "#3a3a5a",     # Lighter borders
            
            # Button palette
            "btn_primary":    "#7c4dff",   # Primary action
            "btn_primary_fg": "#ffffff",
            "btn_success":    "#00c853",   # Success/GO
            "btn_success_fg": "#000000",
            "btn_warning":    "#ff6d00",   # Warning/Caution
            "btn_warning_fg": "#000000",
            "btn_danger":     "#d50000",   # Danger/Quit
            "btn_danger_fg":  "#ffffff",
            "btn_info":       "#0091ea",   # Info/Secondary
            "btn_info_fg":    "#ffffff",
            "btn_neutral":    "#2a2a4a",   # Neutral
            "btn_neutral_fg": "#e8eaed",
            
            # Fonts
            "font_title":     ("Segoe UI", 20, "bold"),
            "font_heading":   ("Segoe UI", 14, "bold"),
            "font_subhead":   ("Segoe UI", 12, "bold"),
            "font_body":      ("Segoe UI", 10),
            "font_body_bold": ("Segoe UI", 10, "bold"),
            "font_small":     ("Segoe UI", 9),
            "font_small_bold":("Segoe UI", 9, "bold"),
            "font_mono":      ("Consolas", 10),
            "font_mono_sm":   ("Consolas", 9),
            "font_btn":       ("Segoe UI", 11, "bold"),
            "font_btn_sm":    ("Segoe UI", 9, "bold"),
        }
        
        # Configure ttk styles for notebooks/tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.TNotebook", background=self._ui["bg_primary"],
                        borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("Modern.TNotebook.Tab",
                        background=self._ui["bg_secondary"],
                        foreground=self._ui["text_secondary"],
                        padding=[16, 8],
                        font=self._ui["font_body_bold"])
        style.map("Modern.TNotebook.Tab",
                  background=[("selected", self._ui["accent"]), ("active", self._ui["bg_hover"])],
                  foreground=[("selected", self._ui["text_bright"]), ("active", self._ui["text_primary"])])
        
        style.configure("TScrollbar",
                        background=self._ui["bg_secondary"],
                        troughcolor=self._ui["bg_primary"],
                        borderwidth=0, arrowsize=12)
    
    def _styled_toplevel(self, title, width=800, height=600, min_width=600, min_height=400):
        """Create a consistently styled Toplevel window"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{width}x{height}")
        win.configure(bg=self._ui["bg_primary"])
        win.minsize(min_width, min_height)
        return win
    
    def _styled_header(self, parent, title, subtitle="", icon=""):
        """Create a styled window header bar"""
        header = tk.Frame(parent, bg=self._ui["bg_secondary"], pady=12)
        header.pack(fill=tk.X)
        
        title_text = f"{icon}  {title}" if icon else title
        tk.Label(header, text=title_text, font=self._ui["font_heading"],
                 bg=self._ui["bg_secondary"], fg=self._ui["accent_light"]).pack(anchor="w", padx=20)
        
        if subtitle:
            tk.Label(header, text=subtitle, font=self._ui["font_small"],
                     bg=self._ui["bg_secondary"], fg=self._ui["text_secondary"]).pack(anchor="w", padx=20)
        
        # Separator line
        sep = tk.Frame(parent, bg=self._ui["accent"], height=2)
        sep.pack(fill=tk.X)
        return header
    
    def _styled_card(self, parent, title="", padx=15, pady=10):
        """Create a styled card frame with optional title"""
        outer = tk.Frame(parent, bg=self._ui["border"], padx=1, pady=1)
        card = tk.Frame(outer, bg=self._ui["bg_card"], padx=padx, pady=pady)
        card.pack(fill=tk.BOTH, expand=True)
        
        if title:
            tk.Label(card, text=title, font=self._ui["font_subhead"],
                     bg=self._ui["bg_card"], fg=self._ui["accent_light"],
                     anchor="w").pack(fill=tk.X, pady=(0, 8))
            sep = tk.Frame(card, bg=self._ui["border"], height=1)
            sep.pack(fill=tk.X, pady=(0, 8))
        
        return outer, card
    
    def _styled_button(self, parent, text, command, style="primary", width=14, small=False):
        """Create a consistently styled button"""
        ui = self._ui
        styles = {
            "primary":  (ui["btn_primary"],  ui["btn_primary_fg"]),
            "success":  (ui["btn_success"],  ui["btn_success_fg"]),
            "warning":  (ui["btn_warning"],  ui["btn_warning_fg"]),
            "danger":   (ui["btn_danger"],   ui["btn_danger_fg"]),
            "info":     (ui["btn_info"],     ui["btn_info_fg"]),
            "neutral":  (ui["btn_neutral"],  ui["btn_neutral_fg"]),
            "gold":     (ui["gold"],         "#000000"),
        }
        bg, fg = styles.get(style, styles["primary"])
        font = ui["font_btn_sm"] if small else ui["font_btn"]
        py = 4 if small else 7
        
        btn = tk.Button(parent, text=text, command=command,
                        font=font, bg=bg, fg=fg,
                        activebackground=bg, activeforeground=fg,
                        relief=tk.FLAT, cursor="hand2",
                        padx=12, pady=py, width=width, bd=0)
        
        # Hover effects
        lighter = self._lighten_color(bg, 30)
        btn.bind("<Enter>", lambda e, b=btn, c=lighter: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn
    
    def _lighten_color(self, hex_color, amount=30):
        """Lighten a hex color by a given amount"""
        try:
            hex_color = hex_color.lstrip('#')
            r = min(255, int(hex_color[0:2], 16) + amount)
            g = min(255, int(hex_color[2:4], 16) + amount)
            b = min(255, int(hex_color[4:6], 16) + amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
    
    def _styled_scrollable(self, parent, bg=None):
        """Create a styled scrollable frame and return (outer_frame, scrollable_inner_frame)"""
        if bg is None:
            bg = self._ui["bg_primary"]
        
        outer = tk.Frame(parent, bg=bg)
        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=bg)
        
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make inner frame fill canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mousewheel — bind only while cursor is inside this canvas
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_leave(event):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        # Also bind on the inner frame so children don't steal focus
        inner.bind("<Enter>", _on_enter)
        
        def _cleanup(event=None):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
        
        parent.winfo_toplevel().bind("<Destroy>", _cleanup, add="+")
        
        return outer, inner

    # ── Next-Achievement Tracker helpers ─────────────────────────────
    def _get_nearest_achievements(self, count=3):
        """Return up to *count* locked achievements closest to completion."""
        results = []
        for ach_id, ach in self.achievements.items():
            if ach.get("unlocked"):
                continue
            cur, goal = self._get_achievement_progress(ach_id)
            pct = cur / max(1, goal)
            results.append((ach_id, ach, cur, goal, pct))
        results.sort(key=lambda x: -x[4])          # highest % first
        return results[:count]

    def _update_next_achievement_tracker(self):
        """Refresh the sidebar mini-tracker showing nearest locked achievements."""
        if not hasattr(self, "_ach_tracker_frame"):
            return
        ui = self._ui
        frame = self._ach_tracker_frame
        for w in frame.winfo_children():
            w.destroy()

        rarity_colors = {"common": "#9aa0a6", "rare": "#00b0ff", "epic": "#b388ff", "legendary": "#ffd740"}
        nearest = self._get_nearest_achievements(3)
        if not nearest:
            tk.Label(frame, text="🎉 All achievements unlocked!", font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["gold"]).pack(padx=8, pady=4)
            return

        for ach_id, ach, cur, goal, pct in nearest:
            rc = rarity_colors.get(ach.get("rarity", "common"), ui["text_secondary"])
            row = tk.Frame(frame, bg=ui["bg_card"])
            row.pack(fill=tk.X, padx=6, pady=2)

            tk.Label(row, text=ach["name"], font=("Segoe UI", 8, "bold"),
                     bg=ui["bg_card"], fg=rc, anchor="w").pack(fill=tk.X)

            bar_bg = tk.Frame(row, bg=ui["border"], height=4)
            bar_bg.pack(fill=tk.X, pady=(1, 0))
            bar_bg.pack_propagate(False)
            if pct > 0:
                tk.Frame(bar_bg, bg=rc).place(relwidth=pct, relheight=1.0)

            tk.Label(row, text=f"{cur}/{goal} ({int(pct*100)}%)", font=("Consolas", 7),
                     bg=ui["bg_card"], fg=ui["text_muted"], anchor="e").pack(anchor="e")

    def _update_session_timer(self):
        """Update the session clock label every second."""
        if not hasattr(self, "_session_start"):
            return
        elapsed = int(time.time() - self._session_start)
        h, m, s = elapsed // 3600, elapsed % 3600 // 60, elapsed % 60
        if hasattr(self, "_session_timer_label"):
            self._session_timer_label.config(text=f"⏱ {h:02d}:{m:02d}:{s:02d}")
        self.root.after(1000, self._update_session_timer)

    def _setup_gui(self):
        """Setup the main game GUI with the modern unified theme"""
        ui = self._ui
        
        # ── Menu bar (hidden, keep for keyboard access) ──────────────────
        menubar = tk.Menu(self.root, bg=ui["bg_secondary"], fg=ui["text_primary"],
                          activebackground=ui["accent"], activeforeground=ui["text_bright"],
                          font=ui["font_body"], relief=tk.FLAT, bd=0)
        self.root.config(menu=menubar)
        
        menu_cfg = dict(tearoff=0, bg=ui["bg_secondary"], fg=ui["text_primary"],
                        activebackground=ui["accent"], activeforeground=ui["text_bright"],
                        font=ui["font_body"], relief=tk.FLAT, bd=0)
        
        game_menu = tk.Menu(menubar, **menu_cfg)
        menubar.add_cascade(label="  File  ", menu=game_menu)
        game_menu.add_command(label="🎮  New Game", command=self.reset_game)
        game_menu.add_command(label="💾  Save Game", command=self.save_game)
        game_menu.add_command(label="📂  Load Game", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="🚪  Quit", command=self.quit_game)
        
        if self.current_username and self.account_manager.has_dev_console_access(self.current_username):
            dev_menu = tk.Menu(menubar, **menu_cfg)
            menubar.add_cascade(label="  Dev  ", menu=dev_menu)
            dev_menu.add_command(label="🔧  Dev Console", command=self.show_dev_console)
        
        # ── Title Banner ─────────────────────────────────────────────────
        banner = tk.Frame(self.root, bg=ui["bg_secondary"], pady=10)
        banner.pack(fill=tk.X)
        
        # Accent line top
        tk.Frame(banner, bg=ui["accent"], height=3).pack(fill=tk.X, side=tk.TOP)
        
        title_row = tk.Frame(banner, bg=ui["bg_secondary"])
        title_row.pack(fill=tk.X, padx=20, pady=(8, 0))
        
        tk.Label(title_row, text="QUESTIONMARK", font=("Segoe UI", 22, "bold"),
                 bg=ui["bg_secondary"], fg=ui["accent_light"]).pack(side=tk.LEFT)
        
        # User info badge (right side of banner)
        user_text = f"👤 {self.current_username}" if self.current_username else ""
        tk.Label(title_row, text=user_text, font=ui["font_small_bold"],
                 bg=ui["bg_secondary"], fg=ui["text_secondary"]).pack(side=tk.RIGHT, padx=5)

        # Subtitle
        tk.Label(banner, text="Deduce the hidden properties by analyzing roll results",
                 font=ui["font_small"], bg=ui["bg_secondary"],
                 fg=ui["text_muted"]).pack(anchor="w", padx=20)
        
        # Accent line bottom
        tk.Frame(self.root, bg=ui["accent"], height=2).pack(fill=tk.X)

        # ── Navigation Ribbon ────────────────────────────────────────────
        nav_ribbon = tk.Frame(self.root, bg=ui["bg_secondary"], pady=0)
        nav_ribbon.pack(fill=tk.X)

        nav_inner = tk.Frame(nav_ribbon, bg=ui["bg_secondary"])
        nav_inner.pack(fill=tk.X, padx=12, pady=6)

        def _nav_btn(parent, icon, label, command, color=None):
            """Create a navigation ribbon button"""
            fg = color or ui["text_secondary"]
            frame = tk.Frame(parent, bg=ui["bg_secondary"], cursor="hand2")
            frame.pack(side=tk.LEFT, padx=1)
            btn = tk.Label(frame, text=f"{icon}\n{label}", font=("Segoe UI", 8),
                           bg=ui["bg_secondary"], fg=fg, padx=10, pady=4,
                           justify=tk.CENTER, cursor="hand2")
            btn.pack()
            hover_bg = ui["bg_hover"]
            normal_bg = ui["bg_secondary"]
            for w in (frame, btn):
                w.bind("<Enter>", lambda e, f=frame, b=btn: (
                    f.config(bg=hover_bg), b.config(bg=hover_bg, fg=ui["text_bright"])))
                w.bind("<Leave>", lambda e, f=frame, b=btn, c=fg: (
                    f.config(bg=normal_bg), b.config(bg=normal_bg, fg=c)))
                w.bind("<Button-1>", lambda e, cmd=command: cmd())
            return frame

        def _nav_sep(parent):
            """Vertical separator between nav groups"""
            sep = tk.Frame(parent, bg=ui["border"], width=1)
            sep.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

        # ── Group 1: Info ──
        _nav_btn(nav_inner, "📜", "History",      self.show_history_window,      ui["info"])
        _nav_btn(nav_inner, "📊", "Stats",        self.show_stats_window,        ui["accent_light"])
        _nav_btn(nav_inner, "🏆", "Achieve",      self.show_achievements_window, ui["gold"])
        _nav_btn(nav_inner, "🏅", "Leader",       self.show_leaderboard,         ui["warning"])

        _nav_sep(nav_inner)

        # ── Group 2: Progression ──
        _nav_btn(nav_inner, "📈", "Progress",     self.show_progression_window,  ui["xp_color"])
        _nav_btn(nav_inner, "⚔️", "Equip",        self.show_equipment_window,    ui["danger"])
        _nav_btn(nav_inner, "�", "Craft",        self.show_crafting_bench,      ui["gold"])
        _nav_btn(nav_inner, "�🛒", "Shop",         self.show_shop_window,         ui["sp_color"])
        _nav_btn(nav_inner, "🎯", "Strategy",     self.show_strategy_window,     ui["accent"])

        _nav_sep(nav_inner)

        # ── Group 3: Activities ──
        _nav_btn(nav_inner, "🏟️", "PvP",          self.show_pvp_arena,           ui["danger"])
        _nav_btn(nav_inner, "⚔️", "Tourney",      self.show_tournament_window,   ui["warning"])
        _nav_btn(nav_inner, "🎲", "Modes",        self.show_game_mode_window,    ui["info"])
        _nav_btn(nav_inner, "🕹️", "Mini",         self.play_mini_game,           ui["success"])
        _nav_btn(nav_inner, "📉", "Analytics",    self.show_analytics_window,    ui["text_secondary"])

        _nav_sep(nav_inner)

        # ── Group 4: Social & Collection ──
        _nav_btn(nav_inner, "🏰", "Clans",       self.show_clans_window,        ui["warning"])
        _nav_btn(nav_inner, "📚", "Pokédex",     self.show_pokedex_window,      ui["info"])

        _nav_sep(nav_inner)

        # ── Group 5: System ──
        _nav_btn(nav_inner, "⚙️", "Settings",     self.show_settings_window,     ui["text_secondary"])
        _nav_btn(nav_inner, "📖", "Tutorial",     self.start_tutorial,           ui["text_secondary"])
        
        # ── Stats Bar ────────────────────────────────────────────────────
        stats_bar = tk.Frame(self.root, bg=ui["bg_card"], pady=8)
        stats_bar.pack(fill=tk.X, padx=12, pady=(8, 0))
        
        def _stat_pill(parent, icon, label, value_text, value_color, var_name=None):
            """Create a compact stat indicator pill"""
            pill = tk.Frame(parent, bg=ui["bg_secondary"], padx=10, pady=4)
            pill.pack(side=tk.LEFT, padx=4)
            
            tk.Label(pill, text=f"{icon} {label}", font=ui["font_small"],
                     bg=ui["bg_secondary"], fg=ui["text_secondary"]).pack(side=tk.LEFT)
            lbl = tk.Label(pill, text=value_text, font=ui["font_small_bold"],
                           bg=ui["bg_secondary"], fg=value_color)
            lbl.pack(side=tk.LEFT, padx=(4, 0))
            if var_name:
                setattr(self, var_name, lbl)
            return lbl
        
        _stat_pill(stats_bar, "🎲", "Rolls", str(self.roll_count), ui["gold"], "roll_label")
        _stat_pill(stats_bar, "🏆", "Wins", str(self.wins_count), ui["success"], "wins_label")
        _stat_pill(stats_bar, "💎", "SP", "0|0|0|0", ui["sp_color"], "sp_label")
        _stat_pill(stats_bar, "⚙️", "Mode", self.difficulty.title(), ui["warning"], "difficulty_label")

        # Session timer (right-aligned in stats bar)
        self._session_start = time.time()
        self._session_timer_label = tk.Label(stats_bar, text="⏱ 00:00:00", font=ui["font_small_bold"],
                                             bg=ui["bg_card"], fg=ui["text_muted"])
        self._session_timer_label.pack(side=tk.RIGHT, padx=8)
        self._update_session_timer()

        # ── Next Achievement Tracker ─────────────────────────────────────
        ach_tracker_outer = tk.Frame(self.root, bg=ui["bg_card"])
        ach_tracker_outer.pack(fill=tk.X, padx=12, pady=(4, 0))

        ach_hdr = tk.Frame(ach_tracker_outer, bg=ui["bg_card"])
        ach_hdr.pack(fill=tk.X)
        tk.Label(ach_hdr, text="📌 Next Achievements", font=ui["font_small_bold"],
                 bg=ui["bg_card"], fg=ui["gold"]).pack(side=tk.LEFT, padx=8, pady=(4, 0))

        self._ach_tracker_frame = tk.Frame(ach_tracker_outer, bg=ui["bg_card"])
        self._ach_tracker_frame.pack(fill=tk.X, padx=4, pady=(0, 4))
        self._update_next_achievement_tracker()
        
        # ── Level / Progress Bar ─────────────────────────────────────────
        level_bar = tk.Frame(self.root, bg=ui["bg_primary"], pady=4)
        level_bar.pack(fill=tk.X, padx=12)
        
        left_info = tk.Frame(level_bar, bg=ui["bg_primary"])
        left_info.pack(side=tk.LEFT)
        
        self.level_display_label = tk.Label(left_info,
            text=f"⭐ Lv.{self.player_level}  |  {self.player_xp}/{self.xp_to_level_up} XP",
            font=ui["font_small_bold"], bg=ui["bg_primary"], fg=ui["xp_color"])
        self.level_display_label.pack(side=tk.LEFT, padx=(4, 12))
        
        self.unlock_progress_label = tk.Label(left_info, text="",
            font=ui["font_small"], bg=ui["bg_primary"], fg=ui["info"])
        self.unlock_progress_label.pack(side=tk.LEFT)
        
        self.unlock_bar_canvas = tk.Canvas(level_bar, width=200, height=10,
                                            bg=ui["bg_input"], highlightthickness=0, bd=0)
        self.unlock_bar_canvas.pack(side=tk.LEFT, padx=8)
        
        # Right side — tokens & charges
        right_info = tk.Frame(level_bar, bg=ui["bg_primary"])
        right_info.pack(side=tk.RIGHT)
        
        self.scanner_button = tk.Button(right_info, text="🔍 SCAN",
            font=ui["font_btn_sm"], bg=ui["accent"], fg=ui["text_bright"],
            relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
            command=self.use_property_scanner)
        if self.mechanic_unlocks.get("quest_system", {}).get("unlocked", False):
            self.scanner_button.pack(side=tk.RIGHT, padx=3)
        
        self.reroll_button = tk.Button(right_info, text="🔄 REROLL",
            font=ui["font_btn_sm"], bg=ui["danger"], fg=ui["text_bright"],
            relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
            command=self.use_reroll)
        if self.player_level >= 3 and self.reroll_charges > 0:
            self.reroll_button.pack(side=tk.RIGHT, padx=3)
        
        self.reroll_display_label = tk.Label(right_info,
            text=f"🔄 {self.reroll_charges}" if self.reroll_charges > 0 else "",
            font=ui["font_small_bold"], bg=ui["bg_primary"], fg=ui["gold"])
        self.reroll_display_label.pack(side=tk.RIGHT, padx=4)
        
        tokens = self.rng_influence["luck_tokens"]["current_tokens"] if hasattr(self, 'rng_influence') else 0
        self.tokens_display_label = tk.Label(right_info,
            text=f"🍀 {tokens}" if tokens > 0 else "",
            font=ui["font_small_bold"], bg=ui["bg_primary"], fg=ui["success"])
        self.tokens_display_label.pack(side=tk.RIGHT, padx=4)
        
        self._update_unlock_progress_bar()
        
        # ── Main Content Area ────────────────────────────────────────────
        content = tk.Frame(self.root, bg=ui["bg_primary"])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=(10, 6))

        # ─── Top: Current Roll (full width, prominent) ───────────────────
        roll_frame = tk.Frame(content, bg=ui["bg_card"], bd=0)
        roll_frame.pack(fill=tk.X, pady=(0, 10))

        # Roll header bar with accent left-border
        roll_header = tk.Frame(roll_frame, bg=ui["bg_card"])
        roll_header.pack(fill=tk.X)

        tk.Frame(roll_header, bg=ui["accent"], width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(roll_header, text="  📝  CURRENT ROLL", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["accent_light"]).pack(side=tk.LEFT, padx=8, pady=8)

        self.roll_text = tk.Label(roll_frame, text="Press  ROLL  or  [Space]  to begin…",
                                  font=("Consolas", 13), bg=ui["bg_card"],
                                  fg=ui["text_primary"], wraplength=880,
                                  justify=tk.LEFT, anchor="w",
                                  padx=20, pady=12, height=2)
        self.roll_text.pack(fill=tk.X)

        # Thin accent divider
        tk.Frame(content, bg=ui["border"], height=1).pack(fill=tk.X, pady=(0, 10))

        # ─── Bottom: Two-column layout ───────────────────────────────────
        columns = tk.Frame(content, bg=ui["bg_primary"])
        columns.pack(fill=tk.BOTH, expand=True)
        columns.columnconfigure(0, weight=3, uniform="col")
        columns.columnconfigure(1, weight=2, uniform="col")

        # ── LEFT COLUMN: Properties Found ────────────────────────────────
        props_panel = tk.Frame(columns, bg=ui["bg_card"], bd=0)
        props_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Properties header
        props_hdr = tk.Frame(props_panel, bg=ui["bg_card"])
        props_hdr.pack(fill=tk.X)
        tk.Frame(props_hdr, bg=ui["info"], width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(props_hdr, text="  🔬  PROPERTIES FOUND", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["info"]).pack(side=tk.LEFT, padx=8, pady=8)

        # Separator
        tk.Frame(props_panel, bg=ui["border"], height=1).pack(fill=tk.X)

        self.props_text = tk.Label(props_panel, text="(Roll to analyze)",
                                   font=ui["font_body"], bg=ui["bg_card"],
                                   fg=ui["text_secondary"], justify=tk.LEFT,
                                   anchor="nw", padx=16, pady=12, height=6)
        self.props_text.pack(fill=tk.BOTH, expand=True)

        # ── RIGHT COLUMN: Target Match ───────────────────────────────────
        match_panel = tk.Frame(columns, bg=ui["bg_card"], bd=0)
        match_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Match header
        match_hdr = tk.Frame(match_panel, bg=ui["bg_card"])
        match_hdr.pack(fill=tk.X)
        tk.Frame(match_hdr, bg=ui["success"], width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(match_hdr, text="  🎯  TARGET MATCH", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["success"]).pack(side=tk.LEFT, padx=8, pady=8)

        # Separator
        tk.Frame(match_panel, bg=ui["border"], height=1).pack(fill=tk.X)

        self.match_label = tk.Label(match_panel, text="0/0 matches",
                                    font=("Segoe UI", 20, "bold"), bg=ui["bg_card"],
                                    fg=ui["danger"], pady=14, height=3)
        self.match_label.pack(fill=tk.BOTH, expand=True)
        
        # ── Action Buttons ───────────────────────────────────────────────
        btn_area = tk.Frame(self.root, bg=ui["bg_primary"])
        btn_area.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0, 4))
        
        # Row 1 — core gameplay
        row1 = tk.Frame(btn_area, bg=ui["bg_primary"])
        row1.pack(fill=tk.X, pady=3)
        
        self.roll_button = self._styled_button(row1, "🎲  ROLL", self.manual_roll, style="success", width=14)
        self.roll_button.pack(side=tk.LEFT, padx=3)
        
        self.auto_button = self._styled_button(row1, "⚡ AUTO-ROLL", self.toggle_auto_roll, style="warning", width=14)
        self.auto_button.config(state=tk.DISABLED)
        self.auto_button.pack(side=tk.LEFT, padx=3)
        
        # Speed control
        speed_frame = tk.Frame(row1, bg=ui["bg_secondary"], padx=8, pady=4)
        speed_frame.pack(side=tk.LEFT, padx=3)
        tk.Label(speed_frame, text="Speed", font=ui["font_small"],
                 bg=ui["bg_secondary"], fg=ui["text_secondary"]).pack(side=tk.LEFT, padx=(0, 4))
        self.speed_var = tk.IntVar(value=self.auto_roll_speed)
        speed_spin = tk.Spinbox(speed_frame, from_=1, to=50, textvariable=self.speed_var,
                               width=3, font=ui["font_mono_sm"], bg=ui["bg_input"],
                               fg=ui["success"], buttonbackground=ui["bg_secondary"],
                               relief=tk.FLAT, bd=1, insertbackground=ui["text_primary"],
                               command=self._update_speed)
        speed_spin.pack(side=tk.LEFT)
        speed_spin.bind('<Return>', lambda e: self._update_speed())
        speed_spin.bind('<FocusOut>', lambda e: self._update_speed())
        
        self.hint_button = self._styled_button(row1, "💡 HINT", self.show_hint, style="gold", width=14)
        self.hint_button.pack(side=tk.LEFT, padx=3)
        
        # Row 2 — secondary actions
        row2 = tk.Frame(btn_area, bg=ui["bg_primary"])
        row2.pack(fill=tk.X, pady=3)
        
        self.history_button = self._styled_button(row2, "📜 HISTORY", self.show_history_window, style="info", width=12)
        self.history_button.pack(side=tk.LEFT, padx=3)
        
        stats_btn = self._styled_button(row2, "📊 STATS", self.show_stats_window, style="primary", width=12)
        stats_btn.pack(side=tk.LEFT, padx=3)
        
        reset_btn = self._styled_button(row2, "🔄 RESET", self.reset_game, style="neutral", width=12)
        reset_btn.pack(side=tk.LEFT, padx=3)
        
        self.quit_button = self._styled_button(row2, "🚪 QUIT", self.quit_game, style="danger", width=12)
        self.quit_button.pack(side=tk.LEFT, padx=3)
        
        # ── Footer / Keyboard Shortcuts ──────────────────────────────────
        footer = tk.Frame(self.root, bg=ui["bg_secondary"], pady=6)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(footer, bg=ui["border"], height=1).pack(fill=tk.X, side=tk.TOP)
        tk.Label(footer,
                 text="[Space] Roll  ·  [A] Auto-roll  ·  [H] History  ·  [S] Stats  ·  [I] Hint  ·  [R] Reset  ·  [Q] Quit",
                 font=ui["font_small"], bg=ui["bg_secondary"],
                 fg=ui["text_muted"]).pack()
        
        # ── Key Bindings ─────────────────────────────────────────────────
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.bind('<space>', lambda e: self.manual_roll() if self.roll_button.cget('state') != 'disabled' else None)
        self.root.bind('<Key-a>', lambda e: self.toggle_auto_roll() if self.auto_button.cget('state') != 'disabled' else None)
        self.root.bind('<Key-h>', lambda e: self.show_history_window())
        self.root.bind('<Key-s>', lambda e: self.show_stats_window())
        self.root.bind('<Key-i>', lambda e: self.show_hint())
        self.root.bind('<Key-q>', lambda e: self.quit_game())
        self.root.bind('<Key-r>', lambda e: self.reset_game() if messagebox.askyesno('Reset Round', 'Start a new round?') else None)
        self.root.bind('<Key-Up>', self._check_konami_code)
        self.root.bind('<Key-Down>', self._check_konami_code)
        self.root.bind('<Key-Left>', self._check_konami_code)
        self.root.bind('<Key-Right>', self._check_konami_code)
        self.root.bind('<KeyPress-b>', self._check_konami_code)
        self.root.bind('<KeyPress-a>', self._check_konami_code)
        self.root.focus_set()
    
    def _update_speed(self):
        """Update auto-roll speed from spinbox"""
        try:
            new_speed = max(1, min(50, self.speed_var.get()))
            self.auto_roll_speed = new_speed
            self.speed_var.set(new_speed)
        except:
            self.speed_var.set(self.auto_roll_speed)
    
    def show_hint(self):
        """Show a hint about missing properties"""
        if not self.target_properties:
            return
        
        # Find unmatched properties
        unmatched = self.target_properties - self._get_current_properties()
        
        if not unmatched:
            self._show_popup_info("Hint", "🎉 All target properties are already discovered!\nKeep rolling to find the perfect match.")
            return
        
        # Pick a random unmatched property to hint at
        hint_prop = random.choice(list(unmatched))
        hint_text = self._get_property_hint(hint_prop)
        
        self._show_popup_info("💡 Hint", f"Try to find a string that:\n\n{hint_text}\n\n({len(unmatched)} more properties to discover)")
    
    def _create_popup(self, title, content, width=500, height=300, buttons=None):
        """
        Create an in-game popup overlay
        
        Args:
            title: Popup title
            content: Content widget or text
            width: Popup width
            height: Popup height
            buttons: List of (button_text, command) tuples
        """
        # Create overlay frame that blocks interaction with main window
        overlay = tk.Frame(self.root, bg="black", relief=tk.RAISED, bd=2)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.configure(bg="#000000")
        overlay.lift()
        
        ui = self._ui
        # Create popup container
        popup_frame = tk.Frame(overlay, bg=ui["bg_secondary"], relief=tk.FLAT, bd=0)
        popup_frame.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
        popup_frame.lift()
        
        # Title bar
        title_frame = tk.Frame(popup_frame, bg=ui["bg_card"], relief=tk.FLAT, bd=0)
        title_frame.pack(fill=tk.X)
        tk.Frame(title_frame, bg=ui["accent"], height=3).pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(title_frame, text=title, bg=ui["bg_card"], fg=ui["accent_light"], 
                              font=ui["font_subhead"], padx=10, pady=8)
        title_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        close_btn = tk.Button(title_frame, text="✕", bg=ui["btn_danger"], fg=ui["text_bright"], 
                             font=ui["font_btn_sm"], width=2, padx=5, pady=2, relief=tk.FLAT,
                             command=lambda: self._close_popup(popup_frame, overlay))
        close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Content area
        content_frame = tk.Frame(popup_frame, bg=ui["bg_secondary"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if isinstance(content, str):
            content_label = tk.Label(content_frame, text=content, bg=ui["bg_secondary"], fg=ui["text_primary"], 
                                    font=("Segoe UI", 10), wraplength=width-40, justify=tk.LEFT)
            content_label.pack(fill=tk.BOTH, expand=True)
        else:
            # If content is a widget, pack it directly
            content.pack(fill=tk.BOTH, expand=True)
        
        # Button area
        if buttons:
            button_frame = tk.Frame(popup_frame, bg="#1a1a1a", relief=tk.RIDGE, bd=1)
            button_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            for btn_text, cmd in buttons:
                def make_cmd(close=True, c=cmd):
                    result = c() if cmd else None
                    if close:
                        self._close_popup(popup_frame, overlay)
                    return result
                
                btn = tk.Button(button_frame, text=btn_text, command=make_cmd, 
                              bg="#0066ff", fg="#ffffff", font=("Segoe UI", 10, "bold"),
                              padx=15, pady=8)
                btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        return popup_frame, overlay
    
    def _close_popup(self, popup_frame, overlay):
        """Close a popup"""
        try:
            popup_frame.destroy()
            overlay.destroy()
        except:
            pass
    
    def _show_popup_info(self, title, message):
        """Show an info popup"""
        self._create_popup(title, message, width=450, height=250, 
                          buttons=[("OK", None)])
    
    def _show_popup_warning(self, title, message):
        """Show a warning popup"""
        self._create_popup(title, message, width=450, height=250, 
                          buttons=[("OK", None)])
    
    def _show_popup_error(self, title, message):
        """Show an error popup"""
        self._create_popup(title, message, width=450, height=250, 
                          buttons=[("OK", None)])
    
    def _show_popup_confirm(self, title, message, yes_callback, no_callback=None):
        """Show a confirmation popup"""
        self._create_popup(title, message, width=450, height=250, 
                          buttons=[("Yes", yes_callback), ("No", no_callback if no_callback else lambda: None)])
    
    def _create_overlay_window(self, title, width=800, height=600):
        """
        Create an overlay window that acts like a Toplevel but is inside the root window
        Returns the main content frame where you can add widgets
        """
        # Create overlay backdrop
        overlay = tk.Frame(self.root, bg="black", relief=tk.RAISED, bd=2)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        
        ui = self._ui
        # Create window container
        window_frame = tk.Frame(overlay, bg=ui["bg_secondary"], relief=tk.FLAT, bd=0)
        window_frame.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
        window_frame.lift()
        
        # Title bar
        title_frame = tk.Frame(window_frame, bg=ui["bg_card"], relief=tk.FLAT, bd=0)
        title_frame.pack(fill=tk.X)
        tk.Frame(title_frame, bg=ui["accent"], height=3).pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(title_frame, text=title, bg=ui["bg_card"], fg=ui["accent_light"], 
                              font=ui["font_subhead"], padx=10, pady=8)
        title_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        close_btn = tk.Button(title_frame, text="✕", bg=ui["btn_danger"], fg=ui["text_bright"], 
                             font=ui["font_btn_sm"], width=2, padx=5, pady=2, relief=tk.FLAT,
                             command=lambda: self._close_overlay_window(window_frame, overlay))
        close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Content area (main frame returned to caller)
        content_frame = tk.Frame(window_frame, bg=ui["bg_secondary"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        return content_frame, window_frame, overlay
    
    def _close_overlay_window(self, window_frame, overlay):
        """Close an overlay window"""
        try:
            window_frame.destroy()
            overlay.destroy()
        except:
            pass
    
    def _get_current_properties(self):
        """Get properties from the most recent roll"""
        if not self.rolls_history:
            return set()
        return self.rolls_history[-1]['properties']
    
    def _get_property_hint(self, prop):
        """Get a helpful hint for a property"""
        hints = {
            "has_numbers": "Contains digits (0-9)",
            "has_symbols": "Contains special characters (!@#$%^&*)",
            "has_uppercase": "Contains capital letters (A-Z)",
            "has_lowercase": "Contains small letters (a-z)",
            "is_long": "Is 15+ characters long",
            "has_spaces": "Contains spaces between words",
            "has_operators": "Contains math symbols (+-*/=)",
            "has_multiple_words": "Has 2+ separate words",
            "has_repeats": "Has repeated characters (aa, 11, etc.)",
            "starts_with_letter": "Begins with a letter",
            "ends_with_symbol": "Ends with a symbol or punctuation",
            "has_punctuation": "Contains punctuation marks (.,!?;:)",
            "has_vowels": "Contains vowel letters (a,e,i,o,u)",
            "is_very_long": "Is 25+ characters long",
            "has_consecutive_letters": "Has letters in alphabetical order (abc, xyz)"
        }
        return hints.get(prop, f"Has the '{prop}' property")
    
    def _change_difficulty(self, new_difficulty):
        """Change difficulty and update UI"""
        self.difficulty = new_difficulty
        self.difficulty_label.config(text=new_difficulty.title())
        # Regenerate target with new difficulty
        self._generate_target()
        self._update_display("", set())  # Reset display
    
    def _celebration_animation(self):
        """Play a celebration animation (non-stacking, reduced flashes)"""
        if not self.animations_enabled:
            return
        # Cancel any running celebration to prevent stacking
        if hasattr(self, '_celebration_after_id') and self._celebration_after_id:
            try:
                self.root.after_cancel(self._celebration_after_id)
            except Exception:
                pass
        
        original_bg = self._ui["bg_primary"]
        colors = [self._ui["success"], self._ui["gold"], self._ui["accent"]]
        
        def flash(count):
            if count < 4:  # 4 quick flashes instead of 10
                color = colors[count % len(colors)]
                self.root.configure(bg=color)
                self._celebration_after_id = self.root.after(80, lambda: flash(count + 1))
            else:
                self.root.configure(bg=original_bg)
                self._celebration_after_id = None
        
        flash(0)
    
    def _play_sound_effect(self, effect_name):
        """Play a sound effect by name"""
        if not self.sound_enabled:
            return
        
        effects = {
            "startup": [(800, 200, 0.1), (1000, 200)],
            "win": [(1200, 150, 0.1), (1400, 150, 0.1), (1600, 200)],
            "loss": [(600, 100)],
            "button_click": [(1000, 50)],
            "achievement": [(1500, 200)],
            "roll": [(600, 100)],
            "success": [(1200, 150, 0.1), (1400, 150, 0.1), (1600, 200)],
            "failure": [(400, 200)],
            "level_up": [(1000, 250, 0.1), (1200, 250, 0.1), (1400, 300)],
            "quest_complete": [(800, 200, 0.1), (1000, 200)],
            "item_acquire": [(600, 100)],
            "trophy": [(1200, 150, 0.1), (1400, 150, 0.1), (1600, 200)],
            "menu_open": [(1000, 200)],
            "menu_close": [(800, 200)],
            "error": [(400, 200)],
            "notification": [(1000, 150)],
            "background": [(440, 1500)],
        }
        
        if effect_name in effects:
            self._play_sound(effects[effect_name])
        else:
            print(f"Sound effect not found: {effect_name}")
    
    def _play_startup_sound(self):
        """Play startup sound"""
        if self.is_april_fools:
            self._play_sound_effect("loss")  # Sad trombone
        else:
            self._play_sound_effect("startup")  # Normal startup
    
    def _check_konami_code(self, event):
        """Check for Konami code (up up down down left right left right b/a)"""
        key_map = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'b': 'ba',
            'a': 'ba'
        }
        
        key = key_map.get(event.keysym, event.char.lower() if event.char else '')
        if key:
            self.konami_code_buffer.append(key)
            if len(self.konami_code_buffer) > 10:
                self.konami_code_buffer.pop(0)
            
            konami_sequence = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'ba']
            if self.konami_code_buffer == konami_sequence:
                self._activate_konami_mode()
                self.konami_code_buffer = []
    
    def _activate_konami_mode(self):
        """Activate special Konami code easter egg mode"""
        self.konami_mode_enabled = True
        self._show_popup_info("SPEED RUN MODE UNLOCKED!", 
                          "Press SPACE faster to unlock ultra-fast rolling!\n\n"
                          "Use this mode to set new speed records!")
        
        # Unlock achievement
        if "hidden_easter_egg" not in self.achievements:
            self.achievements["hidden_easter_egg"] = {"name": "Easter Egg Hunter", "unlocked": True, "description": "Found the hidden Konami code (↑↑↓↓←→←→B/A)!"}
        else:
            self.achievements["hidden_easter_egg"]["unlocked"] = True
        
        self._save_achievements()
    
    def _check_daily_bonus(self):
        """Check if player can claim daily bonus"""
        import datetime
        today = datetime.date.today().isoformat()
        
        if self.last_login_date != today:
            self.daily_bonus_claimed = False
            self.last_login_date = today
    
    def claim_daily_bonus(self):
        """Claim daily login bonus"""
        if self.daily_bonus_claimed:
            self._show_popup_warning("Already Claimed", "You already claimed your daily bonus today!")
            return
        
        # Award bonus SP
        bonus_sp = 50 + (self.stats.get('current_streak', 0) * 5)  # Streak multiplier
        self.sp += bonus_sp
        
        # Bonus achievement tracking
        if "daily_login" not in self.achievements:
            self.achievements["daily_login"] = {"unlocked": False, "count": 0}
        
        self.achievements["daily_login"]["count"] = self.achievements["daily_login"].get("count", 0) + 1
        
        if self.achievements["daily_login"]["count"] >= 7:
            self.achievements["daily_login"]["unlocked"] = True
        
        self.daily_bonus_claimed = True
        self._save_achievements()
        self._save_stats()
        
        self._show_popup_info("🎁 Daily Bonus!", f"You earned {bonus_sp} bonus SP!\nStreak bonus: ×{1 + self.stats.get('current_streak', 0) * 0.1:.1f}")
    
    def _play_roll_sound(self):
        """Play roll sound"""
        self._play_sound([(600, 100)])
    
    def _play_success_sound(self):
        """Play success sound"""
        self._play_sound([(1200, 150, 0.1), (1400, 150, 0.1), (1600, 200)])
    
    def _load_achievements(self):
        """Load achievements from file (per-user) — rarity-based system with SP rewards"""
        ach_file = self.account_manager.get_user_achievements_file(self.current_username) if self.current_username else "achievements.json"

        # ── Achievement catalogue ────────────────────────────────────
        # Rarity tiers:  Common ★  |  Rare ★★  |  Epic ★★★  |  Legendary ★★★★
        # Each has: name, desc, rarity, category, reward (SP), goal (for progress)
        default_achievements = {
            # ── Wins ─────────────────────────────────────────────────
            "first_win":       {"unlocked": False, "name": "First Victory",     "desc": "Win your first sequence",            "rarity": "common",    "category": "wins",       "reward": 5,    "goal": 1},
            "ten_wins":        {"unlocked": False, "name": "Dedicated Player",  "desc": "Win 10 sequences",                   "rarity": "common",    "category": "wins",       "reward": 15,   "goal": 10},
            "fifty_wins":      {"unlocked": False, "name": "Master Deductor",   "desc": "Win 50 sequences",                   "rarity": "rare",      "category": "wins",       "reward": 50,   "goal": 50},
            "hundred_wins":    {"unlocked": False, "name": "Centurion",         "desc": "Win 100 sequences",                  "rarity": "epic",      "category": "wins",       "reward": 150,  "goal": 100},
            "fivehundred_wins":{"unlocked": False, "name": "Unstoppable Force", "desc": "Win 500 sequences",                  "rarity": "legendary", "category": "wins",       "reward": 500,  "goal": 500},

            # ── Rolls ────────────────────────────────────────────────
            "hundred_rolls":   {"unlocked": False, "name": "Getting Started",   "desc": "Make 100 rolls",                     "rarity": "common",    "category": "rolls",      "reward": 5,    "goal": 100},
            "fivehundred_rolls":{"unlocked": False,"name": "Automation Expert", "desc": "Make 500 rolls (unlocks auto-roll)",  "rarity": "common",    "category": "rolls",      "reward": 10,   "goal": 500},
            "thousand_rolls":  {"unlocked": False, "name": "Obsessed",          "desc": "Make 1,000 rolls",                   "rarity": "rare",      "category": "rolls",      "reward": 30,   "goal": 1000},
            "fivek_rolls":     {"unlocked": False, "name": "Roll Addict",       "desc": "Make 5,000 rolls",                   "rarity": "epic",      "category": "rolls",      "reward": 100,  "goal": 5000},
            "tenk_rolls":      {"unlocked": False, "name": "Infinity Roller",   "desc": "Make 10,000 rolls",                  "rarity": "legendary", "category": "rolls",      "reward": 300,  "goal": 10000},

            # ── Streaks ──────────────────────────────────────────────
            "perfectionist":   {"unlocked": False, "name": "Perfectionist",     "desc": "Win 3 in a row",                     "rarity": "common",    "category": "streaks",    "reward": 10,   "goal": 3},
            "streak_breaker":  {"unlocked": False, "name": "Streak Breaker",    "desc": "Win 5 in a row",                     "rarity": "rare",      "category": "streaks",    "reward": 30,   "goal": 5},
            "on_fire":         {"unlocked": False, "name": "On Fire",           "desc": "Win 10 in a row",                    "rarity": "epic",      "category": "streaks",    "reward": 75,   "goal": 10},
            "untouchable":     {"unlocked": False, "name": "Untouchable",       "desc": "Win 25 in a row",                    "rarity": "legendary", "category": "streaks",    "reward": 250,  "goal": 25},

            # ── Speed ────────────────────────────────────────────────
            "speed_demon":     {"unlocked": False, "name": "Speed Demon",       "desc": "Win in under 30 rolls",              "rarity": "common",    "category": "speed",      "reward": 10,   "goal": 30},
            "lightning":       {"unlocked": False, "name": "Lightning Fast",    "desc": "Win in under 10 rolls",              "rarity": "rare",      "category": "speed",      "reward": 40,   "goal": 10},
            "lucky_roll":      {"unlocked": False, "name": "Lucky Roll",        "desc": "Win on the very first roll",         "rarity": "legendary", "category": "speed",      "reward": 200,  "goal": 1},

            # ── Currency ─────────────────────────────────────────────
            "sp_collector":    {"unlocked": False, "name": "SP Collector",      "desc": "Accumulate 50 SP",                   "rarity": "common",    "category": "currency",   "reward": 10,   "goal": 50},
            "sp_hoarder":      {"unlocked": False, "name": "SP Hoarder",        "desc": "Accumulate 500 SP",                  "rarity": "rare",      "category": "currency",   "reward": 25,   "goal": 500},
            "sp_plus_hoarder": {"unlocked": False, "name": "SP+ Hoarder",       "desc": "Collect 10 SP+",                     "rarity": "rare",      "category": "currency",   "reward": 20,   "goal": 10},
            "sp_x_master":     {"unlocked": False, "name": "SPx Master",        "desc": "Collect 5 SPx",                      "rarity": "epic",      "category": "currency",   "reward": 50,   "goal": 5},
            "sp_caret_legend": {"unlocked": False, "name": "SP^ Legend",        "desc": "Collect 1 SP^",                      "rarity": "legendary", "category": "currency",   "reward": 100,  "goal": 1},

            # ── Exploration ──────────────────────────────────────────
            "property_master": {"unlocked": False, "name": "Property Spotter",  "desc": "Discover 10 unique properties",      "rarity": "common",    "category": "exploration","reward": 10,   "goal": 10},
            "explorer":        {"unlocked": False, "name": "Property Explorer", "desc": "Discover all 15 properties",         "rarity": "epic",      "category": "exploration","reward": 75,   "goal": 15},

            # ── Equipment ────────────────────────────────────────────
            "first_craft":     {"unlocked": False, "name": "Apprentice Smith",  "desc": "Craft your first equipment",         "rarity": "common",    "category": "equipment",  "reward": 10,   "goal": 1},
            "equipment_master":{"unlocked": False, "name": "Equipment Master",  "desc": "Craft 5 pieces of equipment",        "rarity": "rare",      "category": "equipment",  "reward": 40,   "goal": 5},
            "full_arsenal":    {"unlocked": False, "name": "Full Arsenal",      "desc": "Craft 10 pieces of equipment",       "rarity": "epic",      "category": "equipment",  "reward": 100,  "goal": 10},

            # ── PvP ──────────────────────────────────────────────────
            "pvp_debut":       {"unlocked": False, "name": "Arena Debut",       "desc": "Win your first PvP duel",            "rarity": "common",    "category": "pvp",        "reward": 15,   "goal": 1},
            "pvp_veteran":     {"unlocked": False, "name": "Arena Veteran",     "desc": "Win 25 PvP duels",                   "rarity": "rare",      "category": "pvp",        "reward": 50,   "goal": 25},
            "pvp_champion":    {"unlocked": False, "name": "Arena Champion",    "desc": "Reach Diamond rank in PvP",          "rarity": "epic",      "category": "pvp",        "reward": 150,  "goal": 1},
            "pvp_legend":      {"unlocked": False, "name": "Arena Legend",      "desc": "Reach 1500 ELO",                     "rarity": "legendary", "category": "pvp",        "reward": 300,  "goal": 1500},

            # ── Special ──────────────────────────────────────────────
            "night_owl":       {"unlocked": False, "name": "Night Owl",         "desc": "Play between 12 AM and 6 AM",        "rarity": "rare",      "category": "special",    "reward": 20,   "goal": 1},
            "mini_game_champion":{"unlocked": False,"name": "Mini-Game Champ",  "desc": "Score 1000+ in mini-game",           "rarity": "epic",      "category": "special",    "reward": 50,   "goal": 1000},
            "april_fool":      {"unlocked": False, "name": "April Fool 🤡",    "desc": "Play on April 1st",                  "rarity": "rare",      "category": "special",    "reward": 25,   "goal": 1},
            "marathon":        {"unlocked": False, "name": "Marathon Runner",   "desc": "Play for 1 hour in one session",     "rarity": "rare",      "category": "special",    "reward": 25,   "goal": 1},
            "completionist":   {"unlocked": False, "name": "Completionist",     "desc": "Unlock every other achievement",     "rarity": "legendary", "category": "special",    "reward": 1000, "goal": 1},
        }

        try:
            with open(ach_file, "r") as f:
                loaded = json.load(f)
                merged = default_achievements.copy()
                for k, v in loaded.items():
                    if k in merged:
                        merged[k]["unlocked"] = v.get("unlocked", False)
                        if "unlock_time" in v:
                            merged[k]["unlock_time"] = v["unlock_time"]
                    else:
                        merged[k] = v
                return merged
        except Exception:
            return default_achievements
    
    def _save_achievements(self):
        """Save achievements to file (per-user)"""
        ach_file = self.account_manager.get_user_achievements_file(self.current_username) if self.current_username else "achievements.json"
        self._save_json(ach_file, self.achievements)
    
    def _load_history(self):
        """Load roll history from file (per-user)"""
        hist_file = self.account_manager.get_user_history_file(self.current_username) if self.current_username else "history.json"
        try:
            with open(hist_file, "r") as f:
                raw_history = json.load(f)
                normalized_history = []
                for entry in raw_history:
                    normalized_history.append({
                        "number": entry.get("number", 0),
                        "string": entry.get("string", ""),
                        "properties": set(entry.get("properties", [])),
                        "target_properties": set(entry.get("target_properties", [])),
                        "matches": entry.get("matches", 0),
                        "total_needed": entry.get("total_needed", 0),
                        "timestamp": entry.get("timestamp", ""),
                        "won": entry.get("won", False),
                        "sp_earned": entry.get("sp_earned", 0),
                        "xp_earned": entry.get("xp_earned", 0),
                        "is_critical": entry.get("is_critical", False),
                        "match_pct": entry.get("match_pct", 0.0)
                    })
                return normalized_history
        except Exception as e:
            return []
    
    def _save_history(self):
        """Save roll history to file (per-user)"""
        hist_file = self.account_manager.get_user_history_file(self.current_username) if self.current_username else "history.json"
        history_to_save = []
        for entry in self.rolls_history:
            props = entry.get("properties", set())
            if isinstance(props, set):
                props = list(props)
            target_props = entry.get("target_properties", set())
            if isinstance(target_props, set):
                target_props = list(target_props)
            history_to_save.append({
                "number": entry.get("number", 0),
                "string": entry.get("string", ""),
                "properties": props,
                "target_properties": target_props,
                "matches": entry.get("matches", 0),
                "total_needed": entry.get("total_needed", 0),
                "timestamp": entry.get("timestamp", ""),
                "won": entry.get("won", False),
                "sp_earned": entry.get("sp_earned", 0),
                "xp_earned": entry.get("xp_earned", 0),
                "is_critical": entry.get("is_critical", False),
                "match_pct": entry.get("match_pct", 0.0)
            })
        self._save_json(hist_file, history_to_save)
    
    def _load_stats(self):
        """Load statistics from file (per-user)"""
        stats_file = self.account_manager.get_user_stats_file(self.current_username) if self.current_username else "stats.json"
        try:
            with open(stats_file, "r") as f:
                stats = json.load(f)
            # Post-process loaded stats
            if stats.get('fastest_win') is None:
                stats['fastest_win'] = float('inf')
            # Ensure property_discoveries exists
            if 'property_discoveries' not in stats:
                stats['property_discoveries'] = {}
            # Set start_time for THIS session
            stats['start_time'] = time.time()
            return stats
        except:
            return {
                "total_rolls": 0,
                "total_wins": 0,
                "best_streak": 0,
                "current_streak": 0,
                "fastest_win": float('inf'),
                "slowest_win": 0,
                "avg_rolls_per_win": 0,
                "property_discoveries": {},
                "play_time": 0,
                "start_time": time.time()
            }
    
    def _save_stats(self):
        """Save statistics to file (per-user)"""
        self.stats["total_rolls"] = self.roll_count
        self.stats["total_wins"] = self.wins_count
        self.stats["play_time"] += time.time() - self.stats.get("start_time", time.time())
        self.stats["start_time"] = time.time()  # Reset start_time for next session
        stats_file = self.account_manager.get_user_stats_file(self.current_username) if self.current_username else "stats.json"
        # Create serializable copy (convert infinity to None)
        stats_to_save = self.stats.copy()
        if stats_to_save.get('fastest_win') == float('inf'):
            stats_to_save['fastest_win'] = None
        self._save_json(stats_file, stats_to_save)
    
    def _get_achievement_progress(self, ach_id):
        """Return (current_value, goal) for a given achievement so we can show progress bars."""
        discoveries = self.stats.get('property_discoveries', {})
        total_sp = self.sp + self.sp_plus * 10 + self.sp_x * 50 + self.sp_caret * 100
        crafted = len(self.equipment_inventory.get("owned", []))
        streak = max(self.stats.get('best_streak', 0), self.stats.get('current_streak', 0), self.winning_streak)
        fastest = self.stats.get('fastest_win', float('inf'))
        session_secs = time.time() - self.stats.get('start_time', time.time())
        ach = self.achievements.get(ach_id, {})
        goal = ach.get("goal", 1)

        progress_map = {
            "first_win": self.wins_count, "ten_wins": self.wins_count,
            "fifty_wins": self.wins_count, "hundred_wins": self.wins_count,
            "fivehundred_wins": self.wins_count,
            "hundred_rolls": self.roll_count, "fivehundred_rolls": self.roll_count,
            "thousand_rolls": self.roll_count, "fivek_rolls": self.roll_count,
            "tenk_rolls": self.roll_count,
            "perfectionist": streak, "streak_breaker": streak,
            "on_fire": streak, "untouchable": streak,
            "speed_demon": goal if fastest <= goal else max(0, goal - int(fastest)) if fastest != float('inf') else 0,
            "lightning": goal if fastest <= goal else max(0, goal - int(fastest)) if fastest != float('inf') else 0,
            "lucky_roll": 1 if fastest == 1 else 0,
            "sp_collector": min(total_sp, goal), "sp_hoarder": min(total_sp, goal),
            "sp_plus_hoarder": self.sp_plus, "sp_x_master": self.sp_x,
            "sp_caret_legend": self.sp_caret,
            "property_master": len(discoveries), "explorer": len(discoveries),
            "first_craft": crafted, "equipment_master": crafted, "full_arsenal": crafted,
            "pvp_debut": getattr(self, 'pvp_wins', 0),
            "pvp_veteran": getattr(self, 'pvp_wins', 0),
            "pvp_champion": 1 if self._pvp_rank_for_elo(getattr(self, 'pvp_elo', 1000))[0] in ('Diamond','Master','Grandmaster','Legend') else 0,
            "pvp_legend": min(getattr(self, 'pvp_elo', 1000), goal),
            "night_owl": 1 if 0 <= datetime.datetime.now().hour <= 6 else 0,
            "mini_game_champion": self.mini_game_best,
            "april_fool": 1 if self.is_april_fools else 0,
            "marathon": 1 if session_secs >= 3600 else 0,
        }
        current = progress_map.get(ach_id, 0)
        return (min(current, goal), goal)

    def _check_achievements(self):
        """Check and unlock achievements"""
        unlocked = []
        discoveries = self.stats.get('property_discoveries', {})
        total_sp = self.sp + self.sp_plus * 10 + self.sp_x * 50 + self.sp_caret * 100
        crafted_count = len(self.equipment_inventory.get("owned", []))
        current_hour = datetime.datetime.now().hour
        streak = max(self.stats.get('best_streak', 0), self.stats.get('current_streak', 0), self.winning_streak)
        fastest = self.stats.get('fastest_win', float('inf'))
        session_secs = time.time() - self.stats.get('start_time', time.time())

        checks = [
            ("first_win",        self.wins_count >= 1),
            ("ten_wins",         self.wins_count >= 10),
            ("fifty_wins",       self.wins_count >= 50),
            ("hundred_wins",     self.wins_count >= 100),
            ("fivehundred_wins", self.wins_count >= 500),
            ("hundred_rolls",    self.roll_count >= 100),
            ("fivehundred_rolls",self.roll_count >= 500),
            ("thousand_rolls",   self.roll_count >= 1000),
            ("fivek_rolls",      self.roll_count >= 5000),
            ("tenk_rolls",       self.roll_count >= 10000),
            ("perfectionist",    streak >= 3),
            ("streak_breaker",   streak >= 5),
            ("on_fire",          streak >= 10),
            ("untouchable",      streak >= 25),
            ("speed_demon",      fastest <= 30),
            ("lightning",        fastest <= 10),
            ("lucky_roll",       fastest == 1),
            ("sp_collector",     total_sp >= 50),
            ("sp_hoarder",       total_sp >= 500),
            ("sp_plus_hoarder",  self.sp_plus >= 10),
            ("sp_x_master",      self.sp_x >= 5),
            ("sp_caret_legend",  self.sp_caret >= 1),
            ("property_master",  len(discoveries) >= 10),
            ("explorer",         len(discoveries) >= 15),
            ("first_craft",      crafted_count >= 1),
            ("equipment_master", crafted_count >= 5),
            ("full_arsenal",     crafted_count >= 10),
            ("pvp_debut",        getattr(self, 'pvp_wins', 0) >= 1),
            ("pvp_veteran",      getattr(self, 'pvp_wins', 0) >= 25),
            ("pvp_champion",     self._pvp_rank_for_elo(getattr(self, 'pvp_elo', 1000))[0] in ('Diamond','Master','Grandmaster','Legend')),
            ("pvp_legend",       getattr(self, 'pvp_elo', 1000) >= 1500),
            ("night_owl",        0 <= current_hour <= 6),
            ("mini_game_champion", self.mini_game_best >= 1000),
            ("april_fool",       self.is_april_fools),
            ("marathon",         session_secs >= 3600),
        ]

        for ach_id, condition in checks:
            name = self.achievements.get(ach_id, {}).get("name", ach_id)
            result = self._check_and_unlock_achievement(ach_id, condition, name)
            if result:
                unlocked.append(result)

        # Completionist — every OTHER achievement unlocked
        non_comp = {k: v for k, v in self.achievements.items() if k != "completionist"}
        if all(v.get("unlocked") for v in non_comp.values()):
            r = self._check_and_unlock_achievement("completionist", True, "Completionist")
            if r:
                unlocked.append(r)

        if unlocked:
            self._show_achievement_popup(unlocked)
            self._save_achievements()

        # Refresh the main-screen mini-tracker
        try:
            self._update_next_achievement_tracker()
        except Exception:
            pass
    
    def _show_achievement_popup(self, achievement_names):
        """Show a polished achievement-unlocked popup with rarity colour and reward info."""
        ui = self._ui
        rarity_colors = {"common": "#9aa0a6", "rare": "#00b0ff", "epic": "#b388ff", "legendary": "#ffd740"}
        rarity_stars  = {"common": "★", "rare": "★★", "epic": "★★★", "legendary": "★★★★"}

        popup = self._styled_toplevel("🏆 Achievement Unlocked!", 440, min(120 + len(achievement_names) * 65, 500), 340, 200)

        tk.Frame(popup, bg=ui["gold"], height=3).pack(fill=tk.X)
        tk.Label(popup, text="🏆 ACHIEVEMENT UNLOCKED!", font=ui["font_heading"],
                 bg=ui["bg_primary"], fg=ui["gold"]).pack(pady=(10, 5))

        for name in achievement_names:
            ach_data = None
            for v in self.achievements.values():
                if v.get("name") == name:
                    ach_data = v
                    break
            rarity = ach_data.get("rarity", "common") if ach_data else "common"
            reward = ach_data.get("reward", 0) if ach_data else 0
            rc = rarity_colors.get(rarity, ui["text_primary"])
            stars = rarity_stars.get(rarity, "★")

            row = tk.Frame(popup, bg=ui["bg_card"], highlightbackground=rc, highlightthickness=1)
            row.pack(fill=tk.X, padx=15, pady=3)
            tk.Label(row, text=f"{stars} {name}", font=ui["font_body_bold"],
                     bg=ui["bg_card"], fg=rc, anchor="w").pack(side=tk.LEFT, padx=8, pady=6)
            if reward:
                tk.Label(row, text=f"+{reward} SP", font=ui["font_small_bold"],
                         bg=ui["bg_card"], fg=ui["sp_color"]).pack(side=tk.RIGHT, padx=8)

        self._styled_button(popup, "Awesome!", popup.destroy, style="gold", width=12).pack(pady=10)
    
    def _apply_theme(self, theme):
        """Apply a theme to the GUI"""
        self.current_theme = theme
        
        ui = self._ui
        if theme == "dark":
            colors = {
                "bg": ui["bg_primary"],
                "fg": ui["text_primary"],
                "accent": ui["accent"],
                "secondary": ui["bg_secondary"],
                "button_bg": ui["btn_success"],
                "button_fg": ui["btn_success_fg"]
            }
        elif theme == "light":
            colors = {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "accent": "#006600",
                "secondary": "#ffffff",
                "button_bg": "#00aa00",
                "button_fg": "#ffffff"
            }
        elif theme == "neon":
            colors = {
                "bg": "#000000",
                "fg": "#00ff00",
                "accent": "#ff00ff",
                "secondary": "#001100",
                "button_bg": "#00ff00",
                "button_fg": "#000000"
            }
        
        # Apply colors to main elements
        self.root.configure(bg=colors["bg"])
        self.roll_button.config(bg=colors["button_bg"], fg=colors["button_fg"])
        self.auto_button.config(bg=ui["btn_warning"], fg=ui["btn_warning_fg"])
        self.history_button.config(bg=ui["btn_info"], fg=ui["btn_info_fg"])
        self.quit_button.config(bg=ui["btn_danger"], fg=ui["btn_danger_fg"])
        
        # Update frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg"])
            elif isinstance(widget, tk.Label):
                if "bg" in widget.config():
                    widget.configure(bg=colors["bg"], fg=colors["fg"])
    
    def show_settings_window(self):
        """Show settings window with account management and daily challenges"""
        ui = self._ui
        settings_win = self._styled_toplevel("Questionmark - Settings & Account", width=700, height=650, min_width=600, min_height=500)

        self._styled_header(settings_win, "Settings & Account", subtitle="Manage your preferences", icon="⚙️")

        style = ttk.Style(settings_win)
        style.configure("Modern.TNotebook", background=ui["bg_primary"])
        style.configure("Modern.TNotebook.Tab", background=ui["bg_secondary"], foreground=ui["text_primary"],
                        padding=[12, 6], font=ui["font_body_bold"])
        style.map("Modern.TNotebook.Tab",
                  background=[("selected", ui["accent"]), ("!selected", ui["bg_secondary"])],
                  foreground=[("selected", ui["text_bright"]), ("!selected", ui["text_secondary"])])

        notebook = ttk.Notebook(settings_win, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ── Account Tab ──
        account_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(account_frame, text="  👤 Account  ")

        if self.current_username:
            acc_info = self.account_manager.accounts.get(self.current_username, {})
            created = acc_info.get("created", "Unknown")
            title = self._get_player_title()

            card_outer, card_inner = self._styled_card(account_frame, title="Account Info")
            card_outer.pack(fill=tk.X, padx=15, pady=15)
            info_text = f"Username: {self.current_username}\nTitle: {title}\nCreated: {created}"
            tk.Label(card_inner, text=info_text, font=ui["font_body"], bg=ui["bg_card"],
                     fg=ui["success"], justify=tk.LEFT).pack(pady=10, padx=10)
        else:
            card_outer, card_inner = self._styled_card(account_frame, title="Account Info")
            card_outer.pack(fill=tk.X, padx=15, pady=15)
            tk.Label(card_inner, text="Playing as Guest\n(Create an account to save progress)",
                     font=ui["font_body"], bg=ui["bg_card"], fg=ui["warning"]).pack(pady=10, padx=10)

        # ── Daily Challenges Tab ──
        challenge_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(challenge_frame, text="  🏆 Daily Challenges  ")

        tk.Label(challenge_frame, text="TODAY'S CHALLENGES", font=ui["font_heading"],
                 bg=ui["bg_primary"], fg=ui["accent_light"]).pack(pady=10)

        challenges_scroll = scrolledtext.ScrolledText(challenge_frame, wrap=tk.WORD, height=20, width=70,
                                                      bg=ui["bg_input"], fg=ui["text_primary"], font=ui["font_small"])
        challenges_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        challenges_scroll.config(state=tk.DISABLED)

        challenge_text = ""
        for ch_id, challenge in self.daily_challenges.items():
            current = self.challenge_progress.get(ch_id, 0)
            target = challenge["target"]
            percent = min(100, int((current / target) * 100))
            progress = "█" * (percent // 10) + "░" * (10 - (percent // 10))
            reward = challenge["reward_sp"]
            challenge_text += f"{challenge['icon']} {challenge['name']}\n"
            challenge_text += f"   {challenge['desc']}\n"
            challenge_text += f"   Progress: {current}/{target} [{progress}] +{reward} SP\n\n"

        challenges_scroll.config(state=tk.NORMAL)
        challenges_scroll.insert(1.0, challenge_text)
        challenges_scroll.config(state=tk.DISABLED)

        # ── Settings Tab ──
        settings_tab_container = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(settings_tab_container, text="  🎮 Game Settings  ")

        settings_scroll_outer, settings_frame = self._styled_scrollable(settings_tab_container, ui["bg_primary"])
        settings_scroll_outer.pack(fill=tk.BOTH, expand=True)

        # Sound settings
        sound_frame = tk.LabelFrame(settings_frame, text="🔊 Audio", bg=ui["bg_card"], fg=ui["accent_light"],
                                    font=ui["font_subhead"])
        sound_frame.pack(fill=tk.X, padx=10, pady=5)

        sound_var = tk.BooleanVar(value=self.sound_enabled)
        tk.Checkbutton(sound_frame, text="Enable Sound Effects", variable=sound_var,
                       command=lambda: setattr(self, 'sound_enabled', sound_var.get()),
                       bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                       activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                       font=ui["font_body"]).pack(anchor=tk.W, padx=10, pady=3)

        music_var = tk.BooleanVar(value=self.background_music_enabled)
        tk.Checkbutton(sound_frame, text="Enable Background Music", variable=music_var,
                       command=lambda: setattr(self, 'background_music_enabled', music_var.get()),
                       bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                       activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                       font=ui["font_body"]).pack(anchor=tk.W, padx=10, pady=3)

        # Animation settings
        anim_frame = tk.LabelFrame(settings_frame, text="✨ Visual", bg=ui["bg_card"], fg=ui["accent_light"],
                                   font=ui["font_subhead"])
        anim_frame.pack(fill=tk.X, padx=10, pady=5)

        anim_var = tk.BooleanVar(value=self.animations_enabled)
        tk.Checkbutton(anim_frame, text="Enable Animations", variable=anim_var,
                       command=lambda: setattr(self, 'animations_enabled', anim_var.get()),
                       bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                       activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                       font=ui["font_body"]).pack(anchor=tk.W, padx=10, pady=3)

        stats_var = tk.BooleanVar(value=self.show_stats_on_win)
        tk.Checkbutton(anim_frame, text="Show Stats Pop-up After Win", variable=stats_var,
                       command=lambda: setattr(self, 'show_stats_on_win', stats_var.get()),
                       bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                       activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                       font=ui["font_body"]).pack(anchor=tk.W, padx=10, pady=3)

        # Theme settings
        theme_frame = tk.LabelFrame(settings_frame, text="🎨 Theme", bg=ui["bg_card"], fg=ui["accent_light"],
                                    font=ui["font_subhead"])
        theme_frame.pack(fill=tk.X, padx=10, pady=5)

        theme_var = tk.StringVar(value=self.current_theme)
        themes = [("Dark", "dark"), ("Light", "light"), ("Neon", "neon")]

        for text, value in themes:
            tk.Radiobutton(theme_frame, text=text, variable=theme_var, value=value,
                           command=lambda v=value: self._apply_theme(v),
                           bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                           activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                           font=ui["font_body"]).pack(anchor=tk.W, padx=10)

        # Performance settings
        perf_frame = tk.LabelFrame(settings_frame, text="⚡ Performance", bg=ui["bg_card"], fg=ui["accent_light"],
                                   font=ui["font_subhead"])
        perf_frame.pack(fill=tk.X, padx=10, pady=5)

        autosave_var = tk.BooleanVar(value=self.auto_save_enabled)
        tk.Checkbutton(perf_frame, text="Auto-save on each win", variable=autosave_var,
                       command=lambda: setattr(self, 'auto_save_enabled', autosave_var.get()),
                       bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                       activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                       font=ui["font_body"]).pack(anchor=tk.W, padx=10, pady=3)

        # Difficulty settings
        diff_frame = tk.LabelFrame(settings_frame, text="🎯 Difficulty", bg=ui["bg_card"], fg=ui["accent_light"],
                                   font=ui["font_subhead"])
        diff_frame.pack(fill=tk.X, padx=10, pady=5)

        diff_var = tk.StringVar(value=self.difficulty)
        difficulties = [("Easy (1-2 properties)", "easy"), ("Normal (2-4 properties)", "normal"), ("Hard (3-5 properties)", "hard")]

        for text, value in difficulties:
            tk.Radiobutton(diff_frame, text=text, variable=diff_var, value=value,
                           command=lambda v=value: self._change_difficulty(v),
                           bg=ui["bg_card"], fg=ui["text_primary"], selectcolor=ui["bg_input"],
                           activebackground=ui["bg_card"], activeforeground=ui["text_primary"],
                           font=ui["font_body"]).pack(anchor=tk.W, padx=10)

        # Save/Load
        save_frame = tk.LabelFrame(settings_frame, text="💾 Save/Load", bg=ui["bg_card"], fg=ui["accent_light"],
                                   font=ui["font_subhead"])
        save_frame.pack(fill=tk.X, padx=10, pady=5)

        btn_row = tk.Frame(save_frame, bg=ui["bg_card"])
        btn_row.pack(fill=tk.X, padx=5, pady=5)
        self._styled_button(btn_row, "💾 Save Game", self.save_game, style="success", small=True).pack(side=tk.LEFT, padx=5, pady=5)
        self._styled_button(btn_row, "📂 Load Game", self.load_game, style="warning", small=True).pack(side=tk.LEFT, padx=5, pady=5)

        # Tutorial
        tutorial_frame = tk.LabelFrame(settings_frame, text="❓ Help", bg=ui["bg_card"], fg=ui["accent_light"],
                                       font=ui["font_subhead"])
        tutorial_frame.pack(fill=tk.X, padx=10, pady=5)

        self._styled_button(tutorial_frame, "📖 Start Tutorial", self.start_tutorial, style="info", small=True).pack(pady=5)

        # ── Dev Console Management Tab (only for DeMarcusThe2nd) ──
        if self.current_username == "DeMarcusThe2nd":
            dev_frame = tk.Frame(notebook, bg=ui["bg_primary"])
            notebook.add(dev_frame, text="  🛠️ Dev Console Access  ")

            tk.Label(dev_frame, text="DEV CONSOLE ACCESS MANAGEMENT", font=ui["font_heading"],
                     bg=ui["bg_primary"], fg=ui["danger"]).pack(pady=10)

            # Current allowed users list
            allowed_frame = tk.LabelFrame(dev_frame, text="Currently Allowed Users", bg=ui["bg_card"],
                                          fg=ui["danger"], font=ui["font_subhead"])
            allowed_frame.pack(fill=tk.X, padx=10, pady=5)

            allowed_listbox = tk.Listbox(allowed_frame, height=8, bg=ui["bg_input"], fg=ui["text_primary"],
                                         selectbackground=ui["danger"], font=ui["font_body"])
            allowed_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Populate list
            allowed_users = self.account_manager.get_dev_console_access()
            for user in allowed_users:
                allowed_listbox.insert(tk.END, user)

            # Add/Remove controls
            control_frame = tk.LabelFrame(dev_frame, text="Manage Access", bg=ui["bg_card"],
                                          fg=ui["danger"], font=ui["font_subhead"])
            control_frame.pack(fill=tk.X, padx=10, pady=5)

            username_var = tk.StringVar()
            tk.Label(control_frame, text="Username:", bg=ui["bg_card"], fg=ui["text_primary"],
                     font=ui["font_body"]).grid(row=0, column=0, padx=5, pady=5)
            username_entry = tk.Entry(control_frame, textvariable=username_var, bg=ui["bg_input"],
                                      fg=ui["text_primary"], insertbackground=ui["text_bright"],
                                      font=ui["font_body"])
            username_entry.grid(row=0, column=1, padx=5, pady=5)

            def add_user():
                username = username_var.get().strip()
                if username and self.account_manager.add_dev_console_access(username):
                    allowed_listbox.insert(tk.END, username)
                    username_var.set("")
                    self._show_popup_info("Success", f"Added {username} to dev console access")
                elif username:
                    self._show_popup_warning("Warning", f"{username} already has access or doesn't exist")

            def remove_user():
                selection = allowed_listbox.curselection()
                if selection:
                    username = allowed_listbox.get(selection[0])
                    if self.account_manager.remove_dev_console_access(username):
                        allowed_listbox.delete(selection[0])
                        messagebox.showinfo("Success", f"Removed {username} from dev console access")

            self._styled_button(control_frame, "✅ Add User", add_user, style="success", small=True).grid(row=0, column=2, padx=5, pady=5)
            self._styled_button(control_frame, "❌ Remove Selected", remove_user, style="danger", small=True).grid(row=1, column=1, columnspan=2, pady=5)

    def start_tutorial(self):
        """Start tutorial mode"""
        self.tutorial_mode = True
        self.tutorial_step = 0
        self.show_tutorial_step()
    
    def show_tutorial_step(self):
        """Show current tutorial step"""
        steps = [
            "Welcome to Questionmark! Click ROLL to generate random strings.",
            "Each roll shows properties the string has. Look for patterns!",
            "The target has multiple properties you need to match ALL of them.",
            "Use the feedback (checkmarks) to deduce which properties are required.",
            "Keep rolling until you find a string with ALL target properties!",
            "Try auto-roll once you unlock it at 500 rolls.",
            "Check your achievements and statistics for more fun!"
        ]
        
        if self.tutorial_step < len(steps):
            self._show_popup_info("Tutorial", steps[self.tutorial_step])
            self.tutorial_step += 1
        else:
            self.tutorial_mode = False
            self._show_popup_info("Tutorial Complete", "You're ready to play!")
    

    
    def _auto_save(self):
        """Auto-save: persist stats to user file + backup to autosave.json"""
        # Always save stats to the real per-user file first
        try:
            self._save_stats()
        except Exception:
            pass
        # Also write a full backup to autosave.json
        game_state = {
            "roll_count": self.roll_count,
            "wins_count": self.wins_count,
            "target_properties": list(self.target_properties),
            "rolls_history": self.rolls_history[-500:],  # Save last 500 rolls for auto-save
            "achievements": self.achievements,
            "stats": self.stats,
            "theme": self.current_theme,
            "sound_enabled": self.sound_enabled,
            "animations_enabled": self.animations_enabled,
            "difficulty": self.difficulty,
            "auto_roll_speed": self.auto_roll_speed,
            "challenge_progress": self.challenge_progress,
            "challenge_completed": {
                "challenge_1": getattr(self, '_challenge_1_completed', False),
                "challenge_2": getattr(self, '_challenge_2_completed', False),
                "challenge_3": getattr(self, '_challenge_3_completed', False),
                "challenge_4": getattr(self, '_challenge_4_completed', False),
                "challenge_5": getattr(self, '_challenge_5_completed', False),
                "challenge_6": getattr(self, '_challenge_6_completed', False),
                "challenge_7": getattr(self, '_challenge_7_completed', False),
                "challenge_8": getattr(self, '_challenge_8_completed', False)
            },
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open("autosave.json", "w") as f:
                json.dump(game_state, f, indent=2)
        except Exception as e:
            pass  # Silent fail for auto-save
    
    def load_game(self):
        """Load game state"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, "r") as f:
                    game_state = json.load(f)
                
                self.roll_count = game_state.get("roll_count", 0)
                self.wins_count = game_state.get("wins_count", 0)
                self.target_properties = set(game_state.get("target_properties", []))
                self.rolls_history = game_state.get("rolls_history", [])
                self.achievements = game_state.get("achievements", self._load_achievements())
                self.stats = game_state.get("stats", self._load_stats())
                self.current_theme = game_state.get("theme", "dark")
                self.sound_enabled = game_state.get("sound_enabled", True)
                self.animations_enabled = game_state.get("animations_enabled", True)
                self.difficulty = game_state.get("difficulty", "normal")
                self.auto_roll_speed = game_state.get("auto_roll_speed", 10)
                self.speed_var.set(self.auto_roll_speed)
                
                # Load challenge data
                self.challenge_progress = game_state.get("challenge_progress", {})
                challenge_completed = game_state.get("challenge_completed", {})
                if challenge_completed.get("challenge_1"): self._challenge_1_completed = True
                if challenge_completed.get("challenge_2"): self._challenge_2_completed = True
                if challenge_completed.get("challenge_3"): self._challenge_3_completed = True
                if challenge_completed.get("challenge_4"): self._challenge_4_completed = True
                if challenge_completed.get("challenge_5"): self._challenge_5_completed = True
                if challenge_completed.get("challenge_6"): self._challenge_6_completed = True
                if challenge_completed.get("challenge_7"): self._challenge_7_completed = True
                if challenge_completed.get("challenge_8"): self._challenge_8_completed = True
                
                # Update UI
                self.roll_label.config(text=str(self.roll_count))
                self.wins_label.config(text=str(self.wins_count))
                self._apply_theme(self.current_theme)
                
                self._show_popup_info("Load", "Game loaded successfully!")
            except Exception as e:
                self._show_popup_error("Load Error", "Failed to load game.")
    
    def show_achievements_window(self):
        """Show achievements window — tabbed by category, with progress bars, rarity, rewards."""
        ui = self._ui
        ach_win = self._styled_toplevel("Questionmark - Achievements", width=780, height=650)

        rarity_colors = {"common": "#9aa0a6", "rare": "#00b0ff", "epic": "#b388ff", "legendary": "#ffd740"}
        rarity_labels = {"common": "★ Common", "rare": "★★ Rare", "epic": "★★★ Epic", "legendary": "★★★★ Legendary"}
        category_icons = {
            "wins": "🏆", "rolls": "🎲", "streaks": "🔥", "speed": "⚡",
            "currency": "💰", "exploration": "🔍", "equipment": "⚔️",
            "pvp": "🗡️", "special": "✨",
        }

        # ── Summary header ───────────────────────────────────────────
        total = len(self.achievements)
        done = sum(1 for a in self.achievements.values() if a.get("unlocked"))
        pct = int(done / max(1, total) * 100)
        total_reward = sum(a.get("reward", 0) for a in self.achievements.values() if a.get("unlocked"))

        hdr_frame = tk.Frame(ach_win, bg=ui["bg_secondary"])
        hdr_frame.pack(fill=tk.X, padx=15, pady=(10, 0))

        tk.Label(hdr_frame, text=f"🏆 Achievements", font=ui["font_title"],
                 bg=ui["bg_secondary"], fg=ui["gold"]).pack(side=tk.LEFT, padx=10)

        right_info = tk.Frame(hdr_frame, bg=ui["bg_secondary"])
        right_info.pack(side=tk.RIGHT, padx=10)
        tk.Label(right_info, text=f"{done}/{total} unlocked ({pct}%)", font=ui["font_body_bold"],
                 bg=ui["bg_secondary"], fg=ui["text_primary"]).pack(anchor="e")
        tk.Label(right_info, text=f"💰 {total_reward} SP earned from achievements", font=ui["font_small"],
                 bg=ui["bg_secondary"], fg=ui["sp_color"]).pack(anchor="e")

        # Overall progress bar
        bar_bg = tk.Frame(ach_win, bg=ui["border"], height=8)
        bar_bg.pack(fill=tk.X, padx=15, pady=(4, 8))
        bar_bg.pack_propagate(False)
        if pct > 0:
            tk.Frame(bar_bg, bg=ui["gold"], width=int(7.5 * pct)).pack(side=tk.LEFT, fill=tk.Y)

        # ── Filter bar ───────────────────────────────────────────────
        filter_frame = tk.Frame(ach_win, bg=ui["bg_primary"])
        filter_frame.pack(fill=tk.X, padx=15, pady=(0, 5))

        filter_var = tk.StringVar(value="all")

        def _rebuild_list(*_args):
            for w in scroll_inner.winfo_children():
                w.destroy()
            chosen = filter_var.get()
            for ach_id, ach in self.achievements.items():
                cat = ach.get("category", "special")
                rarity = ach.get("rarity", "common")
                unlocked = ach.get("unlocked", False)
                if chosen == "locked" and unlocked:
                    continue
                if chosen == "unlocked" and not unlocked:
                    continue
                if chosen not in ("all", "locked", "unlocked") and chosen != cat:
                    continue
                _render_ach_card(scroll_inner, ach_id, ach)

        def _render_ach_card(parent, ach_id, ach):
            unlocked = ach.get("unlocked", False)
            rarity = ach.get("rarity", "common")
            rc = rarity_colors.get(rarity, ui["text_secondary"])
            border_c = ui["success"] if unlocked else rc
            status_icon = "✅" if unlocked else "🔒"
            reward = ach.get("reward", 0)
            cat = ach.get("category", "special")
            cat_icon = category_icons.get(cat, "🎯")

            card = tk.Frame(parent, bg=ui["bg_card"], highlightbackground=border_c,
                            highlightthickness=1)
            card.pack(fill=tk.X, padx=5, pady=3)

            # Top row: icon, name, rarity badge, reward
            top = tk.Frame(card, bg=ui["bg_card"])
            top.pack(fill=tk.X, padx=10, pady=(8, 2))

            tk.Label(top, text=f"{status_icon} {cat_icon}", font=ui["font_body"],
                     bg=ui["bg_card"], fg=rc).pack(side=tk.LEFT)
            tk.Label(top, text=ach["name"], font=ui["font_body_bold"],
                     bg=ui["bg_card"], fg=ui["success"] if unlocked else ui["text_primary"]).pack(side=tk.LEFT, padx=(6, 0))
            tk.Label(top, text=rarity_labels.get(rarity, ""), font=ui["font_small"],
                     bg=ui["bg_card"], fg=rc).pack(side=tk.LEFT, padx=(10, 0))
            if reward:
                tk.Label(top, text=f"+{reward} SP", font=ui["font_small_bold"],
                         bg=ui["bg_card"], fg=ui["sp_color"]).pack(side=tk.RIGHT)

            # Description row
            desc_text = ach["desc"]
            if unlocked and ach.get("unlock_time"):
                try:
                    dt = datetime.datetime.fromisoformat(ach["unlock_time"])
                    desc_text += f"  •  Unlocked {dt.strftime('%b %d, %Y')}"
                except Exception:
                    pass
            tk.Label(card, text=desc_text, font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_secondary"], anchor="w").pack(fill=tk.X, padx=10, pady=(0, 2))

            # Progress bar (only for locked achievements)
            if not unlocked:
                cur, goal = self._get_achievement_progress(ach_id)
                pbar_frame = tk.Frame(card, bg=ui["border"], height=6)
                pbar_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
                pbar_frame.pack_propagate(False)
                fill_pct = min(cur / max(1, goal), 1.0)
                if fill_pct > 0:
                    tk.Frame(pbar_frame, bg=rc).place(relwidth=fill_pct, relheight=1.0)
                tk.Label(card, text=f"{cur}/{goal}", font=("Consolas", 8),
                         bg=ui["bg_card"], fg=ui["text_muted"]).pack(anchor="e", padx=10, pady=(0, 4))
            else:
                tk.Frame(card, height=4, bg=ui["bg_card"]).pack()

        # Filter buttons
        filters = [("All", "all"), ("🔓 Unlocked", "unlocked"), ("🔒 Locked", "locked"), ("—", ""),
                   ("🏆 Wins", "wins"), ("🎲 Rolls", "rolls"), ("🔥 Streaks", "streaks"),
                   ("⚡ Speed", "speed"), ("💰 Currency", "currency"), ("🔍 Explore", "exploration"),
                   ("⚔️ Equip", "equipment"), ("🗡️ PvP", "pvp"), ("✨ Special", "special")]
        for label, val in filters:
            if val == "":
                tk.Label(filter_frame, text="|", bg=ui["bg_primary"], fg=ui["border"]).pack(side=tk.LEFT, padx=2)
                continue
            btn = tk.Radiobutton(filter_frame, text=label, variable=filter_var, value=val,
                                 indicatoron=False, font=ui["font_small_bold"],
                                 bg=ui["bg_secondary"], fg=ui["text_secondary"],
                                 selectcolor=ui["accent"], activebackground=ui["bg_hover"],
                                 activeforeground=ui["text_bright"], relief=tk.FLAT, bd=0,
                                 padx=8, pady=3, command=_rebuild_list)
            btn.pack(side=tk.LEFT, padx=1)

        # ── Scrollable achievement list ──────────────────────────────
        scroll_outer, scroll_inner = self._styled_scrollable(ach_win, bg=ui["bg_primary"])
        scroll_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        _rebuild_list()
    
    def show_stats_window(self):
        """Show statistics window"""
        ui = self._ui
        stats_win = self._styled_toplevel("Questionmark - Statistics", width=750, height=650)
        
        self._styled_header(stats_win, "Statistics", subtitle="Your gameplay overview", icon="📊")
        
        # Scrollable content wrapper
        scroll_outer, content = self._styled_scrollable(stats_win, ui["bg_primary"])
        scroll_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        # Basic stats card
        basic_outer, basic_inner = self._styled_card(content, title="Game Statistics")
        basic_outer.pack(fill=tk.X, pady=(0, 10))
        
        stats_text = f"""Total Rolls: {self.roll_count}
Total Wins: {self.wins_count}
Win Rate: {self.wins_count/max(1, self.roll_count)*100:.1f}%
Best Streak: {self.stats.get('best_streak', 0)}
Current Streak: {self.stats.get('current_streak', 0)}
Average Rolls per Win: {self.roll_count/max(1, self.wins_count):.1f}
Play Time: {self.stats.get('play_time', 0)/3600:.1f} hours"""
        
        tk.Label(basic_inner, text=stats_text, font=ui["font_mono_sm"], bg=ui["bg_card"],
                fg=ui["xp_color"], justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=10, pady=8)
        
        # Property discoveries card
        prop_outer, prop_inner = self._styled_card(content, title="Property Discoveries")
        prop_outer.pack(fill=tk.X, pady=(0, 10))
        
        discoveries = self.stats.get('property_discoveries', {})
        prop_text = ""
        for prop in sorted(self._property_name_display(p) for p in self.possible_properties):
            count = discoveries.get(prop, 0)
            prop_text += f"{prop}: {count}\n"
        
        tk.Label(prop_inner, text=prop_text, font=ui["font_mono_sm"], bg=ui["bg_card"],
                fg=ui["text_primary"], justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=10, pady=8)
        
        # Charts section (if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            chart_outer, chart_inner = self._styled_card(content, title="Charts")
            chart_outer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Create a simple bar chart of property discoveries
            fig, ax = plt.subplots(figsize=(6, 4), facecolor=ui["bg_primary"])
            ax.set_facecolor(ui["bg_card"])
            
            props = list(discoveries.keys())
            counts = list(discoveries.values())
            
            bars = ax.bar(range(len(props)), counts, color=ui["accent"])
            ax.set_xticks(range(len(props)))
            ax.set_xticklabels(props, rotation=45, ha='right', color=ui["text_secondary"])
            ax.set_ylabel('Discoveries', color=ui["text_primary"])
            ax.set_title('Property Discoveries', color=ui["text_bright"])
            ax.tick_params(colors=ui["text_secondary"])
            for spine in ax.spines.values():
                spine.set_color(ui["border"])
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_inner)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Show message about matplotlib not being available
            chart_outer, chart_inner = self._styled_card(content, title="Charts")
            chart_outer.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(chart_inner, text="Install matplotlib for charts:\npip install matplotlib",
                    font=ui["font_body"], bg=ui["bg_card"], fg=ui["warning"], justify=tk.LEFT).pack(pady=10)
        
        # Mini-game button
        btn_frame = tk.Frame(content, bg=ui["bg_primary"])
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        self._styled_button(btn_frame, "🎮  Play Mini-Game", self.play_mini_game, style="primary").pack(pady=5)
    
    def play_mini_game(self):
        """Play a simple mini-game - optimized for performance"""
        ui = self._ui
        mini_win = self._styled_toplevel("Questionmark - Mini-Game", 520, 480)
        
        self._styled_header(mini_win, "Mini-Game", "Test your reflexes!", icon="🎮")
        
        content = tk.Frame(mini_win, bg=ui["bg_primary"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(content, text="Match the properties as fast as possible!",
                font=ui["font_heading"], bg=ui["bg_primary"], fg=ui["accent_light"]).pack(pady=10)
        
        instructions = tk.Label(content, text="Click 'START' and wait for the button to turn GREEN.\n"
                                             "Then click it as fast as possible!\n\n"
                                             "Score = 1000 - (reaction time in ms)\n"
                                             "Higher score = faster reaction!",
                              font=ui["font_body"], bg=ui["bg_primary"], fg=ui["text_secondary"], justify=tk.CENTER)
        instructions.pack(pady=10)
        
        # Define missing variables for reaction game
        start_time = time.time()
        
        btn_holder = tk.Frame(content, bg=ui["bg_primary"])
        btn_holder.pack(pady=15)
        
        button = tk.Button(btn_holder, text="Click Me", font=ui["font_btn"],
                          bg=ui["accent"], fg=ui["text_bright"], relief=tk.FLAT,
                          activebackground=ui["accent_light"], padx=20, pady=10,
                          cursor="hand2")
        
        score_label = tk.Label(content, text="Score: 0", font=ui["font_subhead"],
                              bg=ui["bg_primary"], fg=ui["gold"])
        
        def start_reaction_game():
            """Start the reaction time mini-game"""
            nonlocal start_time
            start_time = time.time()
            button.config(bg=ui["success"], activebackground="#00cc00")
            button.after(random.randint(500, 2000), lambda: button.config(bg=ui["danger"]))
        
        def calculate_reaction():
            """Calculate and display reaction time"""
            reaction_time = time.time() - start_time
            score = max(0, int(1000 - (reaction_time * 1000)))
            
            score_label.config(text=f"Score: {score}")
            
            # Update best score
            if score > self.mini_game_best:
                self.mini_game_best = score
            
            # Check achievement
            if score >= 1000 and not self.achievements["mini_game_champion"]["unlocked"]:
                self.achievements["mini_game_champion"]["unlocked"] = True
                self._show_achievement_popup(["Mini-Game Champion"])
                self._save_achievements()
        
        button.config(command=start_reaction_game)
        button.pack(pady=10)
        score_label.pack(pady=5)
        
        # Timer label
        timer_label = tk.Label(content, text="", font=ui["font_subhead"],
                              bg=ui["bg_primary"], fg=ui["warning"])
        timer_label.pack(pady=5)
        
        def update_timer(remaining):
            """Update timer label and check for timeout"""
            if remaining <= 0:
                button.config(state=tk.DISABLED, bg=ui["danger"])
                timer_label.config(text="Time's up!")
                return
            timer_label.config(text=f"Time: {remaining} seconds")
            mini_win.after(1000, update_timer, remaining - 1)
        
        # Start the timer for 30 seconds
        update_timer(30)
    
    def show_leaderboard(self):
        """Multi-tab leaderboard with player profiles, search, and detailed stats."""
        ui = self._ui
        lb_win = self._styled_toplevel("Questionmark - Leaderboard", width=800, height=650)

        # ── Collect all player data ──────────────────────────────────
        players = []
        for username in self.account_manager.accounts:
            if username.startswith("Guest_"):
                continue
            stats_file = self.account_manager.get_user_stats_file(username)
            meta_file = f"user_{username}_meta.json"
            pvp_file = f"user_{username}_pvp.json"
            try:
                stats = {}
                if os.path.exists(stats_file):
                    with open(stats_file, "r") as f:
                        stats = json.load(f)
                meta = {}
                if os.path.exists(meta_file):
                    with open(meta_file, "r") as f:
                        meta = json.load(f)
                pvp = {}
                if os.path.exists(pvp_file):
                    with open(pvp_file, "r") as f:
                        pvp = json.load(f)
            except Exception:
                continue

            wins = stats.get("total_wins", 0)
            rolls = stats.get("total_rolls", 0)
            streak = stats.get("best_streak", 0)
            level = meta.get("level", 1)
            play_time = stats.get("play_time", 0)
            elo = pvp.get("elo", 1000)
            pvp_wins = pvp.get("wins", 0)
            pvp_losses = pvp.get("losses", 0)
            win_rate = round(wins / max(1, rolls) * 100, 1)

            players.append({
                "name": username, "wins": wins, "rolls": rolls, "streak": streak,
                "level": level, "win_rate": win_rate, "play_time": play_time,
                "elo": elo, "pvp_wins": pvp_wins, "pvp_losses": pvp_losses,
                "title": self._get_player_title_for_wins(wins),
            })

        # ── Your profile card ────────────────────────────────────────
        me = next((p for p in players if p["name"] == self.current_username), None)
        if me:
            profile = tk.Frame(lb_win, bg=ui["bg_card"], highlightbackground=ui["gold"], highlightthickness=2)
            profile.pack(fill=tk.X, padx=15, pady=(10, 4))

            profile_font = ("Segoe UI", 16, "bold") if me["name"] == "DeMarcusThe2nd" else ui["font_subhead"]
            tk.Label(profile, text=f"👤  {me['name']}  —  {me['title']}", font=profile_font,
                     bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", padx=12, pady=(8, 2))

            info_row = tk.Frame(profile, bg=ui["bg_card"])
            info_row.pack(fill=tk.X, padx=12, pady=(0, 8))
            for lbl, val, clr in [
                ("Lv", me["level"], ui["xp_color"]),
                ("Wins", me["wins"], ui["success"]),
                ("Rolls", me["rolls"], ui["info"]),
                ("WR", f'{me["win_rate"]}%', ui["accent_light"]),
                ("Streak", me["streak"], ui["warning"]),
                ("ELO", me["elo"], ui["sp_color"]),
            ]:
                tk.Label(info_row, text=f"{lbl}: ", font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_secondary"]).pack(side=tk.LEFT)
                tk.Label(info_row, text=str(val), font=ui["font_small_bold"],
                         bg=ui["bg_card"], fg=clr).pack(side=tk.LEFT, padx=(0, 14))

        # ── Search bar ───────────────────────────────────────────────
        search_frame = tk.Frame(lb_win, bg=ui["bg_primary"])
        search_frame.pack(fill=tk.X, padx=15, pady=(4, 0))
        tk.Label(search_frame, text="🔍", bg=ui["bg_primary"], fg=ui["text_secondary"]).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=ui["font_small"],
                                bg=ui["bg_card"], fg=ui["text_primary"], insertbackground=ui["text_primary"],
                                relief=tk.FLAT, bd=0)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=4)

        # ── Tabs ─────────────────────────────────────────────────────
        nb = ttk.Notebook(lb_win, style="pointed.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True, padx=15, pady=(6, 15))

        medals = ["🥇", "🥈", "🥉"]

        tab_defs = [
            ("🏆 Wins",     "wins",     True),
            ("🎲 Rolls",    "rolls",    True),
            ("⭐ Level",    "level",    True),
            ("📈 Win Rate", "win_rate", True),
            ("🔥 Streak",   "streak",   True),
            ("🗡️ ELO",      "elo",      True),
        ]

        tab_frames = {}

        def _fill_tab(tab_key, sort_key, higher_better):
            frm = tab_frames[tab_key]
            for w in frm.winfo_children():
                w.destroy()

            query = search_var.get().strip().lower()
            filtered = [p for p in players if query in p["name"].lower()] if query else players
            ranked = sorted(filtered, key=lambda p: p[sort_key], reverse=higher_better)

            if not ranked:
                tk.Label(frm, text="No players found.", font=ui["font_body"],
                         bg=ui["bg_secondary"], fg=ui["warning"]).pack(pady=20)
                return

            for i, p in enumerate(ranked[:100], 1):
                medal = medals[i - 1] if i <= 3 else f"{i}."
                is_me = p["name"] == self.current_username
                row_bg = ui["bg_card"] if is_me else ui["bg_secondary"]
                fg = ui["gold"] if is_me else ui["text_primary"]

                row = tk.Frame(frm, bg=row_bg)
                row.pack(fill=tk.X, padx=4, pady=1)

                tk.Label(row, text=f" {medal}", font=ui["font_body_bold"], bg=row_bg, fg=fg,
                         width=4, anchor="w").pack(side=tk.LEFT, padx=(4, 0))
                tk.Label(row, text=p["name"], font=ui["font_body_bold"], bg=row_bg, fg=fg,
                         width=16, anchor="w").pack(side=tk.LEFT, padx=(4, 0))

                # Primary stat for this tab (larger, coloured)
                val = p[sort_key]
                val_text = f"{val}%" if sort_key == "win_rate" else str(val)
                tk.Label(row, text=val_text, font=ui["font_mono_sm"], bg=row_bg,
                         fg=ui["accent_light"], width=8, anchor="e").pack(side=tk.LEFT, padx=(6, 0))

                # Secondary stats row
                extras = []
                if sort_key != "wins":
                    extras.append(f"W:{p['wins']}")
                if sort_key != "rolls":
                    extras.append(f"R:{p['rolls']}")
                if sort_key != "level":
                    extras.append(f"Lv{p['level']}")
                if sort_key != "streak":
                    extras.append(f"🔥{p['streak']}")
                tk.Label(row, text="  ".join(extras[:3]), font=ui["font_small"],
                         bg=row_bg, fg=ui["text_secondary"], anchor="w").pack(side=tk.LEFT, padx=(12, 0))

                title_font = ("Segoe UI", 13, "bold") if p["name"] == "DeMarcusThe2nd" else ui["font_small"]
                title_fg = ui["gold"] if p["name"] == "DeMarcusThe2nd" else ui["text_muted"]
                tk.Label(row, text=p["title"], font=title_font,
                         bg=row_bg, fg=title_fg).pack(side=tk.RIGHT, padx=(0, 8))

        for label, key, desc in tab_defs:
            tab = tk.Frame(nb, bg=ui["bg_secondary"])
            nb.add(tab, text=label)
            scroll_outer, scroll_inner = self._styled_scrollable(tab, bg=ui["bg_secondary"])
            scroll_outer.pack(fill=tk.BOTH, expand=True)
            tab_frames[key] = scroll_inner

        def _refresh_current(*_a):
            idx = nb.index("current")
            _, key, desc = tab_defs[idx]
            _fill_tab(key, key, desc)

        search_var.trace_add("write", _refresh_current)
        nb.bind("<<NotebookTabChanged>>", _refresh_current)

        # Initial fill
        for _, key, desc in tab_defs:
            _fill_tab(key, key, desc)

    def _get_player_title_for_wins(self, wins):
        """Get title based on wins count"""
        # Special unique title for DeMarcusThe2nd
        if getattr(self, "current_username", None) == "DeMarcusThe2nd":
            return "👑 The One And Only"
        if wins >= 500:
            return "⚜️ Mythic"
        elif wins >= 250:
            return "👑 Grandmaster"
        elif wins >= 100:
            return "🌟 Legend"
        elif wins >= 50:
            return "🏅 Master"
        elif wins >= 25:
            return "⭐ Expert"
        elif wins >= 10:
            return "🎖️ Veteran"
        elif wins >= 5:
            return "📘 Adept"
        return "📗 Novice"
    
    def _generate_random_string(self):
        """Generate a random string between 2-50 characters"""
        length = random.randint(2, 50)
        char_pool = string.ascii_letters + string.digits + "!@#$%^&*+-*=()[]{}|;:,.<>? "
        result = []
        for _ in range(length):
            result.append(random.choice(char_pool))
        return ''.join(result)
    
    def _analyze_string(self, s):
        """Analyze which properties a string contains"""
        properties = set()
        
        if any(c.isdigit() for c in s):
            properties.add("has_numbers")
        
        if any(c in "!@#$%^&*-=()[]{}|;:,.<>?" for c in s):
            properties.add("has_symbols")
        
        if any(c.isupper() for c in s):
            properties.add("has_uppercase")
        
        if any(c.islower() for c in s):
            properties.add("has_lowercase")
        
        if len(s) > 25:
            properties.add("is_long")
        
        if " " in s:
            properties.add("has_spaces")
        
        if any(c in "+-*=/<>" for c in s):
            properties.add("has_operators")
        
        words = s.split()
        if len(words) > 1:
            properties.add("has_multiple_words")
        
        # New harder properties
        if len(set(s)) < len(s):  # Has repeated characters
            properties.add("has_repeats")
        
        if s and s[0].isalpha():
            properties.add("starts_with_letter")
        
        if s and s[-1] in "!@#$%^&*-=()[]{}|;:,.<>?":
            properties.add("ends_with_symbol")
        
        if any(c in "!.,;:?'" for c in s):
            properties.add("has_punctuation")
        
        if any(c in "aeiouAEIOU" for c in s):
            properties.add("has_vowels")
        
        if len(s) > 40:
            properties.add("is_very_long")
        
        # Check for consecutive letters
        for i in range(len(s) - 1):
            if s[i].isalpha() and s[i+1].isalpha():
                properties.add("has_consecutive_letters")
                break
        
        return properties
    
    def _property_name_display(self, prop):
        """Convert property name to display format"""
        display_names = {
            "has_numbers": "Has Numbers",
            "has_symbols": "Has Symbols",
            "has_uppercase": "Has Uppercase",
            "has_lowercase": "Has Lowercase",
            "is_long": "Is Long",
            "has_spaces": "Has Spaces",
            "has_operators": "Has Operators",
            "has_multiple_words": "Has Multiple Words",
            "has_repeats": "Has Repeats",
            "starts_with_letter": "Starts With Letter",
            "ends_with_symbol": "Ends With Symbol",
            "has_punctuation": "Has Punctuation",
            "has_vowels": "Has Vowels",
            "is_very_long": "Is Very Long",
            "has_consecutive_letters": "Has Consecutive Letters"
        }
        return display_names.get(prop, prop)
    
    def _update_display(self, string, properties):
        """Update the GUI display"""
        matches = len(properties & self.target_properties)
        total_targets = len(self.target_properties)
        
        # Update roll text
        preview = string if len(string) <= 80 else string[:80] + "..."
        self.roll_text.config(text=f'"{preview}"')
        
        # Update properties with tooltips
        if properties:
            props_display = []
            for prop in sorted(properties):
                marker = "●" if prop in self.target_properties else "○"
                display_name = self._property_name_display(prop)
                props_display.append(f"{marker} {display_name}")
            props_display = "\n".join(props_display)
        else:
            props_display = "(No notable properties)"
        self.props_text.config(text=props_display)

        # Update match count with progress indicator
        color = self._ui["success"] if matches == total_targets else self._ui["danger"]
        progress_bar = "█" * matches + "░" * (total_targets - matches)
        self.match_label.config(text=f"{matches}/{total_targets} matches\n{progress_bar}", fg=color)
        
        # Update roll count
        self.roll_label.config(text=str(self.roll_count))
        
        # Check auto-roll unlock
        if self.roll_count >= 500 and self.auto_button.cget("state") == tk.DISABLED:
            self.auto_button.config(state=tk.NORMAL)
            self.match_label.config(text="⚡ AUTO-ROLL UNLOCKED! ⚡", fg=self._ui["success"], font=("Segoe UI", 14, "bold"))
        
        # Auto-save every 100 rolls
        if self.roll_count % 100 == 0:
            self._auto_save()
    
    def manual_roll(self):
        """Perform a manual roll with full progression system integration"""
        # ── Debounce: skip if less than 50 ms since last roll ────────
        now_ms = time.time()
        if hasattr(self, '_last_roll_time') and (now_ms - self._last_roll_time) < 0.05:
            return
        self._last_roll_time = now_ms

        self.roll_count += 1
        s = self._generate_random_string()
        properties = self._analyze_string(s)
        
        # === PROGRESSION: Apply pre-roll bonuses from equipment/specialization/karma ===
        self._apply_progression_bonuses_to_roll()
        
        # Update property discoveries
        for prop in properties:
            prop_name = self._property_name_display(prop)
            self.stats['property_discoveries'][prop_name] = self.stats['property_discoveries'].get(prop_name, 0) + 1
        
        import datetime as _dt
        self.rolls_history.append({
            'number': self.roll_count,
            'string': s,
            'properties': properties,
            'target_properties': self.target_properties.copy(),
            'matches': len(properties & self.target_properties),
            'total_needed': len(self.target_properties),
            'timestamp': _dt.datetime.now().isoformat(),
            'won': False,
            'sp_earned': 0,
            'xp_earned': 0,
            'is_critical': False,
            'match_pct': round(len(properties & self.target_properties) / max(1, len(self.target_properties)) * 100, 1)
        })
        
        if len(self.rolls_history) > 500:
            self.rolls_history = self.rolls_history[-500:]
        
        self._update_display(s, properties)
        self._play_roll_sound()
        # Only check achievements every 5 rolls to reduce overhead
        if self.roll_count % 5 == 0:
            self._check_achievements()
        
        # Apply temporary effects
        self._update_temp_effect('temp_luck_boost')
        self._update_temp_effect('temp_xp_boost')
        
        # === PROGRESSION: Reroll charge generation (every 10 rolls at level 3+) ===
        if self.player_level >= 3 and self.roll_count % 10 == 0:
            self.reroll_charges = min(self.reroll_charges + 1, 5)
        
        # Check if won
        won = properties == self.target_properties
        
        # === PROGRESSION: Critical roll check ===
        is_critical = False
        if self.critical_roll_chance > 0 and random.random() < self.critical_roll_chance:
            is_critical = True
        
        # Enrich the latest history entry with win/critical status
        if self.rolls_history:
            self.rolls_history[-1]['won'] = won
            self.rolls_history[-1]['is_critical'] = is_critical
        
        # Update match count display
        matches = len(properties & self.target_properties)
        total_needed = len(self.target_properties)
        
        if self.is_april_fools and "purple_text" in self.target_properties:
            self.match_label.config(text="Good luck finding 'purple_text'", fg="#ff00ff", font=("Segoe UI", 12, "bold"))
        else:
            match_percent = (matches / total_needed * 100) if total_needed > 0 else 0
            if match_percent == 100:
                color = self._ui["success"]
                text = f"{matches}/{total_needed} PERFECT MATCH!"
            elif match_percent >= 75:
                color = self._ui["gold"]
                text = f"{matches}/{total_needed} matches (almost there!)"
            elif match_percent >= 50:
                color = self._ui["warning"]
                text = f"{matches}/{total_needed} matches (halfway!)"
            else:
                color = self._ui["danger"]
                text = f"{matches}/{total_needed} matches"
            
            # Show reroll hint if player has charges and is close to winning
            if self.reroll_charges > 0 and match_percent >= 50 and not won:
                text += f" [🔄×{self.reroll_charges}]"
            
            self._update_label(self.match_label, text, color, ("Segoe UI", 14, "bold"))
        
        if won:
            self.wins_count += 1
            self.wins_label.config(text=str(self.wins_count))
            
            if self.is_april_fools and "purple_text" in self.target_properties:
                self.match_label.config(text="HOW DID YOU...??", fg="#ff00ff", font=("Segoe UI", 16, "bold"))
            elif is_critical:
                self.match_label.config(text="⚡ CRITICAL WIN! ⚡", fg="#ffd700", font=("Segoe UI", 16, "bold"))
            else:
                self.match_label.config(text="SUCCESS!", fg=self._ui["success"], font=("Segoe UI", 16, "bold"))
            
            self._play_success_sound()
            self._celebration_animation()
            
            # Calculate base SP
            sp_type, sp_display = self._calculate_sp(len(s))
            sp_gained = 0
            if sp_type == "sp":
                sp_gained = 5
            elif sp_type == "sp_plus":
                sp_gained = 10
            elif sp_type == "sp_x":
                sp_gained = 15
            elif sp_type == "sp_caret":
                sp_gained = 20
            else:
                sp_gained = 1
                sp_display = "SP"
            
            # Apply game mode bonuses
            mode_bonus = self.apply_mode_bonuses(sp_gained)
            sp_gained = mode_bonus
            
            # Apply skill bonuses and streak multiplier
            sp_gained = self._apply_skill_bonuses(sp_gained)
            streak_mult = self._get_streak_multiplier()
            sp_gained = int(sp_gained * streak_mult)
            
            # === PROGRESSION: Specialization SP bonus ===
            if self.current_specialization:
                spec = self.specialization_trees[self.current_specialization]
                sp_bonus = spec["passive_bonuses"].get("sp_efficiency", 0)
                if sp_bonus > 0:
                    sp_gained = int(sp_gained * (1.0 + sp_bonus))
            
            # === PROGRESSION: Equipment SP bonuses ===
            for slot_key, slot in self.equipment_system["slots"].items():
                if slot["level"] > 0:
                    for effect_key, effect_func in slot["effects"].items():
                        if effect_key == "sp_per_roll":
                            sp_gained += int(effect_func(slot["level"]))
                        elif effect_key == "sp_efficiency":
                            sp_gained = int(sp_gained * (1.0 + effect_func(slot["level"])))
            
            # === PROGRESSION: Prestige permanent bonuses ===
            prestige_level = self.prestige_system["current_level"]
            if prestige_level > 0:
                sp_gained = int(sp_gained * (1.0 + prestige_level * 0.01))
            
            # === PROGRESSION: Reward multiplier from luck tokens ===
            if self.reward_multiplier_active > 1.0:
                sp_gained = int(sp_gained * self.reward_multiplier_active)
                self.reward_multiplier_active = 1.0
            
            # === PROGRESSION: Critical roll 3× bonus ===
            if is_critical:
                sp_gained = sp_gained * 3
            
            # Update winning streak
            self._update_winning_streak(True)
            
            # Award SP
            if sp_type == "sp":
                self.sp += sp_gained
            elif sp_type == "sp_plus":
                self.sp_plus += sp_gained
            elif sp_type == "sp_x":
                self.sp_x += sp_gained
            elif sp_type == "sp_caret":
                self.sp_caret += sp_gained
            else:
                self.sp += sp_gained
            
            self.total_sp_earned_today += sp_gained
            
            # Award XP
            xp_earned = 10 + (sp_gained // 5)
            
            # === PROGRESSION: Specialization XP bonus ===
            if self.current_specialization:
                spec = self.specialization_trees[self.current_specialization]
                xp_bonus = spec["passive_bonuses"].get("xp_efficiency", 0)
                if xp_bonus > 0:
                    xp_earned = int(xp_earned * (1.0 + xp_bonus))
            
            # === PROGRESSION: Prestige XP bonus ===
            if prestige_level > 0:
                xp_earned = int(xp_earned * (1.0 + prestige_level * 0.01))
            
            # === PROGRESSION: Critical XP 3× bonus ===
            if is_critical:
                xp_earned = xp_earned * 3
            
            self._add_xp(xp_earned)
            self._update_sp_label()
            
            # Enrich history entry with SP/XP earned
            if self.rolls_history:
                self.rolls_history[-1]['sp_earned'] = sp_gained
                self.rolls_history[-1]['xp_earned'] = xp_earned
            
            # === PROGRESSION: Auto-invest if unlocked ===
            if self.auto_invest_enabled and sp_gained > 0:
                invest_amount = max(1, sp_gained // 20)  # 5% of SP earned
                best_portfolio = max(
                    self.investment_system["portfolios"].items(),
                    key=lambda x: x[1]["base_return_rate"] if x[1]["current_investment"] < x[1]["max_investment"] else 0
                )
                portfolio = best_portfolio[1]
                if portfolio["current_investment"] + invest_amount <= portfolio["max_investment"]:
                    portfolio["current_investment"] += invest_amount
                    self.investment_system["total_invested"] += invest_amount
            
            # === PROGRESSION: Update all progression systems ===
            self._update_progression_after_roll(True, sp_gained, xp_earned)
            
            # Submit score to active tournaments
            tournament_score = sp_gained
            for tournament in self.tournament_data.get("active_tournaments", []):
                if any(p["username"] == self.current_username for p in tournament.get("participants", [])):
                    self.submit_tournament_score(tournament["id"], tournament_score)
            
            # Update daily challenges
            challenge_rewards = self._update_challenges(sp_type, len(s))
            reward_text = ""
            if challenge_rewards:
                reward_text = "\n\n⭐ CHALLENGES COMPLETED:\n" + challenge_rewards
            
            player_title = self._get_player_title_for_wins(self.wins_count)
            bonus_text = ""
            if mode_bonus > sp_gained:
                bonus_text = f" (Mode Bonus: +{mode_bonus - sp_gained})"
            
            # Build victory message with progression info
            streak_text = f" | Streak: {self.winning_streak}" if self.winning_streak > 1 else ""
            level_text = f" | Level {self.player_level}"
            crit_text = "\n\n⚡ CRITICAL ROLL! ×3 REWARDS!" if is_critical else ""
            reroll_text = f"\n🔄 Rerolls: {self.reroll_charges}" if self.reroll_charges > 0 else ""
            
            messagebox.showinfo("Victory!", 
                f"Won sequence!\n+{sp_gained} {sp_display}{bonus_text}\n+{xp_earned} XP{crit_text}\n\n"
                f"Total: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\n\n"
                f"Rank: {player_title}{streak_text}{level_text}{reroll_text}{reward_text}")
            
            # Show streak bonus
            if self.winning_streak >= 3:
                streak_msg = f"🔥 {self.winning_streak}-WIN STREAK! (×{streak_mult:.1f} SP!)"
                try:
                    self.root.after(500, lambda msg=streak_msg: messagebox.showinfo("🎉 COMBO BONUS!", msg))
                    if self.winning_streak % 5 == 0 and self.animations_enabled:
                        self._flash_screen()
                except:
                    pass
            
            # Update stats
            if len(self.rolls_history) > 0:
                rolls_in_win = self.rolls_history[-1]['number'] - (self.rolls_history[-1]['number'] - len([r for r in self.rolls_history if r.get('number', 0) > self.rolls_history[-1]['number'] - 100]))
                rolls_in_win = max(1, rolls_in_win)
                if self.stats['fastest_win'] == float('inf') or rolls_in_win < self.stats['fastest_win']:
                    self.stats['fastest_win'] = rolls_in_win
                self.stats['slowest_win'] = max(self.stats['slowest_win'], rolls_in_win)
            
            self.stats['current_streak'] += 1
            self.stats['best_streak'] = max(self.stats['best_streak'], self.stats['current_streak'])
            
            if self.stats['current_streak'] >= 3:
                self.challenge_progress["challenge_7"] = max(self.challenge_progress.get("challenge_7", 0), self.stats['current_streak'])
            
            # Batch save
            self._save_stats()
            self._save_achievements()
            self._save_equipment()
            self._save_challenge_progress()
            
            # === NEW SYSTEMS: Pokédex, Clan XP, Crafting Discoveries ===
            self._record_pokedex_entry(s, properties)
            self._contribute_clan_xp(sp_gained)
            self._check_crafting_discoveries(properties)
            
            # Update unlock progress bar
            if hasattr(self, 'unlock_progress_label'):
                self._update_unlock_progress_bar()
            
            # Generate new target after 2 seconds
            self.root.after(2000, self._next_sequence)
        else:
            # === PROGRESSION: Streak protection from luck tokens or level 8 ===
            if self.streak_protection_active:
                self.streak_protection_active = False  # Consume protection
                if hasattr(self, 'match_label'):
                    current_text = self.match_label.cget("text")
                    self.match_label.config(text=current_text + " 🛡️", fg="#00ccff")
            else:
                self.stats['current_streak'] = 0
                self._update_winning_streak(False)
            
            # Update progression systems on loss
            self._update_progression_after_roll(False, 0, 0)
            
            # Update unlock progress bar
            if hasattr(self, 'unlock_progress_label'):
                self._update_unlock_progress_bar()
    
    def toggle_auto_roll(self):
        """Toggle auto-roll"""
        if not self.auto_rolling:
            self.auto_rolling = True
            self.auto_button.config(state=tk.DISABLED, text="⏹ STOP AUTO-ROLL")
            self.roll_button.config(state=tk.DISABLED)
            thread = threading.Thread(target=self.auto_roll_thread, daemon=True)
            thread.start()
        else:
            self.auto_rolling = False
            self.auto_button.config(text="⚡ AUTO-ROLL")
            self.roll_button.config(state=tk.NORMAL)
    
    def _next_sequence(self):
        """Generate next sequence after a win"""
        self.game_won = False
        self._generate_target()
        
        # April Fools funny messages
        if self.is_april_fools:
            funny_messages = [
                "0/0 matches - WHAT DOES IT MEAN???",
                "Impossible challenge (jk it's not)",
                "Good luck buddy 😏",
                "You got this... maybe",
                "Plot twist incoming...",
                "This target is sus",
            ]
            message = random.choice(funny_messages)
            self.match_label.config(text=message, fg=self._ui["danger"], font=("Segoe UI", 14, "bold"))
        else:
            self.match_label.config(text="0/0 matches", fg=self._ui["danger"], font=("Segoe UI", 14, "bold"))
        
        self.roll_text.config(text="(No rolls yet)")
        self.props_text.config(text="(Roll to analyze)")
        self.roll_button.config(state=tk.NORMAL)
        self.history_button.config(state=tk.NORMAL)
    
    
    def auto_roll_thread(self):
        """Auto-roll continuously at speed based on rolls_per_second setting"""
        session_start = self.roll_count
        # Calculate batch size: minimum 10, scales with speed
        batch_size = max(10, int(self.auto_roll_speed))
        
        while self.auto_rolling:
            # Perform continuous batches of rolls
            for roll_idx in range(batch_size):
                if not self.auto_rolling:
                    break
                
                self.roll_count += 1
                s = self._generate_random_string()
                properties = self._analyze_string(s)
                
                # Update property discoveries (lightweight)
                for prop in properties:
                    prop_name = self._property_name_display(prop)
                    self.stats['property_discoveries'][prop_name] = self.stats['property_discoveries'].get(prop_name, 0) + 1
                
                self.rolls_history.append({
                    'number': self.roll_count,
                    'string': s,
                    'properties': properties,
                    'target_properties': self.target_properties.copy()
                })
                
                # Keep only the last 100 rolls to prevent memory issues
                if len(self.rolls_history) > 100:
                    self.rolls_history.pop(0)
                
                # Check if won
                won = properties == self.target_properties
                
                # Apply temporary effects
                self._update_temp_effect('temp_luck_boost')
                self._update_temp_effect('temp_xp_boost')
                
                if won:
                    self.wins_count += 1
                    self.root.after(0, lambda: self.wins_label.config(text=str(self.wins_count)))
                    self.root.after(0, lambda: self.match_label.config(text="SUCCESS!", fg=self._ui["success"], font=("Segoe UI", 16, "bold")))
                    self.root.after(0, self._play_success_sound)
                    self.root.after(0, self._update_display, s, properties)
                    
                    # Calculate base SP
                    sp_type, sp_display = self._calculate_sp(len(s))
                    sp_gained = 0
                    if sp_type == "sp":
                        sp_gained = 5
                    elif sp_type == "sp_plus":
                        sp_gained = 10
                    elif sp_type == "sp_x":
                        sp_gained = 15
                    elif sp_type == "sp_caret":
                        sp_gained = 20
                    else:  # Even short strings get minimum SP
                        sp_gained = 1
                    
                    # Apply game mode bonuses
                    mode_bonus = self.apply_mode_bonuses(sp_gained)
                    sp_gained = mode_bonus
                    
                    # Define xp_earned and streak_mult
                    xp_earned = self.calculate_xp(sp_gained)  # Example calculation
                    streak_mult = 1 + (self.winning_streak - 1) * 0.1  # Example multiplier
                    
                    # Apply skill bonuses and streak multiplier
                    sp_gained = self._apply_skill_bonuses(sp_gained)
                    streak_mult = self._get_streak_multiplier()
                    sp_gained = int(sp_gained * streak_mult)
                    
                    # Update winning streak
                    self._update_winning_streak(True)
                    
                    # Award SP
                    if sp_type == "sp":
                        self.sp += sp_gained
                    elif sp_type == "sp_plus":
                        self.sp_plus += sp_gained
                    elif sp_type == "sp_x":
                        self.sp_x += sp_gained
                    elif sp_type == "sp_caret":
                        self.sp_caret += sp_gained
                    else:
                        # Fallback reward for short strings
                        self.sp += sp_gained
            
                    self.total_sp_earned_today += sp_gained
                    
                    # Award XP based on difficulty and SP
                    xp_earned = 10 + (sp_gained // 5)
                    self._add_xp(xp_earned)
                    
                    self._update_sp_label()
                    
                    # Submit score to active tournaments
                    tournament_score = sp_gained
                    for tournament in self.tournament_data.get("active_tournaments", []):
                        if any(p["username"] == self.current_username for p in tournament.get("participants", [])):
                            self.submit_tournament_score(tournament["id"], tournament_score)
            
                    # Update daily challenges and get rewards
                    challenge_rewards = self._update_challenges(sp_type, len(s))
                    reward_text = ""
                    if challenge_rewards:
                        reward_text = "\n\n⭐ CHALLENGES COMPLETED:\n" + challenge_rewards
            
                    player_title = self._get_player_title_for_wins(self.wins_count)
                    bonus_text = ""
                    if mode_bonus > sp_gained:
                        bonus_text = f" (Mode Bonus: +{mode_bonus - sp_gained})"
            
                    streak_text = f" | Streak: {self.winning_streak}" if self.winning_streak > 1 else ""
                    level_text = f" | Level {self.player_level}"
            
                    messagebox.showinfo("Victory!", f"Won sequence!\n+{sp_gained} {sp_display}{bonus_text}\n+{xp_earned} XP\n\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\n\nRank: {player_title}{streak_text}{level_text}{reward_text}")
            
                    # Show streak bonus message with animation (non-blocking)
                    if self.winning_streak >= 3:
                        streak_msg = f"🔥 {self.winning_streak}-WIN STREAK! (×{streak_mult:.1f} SP!)"
                        try:
                            self.root.after(500, lambda msg=streak_msg: messagebox.showinfo("🎉 COMBO BONUS!", msg))
                            # Flash screen on big streaks
                            if self.winning_streak % 5 == 0 and self.animations_enabled:
                                self._flash_screen()
                        except:
                            pass
                
                # Yield to UI thread every few rolls to prevent freezing
                if (roll_idx + 1) % 5 == 0:
                    time.sleep(0.001)  # Tiny sleep to let UI update
            
            # Update display every batch + small yield to prevent lag
            if self.auto_rolling:
                self.root.after(0, self._update_display, s, properties)
                time.sleep(0.001)  # Yield to allow UI thread to process events
    
        # Auto-roll stopped
        self.root.after(0, self.stop_auto_roll_gui)
    
    def stop_auto_roll_gui(self):
        """Stop auto-roll GUI update"""
        self.auto_rolling = False
        self.auto_button.config(state=tk.NORMAL, text="⚡ AUTO-ROLL")
        self.roll_button.config(state=tk.NORMAL)
    
    def show_history_window(self):
        """Show a fully revamped roll history window with tabs, analytics, search, and export"""
        if not self.rolls_history:
            self.match_label.config(text="No rolls yet!", fg=self._ui["danger"], font=("Segoe UI", 14, "bold"))
            return
        
        import datetime as _dt
        
        history_win = tk.Toplevel(self.root)
        history_win.title("📜 Roll History & Analytics")
        history_win.geometry("900x700")
        history_win.configure(bg="#1a1a2e")
        history_win.minsize(800, 600)
        
        # ── Header with session summary ──────────────────────────────────
        header = tk.Frame(history_win, bg="#16213e", pady=8)
        header.pack(fill=tk.X)
        
        total_rolls = len(self.rolls_history)
        total_wins = sum(1 for e in self.rolls_history if e.get('won'))
        total_sp = sum(e.get('sp_earned', 0) for e in self.rolls_history)
        total_xp = sum(e.get('xp_earned', 0) for e in self.rolls_history)
        win_rate = (total_wins / total_rolls * 100) if total_rolls > 0 else 0
        crits = sum(1 for e in self.rolls_history if e.get('is_critical'))
        
        summary_text = (
            f"📊 {total_rolls} Rolls  |  🏆 {total_wins} Wins ({win_rate:.1f}%)  |  "
            f"⚡ {crits} Crits  |  💰 {total_sp} SP  |  ✨ {total_xp} XP"
        )
        tk.Label(header, text=summary_text, font=("Segoe UI", 11, "bold"),
                 bg="#16213e", fg="#e94560").pack()
        
        # ── Tab buttons ──────────────────────────────────────────────────
        tab_bar = tk.Frame(history_win, bg="#1a1a2e")
        tab_bar.pack(fill=tk.X, padx=10, pady=(8, 0))
        
        # Content area — single frame we swap children in
        content_area = tk.Frame(history_win, bg="#1a1a2e")
        content_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        active_tab = [None]  # mutable so nested funcs can write
        tab_buttons = {}
        
        def _switch_tab(name):
            for child in content_area.winfo_children():
                child.destroy()
            for btn_name, btn in tab_buttons.items():
                if btn_name == name:
                    btn.config(bg="#e94560", fg="#ffffff")
                else:
                    btn.config(bg="#2a2a4a", fg="#aaaaaa")
            active_tab[0] = name
            if name == "timeline":
                self._build_history_timeline_tab(content_area)
            elif name == "analytics":
                self._build_history_analytics_tab(content_area)
            elif name == "search":
                self._build_history_search_tab(content_area)
            elif name == "streaks":
                self._build_history_streaks_tab(content_area)
            elif name == "export":
                self._build_history_export_tab(content_area)
        
        tab_defs = [
            ("timeline", "📜 Timeline"),
            ("analytics", "📈 Analytics"),
            ("streaks", "🔥 Streaks & Records"),
            ("search", "🔍 Search & Filter"),
            ("export", "💾 Export"),
        ]
        for key, label in tab_defs:
            btn = tk.Button(tab_bar, text=label, font=("Segoe UI", 10, "bold"),
                            bg="#2a2a4a", fg="#aaaaaa", relief=tk.FLAT, padx=14, pady=4,
                            activebackground="#e94560", activeforeground="#ffffff",
                            cursor="hand2", command=lambda k=key: _switch_tab(k))
            btn.pack(side=tk.LEFT, padx=2)
            tab_buttons[key] = btn
        
        # Start on timeline
        _switch_tab("timeline")
    
    # ── TIMELINE TAB ─────────────────────────────────────────────────────
    def _build_history_timeline_tab(self, parent):
        """Scrollable timeline of recent rolls with colour-coded cards"""
        outer = tk.Frame(parent, bg="#1a1a2e")
        outer.pack(fill=tk.BOTH, expand=True)
        
        # Filter row
        filt_frame = tk.Frame(outer, bg="#1a1a2e")
        filt_frame.pack(fill=tk.X, pady=(0, 5))
        
        filter_var = tk.StringVar(value="all")
        for val, txt in [("all", "All"), ("wins", "🏆 Wins Only"), ("losses", "❌ Losses Only"), ("crits", "⚡ Crits Only")]:
            tk.Radiobutton(filt_frame, text=txt, variable=filter_var, value=val,
                           font=("Segoe UI", 9), bg="#1a1a2e", fg="#cccccc",
                           selectcolor="#2a2a4a", activebackground="#1a1a2e",
                           activeforeground="#ffffff", indicatoron=0, padx=10, pady=3,
                           relief=tk.FLAT, overrelief=tk.RAISED,
                           command=lambda: _refresh()).pack(side=tk.LEFT, padx=3)
        
        # Page controls
        page_size = 50
        page_var = [0]  # current page index
        
        page_label = tk.Label(filt_frame, text="", font=("Segoe UI", 9),
                              bg="#1a1a2e", fg="#888888")
        page_label.pack(side=tk.RIGHT, padx=5)
        
        def _go_page(delta):
            page_var[0] = max(0, page_var[0] + delta)
            _refresh()
        
        tk.Button(filt_frame, text="◀ Older", font=("Segoe UI", 8), bg="#2a2a4a", fg="#cccccc",
                  relief=tk.FLAT, command=lambda: _go_page(-1)).pack(side=tk.RIGHT, padx=2)
        tk.Button(filt_frame, text="Newer ▶", font=("Segoe UI", 8), bg="#2a2a4a", fg="#cccccc",
                  relief=tk.FLAT, command=lambda: _go_page(1)).pack(side=tk.RIGHT, padx=2)
        
        # Scrollable canvas
        canvas = tk.Canvas(outer, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#1a1a2e")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mousewheel scroll — bind only when cursor is over this canvas
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scroll_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        
        def _refresh():
            for w in scroll_frame.winfo_children():
                w.destroy()
            
            f = filter_var.get()
            if f == "all":
                data = list(self.rolls_history)
            elif f == "wins":
                data = [e for e in self.rolls_history if e.get('won')]
            elif f == "losses":
                data = [e for e in self.rolls_history if not e.get('won')]
            elif f == "crits":
                data = [e for e in self.rolls_history if e.get('is_critical')]
            else:
                data = list(self.rolls_history)
            
            total_pages = max(1, (len(data) + page_size - 1) // page_size)
            page_var[0] = min(page_var[0], total_pages - 1)
            page_var[0] = max(0, page_var[0])
            
            # Reverse so newest first, then paginate
            data_rev = list(reversed(data))
            start = page_var[0] * page_size
            page_data = data_rev[start:start + page_size]
            
            page_label.config(text=f"Page {page_var[0]+1}/{total_pages}  ({len(data)} rolls)")
            
            if not page_data:
                tk.Label(scroll_frame, text="No rolls match this filter.",
                         font=("Segoe UI", 12), bg="#1a1a2e", fg="#888888").pack(pady=30)
                return
            
            for entry in page_data:
                self._create_history_card(scroll_frame, entry)
        
        _refresh()
    
    def _create_history_card(self, parent, entry):
        """Create a single colour-coded roll card"""
        won = entry.get('won', False)
        is_crit = entry.get('is_critical', False)
        matches = entry.get('matches', len(entry.get('properties', set()) & entry.get('target_properties', set())))
        total = entry.get('total_needed', len(entry.get('target_properties', set())))
        match_pct = entry.get('match_pct', round(matches / max(1, total) * 100, 1))
        
        # Card colours
        if won and is_crit:
            bg = "#3d1a6e"
            border_color = "#ffd700"
            status_icon = "⚡🏆"
        elif won:
            bg = "#1a3d2e"
            border_color = "#00ff88"
            status_icon = "🏆"
        elif match_pct >= 75:
            bg = "#3d3d1a"
            border_color = "#ffcc00"
            status_icon = "🔶"
        elif match_pct >= 50:
            bg = "#2e2e1a"
            border_color = "#ff9900"
            status_icon = "🔸"
        else:
            bg = "#2a2a3a"
            border_color = "#555555"
            status_icon = "○"
        
        card = tk.Frame(parent, bg=bg, highlightbackground=border_color,
                        highlightthickness=1, padx=8, pady=5)
        card.pack(fill=tk.X, padx=5, pady=2)
        
        # Row 1: Roll # + status + string preview
        row1 = tk.Frame(card, bg=bg)
        row1.pack(fill=tk.X)
        
        roll_num_text = f"{status_icon} Roll #{entry.get('number', '?')}"
        tk.Label(row1, text=roll_num_text, font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=border_color).pack(side=tk.LEFT)
        
        # Timestamp
        ts = entry.get('timestamp', '')
        if ts:
            try:
                import datetime as _dt
                dt = _dt.datetime.fromisoformat(ts)
                time_str = dt.strftime("%b %d, %H:%M:%S")
            except Exception:
                time_str = ts[:19] if len(ts) >= 19 else ts
        else:
            time_str = ""
        if time_str:
            tk.Label(row1, text=time_str, font=("Segoe UI", 8),
                     bg=bg, fg="#888888").pack(side=tk.RIGHT)
        
        # Row 2: String preview
        preview = entry.get('string', '')
        if len(preview) > 70:
            preview = preview[:67] + "..."
        tk.Label(card, text=f'"{preview}"', font=("Consolas", 9),
                 bg=bg, fg="#cccccc", anchor="w").pack(fill=tk.X)
        
        # Row 3: Match bar + stats
        row3 = tk.Frame(card, bg=bg)
        row3.pack(fill=tk.X, pady=(2, 0))
        
        # Mini match bar
        bar_canvas = tk.Canvas(row3, width=120, height=10, bg="#333333",
                               highlightthickness=0)
        bar_canvas.pack(side=tk.LEFT, padx=(0, 8))
        fill_w = int(120 * match_pct / 100)
        if fill_w > 0:
            if match_pct == 100:
                bar_col = "#00ff88"
            elif match_pct >= 75:
                bar_col = "#ffcc00"
            elif match_pct >= 50:
                bar_col = "#ff9900"
            else:
                bar_col = "#ff4444"
            bar_canvas.create_rectangle(0, 0, fill_w, 10, fill=bar_col, outline="")
        
        tk.Label(row3, text=f"{matches}/{total} ({match_pct}%)",
                 font=("Segoe UI", 9), bg=bg, fg="#cccccc").pack(side=tk.LEFT)
        
        # SP / XP earned
        sp = entry.get('sp_earned', 0)
        xp = entry.get('xp_earned', 0)
        if sp > 0 or xp > 0:
            reward_parts = []
            if sp > 0:
                reward_parts.append(f"+{sp} SP")
            if xp > 0:
                reward_parts.append(f"+{xp} XP")
            reward_text = "  ".join(reward_parts)
            tk.Label(row3, text=reward_text, font=("Segoe UI", 9, "bold"),
                     bg=bg, fg="#ffd700").pack(side=tk.RIGHT)
        
        if is_crit:
            tk.Label(row3, text="⚡CRIT", font=("Segoe UI", 8, "bold"),
                     bg=bg, fg="#ff00ff").pack(side=tk.RIGHT, padx=5)
    
    # ── ANALYTICS TAB ────────────────────────────────────────────────────
    def _build_history_analytics_tab(self, parent):
        """Analytics dashboard with text-based charts and stats"""
        canvas = tk.Canvas(parent, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#1a1a2e")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _mw(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scroll_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        
        hist = self.rolls_history
        if not hist:
            tk.Label(scroll_frame, text="No data yet.", font=("Segoe UI", 14),
                     bg="#1a1a2e", fg="#888888").pack(pady=40)
            return
        
        # ── Win Rate Over Time (last 100 rolls, 10-roll moving window) ───
        section_label = tk.Label(scroll_frame, text="📈 Win Rate Over Time (10-roll windows)",
                                 font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560")
        section_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        recent = hist[-100:]
        window = 10
        rates = []
        for i in range(0, len(recent), window):
            chunk = recent[i:i+window]
            if chunk:
                w = sum(1 for e in chunk if e.get('won'))
                rates.append(w / len(chunk) * 100)
        
        if rates:
            chart_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
            chart_frame.pack(fill=tk.X, padx=10, pady=5)
            
            max_rate = max(rates) if rates else 100
            chart_height = 8
            for i, rate in enumerate(rates):
                bar_len = int(rate / max(1, max_rate) * 40) if max_rate > 0 else 0
                bar = "█" * bar_len + "░" * (40 - bar_len)
                if rate >= 50:
                    color = "#00ff88"
                elif rate >= 25:
                    color = "#ffcc00"
                else:
                    color = "#ff4444"
                lbl = tk.Label(chart_frame, text=f"  {i*window+1:>3}-{min((i+1)*window, len(recent)):>3}  {bar}  {rate:.0f}%",
                               font=("Consolas", 9), bg="#1e1e3a", fg=color, anchor="w")
                lbl.pack(fill=tk.X)
        
        # ── Property Frequency ───────────────────────────────────────────
        section_label2 = tk.Label(scroll_frame, text="🎯 Most Common Properties in Rolls",
                                  font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560")
        section_label2.pack(anchor="w", padx=10, pady=(15, 5))
        
        prop_counts = {}
        for entry in hist:
            for prop in entry.get('properties', set()):
                prop_counts[prop] = prop_counts.get(prop, 0) + 1
        
        sorted_props = sorted(prop_counts.items(), key=lambda x: -x[1])[:10]
        if sorted_props:
            prop_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
            prop_frame.pack(fill=tk.X, padx=10, pady=5)
            
            max_count = sorted_props[0][1] if sorted_props else 1
            for prop, count in sorted_props:
                display = self._property_name_display(prop)
                bar_len = int(count / max_count * 30)
                bar = "█" * bar_len
                pct = count / len(hist) * 100
                tk.Label(prop_frame, text=f"  {display:<28} {bar}  {count} ({pct:.0f}%)",
                         font=("Consolas", 9), bg="#1e1e3a", fg="#00ccff", anchor="w").pack(fill=tk.X)
        
        # ── SP Earnings Over Time ────────────────────────────────────────
        sp_rolls = [e for e in hist if e.get('sp_earned', 0) > 0]
        if sp_rolls:
            section_label3 = tk.Label(scroll_frame, text="💰 SP Earnings (per win)",
                                      font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560")
            section_label3.pack(anchor="w", padx=10, pady=(15, 5))
            
            sp_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
            sp_frame.pack(fill=tk.X, padx=10, pady=5)
            
            recent_sp = sp_rolls[-20:]
            max_sp = max(e.get('sp_earned', 1) for e in recent_sp)
            for e in recent_sp:
                sp = e.get('sp_earned', 0)
                bar_len = int(sp / max(1, max_sp) * 35)
                bar = "█" * bar_len
                crit_marker = " ⚡" if e.get('is_critical') else ""
                tk.Label(sp_frame, text=f"  Roll #{e.get('number','?'):>6}  {bar}  +{sp} SP{crit_marker}",
                         font=("Consolas", 9), bg="#1e1e3a",
                         fg="#ffd700" if e.get('is_critical') else "#ffcc00",
                         anchor="w").pack(fill=tk.X)
            
            # Averages
            avg_sp = sum(e.get('sp_earned', 0) for e in sp_rolls) / len(sp_rolls)
            best_sp = max(e.get('sp_earned', 0) for e in sp_rolls)
            tk.Label(sp_frame, text=f"\n  Average: {avg_sp:.1f} SP  |  Best: {best_sp} SP",
                     font=("Segoe UI", 10, "bold"), bg="#1e1e3a", fg="#ffffff").pack(anchor="w")
        
        # ── Match % Distribution ─────────────────────────────────────────
        section_label4 = tk.Label(scroll_frame, text="📊 Match Percentage Distribution",
                                  font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560")
        section_label4.pack(anchor="w", padx=10, pady=(15, 5))
        
        dist_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
        dist_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buckets = {"0-24%": 0, "25-49%": 0, "50-74%": 0, "75-99%": 0, "100%": 0}
        for e in hist:
            pct = e.get('match_pct', 0)
            if pct == 100:
                buckets["100%"] += 1
            elif pct >= 75:
                buckets["75-99%"] += 1
            elif pct >= 50:
                buckets["50-74%"] += 1
            elif pct >= 25:
                buckets["25-49%"] += 1
            else:
                buckets["0-24%"] += 1
        
        max_bucket = max(buckets.values()) if buckets else 1
        bucket_colors = {"0-24%": "#ff4444", "25-49%": "#ff9900", "50-74%": "#ffcc00", "75-99%": "#88ff00", "100%": "#00ff88"}
        for label, count in buckets.items():
            bar_len = int(count / max(1, max_bucket) * 35)
            bar = "█" * bar_len
            tk.Label(dist_frame, text=f"  {label:>8}  {bar}  {count}",
                     font=("Consolas", 9), bg="#1e1e3a", fg=bucket_colors.get(label, "#cccccc"),
                     anchor="w").pack(fill=tk.X)
    
    # ── STREAKS & RECORDS TAB ────────────────────────────────────────────
    def _build_history_streaks_tab(self, parent):
        """Show streak analysis and personal records"""
        canvas = tk.Canvas(parent, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#1a1a2e")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _mw(event):
            try: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        canvas.bind("<Leave>", lambda e: (canvas.unbind_all("<MouseWheel>") if canvas.winfo_exists() else None))
        scroll_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _mw))
        
        hist = self.rolls_history
        if not hist:
            tk.Label(scroll_frame, text="No data yet.", font=("Segoe UI", 14),
                     bg="#1a1a2e", fg="#888888").pack(pady=40)
            return
        
        # ── Calculate Streaks ────────────────────────────────────────────
        win_streaks = []
        loss_streaks = []
        current_w = 0
        current_l = 0
        best_win_streak = 0
        best_loss_streak = 0
        
        for e in hist:
            if e.get('won'):
                current_w += 1
                if current_l > 0:
                    loss_streaks.append(current_l)
                    best_loss_streak = max(best_loss_streak, current_l)
                    current_l = 0
            else:
                current_l += 1
                if current_w > 0:
                    win_streaks.append(current_w)
                    best_win_streak = max(best_win_streak, current_w)
                    current_w = 0
        # Close last streak
        if current_w > 0:
            win_streaks.append(current_w)
            best_win_streak = max(best_win_streak, current_w)
        if current_l > 0:
            loss_streaks.append(current_l)
            best_loss_streak = max(best_loss_streak, current_l)
        
        # ── Records Section ──────────────────────────────────────────────
        tk.Label(scroll_frame, text="🏅 Personal Records",
                 font=("Segoe UI", 14, "bold"), bg="#1a1a2e", fg="#ffd700").pack(anchor="w", padx=10, pady=(10, 5))
        
        records_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=15, pady=10)
        records_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Find best SP roll
        best_sp_entry = max(hist, key=lambda e: e.get('sp_earned', 0))
        best_sp = best_sp_entry.get('sp_earned', 0)
        best_sp_roll = best_sp_entry.get('number', '?')
        
        # Highest match % without winning
        near_misses = [e for e in hist if not e.get('won') and e.get('match_pct', 0) > 0]
        best_near_miss = max(near_misses, key=lambda e: e.get('match_pct', 0)) if near_misses else None
        
        # Most common winning property combo
        win_entries = [e for e in hist if e.get('won')]
        
        records = [
            ("🔥 Best Win Streak", f"{best_win_streak} wins in a row", "#00ff88"),
            ("💀 Worst Loss Streak", f"{best_loss_streak} losses in a row", "#ff4444"),
            ("💰 Highest SP Earned", f"+{best_sp} SP (Roll #{best_sp_roll})", "#ffd700"),
            ("🏆 Total Wins", f"{len(win_entries)} / {len(hist)} ({len(win_entries)/max(1,len(hist))*100:.1f}%)", "#00ccff"),
            ("⚡ Critical Hits", f"{sum(1 for e in hist if e.get('is_critical'))} crits total", "#ff00ff"),
        ]
        
        if best_near_miss:
            records.append(("😤 Closest Near-Miss", 
                           f"{best_near_miss.get('match_pct', 0)}% match on Roll #{best_near_miss.get('number', '?')}", 
                           "#ff9900"))
        
        for label, value, color in records:
            row = tk.Frame(records_frame, bg="#1e1e3a")
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 11, "bold"),
                     bg="#1e1e3a", fg=color, width=24, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 11),
                     bg="#1e1e3a", fg="#ffffff", anchor="w").pack(side=tk.LEFT)
        
        # ── Streak Timeline Visualization ────────────────────────────────
        tk.Label(scroll_frame, text="📊 Streak Timeline (last 100 rolls)",
                 font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560").pack(anchor="w", padx=10, pady=(15, 5))
        
        streak_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
        streak_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Visual streak bar: W=green block, L=red block
        recent_100 = hist[-100:]
        streak_canvas = tk.Canvas(streak_frame, width=700, height=40,
                                   bg="#1e1e3a", highlightthickness=0)
        streak_canvas.pack(fill=tk.X)
        
        block_w = max(2, 700 // max(1, len(recent_100)))
        for i, e in enumerate(recent_100):
            x = i * block_w
            color = "#00ff88" if e.get('won') else "#ff4444"
            if e.get('is_critical'):
                color = "#ffd700"
            streak_canvas.create_rectangle(x, 2, x + block_w - 1, 38, fill=color, outline="")
        
        # Legend
        legend_frame = tk.Frame(streak_frame, bg="#1e1e3a")
        legend_frame.pack(anchor="w", pady=(5, 0))
        for color, label in [("#00ff88", "Win"), ("#ff4444", "Loss"), ("#ffd700", "Critical Win")]:
            tk.Label(legend_frame, text=f"■ {label}", font=("Segoe UI", 8),
                     bg="#1e1e3a", fg=color).pack(side=tk.LEFT, padx=8)
        
        # ── Hourly Performance ───────────────────────────────────────────
        hourly = {}
        for e in hist:
            ts = e.get('timestamp', '')
            if ts:
                try:
                    import datetime as _dt
                    hour = _dt.datetime.fromisoformat(ts).hour
                    if hour not in hourly:
                        hourly[hour] = {"wins": 0, "total": 0}
                    hourly[hour]["total"] += 1
                    if e.get('won'):
                        hourly[hour]["wins"] += 1
                except Exception:
                    pass
        
        if hourly:
            tk.Label(scroll_frame, text="🕐 Win Rate by Hour of Day",
                     font=("Segoe UI", 12, "bold"), bg="#1a1a2e", fg="#e94560").pack(anchor="w", padx=10, pady=(15, 5))
            
            hour_frame = tk.Frame(scroll_frame, bg="#1e1e3a", padx=10, pady=8)
            hour_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for hour in sorted(hourly.keys()):
                data = hourly[hour]
                rate = data["wins"] / max(1, data["total"]) * 100
                bar_len = int(rate / 100 * 30)
                bar = "█" * bar_len + "░" * (30 - bar_len)
                if rate >= 50:
                    color = "#00ff88"
                elif rate >= 25:
                    color = "#ffcc00"
                else:
                    color = "#ff4444"
                tk.Label(hour_frame, text=f"  {hour:02d}:00  {bar}  {rate:.0f}% ({data['total']} rolls)",
                         font=("Consolas", 9), bg="#1e1e3a", fg=color, anchor="w").pack(fill=tk.X)
    
    # ── SEARCH & FILTER TAB ──────────────────────────────────────────────
    def _build_history_search_tab(self, parent):
        """Full search and filter interface"""
        search_frame = tk.Frame(parent, bg="#1a1a2e")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search box
        tk.Label(search_frame, text="🔍 Search strings:", font=("Segoe UI", 10),
                 bg="#1a1a2e", fg="#cccccc").pack(side=tk.LEFT, padx=5)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Consolas", 10),
                                bg="#2a2a4a", fg="#ffffff", insertbackground="#ffffff", width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Property filter
        tk.Label(search_frame, text="Property:", font=("Segoe UI", 10),
                 bg="#1a1a2e", fg="#cccccc").pack(side=tk.LEFT, padx=(15, 5))
        
        all_props = set()
        for e in self.rolls_history:
            all_props.update(e.get('properties', set()))
        prop_choices = ["Any"] + sorted([self._property_name_display(p) for p in all_props])
        prop_var = tk.StringVar(value="Any")
        prop_menu = tk.OptionMenu(search_frame, prop_var, *prop_choices)
        prop_menu.config(font=("Segoe UI", 9), bg="#2a2a4a", fg="#ffffff")
        prop_menu.pack(side=tk.LEFT, padx=5)
        
        # Min match % filter
        tk.Label(search_frame, text="Min match%:", font=("Segoe UI", 10),
                 bg="#1a1a2e", fg="#cccccc").pack(side=tk.LEFT, padx=(15, 5))
        min_pct_var = tk.StringVar(value="0")
        min_pct_entry = tk.Entry(search_frame, textvariable=min_pct_var, font=("Consolas", 10),
                                 bg="#2a2a4a", fg="#ffffff", insertbackground="#ffffff", width=5)
        min_pct_entry.pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_text = scrolledtext.ScrolledText(parent, font=self._ui["font_mono_sm"],
                                                  bg=self._ui["bg_primary"], fg=self._ui["success"], height=30)
        results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tag configurations for colored text
        results_text.tag_configure("header", foreground="#e94560", font=("Segoe UI", 11, "bold"))
        results_text.tag_configure("win", foreground="#00ff88")
        results_text.tag_configure("loss", foreground="#ff6666")
        results_text.tag_configure("crit", foreground="#ffd700", font=("Consolas", 9, "bold"))
        results_text.tag_configure("dim", foreground="#888888")
        results_text.tag_configure("highlight", foreground="#00ccff", font=("Consolas", 9, "bold"))
        
        def _do_search():
            results_text.config(state=tk.NORMAL)
            results_text.delete(1.0, tk.END)
            
            query = search_var.get().strip().lower()
            selected_prop = prop_var.get()
            try:
                min_pct = float(min_pct_var.get())
            except ValueError:
                min_pct = 0
            
            # Reverse map display name to raw property
            reverse_prop_map = {}
            for e in self.rolls_history:
                for p in e.get('properties', set()):
                    reverse_prop_map[self._property_name_display(p)] = p
            
            filtered = []
            for entry in self.rolls_history:
                # Text search
                if query and query not in entry.get('string', '').lower():
                    continue
                # Property filter
                if selected_prop != "Any":
                    raw_prop = reverse_prop_map.get(selected_prop)
                    if raw_prop and raw_prop not in entry.get('properties', set()):
                        continue
                # Min match % filter
                pct = entry.get('match_pct', 0)
                if pct < min_pct:
                    continue
                filtered.append(entry)
            
            results_text.insert(tk.END, f"Found {len(filtered)} matching rolls\n", "header")
            results_text.insert(tk.END, "─" * 80 + "\n\n", "dim")
            
            # Show results (newest first, capped at 200)
            for entry in reversed(filtered[-200:]):
                won = entry.get('won', False)
                is_crit = entry.get('is_critical', False)
                matches = entry.get('matches', 0)
                total = entry.get('total_needed', 0)
                pct = entry.get('match_pct', 0)
                sp = entry.get('sp_earned', 0)
                
                tag = "crit" if is_crit else ("win" if won else "loss")
                status = "⚡WIN" if is_crit else ("🏆 WIN" if won else "  ✗  ")
                
                preview = entry.get('string', '')[:50]
                if len(entry.get('string', '')) > 50:
                    preview += "..."
                
                line = f"  #{entry.get('number','?'):>6}  {status}  {pct:>5.1f}%  {matches}/{total}"
                if sp > 0:
                    line += f"  +{sp}SP"
                line += f'  "{preview}"\n'
                
                results_text.insert(tk.END, line, tag)
            
            if len(filtered) > 200:
                results_text.insert(tk.END, f"\n... showing 200 of {len(filtered)} results\n", "dim")
            
            results_text.config(state=tk.DISABLED)
        
        # Search button
        tk.Button(search_frame, text="Search", font=("Segoe UI", 10, "bold"),
                  bg="#e94560", fg="#ffffff", relief=tk.FLAT, padx=12,
                  command=_do_search).pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key
        search_entry.bind("<Return>", lambda e: _do_search())
        
        # Run initial search to show all
        _do_search()
    
    # ── EXPORT TAB ───────────────────────────────────────────────────────
    def _build_history_export_tab(self, parent):
        """Export history data and show quick stats"""
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="💾 Export & Manage History",
                 font=("Segoe UI", 14, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=(0, 15))
        
        info_text = (
            f"History contains {len(self.rolls_history)} rolls\n"
            f"Oldest: Roll #{self.rolls_history[0].get('number', '?') if self.rolls_history else 'N/A'}\n"
            f"Newest: Roll #{self.rolls_history[-1].get('number', '?') if self.rolls_history else 'N/A'}\n"
        )
        if self.rolls_history and self.rolls_history[0].get('timestamp'):
            info_text += f"Date range: {self.rolls_history[0].get('timestamp', '')[:10]} → {self.rolls_history[-1].get('timestamp', '')[:10]}\n"
        
        tk.Label(frame, text=info_text, font=("Segoe UI", 11), bg="#1a1a2e",
                 fg="#cccccc", justify=tk.LEFT).pack(anchor="w", pady=5)
        
        btn_frame = tk.Frame(frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=10)
        
        def _export_csv():
            try:
                from tkinter import filedialog
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"{self.current_username}_history.csv"
                )
                if not filepath:
                    return
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("Roll#,String,Matches,Total,MatchPct,Won,SP,XP,Critical,Timestamp\n")
                    for entry in self.rolls_history:
                        s = entry.get('string', '').replace('"', '""')
                        f.write(
                            f"{entry.get('number',0)},"
                            f'"{s}",'
                            f"{entry.get('matches',0)},"
                            f"{entry.get('total_needed',0)},"
                            f"{entry.get('match_pct',0)},"
                            f"{entry.get('won',False)},"
                            f"{entry.get('sp_earned',0)},"
                            f"{entry.get('xp_earned',0)},"
                            f"{entry.get('is_critical',False)},"
                            f"{entry.get('timestamp','')}\n"
                        )
                messagebox.showinfo("Export", f"History exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")
        
        def _export_text():
            try:
                from tkinter import filedialog
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile=f"{self.current_username}_history.txt"
                )
                if not filepath:
                    return
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"ROLL HISTORY FOR {self.current_username}\n")
                    f.write("=" * 70 + "\n\n")
                    for entry in self.rolls_history:
                        won = "WIN" if entry.get('won') else "LOSS"
                        crit = " [CRITICAL]" if entry.get('is_critical') else ""
                        f.write(
                            f"Roll #{entry.get('number',0):>6} | {won}{crit} | "
                            f"{entry.get('matches',0)}/{entry.get('total_needed',0)} "
                            f"({entry.get('match_pct',0):.1f}%)"
                        )
                        if entry.get('sp_earned', 0) > 0:
                            f.write(f" | +{entry.get('sp_earned',0)} SP")
                        if entry.get('timestamp'):
                            f.write(f" | {entry.get('timestamp', '')[:19]}")
                        f.write(f'\n  → "{entry.get("string","")[:60]}"\n\n')
                
                messagebox.showinfo("Export", f"History exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")
        
        def _clear_history():
            if messagebox.askyesno("Clear History", "Are you sure you want to clear all roll history?\nThis cannot be undone!"):
                self.rolls_history = []
                self._save_history()
                messagebox.showinfo("Cleared", "Roll history has been cleared.")
        
        tk.Button(btn_frame, text="📊 Export as CSV", font=self._ui["font_btn"],
                  bg=self._ui["info"], fg="#000000", relief=tk.FLAT, padx=20, pady=8,
                  command=_export_csv).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="📝 Export as Text", font=self._ui["font_btn"],
                  bg=self._ui["success"], fg="#000000", relief=tk.FLAT, padx=20, pady=8,
                  command=_export_text).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="🗑️ Clear History", font=self._ui["font_btn"],
                  bg=self._ui["danger"], fg="#ffffff", relief=tk.FLAT, padx=20, pady=8,
                  command=_clear_history).pack(side=tk.LEFT, padx=10)
        
        # Quick tips
        tk.Label(frame, text=(
            "💡 Tips:\n"
            "• CSV export works great with Excel or Google Sheets\n"
            "• Use the Analytics tab to spot patterns in your rolls\n"
            "• History stores up to 500 rolls — older ones are trimmed automatically\n"
            "• Check Streaks tab to find your peak performance hours"
        ), font=("Segoe UI", 10), bg="#1a1a2e", fg="#888888",
            justify=tk.LEFT).pack(anchor="w", pady=(20, 0))
    
    def save_game(self):
        """Save the current game state"""
        self._save_stats()
        self._save_achievements()
        self._save_equipment()
        self._save_history()
        self._save_settings()
        messagebox.showinfo("Save", "Game saved successfully!")
    
    # ══════════════════════════════════════════════════════════════════
    #  PvP ARENA SYSTEM — Duel AI opponents, climb the ELO ladder,
    #  draft/ban properties, use tactical abilities mid-match
    # ══════════════════════════════════════════════════════════════════

    def _init_pvp_system(self):
        """Initialise all PvP-related state and load persisted data."""
        self.pvp_elo = 1000
        self.pvp_wins = 0
        self.pvp_losses = 0
        self.pvp_draws = 0
        self.pvp_streak = 0
        self.pvp_best_streak = 0
        self.pvp_match_history = []          # list of dicts
        self.pvp_abilities = {               # unlocked tactical abilities
            "lock_property":   {"unlocked": True,  "cooldown": 0, "desc": "Lock one matched property so it can't be lost"},
            "reroll_opponent":  {"unlocked": True,  "cooldown": 0, "desc": "Force opponent to reroll their next string"},
            "double_match":    {"unlocked": False, "cooldown": 0, "desc": "Double your match score for one round"},
            "steal_property":  {"unlocked": False, "cooldown": 0, "desc": "Steal one of the opponent's matched properties"},
            "insight":         {"unlocked": False, "cooldown": 0, "desc": "Reveal 2 of the target properties for free"},
        }
        self.pvp_ability_unlock_elo = {
            "double_match":   1200,
            "steal_property": 1400,
            "insight":        1100,
        }
        # AI opponents – each has a personality that affects how they "roll"
        self.pvp_opponents = [
            {"name": "Bot_Rookie",     "elo": 800,  "icon": "🤖", "style": "random",  "is_bot": True,
             "desc": "A simple bot that rolls randomly. Good for practice.",
             "match_bonus": 0.0,  "ability_chance": 0.0},
            {"name": "Bot_Steady",     "elo": 1000, "icon": "🧑‍💻", "style": "balanced", "is_bot": True,
             "desc": "Plays safe. Matches a few extra properties now and then.",
             "match_bonus": 0.04, "ability_chance": 0.08},
            {"name": "Bot_Sharp",      "elo": 1200, "icon": "🦊", "style": "aggressive", "is_bot": True,
             "desc": "Slightly better luck. Occasionally nails an extra match.",
             "match_bonus": 0.08, "ability_chance": 0.12},
            {"name": "Bot_Tactician",  "elo": 1400, "icon": "🧠", "style": "tactical",  "is_bot": True,
             "desc": "Uses abilities often. Will try to disrupt your strategy.",
             "match_bonus": 0.10, "ability_chance": 0.20},
            {"name": "Bot_Legend",     "elo": 1700, "icon": "👑", "style": "perfect",   "is_bot": True,
             "desc": "The toughest bot. Still beatable with good abilities.",
             "match_bonus": 0.14, "ability_chance": 0.22},
        ]
        self._load_pvp_data()

    # ── persistence ──────────────────────────────────────────────────

    def _load_pvp_data(self):
        """Load PvP data from user's JSON file."""
        if not self.current_username:
            return
        path = f"user_{self.current_username}_pvp.json"
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                self.pvp_elo = data.get("elo", 1000)
                self.pvp_wins = data.get("wins", 0)
                self.pvp_losses = data.get("losses", 0)
                self.pvp_draws = data.get("draws", 0)
                self.pvp_streak = data.get("streak", 0)
                self.pvp_best_streak = data.get("best_streak", 0)
                self.pvp_match_history = data.get("history", [])
                saved_abilities = data.get("abilities", {})
                for key, val in saved_abilities.items():
                    if key in self.pvp_abilities:
                        self.pvp_abilities[key]["unlocked"] = val.get("unlocked", False)
        except Exception:
            pass

    def _save_pvp_data(self):
        """Persist PvP data to user's JSON file."""
        if not self.current_username:
            return
        path = f"user_{self.current_username}_pvp.json"
        data = {
            "elo": self.pvp_elo,
            "wins": self.pvp_wins,
            "losses": self.pvp_losses,
            "draws": self.pvp_draws,
            "streak": self.pvp_streak,
            "best_streak": self.pvp_best_streak,
            "history": self.pvp_match_history[-100:],   # keep last 100
            "abilities": {k: {"unlocked": v["unlocked"]} for k, v in self.pvp_abilities.items()},
        }
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ── ELO helpers ──────────────────────────────────────────────────

    def _pvp_elo_change(self, player_elo, opponent_elo, result):
        """Calculate ELO change.  result: 1=win, 0.5=draw, 0=loss"""
        K = 32
        expected = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
        return round(K * (result - expected))

    def _pvp_rank_for_elo(self, elo):
        """Return (rank_name, rank_color) for an ELO value."""
        ui = self._ui
        if elo >= 1800:
            return "Grandmaster", ui["gold"]
        elif elo >= 1500:
            return "Diamond", ui["info"]
        elif elo >= 1300:
            return "Platinum", ui["accent_light"]
        elif elo >= 1100:
            return "Gold", ui["warning"]
        elif elo >= 900:
            return "Silver", ui["text_secondary"]
        else:
            return "Bronze", "#cd7f32"

    # ── Arena Window ─────────────────────────────────────────────────

    def show_pvp_arena(self):
        """Open the PvP Arena hub – bots, player challenges, rankings, history."""
        ui = self._ui
        arena = self._styled_toplevel("🏟️ PvP Arena", 860, 700, 720, 580)
        self._styled_header(arena, "PvP Arena", "Challenge opponents and climb the ladder", icon="🏟️")

        notebook = ttk.Notebook(arena, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ── Player card (shared header) ──────────────────────────────
        def _player_card(parent):
            pc = tk.Frame(parent, bg=ui["bg_card"], padx=20, pady=14)
            pc.pack(fill=tk.X, padx=15, pady=(15, 6))
            rank_name, rank_color = self._pvp_rank_for_elo(self.pvp_elo)
            name_text = self.current_username or "Guest"
            tk.Label(pc, text=f"👤  {name_text}", font=ui["font_heading"],
                     bg=ui["bg_card"], fg=ui["text_primary"]).pack(side=tk.LEFT)
            tk.Label(pc, text=f"ELO {self.pvp_elo}  ·  {rank_name}",
                     font=ui["font_body_bold"], bg=ui["bg_card"], fg=rank_color
                     ).pack(side=tk.LEFT, padx=20)
            tk.Label(pc, text=f"W {self.pvp_wins} / L {self.pvp_losses} / D {self.pvp_draws}",
                     font=ui["font_mono_sm"], bg=ui["bg_card"], fg=ui["text_secondary"]
                     ).pack(side=tk.RIGHT)

        # ── TAB 1 — Fight Bots ───────────────────────────────────────
        fight_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(fight_tab, text="  🤖 Bots  ")

        _player_card(fight_tab)

        tk.Label(fight_tab, text="AI Opponents — great for practice:", font=ui["font_subhead"],
                 bg=ui["bg_primary"], fg=ui["text_primary"]).pack(anchor="w", padx=18, pady=(12, 4))

        opp_frame = tk.Frame(fight_tab, bg=ui["bg_primary"])
        opp_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))

        for opp in self.pvp_opponents:
            row = tk.Frame(opp_frame, bg=ui["bg_card"], pady=8, padx=14)
            row.pack(fill=tk.X, pady=3)
            opp_rank, opp_color = self._pvp_rank_for_elo(opp["elo"])
            tk.Label(row, text=f'{opp["icon"]}  {opp["name"]}', font=ui["font_body_bold"],
                     bg=ui["bg_card"], fg=ui["text_primary"]).pack(side=tk.LEFT)
            tk.Label(row, text=f'ELO {opp["elo"]}  ·  {opp_rank}', font=ui["font_small"],
                     bg=ui["bg_card"], fg=opp_color).pack(side=tk.LEFT, padx=14)
            tk.Label(row, text=opp["desc"], font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.LEFT, padx=8)
            elo_delta = self._pvp_elo_change(self.pvp_elo, opp["elo"], 1)
            gain_text = f"+{elo_delta}" if elo_delta > 0 else str(elo_delta)
            self._styled_button(row, f"⚔️ Fight ({gain_text})",
                                lambda o=opp: self._pvp_start_draft(arena, o),
                                style="danger", width=14, small=True).pack(side=tk.RIGHT)

        # ── TAB 2 — Challenge Player ─────────────────────────────────
        player_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(player_tab, text="  👥 Challenge Player  ")

        _player_card(player_tab)

        tk.Label(player_tab, text="Challenge a registered player (simulated from their stats):",
                 font=ui["font_subhead"], bg=ui["bg_primary"], fg=ui["text_primary"]
                 ).pack(anchor="w", padx=18, pady=(12, 4))

        search_frame = tk.Frame(player_tab, bg=ui["bg_primary"])
        search_frame.pack(fill=tk.X, padx=15, pady=(0, 6))
        tk.Label(search_frame, text="🔍", bg=ui["bg_primary"], fg=ui["text_secondary"]).pack(side=tk.LEFT)
        pvp_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=pvp_search_var, font=ui["font_small"],
                 bg=ui["bg_card"], fg=ui["text_primary"], insertbackground=ui["text_primary"],
                 relief=tk.FLAT, bd=0).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=4)

        player_scroll_outer, player_scroll_inner = self._styled_scrollable(player_tab, bg=ui["bg_primary"])
        player_scroll_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))

        def _load_player_opponents():
            """Build a list of real-player opponents from account data."""
            opponents = []
            for username in self.account_manager.accounts:
                if username.startswith("Guest_") or username == self.current_username:
                    continue
                pvp_file = f"user_{username}_pvp.json"
                stats_file = self.account_manager.get_user_stats_file(username)
                p_elo = 1000
                p_wins = 0
                p_losses = 0
                p_rolls = 0
                p_total_wins = 0
                try:
                    if os.path.exists(pvp_file):
                        with open(pvp_file, "r") as f:
                            pd = json.load(f)
                        p_elo = pd.get("elo", 1000)
                        p_wins = pd.get("wins", 0)
                        p_losses = pd.get("losses", 0)
                    if os.path.exists(stats_file):
                        with open(stats_file, "r") as f:
                            sd = json.load(f)
                        p_rolls = sd.get("total_rolls", 0)
                        p_total_wins = sd.get("total_wins", 0)
                except Exception:
                    pass
                # Derive a simulated "match_bonus" from their stats (scaled 0..0.12)
                wr = p_total_wins / max(1, p_rolls)
                sim_bonus = min(0.12, round(wr * 0.4, 3))
                sim_ability = min(0.18, round(p_wins * 0.003, 3))
                opponents.append({
                    "name": username,
                    "elo": p_elo,
                    "icon": "👤",
                    "style": "balanced",
                    "is_bot": False,
                    "desc": f"W{p_wins}/L{p_losses}  ·  {p_total_wins} game wins",
                    "match_bonus": sim_bonus,
                    "ability_chance": sim_ability,
                })
            opponents.sort(key=lambda x: x["elo"], reverse=True)
            return opponents

        real_players = _load_player_opponents()

        def _fill_player_list(*_a):
            for w in player_scroll_inner.winfo_children():
                w.destroy()
            query = pvp_search_var.get().strip().lower()
            filtered = [p for p in real_players if query in p["name"].lower()] if query else real_players

            if not filtered:
                tk.Label(player_scroll_inner, text="No players found. Invite friends to register!",
                         font=ui["font_body"], bg=ui["bg_primary"], fg=ui["warning"]).pack(pady=20)
                return

            for p_opp in filtered:
                row = tk.Frame(player_scroll_inner, bg=ui["bg_card"], pady=8, padx=14)
                row.pack(fill=tk.X, pady=3)
                o_rank, o_color = self._pvp_rank_for_elo(p_opp["elo"])
                tk.Label(row, text=f'👤  {p_opp["name"]}', font=ui["font_body_bold"],
                         bg=ui["bg_card"], fg=ui["text_primary"]).pack(side=tk.LEFT)
                tk.Label(row, text=f'ELO {p_opp["elo"]}  ·  {o_rank}', font=ui["font_small"],
                         bg=ui["bg_card"], fg=o_color).pack(side=tk.LEFT, padx=14)
                tk.Label(row, text=p_opp["desc"], font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.LEFT, padx=8)
                elo_d = self._pvp_elo_change(self.pvp_elo, p_opp["elo"], 1)
                gt = f"+{elo_d}" if elo_d > 0 else str(elo_d)
                self._styled_button(row, f"⚔️ Challenge ({gt})",
                                    lambda o=p_opp: self._pvp_start_draft(arena, o),
                                    style="success", width=16, small=True).pack(side=tk.RIGHT)

        pvp_search_var.trace_add("write", _fill_player_list)
        _fill_player_list()

        # ── TAB 3 — Abilities ────────────────────────────────────────
        abil_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(abil_tab, text="  🎯 Abilities  ")

        tk.Label(abil_tab, text="Tactical Abilities", font=ui["font_heading"],
                 bg=ui["bg_primary"], fg=ui["accent_light"]).pack(anchor="w", padx=18, pady=(15, 4))
        tk.Label(abil_tab, text="Use these mid-duel to gain a strategic edge. New abilities unlock at higher ELO.",
                 font=ui["font_small"], bg=ui["bg_primary"], fg=ui["text_muted"]
                 ).pack(anchor="w", padx=18, pady=(0, 10))

        for key, info in self.pvp_abilities.items():
            af = tk.Frame(abil_tab, bg=ui["bg_card"], padx=14, pady=10)
            af.pack(fill=tk.X, padx=15, pady=3)
            display_name = key.replace("_", " ").title()
            locked = not info["unlocked"]
            elo_req = self.pvp_ability_unlock_elo.get(key, 0)
            fg = ui["text_muted"] if locked else ui["text_primary"]
            status_text = f"🔒 Unlock at ELO {elo_req}" if locked else "✅ Unlocked"
            status_color = ui["text_muted"] if locked else ui["success"]
            tk.Label(af, text=display_name, font=ui["font_body_bold"],
                     bg=ui["bg_card"], fg=fg).pack(side=tk.LEFT)
            tk.Label(af, text=f"  —  {info['desc']}", font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(side=tk.LEFT, padx=8)
            tk.Label(af, text=status_text, font=ui["font_small_bold"],
                     bg=ui["bg_card"], fg=status_color).pack(side=tk.RIGHT)

        # ── TAB 4 — History ──────────────────────────────────────────
        hist_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(hist_tab, text="  📜 History  ")

        if not self.pvp_match_history:
            tk.Label(hist_tab, text="No PvP matches yet. Go fight someone!",
                     font=ui["font_body"], bg=ui["bg_primary"], fg=ui["text_muted"]
                     ).pack(pady=40)
        else:
            scroll_outer, scroll_inner = self._styled_scrollable(hist_tab, ui["bg_primary"])
            scroll_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            for match in reversed(self.pvp_match_history[-50:]):
                mf = tk.Frame(scroll_inner, bg=ui["bg_card"], padx=12, pady=6)
                mf.pack(fill=tk.X, pady=2)
                result = match.get("result", "?")
                r_color = ui["success"] if result == "WIN" else ui["danger"] if result == "LOSS" else ui["warning"]
                tk.Label(mf, text=result, font=ui["font_body_bold"], bg=ui["bg_card"],
                         fg=r_color, width=5).pack(side=tk.LEFT)
                tk.Label(mf, text=f'vs {match.get("opponent", "?")}', font=ui["font_body"],
                         bg=ui["bg_card"], fg=ui["text_primary"]).pack(side=tk.LEFT, padx=8)
                tk.Label(mf, text=f'{match.get("score", "")}-{match.get("opp_score", "")}',
                         font=ui["font_mono_sm"], bg=ui["bg_card"], fg=ui["text_secondary"]
                         ).pack(side=tk.LEFT, padx=8)
                elo_chg = match.get("elo_change", 0)
                ec_text = f"+{elo_chg}" if elo_chg >= 0 else str(elo_chg)
                ec_color = ui["success"] if elo_chg >= 0 else ui["danger"]
                tk.Label(mf, text=ec_text, font=ui["font_small_bold"], bg=ui["bg_card"],
                         fg=ec_color).pack(side=tk.RIGHT, padx=4)

        # ── TAB 5 — PvP Leaderboard (real players only) ─────────────
        pvp_lb_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(pvp_lb_tab, text="  🏆 PvP Leaderboard  ")

        tk.Label(pvp_lb_tab, text="PvP Leaderboard — Real Players Only", font=ui["font_heading"],
                 bg=ui["bg_primary"], fg=ui["gold"]).pack(anchor="w", padx=18, pady=(15, 4))
        tk.Label(pvp_lb_tab, text="Ranked by ELO. Bots are not shown.",
                 font=ui["font_small"], bg=ui["bg_primary"], fg=ui["text_muted"]
                 ).pack(anchor="w", padx=18, pady=(0, 10))

        pvp_lb_scroll_outer, pvp_lb_inner = self._styled_scrollable(pvp_lb_tab, ui["bg_primary"])
        pvp_lb_scroll_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Collect all real player PvP stats
        pvp_leaders = []
        for username in self.account_manager.accounts:
            if username.startswith("Guest_"):
                continue
            pvp_file = f"user_{username}_pvp.json"
            try:
                if os.path.exists(pvp_file):
                    with open(pvp_file, "r") as f:
                        pd = json.load(f)
                    pvp_leaders.append({
                        "name": username,
                        "elo": pd.get("elo", 1000),
                        "wins": pd.get("wins", 0),
                        "losses": pd.get("losses", 0),
                        "draws": pd.get("draws", 0),
                        "best_streak": pd.get("best_streak", 0),
                    })
                else:
                    pvp_leaders.append({"name": username, "elo": 1000, "wins": 0, "losses": 0, "draws": 0, "best_streak": 0})
            except Exception:
                pass
        pvp_leaders.sort(key=lambda x: x["elo"], reverse=True)

        medals = ["🥇", "🥈", "🥉"]
        if not pvp_leaders:
            tk.Label(pvp_lb_inner, text="No players yet!", font=ui["font_body"],
                     bg=ui["bg_primary"], fg=ui["warning"]).pack(pady=20)
        else:
            for i, pl in enumerate(pvp_leaders[:50], 1):
                medal = medals[i - 1] if i <= 3 else f"{i}."
                is_me = pl["name"] == self.current_username
                row_bg = ui["bg_card"] if is_me else ui["bg_secondary"]
                fg = ui["gold"] if is_me else ui["text_primary"]
                r_name, r_color = self._pvp_rank_for_elo(pl["elo"])

                row = tk.Frame(pvp_lb_inner, bg=row_bg)
                row.pack(fill=tk.X, padx=4, pady=1)
                tk.Label(row, text=f" {medal}", font=ui["font_body_bold"], bg=row_bg, fg=fg,
                         width=4, anchor="w").pack(side=tk.LEFT, padx=(4, 0))
                name_font = ("Segoe UI", 13, "bold") if pl["name"] == "DeMarcusThe2nd" else ui["font_body_bold"]
                tk.Label(row, text=pl["name"], font=name_font, bg=row_bg, fg=fg,
                         width=16, anchor="w").pack(side=tk.LEFT, padx=(4, 0))
                tk.Label(row, text=f'ELO {pl["elo"]}', font=ui["font_mono_sm"], bg=row_bg,
                         fg=r_color, width=9, anchor="e").pack(side=tk.LEFT, padx=(6, 0))
                tk.Label(row, text=r_name, font=ui["font_small_bold"], bg=row_bg,
                         fg=r_color, width=12, anchor="w").pack(side=tk.LEFT, padx=(8, 0))
                wld = f"W{pl['wins']} / L{pl['losses']} / D{pl['draws']}"
                tk.Label(row, text=wld, font=ui["font_small"], bg=row_bg,
                         fg=ui["text_secondary"]).pack(side=tk.LEFT, padx=(12, 0))
                tk.Label(row, text=f"🔥{pl['best_streak']}", font=ui["font_small"], bg=row_bg,
                         fg=ui["warning"]).pack(side=tk.RIGHT, padx=(0, 8))

        # ── TAB 6 — Rank Tiers ──────────────────────────────────────
        rank_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(rank_tab, text="  📊 Ranks  ")

        tk.Label(rank_tab, text="ELO Rank Tiers", font=ui["font_heading"],
                 bg=ui["bg_primary"], fg=ui["accent_light"]).pack(anchor="w", padx=18, pady=(15, 10))

        tiers = [
            ("Grandmaster", 1800, self._ui["gold"],          "👑"),
            ("Diamond",     1500, self._ui["info"],           "💎"),
            ("Platinum",    1300, self._ui["accent_light"],   "🔷"),
            ("Gold",        1100, self._ui["warning"],        "🥇"),
            ("Silver",       900, self._ui["text_secondary"], "🥈"),
            ("Bronze",         0, "#cd7f32",                  "🥉"),
        ]
        for tier_name, min_elo, color, icon in tiers:
            tf = tk.Frame(rank_tab, bg=ui["bg_card"], padx=14, pady=8)
            tf.pack(fill=tk.X, padx=15, pady=2)
            is_current = (self._pvp_rank_for_elo(self.pvp_elo)[0] == tier_name)
            border_color = color if is_current else ui["bg_card"]
            highlight = tk.Frame(tf, bg=border_color, width=4)
            highlight.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
            tk.Label(tf, text=f"{icon}  {tier_name}", font=ui["font_body_bold"],
                     bg=ui["bg_card"], fg=color).pack(side=tk.LEFT)
            tk.Label(tf, text=f"ELO {min_elo}+", font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.LEFT, padx=14)
            if is_current:
                tk.Label(tf, text="◀ YOU", font=ui["font_small_bold"],
                         bg=ui["bg_card"], fg=ui["gold"]).pack(side=tk.RIGHT)

    # ── Draft Phase ──────────────────────────────────────────────────

    def _pvp_start_draft(self, parent_win, opponent):
        """Open the property draft/ban phase before a duel."""
        ui = self._ui
        parent_win.destroy()

        draft_win = self._styled_toplevel("⚔️ Pre-Match Draft", 700, 560, 600, 450)
        self._styled_header(draft_win, "Draft Phase", f"Ban properties before fighting {opponent['name']}", icon="📋")

        info_frame = tk.Frame(draft_win, bg=ui["bg_card"], padx=16, pady=10)
        info_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        tk.Label(info_frame, text="Each side bans 2 properties from the target pool.\n"
                 "Banned properties CANNOT appear as targets — reducing RNG!",
                 font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_secondary"],
                 justify=tk.LEFT).pack(anchor="w")

        # Generate the 6 target candidates (more than usual, so bans matter)
        all_props = list(self.possible_properties)
        random.shuffle(all_props)
        draft_pool = all_props[:8]   # 8 candidates, 4 banned, 4 remain as targets

        banned_by_player = []
        banned_by_opponent = []

        # Display pool
        tk.Label(draft_win, text="Property Pool — click to BAN (2 picks):",
                 font=ui["font_subhead"], bg=ui["bg_primary"], fg=ui["text_primary"]
                 ).pack(anchor="w", padx=18, pady=(8, 4))

        pool_frame = tk.Frame(draft_win, bg=ui["bg_primary"])
        pool_frame.pack(fill=tk.X, padx=15)

        btn_refs = {}

        def _ban_property(prop, btn):
            if len(banned_by_player) >= 2:
                return
            banned_by_player.append(prop)
            btn.config(text=f"🚫 {self._property_name_display(prop)}", state=tk.DISABLED,
                       bg=ui["danger"], fg=ui["text_bright"])
            if len(banned_by_player) == 2:
                # AI bans
                available = [p for p in draft_pool if p not in banned_by_player]
                if opponent["style"] == "tactical":
                    # Tactical bot bans the hardest properties
                    hard = ["is_very_long", "ends_with_symbol", "has_consecutive_letters",
                            "has_operators", "has_multiple_words"]
                    for h in hard:
                        if h in available and len(banned_by_opponent) < 2:
                            banned_by_opponent.append(h)
                    while len(banned_by_opponent) < 2 and available:
                        pick = random.choice([p for p in available if p not in banned_by_opponent])
                        banned_by_opponent.append(pick)
                else:
                    picks = random.sample(available, min(2, len(available)))
                    banned_by_opponent.extend(picks)
                # Mark AI bans in UI
                for p in banned_by_opponent:
                    if p in btn_refs:
                        btn_refs[p].config(
                            text=f"🤖 {self._property_name_display(p)}",
                            state=tk.DISABLED, bg=ui["warning"], fg="#000000")
                # Show proceed button
                proceed_btn.pack(pady=15)
                status_label.config(text=f"✅ Draft complete! {opponent['icon']} {opponent['name']} banned 2 properties.")

        for i, prop in enumerate(draft_pool):
            bf = tk.Frame(pool_frame, bg=ui["bg_primary"])
            bf.pack(fill=tk.X, pady=2)
            b = tk.Button(bf, text=f"  {self._property_name_display(prop)}  ",
                          font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_primary"],
                          relief=tk.FLAT, cursor="hand2", padx=12, pady=5, anchor="w",
                          command=lambda p=prop, btn_holder=[None]: None)
            b.pack(fill=tk.X)
            btn_refs[prop] = b
            # re-bind command now that btn exists
            b.config(command=lambda p=prop, bt=b: _ban_property(p, bt))

        status_label = tk.Label(draft_win, text="Select 2 properties to ban ⬆️",
                                font=ui["font_body_bold"], bg=ui["bg_primary"], fg=ui["info"])
        status_label.pack(pady=(10, 0))

        # Build the final target from remaining properties
        def _proceed():
            remaining = [p for p in draft_pool if p not in banned_by_player and p not in banned_by_opponent]
            target_count = min(len(remaining), max(2, len(remaining)))
            # Use difficulty to decide how many targets
            if self.difficulty == "easy":
                target_count = min(2, len(remaining))
            elif self.difficulty == "hard":
                target_count = min(4, len(remaining))
            else:
                target_count = min(3, len(remaining))
            final_targets = set(random.sample(remaining, target_count))
            draft_win.destroy()
            self._pvp_start_duel(opponent, final_targets, banned_by_player, banned_by_opponent)

        proceed_btn = self._styled_button(draft_win, "⚔️ BEGIN DUEL", _proceed, style="danger", width=20)
        # hidden until draft is done

    # ── Duel Engine ──────────────────────────────────────────────────

    def _pvp_start_duel(self, opponent, targets, player_bans, opp_bans):
        """Run a best-of-5-rounds duel against an AI opponent."""
        ui = self._ui
        duel_win = self._styled_toplevel(f"⚔️ vs {opponent['name']}", 850, 650, 700, 550)

        total_rounds = 5
        state = {
            "round": 1,
            "player_score": 0,
            "opp_score": 0,
            "player_locked": set(),      # locked (safe) properties
            "opp_locked": set(),
            "player_matches": set(),
            "opp_matches": set(),
            "targets": targets,
            "abilities_used": set(),
            "opp_rerolled": False,        # if player forced opponent reroll
            "player_doubled": False,      # if double_match is active
            "round_log": [],
        }

        # ── Header ──────────────────────────────────────────────────
        self._styled_header(duel_win, f"Duel — vs {opponent['icon']} {opponent['name']}",
                            f"Best of {total_rounds} rounds  ·  Target: {len(targets)} properties",
                            icon="⚔️")

        # Scoreboard
        score_bar = tk.Frame(duel_win, bg=ui["bg_card"], pady=10, padx=20)
        score_bar.pack(fill=tk.X, padx=15, pady=(5, 4))

        p_name = self.current_username or "You"
        player_score_lbl = tk.Label(score_bar, text=f"👤 {p_name}:  0",
                                    font=("Segoe UI", 16, "bold"), bg=ui["bg_card"], fg=ui["success"])
        player_score_lbl.pack(side=tk.LEFT)
        tk.Label(score_bar, text="  vs  ", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.LEFT)
        opp_score_lbl = tk.Label(score_bar, text=f"{opponent['icon']} {opponent['name']}:  0",
                                 font=("Segoe UI", 16, "bold"), bg=ui["bg_card"], fg=ui["danger"])
        opp_score_lbl.pack(side=tk.LEFT)
        round_lbl = tk.Label(score_bar, text="Round 1/5", font=ui["font_body_bold"],
                             bg=ui["bg_card"], fg=ui["warning"])
        round_lbl.pack(side=tk.RIGHT)

        # Target display
        target_frame = tk.Frame(duel_win, bg=ui["bg_secondary"], padx=12, pady=6)
        target_frame.pack(fill=tk.X, padx=15, pady=(0, 6))
        target_str = " · ".join(self._property_name_display(t) for t in targets)
        tk.Label(target_frame, text=f"🎯 Targets: {target_str}",
                 font=ui["font_small_bold"], bg=ui["bg_secondary"], fg=ui["accent_light"]).pack(anchor="w")
        bans_str = ", ".join(self._property_name_display(b) for b in player_bans + opp_bans) or "None"
        tk.Label(target_frame, text=f"🚫 Banned: {bans_str}",
                 font=ui["font_small"], bg=ui["bg_secondary"], fg=ui["text_muted"]).pack(anchor="w")

        # Roll display area
        roll_area = tk.Frame(duel_win, bg=ui["bg_primary"])
        roll_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=4)

        # Player side
        p_side = tk.Frame(roll_area, bg=ui["bg_card"], padx=14, pady=10)
        p_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        tk.Label(p_side, text=f"👤 {p_name}", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["success"]).pack(anchor="w")
        p_roll_lbl = tk.Label(p_side, text="—", font=("Consolas", 11), bg=ui["bg_card"],
                              fg=ui["text_primary"], wraplength=350, justify=tk.LEFT, anchor="nw")
        p_roll_lbl.pack(fill=tk.X, pady=4)
        p_match_lbl = tk.Label(p_side, text="Matches: 0", font=ui["font_body_bold"],
                               bg=ui["bg_card"], fg=ui["text_secondary"])
        p_match_lbl.pack(anchor="w")

        # Opponent side
        o_side = tk.Frame(roll_area, bg=ui["bg_card"], padx=14, pady=10)
        o_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))
        tk.Label(o_side, text=f"{opponent['icon']} {opponent['name']}", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["danger"]).pack(anchor="w")
        o_roll_lbl = tk.Label(o_side, text="—", font=("Consolas", 11), bg=ui["bg_card"],
                              fg=ui["text_primary"], wraplength=350, justify=tk.LEFT, anchor="nw")
        o_roll_lbl.pack(fill=tk.X, pady=4)
        o_match_lbl = tk.Label(o_side, text="Matches: 0", font=ui["font_body_bold"],
                               bg=ui["bg_card"], fg=ui["text_secondary"])
        o_match_lbl.pack(anchor="w")

        # Log
        log_lbl = tk.Label(duel_win, text="", font=ui["font_small"],
                           bg=ui["bg_primary"], fg=ui["text_muted"], wraplength=800, justify=tk.LEFT)
        log_lbl.pack(fill=tk.X, padx=18, pady=2)

        # ── Ability + Roll buttons ───────────────────────────────────
        btn_row = tk.Frame(duel_win, bg=ui["bg_primary"])
        btn_row.pack(fill=tk.X, padx=15, pady=(4, 10))

        def _use_ability(key):
            info = self.pvp_abilities[key]
            if not info["unlocked"] or info["cooldown"] > 0 or key in state["abilities_used"]:
                return
            state["abilities_used"].add(key)
            info["cooldown"] = 2
            if key == "lock_property":
                if state["player_matches"]:
                    locked = random.choice(list(state["player_matches"]))
                    state["player_locked"].add(locked)
                    log_lbl.config(text=f"🔒 Locked: {self._property_name_display(locked)}")
            elif key == "reroll_opponent":
                state["opp_rerolled"] = True
                log_lbl.config(text=f"🔄 Opponent must reroll next round!")
            elif key == "double_match":
                state["player_doubled"] = True
                log_lbl.config(text=f"⚡ Double Match active for next roll!")
            elif key == "steal_property":
                if state["opp_matches"] - state["opp_locked"]:
                    stolen = random.choice(list(state["opp_matches"] - state["opp_locked"]))
                    state["opp_matches"].discard(stolen)
                    state["player_matches"].add(stolen)
                    log_lbl.config(text=f"🏴‍☠️ Stole: {self._property_name_display(stolen)}!")
            elif key == "insight":
                revealed = random.sample(list(targets), min(2, len(targets)))
                names = ", ".join(self._property_name_display(r) for r in revealed)
                log_lbl.config(text=f"🔍 Insight revealed: {names}")

        # Ability buttons
        for key, info in self.pvp_abilities.items():
            if info["unlocked"]:
                display_name = key.replace("_", " ").title()
                ab = self._styled_button(btn_row, f"🎯 {display_name}",
                                         lambda k=key: _use_ability(k),
                                         style="info", width=14, small=True)
                ab.pack(side=tk.LEFT, padx=2)

        def _do_round():
            rnd = state["round"]
            if rnd > total_rounds:
                return

            # Player rolls
            p_string = self._generate_random_string()
            p_props = self._analyze_string(p_string)
            p_matches = p_props & state["targets"]
            # Add locked properties back
            p_matches = p_matches | state["player_locked"]
            p_score = len(p_matches)
            if state["player_doubled"]:
                p_score = min(p_score * 2, len(targets))
                state["player_doubled"] = False

            # Opponent rolls (AI influenced by style)
            o_string = self._generate_random_string()
            o_props = self._analyze_string(o_string)

            # If we forced a reroll, generate a worse string
            if state["opp_rerolled"]:
                o_string = self._generate_random_string()
                o_props = self._analyze_string(o_string)
                state["opp_rerolled"] = False

            o_matches = o_props & state["targets"]
            # AI match bonus — adds synthetic matches based on difficulty
            bonus_chance = opponent["match_bonus"]
            for t in state["targets"]:
                if t not in o_matches and random.random() < bonus_chance:
                    o_matches.add(t)
            o_matches = o_matches | state["opp_locked"]
            o_score = len(o_matches)

            # AI ability usage
            if random.random() < opponent["ability_chance"] and rnd > 1:
                # AI locks a property it matched
                if o_matches - state["opp_locked"]:
                    lock = random.choice(list(o_matches - state["opp_locked"]))
                    state["opp_locked"].add(lock)

            state["player_matches"] = p_matches
            state["opp_matches"] = o_matches

            # Determine round winner
            if p_score > o_score:
                state["player_score"] += 1
                round_result = "✅ You win this round!"
                result_color = ui["success"]
            elif o_score > p_score:
                state["opp_score"] += 1
                round_result = f"❌ {opponent['name']} wins this round!"
                result_color = ui["danger"]
            else:
                round_result = "🤝 Round tied — no points awarded"
                result_color = ui["warning"]

            # Update UI
            p_roll_lbl.config(text=p_string[:60])
            p_match_lbl.config(text=f"Matches: {p_score}/{len(targets)}",
                               fg=ui["success"] if p_score >= o_score else ui["danger"])
            o_roll_lbl.config(text=o_string[:60])
            o_match_lbl.config(text=f"Matches: {o_score}/{len(targets)}",
                               fg=ui["success"] if o_score >= p_score else ui["danger"])
            player_score_lbl.config(text=f"👤 {p_name}:  {state['player_score']}")
            opp_score_lbl.config(text=f"{opponent['icon']} {opponent['name']}:  {state['opp_score']}")
            round_lbl.config(text=f"Round {rnd}/{total_rounds}")
            log_lbl.config(text=round_result, fg=result_color)

            state["round_log"].append({
                "round": rnd, "p_score": p_score, "o_score": o_score,
                "p_string": p_string[:30], "o_string": o_string[:30]
            })

            # Reduce cooldowns
            for k, v in self.pvp_abilities.items():
                if v["cooldown"] > 0:
                    v["cooldown"] -= 1

            state["round"] += 1

            # Check for early win (clinched majority)
            needed = (total_rounds // 2) + 1
            if state["player_score"] >= needed or state["opp_score"] >= needed or rnd >= total_rounds:
                roll_btn.config(state=tk.DISABLED)
                duel_win.after(800, lambda: self._pvp_finish_duel(duel_win, opponent, state))

        roll_btn = self._styled_button(btn_row, "🎲 ROLL ROUND", _do_round, style="success", width=16)
        roll_btn.pack(side=tk.RIGHT, padx=4)

    # ── Finish Screen ────────────────────────────────────────────────

    def _pvp_finish_duel(self, duel_win, opponent, state):
        """Show result screen, update ELO, save match."""
        ui = self._ui
        duel_win.destroy()

        ps = state["player_score"]
        os_ = state["opp_score"]
        if ps > os_:
            result = "WIN"
            elo_result = 1
            self.pvp_wins += 1
            self.pvp_streak += 1
            self.pvp_best_streak = max(self.pvp_best_streak, self.pvp_streak)
            # Grant SP reward
            sp_reward = max(5, int(10 * (opponent["elo"] / 1000)))
            self.sp += sp_reward
            xp_reward = max(20, int(50 * (opponent["elo"] / 1000)))
            self.player_xp += xp_reward
        elif os_ > ps:
            result = "LOSS"
            elo_result = 0
            self.pvp_losses += 1
            self.pvp_streak = 0
            sp_reward = 2
            self.sp += sp_reward
            xp_reward = 10
            self.player_xp += xp_reward
        else:
            result = "DRAW"
            elo_result = 0.5
            self.pvp_draws += 1
            sp_reward = 4
            self.sp += sp_reward
            xp_reward = 15
            self.player_xp += xp_reward

        elo_change = self._pvp_elo_change(self.pvp_elo, opponent["elo"], elo_result)
        self.pvp_elo = max(0, self.pvp_elo + elo_change)

        # Check ability unlocks
        for key, elo_req in self.pvp_ability_unlock_elo.items():
            if self.pvp_elo >= elo_req and not self.pvp_abilities[key]["unlocked"]:
                self.pvp_abilities[key]["unlocked"] = True

        # Record match
        import datetime
        self.pvp_match_history.append({
            "opponent": opponent["name"],
            "result": result,
            "score": ps,
            "opp_score": os_,
            "elo_change": elo_change,
            "elo_after": self.pvp_elo,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "rounds": state["round_log"],
        })

        self._save_pvp_data()

        # If the opponent is a real player (not a bot), update their PvP file too
        if not opponent.get("is_bot", True):
            opp_pvp_path = f"user_{opponent['name']}_pvp.json"
            try:
                opp_data = {}
                if os.path.exists(opp_pvp_path):
                    with open(opp_pvp_path, "r") as f:
                        opp_data = json.load(f)
                opp_elo_before = opp_data.get("elo", 1000)
                # Opponent gets the mirror result
                if result == "WIN":
                    opp_elo_result = 0       # they lost
                    opp_data["losses"] = opp_data.get("losses", 0) + 1
                    opp_data["streak"] = 0
                elif result == "LOSS":
                    opp_elo_result = 1       # they won
                    opp_data["wins"] = opp_data.get("wins", 0) + 1
                    opp_data["streak"] = opp_data.get("streak", 0) + 1
                    opp_data["best_streak"] = max(opp_data.get("best_streak", 0), opp_data["streak"])
                else:
                    opp_elo_result = 0.5
                    opp_data["draws"] = opp_data.get("draws", 0) + 1
                opp_elo_chg = self._pvp_elo_change(opp_elo_before, self.pvp_elo - elo_change, opp_elo_result)
                opp_data["elo"] = max(0, opp_elo_before + opp_elo_chg)
                opp_hist = opp_data.get("history", [])
                opp_hist.append({
                    "opponent": self.current_username,
                    "result": "LOSS" if result == "WIN" else "WIN" if result == "LOSS" else "DRAW",
                    "score": os_,
                    "opp_score": ps,
                    "elo_change": opp_elo_chg,
                    "elo_after": opp_data["elo"],
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                opp_data["history"] = opp_hist[-100:]
                with open(opp_pvp_path, "w") as f:
                    json.dump(opp_data, f, indent=2)
            except Exception:
                pass

        # ── Result Window ────────────────────────────────────────────
        res_win = self._styled_toplevel("⚔️ Duel Result", 550, 480, 450, 380)

        if result == "WIN":
            icon, title_text, color = "🏆", "VICTORY!", ui["success"]
        elif result == "LOSS":
            icon, title_text, color = "💀", "DEFEAT", ui["danger"]
        else:
            icon, title_text, color = "🤝", "DRAW", ui["warning"]

        self._styled_header(res_win, title_text, f"vs {opponent['icon']} {opponent['name']}", icon=icon)

        # Big result
        result_frame = tk.Frame(res_win, bg=ui["bg_card"], padx=20, pady=20)
        result_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

        tk.Label(result_frame, text=f"{icon} {title_text}", font=("Segoe UI", 28, "bold"),
                 bg=ui["bg_card"], fg=color).pack()
        tk.Label(result_frame, text=f"Score: {ps} – {os_}", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["text_primary"]).pack(pady=(8, 0))

        # Details
        details_frame = tk.Frame(res_win, bg=ui["bg_primary"])
        details_frame.pack(fill=tk.X, padx=20, pady=5)

        rank_name, rank_color = self._pvp_rank_for_elo(self.pvp_elo)
        elo_text = f"+{elo_change}" if elo_change >= 0 else str(elo_change)
        elo_color = ui["success"] if elo_change >= 0 else ui["danger"]

        rewards = [
            ("ELO Change", elo_text, elo_color),
            ("New ELO", str(self.pvp_elo), rank_color),
            ("Rank", rank_name, rank_color),
            ("SP Earned", f"+{sp_reward}", ui["sp_color"]),
            ("XP Earned", f"+{xp_reward}", ui["xp_color"]),
            ("Win Streak", str(self.pvp_streak), ui["gold"]),
        ]
        for label, value, clr in rewards:
            row = tk.Frame(details_frame, bg=ui["bg_card"], padx=12, pady=5)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, font=ui["font_body"], bg=ui["bg_card"],
                     fg=ui["text_secondary"]).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=ui["font_body_bold"], bg=ui["bg_card"],
                     fg=clr).pack(side=tk.RIGHT)

        # Round breakdown
        if state["round_log"]:
            tk.Label(res_win, text="Round Breakdown:", font=ui["font_subhead"],
                     bg=ui["bg_primary"], fg=ui["text_primary"]).pack(anchor="w", padx=22, pady=(10, 4))
            for rd in state["round_log"]:
                rf = tk.Frame(res_win, bg=ui["bg_secondary"], padx=10, pady=3)
                rf.pack(fill=tk.X, padx=22, pady=1)
                rd_color = ui["success"] if rd["p_score"] > rd["o_score"] else \
                           ui["danger"] if rd["o_score"] > rd["p_score"] else ui["warning"]
                tk.Label(rf, text=f"R{rd['round']}: You {rd['p_score']} – {rd['o_score']} Opp",
                         font=ui["font_small"], bg=ui["bg_secondary"], fg=rd_color).pack(side=tk.LEFT)

        # Buttons
        btn_frame = tk.Frame(res_win, bg=ui["bg_primary"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(12, 15))
        self._styled_button(btn_frame, "🏟️ Back to Arena",
                            lambda: (res_win.destroy(), self.show_pvp_arena()),
                            style="primary", width=16).pack(side=tk.LEFT, padx=4)
        self._styled_button(btn_frame, "⚔️ Rematch",
                            lambda o=opponent: (res_win.destroy(), self._pvp_rematch(o)),
                            style="danger", width=14).pack(side=tk.LEFT, padx=4)
        self._styled_button(btn_frame, "🚪 Close", res_win.destroy,
                            style="neutral", width=10).pack(side=tk.RIGHT, padx=4)

    def _pvp_rematch(self, opponent):
        """Quick rematch — open a throwaway parent for the draft phase."""
        placeholder = self._styled_toplevel("⚔️ Matchmaking...", 300, 100)
        self._pvp_start_draft(placeholder, opponent)

    def reset_game(self):
        """Reset current round (preserves lifetime stats like roll count and wins)"""
        self.target_properties = set()
        self.game_won = False
        self.winning_streak = 0
        self.session_win_count = 0
        self._generate_target()
        self._update_display("", set())
    
    def quit_game(self):
        """Save game state and quit the application"""
        self._save_stats()
        self._save_achievements()
        self._save_equipment()
        self._save_settings()
        self._save_pvp_data()
        self.root.destroy()
    
    def show_progression_window(self):
        """Show the comprehensive player progression hub."""
        ui = self._ui
        pw = self._styled_toplevel("📈 Progression Hub", width=880, height=740)
        self._styled_header(pw, "Player Progression", "Your complete journey at a glance", icon="📈")

        notebook = ttk.Notebook(pw, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ── TAB 1 — Overview (Hero Card) ─────────────────────────────
        ov_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(ov_tab, text="  🏠 Overview  ")

        ov_scroll_outer, ov_inner = self._styled_scrollable(ov_tab, bg=ui["bg_primary"])
        ov_scroll_outer.pack(fill=tk.BOTH, expand=True)

        # ── Hero banner
        hero = tk.Frame(ov_inner, bg=ui["bg_card"], padx=20, pady=14)
        hero.pack(fill=tk.X, padx=12, pady=(12, 6))

        title = self._get_player_title_for_wins(self.wins_count)
        rank_name, rank_color = self._pvp_rank_for_elo(getattr(self, "pvp_elo", 1000))
        tk.Label(hero, text=f"{title}  {self.current_username or 'Player'}",
                 font=("Segoe UI", 20, "bold"), bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w")
        tk.Label(hero, text=f"Level {self.player_level}  ·  {rank_name} ({getattr(self, 'pvp_elo', 1000)} ELO)",
                 font=ui["font_body"], bg=ui["bg_card"], fg=rank_color).pack(anchor="w", pady=(2, 0))

        # XP progress bar
        xp_bar_frame = tk.Frame(hero, bg=ui["bg_card"])
        xp_bar_frame.pack(fill=tk.X, pady=(8, 0))
        xp_ratio = min(1.0, self.player_xp / max(1, self.xp_to_level_up))
        tk.Label(xp_bar_frame, text=f"XP: {self.player_xp}/{self.xp_to_level_up}  ({xp_ratio:.0%})",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["xp_color"]).pack(anchor="w")
        xp_bg = tk.Frame(xp_bar_frame, bg=ui["border"], height=10)
        xp_bg.pack(fill=tk.X, pady=(2, 0))
        xp_bg.update_idletasks()
        xp_fill = tk.Frame(xp_bg, bg=ui["xp_color"], height=10)
        xp_fill.place(x=0, y=0, relwidth=max(0.01, xp_ratio))

        # ── Key stats grid (2 columns)
        grid = tk.Frame(ov_inner, bg=ui["bg_primary"])
        grid.pack(fill=tk.X, padx=12, pady=6)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        def _stat_card(parent, icon, label, value, color, r, c):
            f = tk.Frame(parent, bg=ui["bg_card"], padx=12, pady=8)
            f.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            tk.Label(f, text=f"{icon} {label}", font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_muted"]).pack(anchor="w")
            tk.Label(f, text=str(value), font=("Segoe UI", 18, "bold"),
                     bg=ui["bg_card"], fg=color).pack(anchor="w")

        _stat_card(grid, "🏆", "Total Wins",       self.wins_count, ui["gold"], 0, 0)
        _stat_card(grid, "🎲", "Total Rolls",       self.roll_count, ui["info"], 0, 1)
        _stat_card(grid, "🔥", "Current Streak",    self.winning_streak, ui["warning"], 1, 0)
        _stat_card(grid, "⚡", "Best Streak",        self.max_winning_streak, ui["danger"], 1, 1)
        _stat_card(grid, "💰", "SP",                 self.sp, ui["sp_color"], 2, 0)
        pvp_elo = getattr(self, "pvp_elo", 1000)
        _stat_card(grid, "⚔️", "PvP ELO",           pvp_elo, ui["accent_light"], 2, 1)

        # ── Active Effects
        effects_card = tk.Frame(ov_inner, bg=ui["bg_card"], padx=14, pady=8)
        effects_card.pack(fill=tk.X, padx=12, pady=(4, 6))
        tk.Label(effects_card, text="✨ Active Effects", font=ui["font_small_bold"],
                 bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w")

        active_effects = []
        if self.current_specialization:
            spec = self.specialization_trees.get(self.current_specialization, {})
            active_effects.append(f"{spec.get('icon', '🔧')} Specialization: {spec.get('name', '?')}")
        if self.rng_influence.get("ritual_system", {}).get("active_ritual"):
            rk = self.rng_influence["ritual_system"]["active_ritual"]
            rit = self.rng_influence["ritual_system"]["available_rituals"].get(rk, {})
            active_effects.append(f"🕯️ Ritual: {rit.get('name', rk)}")
        if self.temp_luck_boost > 0:
            active_effects.append(f"🍀 Luck Boost: +{self.temp_luck_boost:.0%}")
        if self.prestige_system.get("current_level", 0) > 0:
            active_effects.append(f"♻️ Prestige Level {self.prestige_system['current_level']}")
        if not active_effects:
            active_effects.append("None — keep playing to earn effects!")
        tk.Label(effects_card, text="  ·  ".join(active_effects), font=ui["font_small"],
                 bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(2, 0))

        # ── TAB 2 — Stats Deep Dive ──────────────────────────────────
        stats_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(stats_tab, text="  📊 Stats  ")

        so, si = self._styled_scrollable(stats_tab, bg=ui["bg_primary"])
        so.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        discoveries = self.stats.get("property_discoveries", {})
        play_time = self.stats.get("play_time", 0) + (time.time() - self.stats.get("start_time", time.time()))
        fastest = self.stats.get("fastest_win", float("inf"))
        slowest = self.stats.get("slowest_win", 0)
        avg_rpw = self.stats.get("avg_rolls_per_win", 0)
        win_rate = (self.wins_count / max(1, self.roll_count)) * 100

        stat_sections = [
            ("🎯 Core Stats", [
                ("Total Wins", str(self.wins_count)),
                ("Total Rolls", str(self.roll_count)),
                ("Win Rate", f"{win_rate:.1f}%"),
                ("Best Streak", str(self.max_winning_streak)),
                ("Current Streak", str(self.winning_streak)),
            ]),
            ("⏱️ Performance", [
                ("Fastest Win", f"{fastest} rolls" if fastest != float("inf") else "—"),
                ("Slowest Win", f"{slowest} rolls" if slowest > 0 else "—"),
                ("Avg Rolls/Win", f"{avg_rpw:.1f}" if avg_rpw > 0 else "—"),
                ("Play Time", f"{play_time / 3600:.1f} hours"),
            ]),
            ("⚔️ PvP", [
                ("ELO Rating", str(getattr(self, "pvp_elo", 1000))),
                ("PvP Wins", str(getattr(self, "pvp_wins", 0))),
                ("PvP Losses", str(getattr(self, "pvp_losses", 0))),
                ("PvP Best Streak", str(getattr(self, "pvp_best_streak", 0))),
            ]),
            ("🔬 Properties", [
                ("Discovered", f"{len(discoveries)}/15"),
            ]),
            ("💰 Economy", [
                ("Current SP", str(self.sp)),
                ("SP+ Owned", str(self.sp_plus)),
                ("SPx Owned", str(self.sp_x)),
                ("SP^ Owned", str(self.sp_caret)),
                ("Net Worth", str(self.sp + self.sp_plus * 10 + self.sp_x * 50 + self.sp_caret * 100)),
                ("All-Time SP Earned", str(self.meta_progression.get("total_sp_earned_all_time", 0))),
            ]),
        ]

        for section_title, rows in stat_sections:
            sf = tk.Frame(si, bg=ui["bg_card"], padx=14, pady=8)
            sf.pack(fill=tk.X, padx=8, pady=4)
            tk.Label(sf, text=section_title, font=ui["font_subhead"],
                     bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w", pady=(0, 4))
            for lbl, val in rows:
                row = tk.Frame(sf, bg=ui["bg_card"])
                row.pack(fill=tk.X, pady=1)
                tk.Label(row, text=lbl, font=ui["font_body"], bg=ui["bg_card"],
                         fg=ui["text_secondary"]).pack(side=tk.LEFT)
                tk.Label(row, text=val, font=ui["font_body_bold"], bg=ui["bg_card"],
                         fg=ui["text_primary"]).pack(side=tk.RIGHT)

        # ── TAB 3 — Progress Bars ────────────────────────────────────
        prog_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(prog_tab, text="  📶 Progress  ")

        po, pi = self._styled_scrollable(prog_tab, bg=ui["bg_primary"])
        po.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def _progress_bar(parent, label, current, maximum, color, extra_text=""):
            pf = tk.Frame(parent, bg=ui["bg_card"], padx=14, pady=8)
            pf.pack(fill=tk.X, padx=8, pady=3)
            ratio = min(1.0, current / max(1, maximum))
            hdr = tk.Frame(pf, bg=ui["bg_card"])
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=label, font=ui["font_body_bold"], bg=ui["bg_card"],
                     fg=ui["text_primary"]).pack(side=tk.LEFT)
            right_text = f"{current}/{maximum}  ({ratio:.0%})"
            if extra_text:
                right_text += f"  {extra_text}"
            tk.Label(hdr, text=right_text, font=ui["font_small"], bg=ui["bg_card"],
                     fg=color).pack(side=tk.RIGHT)
            bar_bg = tk.Frame(pf, bg=ui["border"], height=12)
            bar_bg.pack(fill=tk.X, pady=(4, 0))
            bar_bg.update_idletasks()
            bar_fill = tk.Frame(bar_bg, bg=color, height=12)
            bar_fill.place(x=0, y=0, relwidth=max(0.005, ratio))

        # XP to next level
        _progress_bar(pi, "⭐ Level Progress", self.player_xp, self.xp_to_level_up, ui["xp_color"])

        # Wins milestones
        win_milestones = [10, 25, 50, 100, 250, 500, 1000]
        next_wm = next((m for m in win_milestones if self.wins_count < m), 1000)
        _progress_bar(pi, "🏆 Wins → Next Milestone", self.wins_count, next_wm, ui["gold"])

        # Achievements
        total_ach = len(self.achievements)
        done_ach = sum(1 for a in self.achievements.values() if a.get("completed") or a.get("unlocked"))
        _progress_bar(pi, "🎖️ Achievements", done_ach, total_ach, ui["warning"])

        # Properties discovered
        _progress_bar(pi, "🔬 Properties Discovered", len(discoveries), 15, ui["info"])

        # PvP ELO milestones
        elo_milestones = [("Bronze", 1000), ("Silver", 1100), ("Gold", 1200),
                          ("Platinum", 1300), ("Diamond", 1400), ("Master", 1600), ("Legend", 1800)]
        next_elo_name, next_elo_val = "Legend", 1800
        for en, ev in elo_milestones:
            if pvp_elo < ev:
                next_elo_name, next_elo_val = en, ev
                break
        _progress_bar(pi, f"⚔️ ELO → {next_elo_name}", pvp_elo, next_elo_val, ui["accent_light"])

        # Roll milestones
        roll_milestones = [100, 500, 1000, 5000, 10000, 50000]
        next_rm = next((m for m in roll_milestones if self.roll_count < m), 50000)
        _progress_bar(pi, "🎲 Rolls → Next Milestone", self.roll_count, next_rm, ui["text_secondary"])

        # Tournament personal bests
        t_scores = self.tournament_data.get("scores", {})
        for mode, icon, unit, goal in [("speed", "⚡", "rolls", 5), ("survival", "🛡️", "rounds", 10), ("blitz", "🔥", "pts", 50)]:
            ms = t_scores.get(mode, {})
            best = ms.get("best")
            if best is not None:
                if mode == "speed":
                    _progress_bar(pi, f"{icon} Speed Trial Best", max(0, goal - best + goal), goal * 2, ui["warning"],
                                  extra_text=f"({best} rolls)")
                else:
                    _progress_bar(pi, f"{icon} {mode.title()} Best", best, goal, ui["success"],
                                  extra_text=f"(goal: {goal})")
            else:
                _progress_bar(pi, f"{icon} {mode.title()} (not played yet)", 0, goal, ui["text_muted"])

        # ── TAB 4 — Quests ───────────────────────────────────────────
        quests_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(quests_tab, text="  📜 Quests  ")

        qo, qi = self._styled_scrollable(quests_tab, bg=ui["bg_primary"])
        qo.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if not self.active_quests:
            tk.Label(qi, text="No active quests.\nClick below to generate daily quests!",
                     font=ui["font_body"], bg=ui["bg_primary"], fg=ui["text_muted"]).pack(pady=30)
        else:
            for qid, quest in self.active_quests.items():
                is_done = qid in self.completed_quests
                qf = tk.Frame(qi, bg=ui["bg_card"], padx=14, pady=8)
                qf.pack(fill=tk.X, padx=8, pady=3)
                # Header row
                hdr = tk.Frame(qf, bg=ui["bg_card"])
                hdr.pack(fill=tk.X)
                status_icon = "✅" if is_done else "⏳"
                tk.Label(hdr, text=f"{status_icon} {quest['name']}",
                         font=ui["font_body_bold"], bg=ui["bg_card"],
                         fg=ui["success"] if is_done else ui["text_primary"]).pack(side=tk.LEFT)
                tk.Label(hdr, text=quest.get("type", "").title(),
                         font=ui["font_small"], bg=ui["bg_card"], fg=ui["info"]).pack(side=tk.RIGHT)
                # Description
                tk.Label(qf, text=quest.get("description", ""), font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_secondary"], anchor="w").pack(fill=tk.X, pady=(2, 0))
                # Progress bar
                cur = quest.get("current", 0)
                tgt = quest.get("target", 1)
                ratio = min(1.0, cur / max(1, tgt))
                prog_f = tk.Frame(qf, bg=ui["bg_card"])
                prog_f.pack(fill=tk.X, pady=(4, 0))
                bar_bg = tk.Frame(prog_f, bg=ui["border"], height=8)
                bar_bg.pack(fill=tk.X)
                bar_bg.update_idletasks()
                bar_fill = tk.Frame(bar_bg, bg=ui["success"] if is_done else ui["info"], height=8)
                bar_fill.place(x=0, y=0, relwidth=max(0.01, ratio))
                tk.Label(prog_f, text=f"{cur}/{tgt}", font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_muted"]).pack(anchor="e")
                # Rewards
                rwd_parts = []
                if quest.get("reward_xp"):
                    rwd_parts.append(f"+{quest['reward_xp']} XP")
                if quest.get("reward_sp"):
                    rwd_parts.append(f"+{quest['reward_sp']} SP")
                if quest.get("reward_title"):
                    rwd_parts.append(f'Title: "{quest["reward_title"]}"')
                if rwd_parts:
                    tk.Label(qf, text="  ".join(rwd_parts), font=ui["font_small"],
                             bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(2, 0))

        # Generate quests button
        btn_f = tk.Frame(quests_tab, bg=ui["bg_primary"])
        btn_f.pack(fill=tk.X, padx=12, pady=8)
        self._styled_button(btn_f, "🔄 Generate New Daily Quests",
                            lambda: (self._generate_daily_quests(), pw.destroy(), self.show_progression_window()),
                            style="info", width=24).pack()

        # ── TAB 5 — Specializations ──────────────────────────────────
        spec_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(spec_tab, text="  🔧 Specializations  ")

        spo, spi = self._styled_scrollable(spec_tab, bg=ui["bg_primary"])
        spo.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Current specialization banner
        if self.current_specialization:
            spec = self.specialization_trees.get(self.current_specialization, {})
            cur_f = tk.Frame(spi, bg=ui["bg_card"], padx=14, pady=10)
            cur_f.pack(fill=tk.X, padx=8, pady=6)
            tk.Label(cur_f, text=f"{spec.get('icon', '🔧')} Active: {spec.get('name', '?')}",
                     font=ui["font_heading"], bg=ui["bg_card"], fg=ui["success"]).pack(anchor="w")
            tk.Label(cur_f, text=spec.get("description", ""), font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(anchor="w", pady=(2, 0))
            # Passive bonuses
            bonuses_text = []
            for bk, bv in spec.get("passive_bonuses", {}).items():
                bn = bk.replace("_", " ").title()
                bonuses_text.append(f"{bn}: +{bv:.1%}" if isinstance(bv, float) and bv < 1 else f"{bn}: +{bv}")
            if bonuses_text:
                tk.Label(cur_f, text="Bonuses: " + "  ·  ".join(bonuses_text), font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(4, 0))

        # All specs
        for spec_key, spec in self.specialization_trees.items():
            sf = tk.Frame(spi, bg=ui["bg_card"], padx=14, pady=8)
            sf.pack(fill=tk.X, padx=8, pady=3)
            is_active = self.current_specialization == spec_key
            is_unlocked = spec.get("unlocked", False)
            # Header
            hdr = tk.Frame(sf, bg=ui["bg_card"])
            hdr.pack(fill=tk.X)
            name_color = ui["success"] if is_active else ui["text_primary"] if is_unlocked else ui["text_muted"]
            status = "✅ ACTIVE" if is_active else "🔓 Unlocked" if is_unlocked else f"🔒 {spec.get('unlock_cost', '?')} SP"
            tk.Label(hdr, text=f"{spec.get('icon', '?')} {spec.get('name', spec_key)}",
                     font=ui["font_body_bold"], bg=ui["bg_card"], fg=name_color).pack(side=tk.LEFT)
            tk.Label(hdr, text=status, font=ui["font_small_bold"], bg=ui["bg_card"],
                     fg=ui["success"] if is_active else ui["info"] if is_unlocked else ui["text_muted"]).pack(side=tk.RIGHT)
            tk.Label(sf, text=spec.get("description", ""), font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(anchor="w", pady=(2, 0))
            # Buttons
            if not is_unlocked:
                self._styled_button(sf, f"Unlock ({spec.get('unlock_cost', '?')} SP)",
                                    lambda s=spec_key: (self._unlock_specialization(s), pw.destroy(), self.show_progression_window()),
                                    style="warning", width=16, small=True).pack(anchor="w", pady=(4, 0))
            elif not is_active:
                self._styled_button(sf, "Select",
                                    lambda s=spec_key: (self._switch_specialization(s), pw.destroy(), self.show_progression_window()),
                                    style="primary", width=10, small=True).pack(anchor="w", pady=(4, 0))

        # ── TAB 6 — Prestige ─────────────────────────────────────────
        prest_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(prest_tab, text="  ♻️ Prestige  ")

        prest_level = self.prestige_system.get("current_level", 0)
        prest_pts = self.prestige_system.get("prestige_points", 0)
        perm_bonuses = self.prestige_system.get("permanent_bonuses", {})

        # Prestige status card
        ps_card = tk.Frame(prest_tab, bg=ui["bg_card"], padx=18, pady=12)
        ps_card.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(ps_card, text=f"♻️ Prestige Level {prest_level}",
                 font=("Segoe UI", 20, "bold"), bg=ui["bg_card"],
                 fg=ui["gold"] if prest_level > 0 else ui["text_muted"]).pack(anchor="w")
        tk.Label(ps_card, text=f"Prestige Points: {prest_pts} PP  ·  Total Prestiges: {self.prestige_system.get('total_prestiges', 0)}",
                 font=ui["font_body"], bg=ui["bg_card"], fg=ui["sp_color"]).pack(anchor="w", pady=(2, 0))

        if perm_bonuses:
            bonuses_text = "  ·  ".join(f"{k.replace('_', ' ').title()}: +{v}%" for k, v in perm_bonuses.items())
            tk.Label(ps_card, text=f"Permanent Bonuses:  {bonuses_text}", font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["success"]).pack(anchor="w", pady=(4, 0))

        # Requirements
        req_card = tk.Frame(prest_tab, bg=ui["bg_card"], padx=18, pady=10)
        req_card.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(req_card, text="⚡ Prestige Requirements", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w", pady=(0, 4))

        total_wins_at = self.meta_progression.get("total_wins_all_time", 0)
        req_data = [
            ("Total Wins ≥ 1000", total_wins_at >= 1000, f"{total_wins_at}/1000"),
            ("Level ≥ 25", self.player_level >= 25, f"{self.player_level}/25"),
        ]
        can_prestige = all(ok for _, ok, _ in req_data)
        for req_name, met, progress in req_data:
            rf = tk.Frame(req_card, bg=ui["bg_card"])
            rf.pack(fill=tk.X, pady=1)
            icon = "✅" if met else "❌"
            tk.Label(rf, text=f"  {icon} {req_name}", font=ui["font_body"], bg=ui["bg_card"],
                     fg=ui["success"] if met else ui["danger"]).pack(side=tk.LEFT)
            tk.Label(rf, text=progress, font=ui["font_mono_sm"], bg=ui["bg_card"],
                     fg=ui["text_secondary"]).pack(side=tk.RIGHT)

        if can_prestige:
            self._styled_button(req_card, "⚡ PRESTIGE RESET",
                                lambda: (self._perform_prestige_reset(), pw.destroy(), self.show_progression_window()),
                                style="warning", width=18).pack(anchor="w", pady=(8, 0))
        else:
            tk.Label(req_card, text="Keep playing to unlock prestige!",
                     font=ui["font_small"], bg=ui["bg_card"], fg=ui["text_muted"]).pack(anchor="w", pady=(6, 0))

        # Prestige upgrades
        pup_outer, pup_inner = self._styled_scrollable(prest_tab, bg=ui["bg_primary"])
        pup_outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))
        tk.Label(pup_inner, text="🛒 Prestige Upgrades", font=ui["font_subhead"],
                 bg=ui["bg_primary"], fg=ui["accent_light"]).pack(anchor="w", padx=8, pady=(4, 4))

        for upg_key, upg in self.prestige_system.get("available_upgrades", {}).items():
            uf = tk.Frame(pup_inner, bg=ui["bg_card"], padx=12, pady=6)
            uf.pack(fill=tk.X, padx=8, pady=2)
            purchased = upg.get("purchased", False)
            hdr = tk.Frame(uf, bg=ui["bg_card"])
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=upg.get("name", upg_key), font=ui["font_body_bold"], bg=ui["bg_card"],
                     fg=ui["success"] if purchased else ui["text_primary"]).pack(side=tk.LEFT)
            status_txt = "✅ Purchased" if purchased else f"{upg.get('cost', '?')} PP"
            tk.Label(hdr, text=status_txt, font=ui["font_small_bold"], bg=ui["bg_card"],
                     fg=ui["success"] if purchased else ui["warning"]).pack(side=tk.RIGHT)
            tk.Label(uf, text=upg.get("description", ""), font=ui["font_small"],
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(anchor="w", pady=(2, 0))
            if not purchased and prest_pts >= upg.get("cost", 999999):
                self._styled_button(uf, "Purchase",
                                    lambda u=upg_key: (self._purchase_prestige_upgrade(u), pw.destroy(), self.show_progression_window()),
                                    style="success", width=10, small=True).pack(anchor="w", pady=(4, 0))
    
    def show_equipment_window(self):
        """Show equipment crafting window"""
        ui = self._ui
        equip_window = self._styled_toplevel("⚔️ Equipment Crafting", 750, 650)
        
        # Header
        self._styled_header(equip_window, "Equipment Crafting", "Forge powerful gear", icon="⚔️")
        
        # Current inventory card
        inv_outer, inv_card = self._styled_card(equip_window, "Current Equipment")
        inv_outer.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        inv_text = f"Gauntlet: {self.equipped_gauntlet or 'None'} | Device: {self.equipped_device or 'None'}\n"
        inv_text += f"SP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}"
        inv_label = tk.Label(inv_card, text=inv_text, bg=ui["bg_card"], fg=ui["text_primary"],
                            font=ui["font_body"], justify=tk.LEFT)
        inv_label.pack(padx=10, pady=5)
        
        # Recipe list card
        recipes_outer, recipes_card = self._styled_card(equip_window, "Available Recipes (Click Craft to craft)")
        recipes_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Create scrollable frame
        scroll_outer, scrollable_frame = self._styled_scrollable(recipes_card, ui["bg_card"])
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        def craft_item(item_id, recipe):
            cost = recipe['cost']
            can_craft = True
            message = ""
            
            if "sp" in cost and self.sp < cost["sp"]:
                can_craft = False
                message = f"Need {cost['sp']} SP (have {self.sp})"
            elif "sp_plus" in cost and self.sp_plus < cost["sp_plus"]:
                can_craft = False
                message = f"Need {cost['sp_plus']} SP+ (have {self.sp_plus})"
            elif "sp_x" in cost and self.sp_x < cost["sp_x"]:
                can_craft = False
                message = f"Need {cost['sp_x']} SPx (have {self.sp_x})"
            elif "sp_caret" in cost and self.sp_caret < cost["sp_caret"]:
                can_craft = False
                message = f"Need {cost['sp_caret']} SP^ (have {self.sp_caret})"
            
            if not can_craft:
                self._show_popup_error("Cannot Craft", message)
                return
            
            if "sp" in cost:
                self.sp -= cost["sp"]
            if "sp_plus" in cost:
                self.sp_plus -= cost["sp_plus"]
            if "sp_x" in cost:
                self.sp_x -= cost["sp_x"]
            if "sp_caret" in cost:
                self.sp_caret -= cost["sp_caret"]
            
            if "owned" not in self.equipment_inventory:
                self.equipment_inventory["owned"] = []
            self.equipment_inventory["owned"].append(item_id)
            
            if recipe['type'] == 'gauntlet':
                self.equipped_gauntlet = item_id
            elif recipe['type'] == 'device':
                self.equipped_device = item_id
            
            self._save_equipment()
            self._update_sp_label()
            
            self._show_popup_info("Crafted!", f"Successfully crafted {recipe['desc']}")
            inv_label.config(text=f"Gauntlet: {self.equipped_gauntlet or 'None'} | Device: {self.equipped_device or 'None'}\nSP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}")
        
        def equip_item(item_id, recipe):
            if recipe['type'] == 'gauntlet':
                self.equipped_gauntlet = item_id
            elif recipe['type'] == 'device':
                self.equipped_device = item_id
            
            self._save_equipment()
            self._show_popup_info("Equipped!", f"Equipped {recipe['desc']}")
            inv_label.config(text=f"Gauntlet: {self.equipped_gauntlet or 'None'} | Device: {self.equipped_device or 'None'}\nSP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}")
        
        for item_id, recipe in self.equipment_recipes.items():
            btn_frame = tk.Frame(scrollable_frame, bg=ui["bg_card"])
            btn_frame.pack(fill=tk.X, padx=5, pady=3)
            
            is_owned = "owned" in self.equipment_inventory and item_id in self.equipment_inventory["owned"]
            
            label = tk.Label(btn_frame, text=f"{recipe['desc']}", bg=ui["bg_card"], fg=ui["success"],
                           font=ui["font_body"], width=35, anchor="w")
            label.pack(side=tk.LEFT, padx=5)
            
            if is_owned:
                status_label = tk.Label(btn_frame, text="[BOUGHT]", bg=ui["bg_card"], fg=ui["success"],
                                       font=ui["font_small_bold"], width=8)
                status_label.pack(side=tk.LEFT, padx=3)
            else:
                cost_text = ""
                if "sp" in recipe['cost']:
                    cost_text += f"SP:{recipe['cost']['sp']} "
                if "sp_plus" in recipe['cost']:
                    cost_text += f"SP+:{recipe['cost']['sp_plus']} "
                if "sp_x" in recipe['cost']:
                    cost_text += f"SPx:{recipe['cost']['sp_x']} "
                if "sp_caret" in recipe['cost']:
                    cost_text += f"SP^:{recipe['cost']['sp_caret']}"
                
                cost_label = tk.Label(btn_frame, text=cost_text, bg=ui["bg_card"], fg=ui["gold"],
                                     font=ui["font_small"], width=20, anchor="e")
                cost_label.pack(side=tk.LEFT, padx=3)
            
            if is_owned:
                action_btn = self._styled_button(btn_frame, "Equip",
                                      command=lambda iid=item_id, rec=recipe: equip_item(iid, rec),
                                      style="success", width=6, small=True)
            else:
                action_btn = self._styled_button(btn_frame, "Craft",
                                      command=lambda iid=item_id, rec=recipe: craft_item(iid, rec),
                                      style="primary", width=6, small=True)
            action_btn.pack(side=tk.LEFT, padx=3)
    
    def show_shop_window(self):
        """Show shop and marketplace window"""
        ui = self._ui
        shop_window = self._styled_toplevel("🛒 Shop & Marketplace", 750, 650)
        
        # Header
        self._styled_header(shop_window, "Shop & Marketplace", "Buy items and upgrades", icon="🛒")
        
        # Current balance card
        balance_outer, balance_card = self._styled_card(shop_window, "Balance")
        balance_outer.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        balance_text = f"SP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}"
        balance_label = tk.Label(balance_card, text=balance_text, bg=ui["bg_card"], fg=ui["gold"],
                                font=ui["font_body_bold"])
        balance_label.pack(pady=5)
        
        # Shop items card
        items_outer, items_card = self._styled_card(shop_window, "Available Items & Upgrades (Click Buy)")
        items_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Create scrollable frame
        scroll_outer, scrollable_frame = self._styled_scrollable(items_card, ui["bg_card"])
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        # Initialize shop inventory if not exists
        if "shop_purchases" not in self.equipment_inventory:
            self.equipment_inventory["shop_purchases"] = []
        
        shop_items = [
            ("luck_potion", "🔮 Luck Potion", "SP", 50, "Boost luck by 20% for 10 rolls"),
            ("speed_potion", "⚡ Speed Potion", "SP+", 10, "Speed up auto-roll by 50% for 5 min"),
            ("strength_potion", "💪 Strength Potion", "SPx", 5, "Double damage for 3 rolls"),
            ("xp_booster", "🌟 XP Booster", "SP^", 2, "Gain 2x XP from next 5 wins"),
            ("sp_converter", "💰 SP Converter", "SP", 100, "Convert 100 SP to 10 SP+"),
            ("premium_unlock", "⭐ Premium Equipment", "SP+", 50, "Unlock premium crafting"),
        ]
        
        def buy_item(item_id, cost_type, cost_amount, label_text):
            if cost_type == "SP" and self.sp < cost_amount:
                self._show_popup_error("Insufficient Funds", f"Need {cost_amount} SP (have {self.sp})")
                return
            elif cost_type == "SP+" and self.sp_plus < cost_amount:
                self._show_popup_error("Insufficient Funds", f"Need {cost_amount} SP+ (have {self.sp_plus})")
                return
            elif cost_type == "SPx" and self.sp_x < cost_amount:
                self._show_popup_error("Insufficient Funds", f"Need {cost_amount} SPx (have {self.sp_x})")
                return
            elif cost_type == "SP^" and self.sp_caret < cost_amount:
                self._show_popup_error("Insufficient Funds", f"Need {cost_amount} SP^ (have {self.sp_caret})")
                return
            
            if cost_type == "SP":
                self.sp -= cost_amount
            elif cost_type == "SP+":
                self.sp_plus -= cost_amount
            elif cost_type == "SPx":
                self.sp_x -= cost_amount
            elif cost_type == "SP^":
                self.sp_caret -= cost_amount
            
            # Track purchase
            if item_id not in self.equipment_inventory["shop_purchases"]:
                self.equipment_inventory["shop_purchases"].append(item_id)
            
            self._update_sp_label()
            balance_label.config(text=f"SP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}")
            
            self._show_popup_info("Purchase Successful", f"Purchased {label_text}!")
            self.save_game()
        
        def use_item(item_id, label_text):
            # Handle item usage - apply effects based on item type
            if item_id == "luck_potion":
                self._show_popup_info("Item Used", "Luck Potion activated! You now have 20% luck boost for your next 10 rolls.")
            elif item_id == "speed_potion":
                self._show_popup_info("Item Used", "Speed Potion activated! Auto-roll speed increased by 50% for 5 minutes.")
            elif item_id == "strength_potion":
                self._show_popup_info("Item Used", "Strength Potion activated! Your damage is doubled for the next 3 rolls.")
            elif item_id == "xp_booster":
                self._show_popup_info("Item Used", "XP Booster activated! You will gain 2x XP from your next 5 wins.")
            elif item_id == "sp_converter":
                if self.sp >= 100:
                    self.sp -= 100
                    self.sp_plus += 10
                    self._update_sp_label()
                    balance_label.config(text=f"SP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}")
                    self._show_popup_info("Conversion Complete", "Converted 100 SP to 10 SP+")
                    self.save_game()
                else:
                    self._show_popup_error("Insufficient SP", f"Need 100 SP (have {self.sp})")
                    return
            elif item_id == "premium_unlock":
                self._show_popup_info("Item Used", "Premium Equipment unlocked! You can now craft exclusive gear.")
            
            if item_id != "sp_converter":  # sp_converter handles its own save
                self.save_game()
        
        for item_id, label, cost_type, cost_amount, desc in shop_items:
            btn_frame = tk.Frame(scrollable_frame, bg=ui["bg_card"])
            btn_frame.pack(fill=tk.X, padx=5, pady=3)
            
            item_label = tk.Label(btn_frame, text=f"{label}", bg=ui["bg_card"], fg=ui["success"],
                                 font=ui["font_body"], width=30, anchor="w")
            item_label.pack(side=tk.LEFT, padx=5)
            
            desc_label = tk.Label(btn_frame, text=f"{desc}", bg=ui["bg_card"], fg=ui["text_secondary"],
                                 font=ui["font_small"], width=25, anchor="w")
            desc_label.pack(side=tk.LEFT, padx=3)
            
            cost_label = tk.Label(btn_frame, text=f"{cost_type}: {cost_amount}", bg=ui["bg_card"], fg=ui["gold"],
                                 font=ui["font_small_bold"], width=12, anchor="e")
            cost_label.pack(side=tk.LEFT, padx=3)
            
            # Check if item is already purchased
            is_purchased = item_id in self.equipment_inventory["shop_purchases"]
            
            if is_purchased:
                use_btn = self._styled_button(btn_frame, "Use",
                                   command=lambda iid=item_id, l=label: use_item(iid, l),
                                   style="success", width=5, small=True)
                use_btn.pack(side=tk.LEFT, padx=3)
            else:
                buy_btn = self._styled_button(btn_frame, "Buy",
                                   command=lambda iid=item_id, ct=cost_type, ca=cost_amount, l=label: buy_item(iid, ct, ca, l),
                                   style="primary", width=5, small=True)
                buy_btn.pack(side=tk.LEFT, padx=3)
    
    def show_tournament_window(self):
        """Show the playable tournaments hub with real gameplay modes."""
        ui = self._ui
        tw = self._styled_toplevel("⚔️ Tournaments", width=820, height=680)
        self._styled_header(tw, "Tournaments", "Real competitive challenges with SP prizes", icon="⚔️")

        # Ensure tournament_data has the right shape
        if "scores" not in self.tournament_data:
            self.tournament_data["scores"] = {}

        notebook = ttk.Notebook(tw, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ── Helper: personal best for a mode ─────────────────────────
        def _pb(mode):
            return self.tournament_data.get("scores", {}).get(mode, {}).get("best", None)

        # ── TAB 1 — Speed Trial ──────────────────────────────────────
        speed_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(speed_tab, text="  ⚡ Speed Trial  ")

        speed_card = tk.Frame(speed_tab, bg=ui["bg_card"], padx=20, pady=16)
        speed_card.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(speed_card, text="⚡ SPEED TRIAL", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["warning"]).pack(anchor="w")
        tk.Label(speed_card, text="Match a random target in as FEW rolls as possible.\n"
                 "Difficulty increases each attempt. Lower roll count = better score.",
                 font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_secondary"],
                 justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        pb = _pb("speed")
        pb_text = f"🏆 Personal best: {pb} rolls" if pb is not None else "🏆 No attempts yet"
        tk.Label(speed_card, text=pb_text, font=ui["font_body_bold"],
                 bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(8, 0))
        tk.Label(speed_card, text="Prizes:  🥇 <5 rolls → 500 SP  |  🥈 <10 → 200 SP  |  🥉 <20 → 50 SP",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["sp_color"]).pack(anchor="w", pady=(4, 0))
        self._styled_button(speed_card, "▶ START SPEED TRIAL",
                            lambda: self._tournament_speed_trial(tw),
                            style="warning", width=22).pack(anchor="w", pady=(12, 0))

        # ── TAB 2 — Survival Gauntlet ────────────────────────────────
        surv_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(surv_tab, text="  🛡️ Survival  ")

        surv_card = tk.Frame(surv_tab, bg=ui["bg_card"], padx=20, pady=16)
        surv_card.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(surv_card, text="🛡️ SURVIVAL GAUNTLET", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["success"]).pack(anchor="w")
        tk.Label(surv_card, text="Win consecutive rounds — each harder than the last.\n"
                 "You get a roll budget per round. Fail to match = elimination.\n"
                 "Score = rounds survived.",
                 font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_secondary"],
                 justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        pb2 = _pb("survival")
        pb2_text = f"🏆 Personal best: {pb2} rounds" if pb2 is not None else "🏆 No attempts yet"
        tk.Label(surv_card, text=pb2_text, font=ui["font_body_bold"],
                 bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(8, 0))
        tk.Label(surv_card, text="Prizes:  10+ rounds → 1000 SP  |  5+ → 300 SP  |  3+ → 100 SP",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["sp_color"]).pack(anchor="w", pady=(4, 0))
        self._styled_button(surv_card, "▶ START SURVIVAL GAUNTLET",
                            lambda: self._tournament_survival(tw),
                            style="success", width=22).pack(anchor="w", pady=(12, 0))

        # ── TAB 3 — Property Blitz ───────────────────────────────────
        blitz_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(blitz_tab, text="  🔥 Blitz  ")

        blitz_card = tk.Frame(blitz_tab, bg=ui["bg_card"], padx=20, pady=16)
        blitz_card.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(blitz_card, text="🔥 PROPERTY BLITZ", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["danger"]).pack(anchor="w")
        tk.Label(blitz_card, text="60-second timed challenge! Roll as fast as you can.\n"
                 "Each winning match earns points based on difficulty.\n"
                 "Score = total points when the clock hits zero.",
                 font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_secondary"],
                 justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        pb3 = _pb("blitz")
        pb3_text = f"🏆 Personal best: {pb3} pts" if pb3 is not None else "🏆 No attempts yet"
        tk.Label(blitz_card, text=pb3_text, font=ui["font_body_bold"],
                 bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w", pady=(8, 0))
        tk.Label(blitz_card, text="Prizes:  50+ pts → 800 SP  |  25+ → 300 SP  |  10+ → 100 SP",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["sp_color"]).pack(anchor="w", pady=(4, 0))
        self._styled_button(blitz_card, "▶ START BLITZ",
                            lambda: self._tournament_blitz(tw),
                            style="danger", width=22).pack(anchor="w", pady=(12, 0))

        # ── TAB 4 — Leaderboard ──────────────────────────────────────
        lb_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(lb_tab, text="  🏆 Leaderboard  ")

        lb_nb = ttk.Notebook(lb_tab, style="Modern.TNotebook")
        lb_nb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for mode_label, mode_key, unit, lower_better in [
            ("⚡ Speed", "speed", "rolls", True),
            ("🛡️ Survival", "survival", "rounds", False),
            ("🔥 Blitz", "blitz", "pts", False),
        ]:
            mf = tk.Frame(lb_nb, bg=ui["bg_primary"])
            lb_nb.add(mf, text=f"  {mode_label}  ")
            scroll_o, scroll_i = self._styled_scrollable(mf, bg=ui["bg_secondary"])
            scroll_o.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            entries = []
            for username in self.account_manager.accounts:
                if username.startswith("Guest_"):
                    continue
                t_file = f"user_{username}_tournament.json"
                try:
                    if os.path.exists(t_file):
                        with open(t_file, "r") as f:
                            td = json.load(f)
                        best = td.get("scores", {}).get(mode_key, {}).get("best")
                        if best is not None:
                            entries.append({"name": username, "score": best})
                except Exception:
                    pass
            # Also include current user from memory
            my_best = _pb(mode_key)
            if my_best is not None:
                existing = [e for e in entries if e["name"] == self.current_username]
                if not existing:
                    entries.append({"name": self.current_username, "score": my_best})
                else:
                    existing[0]["score"] = my_best

            entries.sort(key=lambda x: x["score"], reverse=not lower_better)
            medals = ["🥇", "🥈", "🥉"]
            if not entries:
                tk.Label(scroll_i, text="No scores yet — be the first!",
                         font=ui["font_body"], bg=ui["bg_secondary"], fg=ui["warning"]).pack(pady=20)
            else:
                for idx, e in enumerate(entries[:30], 1):
                    med = medals[idx - 1] if idx <= 3 else f"{idx}."
                    is_me = e["name"] == self.current_username
                    rbg = ui["bg_card"] if is_me else ui["bg_secondary"]
                    fc = ui["gold"] if is_me else ui["text_primary"]
                    row = tk.Frame(scroll_i, bg=rbg)
                    row.pack(fill=tk.X, padx=4, pady=1)
                    tk.Label(row, text=f" {med}", font=ui["font_body_bold"], bg=rbg,
                             fg=fc, width=4, anchor="w").pack(side=tk.LEFT, padx=(4, 0))
                    t_name_font = ("Segoe UI", 13, "bold") if e["name"] == "DeMarcusThe2nd" else ui["font_body_bold"]
                    tk.Label(row, text=e["name"], font=t_name_font, bg=rbg,
                             fg=fc, width=16, anchor="w").pack(side=tk.LEFT, padx=(4, 0))
                    tk.Label(row, text=f'{e["score"]} {unit}', font=ui["font_mono_sm"], bg=rbg,
                             fg=ui["accent_light"]).pack(side=tk.RIGHT, padx=(0, 10))

        # ── TAB 5 — My Results ───────────────────────────────────────
        my_tab = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(my_tab, text="  📊 My Results  ")

        scores = self.tournament_data.get("scores", {})
        history = self.tournament_data.get("history", [])

        my_card = tk.Frame(my_tab, bg=ui["bg_card"], padx=20, pady=14)
        my_card.pack(fill=tk.X, padx=15, pady=(15, 8))
        tk.Label(my_card, text="📊 Your Tournament Stats", font=ui["font_heading"],
                 bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w")
        for mode, icon, unit in [("speed", "⚡", "rolls"), ("survival", "🛡️", "rounds"), ("blitz", "🔥", "pts")]:
            ms = scores.get(mode, {})
            best = ms.get("best", "—")
            plays = ms.get("plays", 0)
            tk.Label(my_card, text=f"  {icon} {mode.title():12s} Best: {best} {unit}   |   Played: {plays}x",
                     font=ui["font_mono_sm"], bg=ui["bg_card"], fg=ui["text_primary"]).pack(anchor="w", pady=1)

        # Recent history
        if history:
            tk.Label(my_tab, text="Recent Attempts:", font=ui["font_subhead"],
                     bg=ui["bg_primary"], fg=ui["text_primary"]).pack(anchor="w", padx=18, pady=(10, 4))
            hist_outer, hist_inner = self._styled_scrollable(my_tab, bg=ui["bg_secondary"])
            hist_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
            for h in reversed(history[-30:]):
                hf = tk.Frame(hist_inner, bg=ui["bg_card"], padx=10, pady=4)
                hf.pack(fill=tk.X, pady=1)
                tk.Label(hf, text=h.get("mode", "?").title(), font=ui["font_small_bold"],
                         bg=ui["bg_card"], fg=ui["info"], width=10, anchor="w").pack(side=tk.LEFT)
                tk.Label(hf, text=f'Score: {h.get("score", 0)}', font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_primary"]).pack(side=tk.LEFT, padx=8)
                sp_r = h.get("sp_reward", 0)
                if sp_r > 0:
                    tk.Label(hf, text=f'+{sp_r} SP', font=ui["font_small_bold"],
                             bg=ui["bg_card"], fg=ui["sp_color"]).pack(side=tk.RIGHT, padx=4)
                tk.Label(hf, text=h.get("date", ""), font=ui["font_mono_sm"],
                         bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.RIGHT, padx=4)
        else:
            tk.Label(my_tab, text="No tournament attempts yet. Play one above!",
                     font=ui["font_body"], bg=ui["bg_primary"], fg=ui["text_muted"]).pack(pady=30)

    # ── Tournament: save helpers ─────────────────────────────────────

    def _load_user_tournament_scores(self):
        """Load tournament scores/history from user-specific file."""
        if self.current_username:
            t_file = f"user_{self.current_username}_tournament.json"
            try:
                if os.path.exists(t_file):
                    with open(t_file, "r") as f:
                        data = json.load(f)
                    self.tournament_data["scores"] = data.get("scores", {})
                    self.tournament_data["history"] = data.get("history", [])
                    return
            except Exception:
                pass
        if "scores" not in self.tournament_data:
            self.tournament_data["scores"] = {}
        if "history" not in self.tournament_data:
            self.tournament_data["history"] = []

    def _tournament_record_score(self, mode, score, sp_reward):
        """Persist a tournament score and award SP."""
        if "scores" not in self.tournament_data:
            self.tournament_data["scores"] = {}
        if "history" not in self.tournament_data:
            self.tournament_data["history"] = []

        ms = self.tournament_data["scores"].setdefault(mode, {"best": None, "plays": 0})
        ms["plays"] += 1

        is_pb = False
        if mode == "speed":
            if ms["best"] is None or score < ms["best"]:
                ms["best"] = score
                is_pb = True
        else:
            if ms["best"] is None or score > ms["best"]:
                ms["best"] = score
                is_pb = True

        self.tournament_data["history"].append({
            "mode": mode, "score": score, "sp_reward": sp_reward,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "is_pb": is_pb,
        })
        # Keep history bounded
        self.tournament_data["history"] = self.tournament_data["history"][-100:]

        # Save to user-specific file for the leaderboard
        if self.current_username:
            t_file = f"user_{self.current_username}_tournament.json"
            try:
                with open(t_file, "w") as f:
                    json.dump({"scores": self.tournament_data["scores"],
                               "history": self.tournament_data["history"]}, f, indent=2)
            except Exception:
                pass

        # Award SP
        if sp_reward > 0:
            self.sp += sp_reward
            self._update_sp_label()
        return is_pb

    # ── Tournament: Speed Trial ──────────────────────────────────────

    def _tournament_speed_trial(self, parent_win):
        """Playable speed trial — match the target in as few rolls as possible."""
        ui = self._ui
        parent_win.destroy()
        win = self._styled_toplevel("⚡ Speed Trial", 750, 560)

        # Generate a medium-hard target (3 properties)
        all_props = list(self.possible_properties)
        random.shuffle(all_props)
        target = set(all_props[:3])

        state = {"rolls": 0, "finished": False}

        def _on_close():
            state["finished"] = True
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

        self._styled_header(win, "Speed Trial", "Match the target in as few rolls as possible!", icon="⚡")

        # Target display
        tgt_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=10)
        tgt_frame.pack(fill=tk.X, padx=15, pady=(5, 8))
        tk.Label(tgt_frame, text="🎯 TARGET PROPERTIES:", font=ui["font_subhead"],
                 bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w")
        tgt_str = "  •  ".join(self._property_name_display(p) for p in sorted(target))
        tk.Label(tgt_frame, text=tgt_str, font=ui["font_body_bold"],
                 bg=ui["bg_card"], fg=ui["text_primary"]).pack(anchor="w", pady=(4, 0))
        tk.Label(tgt_frame, text="⚠️ Roll must have EXACTLY these properties — no more, no less!",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["warning"]).pack(anchor="w", pady=(4, 0))

        # Stats bar
        stats_bar = tk.Frame(win, bg=ui["bg_secondary"], padx=14, pady=8)
        stats_bar.pack(fill=tk.X, padx=15, pady=(0, 8))
        roll_count_lbl = tk.Label(stats_bar, text="Rolls: 0", font=("Segoe UI", 18, "bold"),
                                  bg=ui["bg_secondary"], fg=ui["warning"])
        roll_count_lbl.pack(side=tk.LEFT)
        match_lbl = tk.Label(stats_bar, text="Matches: 0/3", font=ui["font_body_bold"],
                             bg=ui["bg_secondary"], fg=ui["text_secondary"])
        match_lbl.pack(side=tk.RIGHT)

        # Roll display
        roll_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=10)
        roll_frame.pack(fill=tk.X, padx=15, pady=(0, 4))
        roll_str_lbl = tk.Label(roll_frame, text="Press ROLL to begin…",
                                font=("Consolas", 13), bg=ui["bg_card"],
                                fg=ui["text_primary"], wraplength=680, justify=tk.LEFT, anchor="w")
        roll_str_lbl.pack(fill=tk.X)
        roll_props_lbl = tk.Label(roll_frame, text="", font=ui["font_small"],
                                  bg=ui["bg_card"], fg=ui["text_muted"], anchor="w", justify=tk.LEFT)
        roll_props_lbl.pack(fill=tk.X, pady=(4, 0))

        result_lbl = tk.Label(win, text="", font=ui["font_heading"],
                              bg=ui["bg_primary"], fg=ui["success"])
        result_lbl.pack(pady=4)

        def _roll():
            if state["finished"]:
                return
            state["rolls"] += 1
            s = self._generate_random_string()
            props = self._analyze_string(s)
            matches = props & target
            extras = props - target
            roll_count_lbl.config(text=f"Rolls: {state['rolls']}")
            extra_str = f"  (+{len(extras)} extra)" if extras else ""
            match_lbl.config(text=f"Matches: {len(matches)}/{len(target)}{extra_str}")
            roll_str_lbl.config(text=s[:80])
            props_display = ", ".join(self._property_name_display(p) for p in sorted(props))
            roll_props_lbl.config(text=f"Properties: {props_display}")

            if props == target:
                state["finished"] = True
                roll_btn.config(state=tk.DISABLED)
                # Calculate reward
                rolls = state["rolls"]
                if rolls <= 5:
                    sp_r = 500
                elif rolls <= 10:
                    sp_r = 200
                elif rolls <= 20:
                    sp_r = 50
                else:
                    sp_r = 10
                is_pb = self._tournament_record_score("speed", rolls, sp_r)
                pb_str = " 🏆 NEW PERSONAL BEST!" if is_pb else ""
                result_lbl.config(
                    text=f"🎉 MATCHED in {rolls} rolls! +{sp_r} SP{pb_str}",
                    fg=ui["success"])
                back_btn.pack(side=tk.LEFT, padx=6)

        btn_row = tk.Frame(win, bg=ui["bg_primary"])
        btn_row.pack(fill=tk.X, padx=15, pady=(8, 12))
        roll_btn = self._styled_button(btn_row, "🎲 ROLL", _roll, style="warning", width=14)
        roll_btn.pack(side=tk.LEFT, padx=4)
        back_btn = self._styled_button(btn_row, "🏠 Back to Tournaments",
                                       lambda: (win.destroy(), self.show_tournament_window()),
                                       style="primary", width=20)
        # back_btn shown after finish
        def _speed_quit():
            if not state["finished"] and state["rolls"] > 0:
                state["finished"] = True
                roll_btn.config(state=tk.DISABLED)
                self._tournament_record_score("speed", state["rolls"], 0)
                result_lbl.config(text=f"🚪 Quit after {state['rolls']} rolls (no prize)", fg=ui["text_muted"])
                back_btn.pack(side=tk.LEFT, padx=6)
            else:
                win.destroy()
        quit_btn = self._styled_button(btn_row, "🚪 Quit", _speed_quit,
                            style="neutral", width=8)
        quit_btn.pack(side=tk.RIGHT, padx=4)
        win.bind("<space>", lambda e: _roll())

    # ── Tournament: Survival Gauntlet ────────────────────────────────

    def _tournament_survival(self, parent_win):
        """Playable survival — win consecutive rounds with limited rolls each."""
        ui = self._ui
        parent_win.destroy()
        win = self._styled_toplevel("🛡️ Survival Gauntlet", 750, 600)

        state = {
            "round_num": 1, "score": 0, "rolls_left": 15,
            "target": set(), "finished": False, "total_wins": 0,
        }

        def _on_close():
            state["finished"] = True
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

        def _new_round():
            """Generate the next round target — harder each round."""
            rnd = state["round_num"]
            n_props = min(2 + (rnd - 1) // 3, 5)  # 2 → 3 → 4 → 5
            budget = max(5, 18 - rnd)               # 17, 16, 15, ... min 5
            all_p = list(self.possible_properties)
            random.shuffle(all_p)
            state["target"] = set(all_p[:n_props])
            state["rolls_left"] = budget

        _new_round()

        self._styled_header(win, "Survival Gauntlet", "Win consecutive rounds to earn big rewards!", icon="🛡️")

        # Info bar
        info_bar = tk.Frame(win, bg=ui["bg_secondary"], padx=14, pady=8)
        info_bar.pack(fill=tk.X, padx=15, pady=(5, 8))
        round_lbl = tk.Label(info_bar, text=f"Round 1", font=("Segoe UI", 18, "bold"),
                             bg=ui["bg_secondary"], fg=ui["success"])
        round_lbl.pack(side=tk.LEFT)
        rolls_left_lbl = tk.Label(info_bar, text=f"Rolls left: {state['rolls_left']}",
                                  font=ui["font_body_bold"], bg=ui["bg_secondary"], fg=ui["warning"])
        rolls_left_lbl.pack(side=tk.RIGHT)
        wins_lbl = tk.Label(info_bar, text="Rounds won: 0", font=ui["font_body_bold"],
                            bg=ui["bg_secondary"], fg=ui["gold"])
        wins_lbl.pack(side=tk.RIGHT, padx=20)

        # Target
        tgt_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=8)
        tgt_frame.pack(fill=tk.X, padx=15, pady=(0, 6))
        tgt_label = tk.Label(tgt_frame, text="", font=ui["font_body_bold"],
                             bg=ui["bg_card"], fg=ui["accent_light"], anchor="w", justify=tk.LEFT)
        tgt_label.pack(fill=tk.X)
        tk.Label(tgt_frame, text="⚠️ Exact match only — no extra properties!",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["warning"]).pack(anchor="w")

        def _update_target_display():
            tgt_str = "🎯 Target:  " + "  •  ".join(
                self._property_name_display(p) for p in sorted(state["target"]))
            tgt_label.config(text=tgt_str)
            rolls_left_lbl.config(text=f"Rolls left: {state['rolls_left']}")
            round_lbl.config(text=f"Round {state['round_num']}")
            wins_lbl.config(text=f"Rounds won: {state['total_wins']}")

        _update_target_display()

        # Roll display
        roll_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=10)
        roll_frame.pack(fill=tk.X, padx=15, pady=(0, 4))
        roll_str_lbl = tk.Label(roll_frame, text="Press ROLL to start round 1…",
                                font=("Consolas", 13), bg=ui["bg_card"],
                                fg=ui["text_primary"], wraplength=680, justify=tk.LEFT, anchor="w")
        roll_str_lbl.pack(fill=tk.X)
        roll_props_lbl = tk.Label(roll_frame, text="", font=ui["font_small"],
                                  bg=ui["bg_card"], fg=ui["text_muted"], anchor="w")
        roll_props_lbl.pack(fill=tk.X, pady=(4, 0))
        match_lbl = tk.Label(roll_frame, text="", font=ui["font_body_bold"],
                             bg=ui["bg_card"], fg=ui["text_secondary"])
        match_lbl.pack(anchor="w", pady=(2, 0))

        result_lbl = tk.Label(win, text="", font=ui["font_heading"],
                              bg=ui["bg_primary"], fg=ui["success"])
        result_lbl.pack(pady=4)

        def _finish(reason):
            state["finished"] = True
            roll_btn.config(state=tk.DISABLED)
            giveup_btn.config(state=tk.DISABLED)
            rounds_won = state["total_wins"]
            if rounds_won >= 10:
                sp_r = 1000
            elif rounds_won >= 5:
                sp_r = 300
            elif rounds_won >= 3:
                sp_r = 100
            else:
                sp_r = max(10, rounds_won * 15)
            is_pb = self._tournament_record_score("survival", rounds_won, sp_r)
            pb_str = " 🏆 NEW PERSONAL BEST!" if is_pb else ""
            result_lbl.config(
                text=f"{reason}\nSurvived {rounds_won} rounds! +{sp_r} SP{pb_str}",
                fg=ui["danger"] if "Eliminated" in reason else ui["success"])
            back_btn.pack(side=tk.LEFT, padx=6)

        def _roll():
            if state["finished"]:
                return
            state["rolls_left"] -= 1
            s = self._generate_random_string()
            props = self._analyze_string(s)
            matches = props & state["target"]
            extras = props - state["target"]
            roll_str_lbl.config(text=s[:80])
            props_display = ", ".join(self._property_name_display(p) for p in sorted(props))
            roll_props_lbl.config(text=f"Properties: {props_display}")
            extra_str = f"  (+{len(extras)} extra)" if extras else ""
            match_lbl.config(text=f"Matches: {len(matches)}/{len(state['target'])}{extra_str}")
            rolls_left_lbl.config(text=f"Rolls left: {state['rolls_left']}")

            if props == state["target"]:
                # Won this round
                state["total_wins"] += 1
                state["round_num"] += 1
                _new_round()
                _update_target_display()
                roll_str_lbl.config(text=f"✅ Round won! New target generated. Keep going!")
                roll_props_lbl.config(text="")
                match_lbl.config(text="")
                result_lbl.config(text=f"✅ Round {state['round_num'] - 1} cleared!", fg=ui["success"])
            elif state["rolls_left"] <= 0:
                _finish("💀 Eliminated — ran out of rolls!")

        btn_row = tk.Frame(win, bg=ui["bg_primary"])
        btn_row.pack(fill=tk.X, padx=15, pady=(8, 12))
        roll_btn = self._styled_button(btn_row, "🎲 ROLL", _roll, style="success", width=14)
        roll_btn.pack(side=tk.LEFT, padx=4)
        back_btn = self._styled_button(btn_row, "🏠 Back to Tournaments",
                                       lambda: (win.destroy(), self.show_tournament_window()),
                                       style="primary", width=20)
        giveup_btn = self._styled_button(btn_row, "🏳️ Give Up",
                            lambda: _finish("🏳️ You surrendered!") if not state["finished"] else None,
                            style="neutral", width=10)
        giveup_btn.pack(side=tk.RIGHT, padx=4)
        win.bind("<space>", lambda e: _roll())

    # ── Tournament: Property Blitz ───────────────────────────────────

    def _tournament_blitz(self, parent_win):
        """Playable blitz — 60-second timed challenge, score as many points as possible."""
        ui = self._ui
        parent_win.destroy()
        win = self._styled_toplevel("🔥 Property Blitz", 750, 580)

        state = {
            "time_left": 60, "points": 0, "wins": 0, "rolls": 0,
            "target": set(), "finished": False, "timer_id": None,
        }

        def _on_close():
            state["finished"] = True
            if state["timer_id"]:
                try:
                    win.after_cancel(state["timer_id"])
                except Exception:
                    pass
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

        def _new_target():
            n = random.randint(2, 4)
            all_p = list(self.possible_properties)
            random.shuffle(all_p)
            state["target"] = set(all_p[:n])

        _new_target()

        self._styled_header(win, "Property Blitz", "60 seconds — GO GO GO!", icon="🔥")

        # Timer + score bar
        timer_bar = tk.Frame(win, bg=ui["bg_secondary"], padx=14, pady=8)
        timer_bar.pack(fill=tk.X, padx=15, pady=(5, 8))
        timer_lbl = tk.Label(timer_bar, text="⏱ 60s", font=("Segoe UI", 22, "bold"),
                             bg=ui["bg_secondary"], fg=ui["danger"])
        timer_lbl.pack(side=tk.LEFT)
        points_lbl = tk.Label(timer_bar, text="Points: 0", font=("Segoe UI", 18, "bold"),
                              bg=ui["bg_secondary"], fg=ui["gold"])
        points_lbl.pack(side=tk.RIGHT)
        wins_lbl = tk.Label(timer_bar, text="Wins: 0  |  Rolls: 0", font=ui["font_body_bold"],
                            bg=ui["bg_secondary"], fg=ui["text_secondary"])
        wins_lbl.pack(side=tk.RIGHT, padx=20)

        # Target
        tgt_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=8)
        tgt_frame.pack(fill=tk.X, padx=15, pady=(0, 6))
        tgt_label = tk.Label(tgt_frame, text="", font=ui["font_body_bold"],
                             bg=ui["bg_card"], fg=ui["accent_light"], anchor="w")
        tgt_label.pack(fill=tk.X)
        tk.Label(tgt_frame, text="⚠️ Exact match only — no extra properties!",
                 font=ui["font_small"], bg=ui["bg_card"], fg=ui["warning"]).pack(anchor="w")

        def _update_target_display():
            tgt_str = "🎯 Target (" + str(len(state["target"])) + " props):  " + \
                      "  •  ".join(self._property_name_display(p) for p in sorted(state["target"]))
            tgt_label.config(text=tgt_str)

        _update_target_display()

        # Roll display
        roll_frame = tk.Frame(win, bg=ui["bg_card"], padx=14, pady=10)
        roll_frame.pack(fill=tk.X, padx=15, pady=(0, 4))
        roll_str_lbl = tk.Label(roll_frame, text="Press ROLL or [Space] — clock starts on first roll!",
                                font=("Consolas", 13), bg=ui["bg_card"],
                                fg=ui["text_primary"], wraplength=680, justify=tk.LEFT, anchor="w")
        roll_str_lbl.pack(fill=tk.X)
        roll_props_lbl = tk.Label(roll_frame, text="", font=ui["font_small"],
                                  bg=ui["bg_card"], fg=ui["text_muted"], anchor="w")
        roll_props_lbl.pack(fill=tk.X, pady=(4, 0))
        match_lbl = tk.Label(roll_frame, text="", font=ui["font_body_bold"],
                             bg=ui["bg_card"], fg=ui["text_secondary"])
        match_lbl.pack(anchor="w")

        result_lbl = tk.Label(win, text="", font=ui["font_heading"],
                              bg=ui["bg_primary"], fg=ui["success"])
        result_lbl.pack(pady=4)

        def _tick():
            if state["finished"]:
                return
            state["time_left"] -= 1
            t = state["time_left"]
            color = ui["danger"] if t <= 10 else ui["warning"] if t <= 30 else ui["success"]
            timer_lbl.config(text=f"⏱ {t}s", fg=color)
            if t <= 0:
                _finish()
            else:
                state["timer_id"] = win.after(1000, _tick)

        started = {"v": False}

        def _finish():
            if state["finished"]:
                return
            state["finished"] = True
            roll_btn.config(state=tk.DISABLED)
            if state["timer_id"]:
                win.after_cancel(state["timer_id"])
            pts = state["points"]
            if pts >= 50:
                sp_r = 800
            elif pts >= 25:
                sp_r = 300
            elif pts >= 10:
                sp_r = 100
            else:
                sp_r = max(5, pts * 3)
            is_pb = self._tournament_record_score("blitz", pts, sp_r)
            pb_str = " 🏆 NEW PERSONAL BEST!" if is_pb else ""
            result_lbl.config(
                text=f"⏱ TIME'S UP!  {pts} points in {state['rolls']} rolls ({state['wins']} wins). +{sp_r} SP{pb_str}",
                fg=ui["gold"])
            timer_lbl.config(text="⏱ 0s", fg=ui["danger"])
            back_btn.pack(side=tk.LEFT, padx=6)

        def _roll():
            if state["finished"]:
                return
            if not started["v"]:
                started["v"] = True
                state["timer_id"] = win.after(1000, _tick)
            state["rolls"] += 1
            s = self._generate_random_string()
            props = self._analyze_string(s)
            matches = props & state["target"]
            extras = props - state["target"]
            roll_str_lbl.config(text=s[:80])
            props_display = ", ".join(self._property_name_display(p) for p in sorted(props))
            roll_props_lbl.config(text=f"Properties: {props_display}")
            extra_str = f"  (+{len(extras)} extra)" if extras else ""
            match_lbl.config(text=f"Matches: {len(matches)}/{len(state['target'])}{extra_str}")
            wins_lbl.config(text=f"Wins: {state['wins']}  |  Rolls: {state['rolls']}")

            if props == state["target"]:
                pts = len(state["target"]) * 3   # more props = more pts
                state["points"] += pts
                state["wins"] += 1
                points_lbl.config(text=f"Points: {state['points']}")
                _new_target()
                _update_target_display()
                match_lbl.config(text=f"✅ +{pts} pts! New target!")

        btn_row = tk.Frame(win, bg=ui["bg_primary"])
        btn_row.pack(fill=tk.X, padx=15, pady=(8, 12))
        roll_btn = self._styled_button(btn_row, "🎲 ROLL", _roll, style="danger", width=14)
        roll_btn.pack(side=tk.LEFT, padx=4)
        back_btn = self._styled_button(btn_row, "🏠 Back to Tournaments",
                                       lambda: (win.destroy(), self.show_tournament_window()),
                                       style="primary", width=20)
        def _blitz_quit():
            if not state["finished"]:
                _finish()
            win.destroy()
        self._styled_button(btn_row, "🚪 Quit", _blitz_quit,
                            style="neutral", width=8).pack(side=tk.RIGHT, padx=4)
        win.bind("<space>", lambda e: _roll())

    def show_game_mode_window(self):
        """Show game modes window"""
        ui = self._ui
        mode_window = self._styled_toplevel("Game Modes", width=700, height=600)
        self._styled_header(mode_window, title="Game Modes", subtitle="Choose your playstyle", icon="🎮")
        
        # Current mode display
        current_mode_label = tk.Label(mode_window, text=f"Currently: {self.current_game_mode}", 
                                     bg=ui["bg_primary"], fg=ui["warning"], font=ui["font_subhead"])
        current_mode_label.pack(pady=(10, 5))
        
        # Modes list with select buttons
        section_label = tk.Label(mode_window, text="Available Modes (Click Select)", bg=ui["bg_primary"],
                                fg=ui["success"], font=ui["font_body_bold"])
        section_label.pack(anchor="w", padx=15, pady=(5, 2))
        
        sep = tk.Frame(mode_window, bg=ui["border"], height=1)
        sep.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        scroll_outer, modes_list_frame = self._styled_scrollable(mode_window, bg=ui["bg_card"])
        scroll_outer.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        game_modes = [
            ("Classic", "The original Questionmark", True, ""),
            ("Speed Run", "Fast-paced with shorter lists", self.wins_count >= 50, "50 wins to unlock"),
            ("Hardcore", "Single life, double XP reward", self.wins_count >= 100, "100 wins to unlock"),
            ("Chaos", "Random everything! (April Fools)", self.is_april_fools, "April 1st only"),
            ("Midnight", "Play between 12 AM - 6 AM", True, "Time-based availability"),
            ("Tournament", "Ranked competitive mode", True, "See Tournaments"),
        ]
        
        def select_mode(mode_name):
            if mode_name == "Speed Run" and self.wins_count < 50:
                self._show_popup_error("Locked", "Unlock Speed Run Mode with 50 wins!")
                return
            elif mode_name == "Hardcore" and self.wins_count < 100:
                self._show_popup_error("Locked", "Unlock Hardcore Mode with 100 wins!")
                return
            elif mode_name == "Chaos" and not self.is_april_fools:
                self._show_popup_error("Seasonal", "Chaos Mode is only available on April 1st!")
                return
            
            self.current_game_mode = mode_name
            
            if mode_name == "Speed Run":
                self.difficulty = "hard"
            elif mode_name == "Hardcore":
                self.difficulty = "hard"
            else:
                self.difficulty = "normal"
            
            self._show_popup_info("Success", f"Switched to {mode_name} Mode!")
            current_mode_label.config(text=f"Currently: {self.current_game_mode}")
        
        for mode_name, desc, unlocked, note in game_modes:
            mode_frame = tk.Frame(modes_list_frame, bg=ui["bg_card"], bd=1, relief=tk.FLAT,
                                 highlightbackground=ui["border"], highlightthickness=1)
            mode_frame.pack(fill=tk.X, padx=8, pady=4)
            
            title = tk.Label(mode_frame, text=mode_name, bg=ui["bg_card"], fg=ui["success"], 
                           font=ui["font_body_bold"], width=15, anchor="w")
            title.pack(side=tk.LEFT, padx=10, pady=8)
            
            info_text = desc
            if note:
                info_text += f" ({note})"
            
            info = tk.Label(mode_frame, text=info_text, bg=ui["bg_card"], fg=ui["text_secondary"], 
                          font=ui["font_small"], anchor="w")
            info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            is_current = mode_name == self.current_game_mode
            if is_current:
                select_btn = self._styled_button(mode_frame, text="✓ Active",
                                                command=lambda m=mode_name: select_mode(m),
                                                style="neutral", width=10, small=True)
            else:
                select_btn = self._styled_button(mode_frame, text="Select",
                                                command=lambda m=mode_name: select_mode(m),
                                                style="success", width=10, small=True)
            select_btn.pack(side=tk.RIGHT, padx=10, pady=6)
            if not unlocked:
                select_btn.config(state=tk.DISABLED)
    
    def show_strategy_window(self):
        """Show strategy configuration window with talents, effects, and strategies"""
        ui = self._ui
        strategy_win = self._styled_toplevel("Strategy Panel", width=800, height=700)
        
        # Header
        self._styled_header(strategy_win, title="Strategy Configuration", subtitle="Talents, effects, and roll strategies", icon="🎯")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(strategy_win, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== TALENT TREE TAB =====
        talent_frame = tk.Frame(notebook, bg=ui["bg_card"])
        notebook.add(talent_frame, text="📚 Talent Tree")
        
        talent_outer, talent_scrollable = self._styled_scrollable(talent_frame, bg=ui["bg_card"])
        talent_outer.pack(fill=tk.BOTH, expand=True)
        
        for branch_name, branch_data in self.talent_tree.items():
            branch_frame = tk.LabelFrame(talent_scrollable, text=f"{branch_data['name']} (Lv. {branch_data['current_level']}/3)", 
                                        bg=ui["bg_card"], fg=ui["accent_light"], font=ui["font_body_bold"])
            branch_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Current level description
            if branch_data['current_level'] > 0:
                current = branch_data['levels'][branch_data['current_level'] - 1]
                info_text = f"✓ {current['desc']}"
                tk.Label(branch_frame, text=info_text, bg=ui["bg_card"], fg=ui["success"], 
                        font=ui["font_small"]).pack(anchor="w", padx=10, pady=5)
            
            # Next level button
            if branch_data['current_level'] < len(branch_data['levels']):
                next_level = branch_data['levels'][branch_data['current_level']]
                cost = next_level['cost']
                
                button_text = f"Upgrade → Lv.{next_level['level']}: {next_level['desc']} (Cost: {cost} SP)"
                
                def upgrade_talent(bn=branch_name, cost=cost):
                    success, msg = self.unlock_talent(bn)
                    self._show_popup_info("Talent Update", msg)
                    if success:
                        strategy_win.destroy()
                        self.show_strategy_window()  # Refresh
                
                if self.sp >= cost:
                    btn = self._styled_button(branch_frame, text=button_text, command=upgrade_talent, style="success", width=0, small=True)
                else:
                    btn = self._styled_button(branch_frame, text=button_text, command=upgrade_talent, style="danger", width=0, small=True)
                    btn.config(state=tk.DISABLED)
                btn.pack(fill=tk.X, padx=10, pady=5)
            else:
                tk.Label(branch_frame, text="✓ MAXED", bg=ui["bg_card"], fg=ui["info"], 
                        font=ui["font_small_bold"]).pack(anchor="w", padx=10, pady=5)
        
        # ===== ROLL STRATEGIES TAB =====
        strategy_frame = tk.Frame(notebook, bg=ui["bg_card"])
        notebook.add(strategy_frame, text="⚔️ Roll Strategies")
        
        strat_outer, strategy_scrollable = self._styled_scrollable(strategy_frame, bg=ui["bg_card"])
        strat_outer.pack(fill=tk.BOTH, expand=True)
        
        for strat_name, strat_data in self.roll_strategies.items():
            is_active = strat_name == self.current_roll_strategy
            strat_frame = tk.LabelFrame(strategy_scrollable, 
                                       text=f"{'✓' if is_active else '◯'} {strat_data['name']}", 
                                       bg=ui["bg_card"], fg=ui["gold"] if is_active else ui["text_secondary"], 
                                       font=ui["font_body_bold"])
            strat_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Description
            tk.Label(strat_frame, text=strat_data['desc'], bg=ui["bg_card"], fg=ui["text_secondary"], 
                    font=ui["font_small"]).pack(anchor="w", padx=10, pady=2)
            
            # Stats
            stats_text = f"SP Multiplier: {strat_data['sp_multiplier']:.1f}x  |  Difficulty: {strat_data['difficulty'].upper()}  |  Win Bonus: +{strat_data['win_bonus']} SP"
            tk.Label(strat_frame, text=stats_text, bg=ui["bg_card"], fg=ui["success"], 
                    font=ui["font_small_bold"]).pack(anchor="w", padx=10, pady=2)
            
            # Cost
            if strat_data['cost'] > 0:
                cost_text = f"Cost: {strat_data['cost']} SP per roll"
                tk.Label(strat_frame, text=cost_text, bg=ui["bg_card"], fg=ui["warning"], 
                        font=ui["font_small"]).pack(anchor="w", padx=10, pady=2)
            
            # Select button
            def select_strategy(sn=strat_name):
                success, msg = self.set_roll_strategy(sn)
                self._show_popup_info("Strategy", msg)
                if success:
                    strategy_win.destroy()
                    self.show_strategy_window()
            
            if is_active:
                btn = self._styled_button(strat_frame, text="✓ ACTIVE", command=select_strategy, style="neutral", width=0, small=True)
            else:
                btn = self._styled_button(strat_frame, text="SELECT", command=select_strategy, style="success", width=0, small=True)
            btn.pack(fill=tk.X, padx=10, pady=5)
        
        # ===== ACTIVE EFFECTS TAB =====
        effects_frame = tk.Frame(notebook, bg=ui["bg_card"])
        notebook.add(effects_frame, text="✨ Active Effects")
        
        effects_outer, effects_scrollable = self._styled_scrollable(effects_frame, bg=ui["bg_card"])
        effects_outer.pack(fill=tk.BOTH, expand=True)
        
        for effect_name, effect_data in self.active_effects.items():
            effect_frame = tk.LabelFrame(effects_scrollable, 
                                        text=f"{'✓' if effect_data['enabled'] else '◯'} {effect_data['name']}", 
                                        bg=ui["bg_card"], fg=ui["gold"] if effect_data['enabled'] else ui["text_secondary"], 
                                        font=ui["font_body_bold"])
            effect_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Description
            tk.Label(effect_frame, text=effect_data['desc'], bg=ui["bg_card"], fg=ui["text_secondary"], 
                    font=ui["font_small"]).pack(anchor="w", padx=10, pady=2)
            
            # Toggle button
            def toggle_effect(en=effect_name):
                success, msg = self.toggle_active_effect(en)
                self._show_popup_info("Effect", msg)
                if success:
                    strategy_win.destroy()
                    self.show_strategy_window()
            
            if effect_data['enabled']:
                btn = self._styled_button(effect_frame, text="✓ ACTIVE", command=toggle_effect, style="neutral", width=0, small=True)
            else:
                btn = self._styled_button(effect_frame, text="ACTIVATE", command=toggle_effect, style="success", width=0, small=True)
            btn.pack(fill=tk.X, padx=10, pady=5)
        
        # ===== SUMMARY TAB =====
        summary_frame = tk.Frame(notebook, bg=ui["bg_card"])
        notebook.add(summary_frame, text="📊 Summary")
        
        summary_text = tk.Text(summary_frame, bg=ui["bg_input"], fg=ui["success"], font=ui["font_mono"], 
                              height=20, width=80)
        summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get current setup info
        bonuses = self.get_talent_bonuses()
        current_strat = self.roll_strategies[self.current_roll_strategy]
        active_count = sum(1 for e in self.active_effects.values() if e['enabled'])
        
        summary_info = f"""
╔════════════════════════════════════════╗
║       STRATEGY SETUP SUMMARY           ║
╚════════════════════════════════════════╝

CURRENT ROLL STRATEGY:
  {current_strat['name']}
  SP Multiplier: {current_strat['sp_multiplier']:.1f}x
  Difficulty: {current_strat['difficulty'].upper()}
  Win Bonus: +{current_strat['win_bonus']} SP
  Cost per roll: {current_strat['cost']} SP

TALENT TREE BONUSES:
  • Overall SP Multiplier: {bonuses['sp_multiplier']:.1%}
  • Property Detection: +{bonuses['property_detection']:.1%}
  • Luck Bonus: +{bonuses['luck_bonus']:.1%}
  • Streak Bonus: {bonuses['streak_bonus']:.1%}

ACTIVE EFFECTS: {active_count}/4
"""
        for effect_name, effect_data in self.active_effects.items():
            if effect_data['enabled']:
                summary_info += f"  ✓ {effect_data['name']}\n"
        
        summary_info += f"""
CURRENT RESOURCES:
  • SP: {self.sp}
  • SP+: {self.sp_plus}
  • SPx: {self.sp_x}
  • SP^: {self.sp_caret}

═══════════════════════════════════════
STRATEGY TIPS:
• Precision mastery improves property detection
• Efficiency increases SP gains
• Fortune helps with match chances
• Streak specialist multiplies consecutive wins
• Strategies affect both SP and difficulty
• Active effects cost SP per session
═══════════════════════════════════════
"""
        summary_text.insert(1.0, summary_info)
        summary_text.config(state=tk.DISABLED)
    
    def show_analytics_window(self):
        """Show analytics window"""
        ui = self._ui
        analytics_window = self._styled_toplevel("Analytics", width=700, height=600)
        
        # Header
        self._styled_header(analytics_window, title="Player Analytics", subtitle="Stats, achievements, and progression", icon="📊")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(analytics_window, style="Modern.TNotebook")
        notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Stats Overview Tab
        stats_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(stats_frame, text="Overview")
        
        stats_text = scrolledtext.ScrolledText(stats_frame, height=20, width=80, bg=ui["bg_input"], fg=ui["info"], 
                                              font=ui["font_mono_sm"])
        stats_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        win_rate = (self.wins_count / self.roll_count * 100) if self.roll_count > 0 else 0
        avg_rolls = (self.roll_count / self.wins_count) if self.wins_count > 0 else 0
        
        stats_info = f"""
╔══════════════════════════════════════════════════════════╗
║                    PLAYER STATISTICS                      ║
╚══════════════════════════════════════════════════════════╝

📈 CORE STATS:
   Total Rolls:        {self.roll_count}
   Total Wins:         {self.wins_count}
   Win Rate:           {win_rate:.2f}%
   Avg Rolls/Win:      {avg_rolls:.2f}
   Fastest Win:        {self.stats.get('fastest_win', 'N/A')} rolls
   Current Level:      {self.player_level}
   Current XP:         {self.player_xp}/{self.xp_to_level_up}

🔥 SESSION STATS:
   Session Wins:       {self.session_win_count}
   Current Streak:     {self.winning_streak}
   Max Streak:         {self.max_winning_streak}
   SP Earned Today:    {self.total_sp_earned_today}

💎 EQUIPMENT:
   Regular SP:         {self.sp}
   SP+ (10 chars):     {self.sp_plus}
   SPx (20 chars):     {self.sp_x}
   SP^ (40+ chars):    {self.sp_caret}
"""
        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)
        
        # Achievements Tab
        ach_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(ach_frame, text="Achievements")
        
        ach_text = scrolledtext.ScrolledText(ach_frame, height=20, width=80, bg=ui["bg_input"], fg=ui["gold"], 
                                            font=ui["font_mono_sm"])
        ach_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        achievements_info = "🏆 ACHIEVEMENTS UNLOCKED:\n\n"
        unlocked_count = 0
        for ach_id, ach_data in self.achievements.items():
            if ach_data.get("unlocked", False):
                achievements_info += f"  ✓ {ach_data.get('name', ach_id)}\n    {ach_data.get('desc', '')}\n\n"
                unlocked_count += 1
        
        achievements_info += f"\n\nTotal: {unlocked_count}/{len(self.achievements)} achievements"
        ach_text.insert(tk.END, achievements_info)
        ach_text.config(state=tk.DISABLED)
        
        # Progression Tab
        prog_frame = tk.Frame(notebook, bg=ui["bg_primary"])
        notebook.add(prog_frame, text="Progression")
        
        prog_text = scrolledtext.ScrolledText(prog_frame, height=20, width=80, bg=ui["bg_input"], fg=ui["success"], 
                                             font=ui["font_mono_sm"])
        prog_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        progression_info = f"""
PROGRESSION MILESTONES:

Level {self.player_level}: {self._get_player_title_for_wins(self.wins_count)}

Next Level: {self.xp_to_level_up - self.player_xp} XP remaining

UNLOCK MILESTONES:
  ✓ Auto-Roll Unlocked (500 rolls)
  {'✓' if self.wins_count >= 50 else '✗'} Speed Run Mode (50 wins)
  {'✓' if self.wins_count >= 100 else '✗'} Hardcore Mode (100 wins)
  {'✓' if self.wins_count >= 25 else '✗'} Premium Equipment (25 wins)

DISCOVERY STATS:
  Properties Discovered: {len(self.stats.get('property_discoveries', {}))} / 15
"""
        prog_text.insert(tk.END, progression_info)
        prog_text.config(state=tk.DISABLED)
    
    # ===== CRAFTING BENCH WINDOW =====
    
    def show_crafting_bench(self):
        """Show the advanced crafting bench window"""
        ui = self._ui
        craft_win = self._styled_toplevel("🔨 Advanced Crafting Bench", 880, 740)
        self._styled_header(craft_win, "Advanced Crafting Bench",
                            "Discover property combos from wins → Forge powerful gear", icon="🔨")
        
        # ── Top stats bar ──
        stats_outer, stats_card = self._styled_card(craft_win, "Crafting Stats")
        stats_outer.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        xp_needed = self.crafting_level * 50
        discovered = len(self.discovered_combos)
        total_recipes = len(self.crafting_recipes)
        crafted_count = len(self.crafted_items)
        
        stats_row = tk.Frame(stats_card, bg=ui["bg_card"])
        stats_row.pack(fill=tk.X)
        
        for label_text, value_text, color in [
            ("Crafting Level", str(self.crafting_level), ui["accent_light"]),
            ("XP", f"{self.crafting_xp}/{xp_needed}", ui["xp_color"]),
            ("Discovered", f"{discovered}/{total_recipes}", ui["info"]),
            ("Crafted", f"{crafted_count}/{total_recipes}", ui["success"]),
            ("SP", f"{self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}", ui["sp_color"]),
        ]:
            pill = tk.Frame(stats_row, bg=ui["bg_secondary"], padx=10, pady=6)
            pill.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            tk.Label(pill, text=label_text, font=ui["font_small"], bg=ui["bg_secondary"],
                     fg=ui["text_muted"]).pack()
            tk.Label(pill, text=value_text, font=ui["font_body_bold"], bg=ui["bg_secondary"],
                     fg=color).pack()
        
        # ── Filter buttons ──
        filter_frame = tk.Frame(craft_win, bg=ui["bg_primary"])
        filter_frame.pack(fill=tk.X, padx=15, pady=5)
        
        current_filter = [0]  # 0=All, 1-5=tier
        
        def refresh_recipes():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            tier_filter = current_filter[0]
            for item_id, recipe in sorted(self.crafting_recipes.items(), key=lambda x: (x[1]["tier"], x[1]["name"])):
                if tier_filter > 0 and recipe["tier"] != tier_filter:
                    continue
                
                tier_info = self.crafting_tiers[recipe["tier"]]
                is_discovered = recipe["combo"] in self.discovered_combos
                is_crafted = item_id in self.crafted_items
                can_craft = is_discovered and not is_crafted and self.crafting_level >= recipe["crafting_level"]
                
                # Recipe card
                card_bg = ui["bg_card"] if not is_crafted else "#1a2a1a"
                row = tk.Frame(scrollable_frame, bg=card_bg, pady=8, padx=12)
                row.pack(fill=tk.X, padx=5, pady=3)
                
                # Left: icon + name
                left = tk.Frame(row, bg=card_bg)
                left.pack(side=tk.LEFT, fill=tk.Y)
                
                name_color = tier_info["color"] if is_discovered else ui["text_muted"]
                tk.Label(left, text=f"{tier_info['icon']} {recipe['name']}", font=ui["font_body_bold"],
                         bg=card_bg, fg=name_color, anchor="w").pack(anchor="w")
                
                tier_text = f"Tier {recipe['tier']}: {tier_info['name']} • {recipe['type'].capitalize()}"
                if is_crafted:
                    tier_text += " • ✅ CRAFTED"
                tk.Label(left, text=tier_text, font=ui["font_small"],
                         bg=card_bg, fg=tier_info["color"], anchor="w").pack(anchor="w")
                
                # Combo display
                if is_discovered:
                    combo_text = " + ".join(sorted(recipe["combo"]))
                    combo_color = ui["success"]
                    combo_prefix = "🔓 "
                else:
                    combo_text = " + ".join(["???" for _ in recipe["combo"]])
                    combo_color = ui["text_muted"]
                    combo_prefix = "🔒 "
                tk.Label(left, text=f"{combo_prefix}{combo_text}", font=ui["font_small"],
                         bg=card_bg, fg=combo_color, anchor="w").pack(anchor="w")
                
                tk.Label(left, text=recipe["desc"], font=ui["font_small"],
                         bg=card_bg, fg=ui["text_secondary"], anchor="w").pack(anchor="w")
                
                # Right: cost + craft button
                right = tk.Frame(row, bg=card_bg)
                right.pack(side=tk.RIGHT, fill=tk.Y)
                
                cost_parts = []
                cost = recipe["cost"]
                if cost.get("sp", 0): cost_parts.append(f"{cost['sp']} SP")
                if cost.get("sp_plus", 0): cost_parts.append(f"{cost['sp_plus']} SP+")
                if cost.get("sp_x", 0): cost_parts.append(f"{cost['sp_x']} SPx")
                if cost.get("sp_caret", 0): cost_parts.append(f"{cost['sp_caret']} SP^")
                cost_text = " • ".join(cost_parts)
                
                tk.Label(right, text=cost_text, font=ui["font_small"],
                         bg=card_bg, fg=ui["gold"], anchor="e").pack(anchor="e")
                
                if recipe["crafting_level"] > self.crafting_level:
                    tk.Label(right, text=f"Req. Level {recipe['crafting_level']}", font=ui["font_small"],
                             bg=card_bg, fg=ui["danger"], anchor="e").pack(anchor="e")
                
                if is_crafted:
                    tk.Label(right, text="✅ Owned", font=ui["font_small_bold"],
                             bg=card_bg, fg=ui["success"], anchor="e").pack(anchor="e", pady=2)
                elif can_craft:
                    def do_craft(iid=item_id):
                        success, msg = self._craft_item(iid)
                        if success:
                            messagebox.showinfo("🔨 Crafted!", msg)
                        else:
                            self._show_popup_error("Cannot Craft", msg)
                        refresh_recipes()
                    
                    craft_btn = self._styled_button(right, "🔨 Craft", do_craft,
                                                    style="gold", width=8, small=True)
                    craft_btn.pack(anchor="e", pady=2)
                elif is_discovered:
                    tk.Label(right, text="Insufficient", font=ui["font_small"],
                             bg=card_bg, fg=ui["danger"], anchor="e").pack(anchor="e", pady=2)
                else:
                    tk.Label(right, text="🔒 Locked", font=ui["font_small"],
                             bg=card_bg, fg=ui["text_muted"], anchor="e").pack(anchor="e", pady=2)
                
                # Separator
                sep = tk.Frame(scrollable_frame, bg=ui["border"], height=1)
                sep.pack(fill=tk.X, padx=10)
        
        def set_filter(t):
            current_filter[0] = t
            for b in filter_btns:
                b.config(bg=ui["bg_secondary"], fg=ui["text_secondary"])
            filter_btns[t].config(bg=ui["accent"], fg="#ffffff")
            refresh_recipes()
        
        filter_labels = ["All", "⚪ Common", "🟢 Uncommon", "🔵 Rare", "🟣 Epic", "🟠 Legendary"]
        filter_btns = []
        for i, label in enumerate(filter_labels):
            btn = tk.Label(filter_frame, text=label, font=ui["font_small_bold"],
                           bg=ui["bg_secondary"] if i != 0 else ui["accent"],
                           fg=ui["text_secondary"] if i != 0 else "#ffffff",
                           padx=12, pady=4, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, idx=i: set_filter(idx))
            filter_btns.append(btn)
        
        # ── Scrollable recipe list ──
        recipe_outer, recipe_card = self._styled_card(craft_win, "Recipes")
        recipe_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        scroll_outer, scrollable_frame = self._styled_scrollable(recipe_card, ui["bg_card"])
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        refresh_recipes()
    
    # ===== CLANS WINDOW =====
    
    def show_clans_window(self):
        """Show the Clans / Guilds window"""
        ui = self._ui
        clan_win = self._styled_toplevel("🏰 Clans & Guilds", 880, 740)
        self._styled_header(clan_win, "Clans & Guilds",
                            "Join forces, earn shared perks, dominate the leaderboard", icon="🏰")
        
        # Tab system
        tab_frame = tk.Frame(clan_win, bg=ui["bg_secondary"])
        tab_frame.pack(fill=tk.X)
        
        content_frame = tk.Frame(clan_win, bg=ui["bg_primary"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        current_tab = [0]
        
        def clear_content():
            for w in content_frame.winfo_children():
                w.destroy()
        
        def show_my_clan():
            clear_content()
            current_tab[0] = 0
            update_tab_styles()
            
            if not self.player_clan:
                # Not in a clan — show create/join options
                no_clan_outer, no_clan_card = self._styled_card(content_frame, "You're not in a clan yet")
                no_clan_outer.pack(fill=tk.X, padx=15, pady=15)
                
                tk.Label(no_clan_card, text="Join a clan to earn shared perks and compete on the clan leaderboard!",
                         font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_secondary"],
                         wraplength=600).pack(pady=10)
                
                # Create clan
                create_frame = tk.Frame(no_clan_card, bg=ui["bg_card"])
                create_frame.pack(fill=tk.X, pady=10)
                tk.Label(create_frame, text="Create a New Clan:", font=ui["font_subhead"],
                         bg=ui["bg_card"], fg=ui["accent_light"]).pack(anchor="w")
                
                name_row = tk.Frame(create_frame, bg=ui["bg_card"])
                name_row.pack(fill=tk.X, pady=5)
                name_entry = tk.Entry(name_row, font=ui["font_body"], bg=ui["bg_secondary"],
                                      fg=ui["text_primary"], insertbackground=ui["text_primary"],
                                      relief=tk.FLAT, width=25)
                name_entry.pack(side=tk.LEFT, padx=(0, 10))
                name_entry.insert(0, "Enter clan name...")
                name_entry.bind("<FocusIn>", lambda e: name_entry.delete(0, tk.END) if name_entry.get() == "Enter clan name..." else None)
                
                def do_create():
                    success, msg = self._create_clan(name_entry.get())
                    if success:
                        messagebox.showinfo("🏰 Clan Created!", msg)
                        show_my_clan()
                    else:
                        self._show_popup_error("Error", msg)
                
                self._styled_button(name_row, "Create", do_create, style="success", width=8).pack(side=tk.LEFT)
                
                # Browse button
                tk.Label(no_clan_card, text="— or —", font=ui["font_body"],
                         bg=ui["bg_card"], fg=ui["text_muted"]).pack(pady=5)
                self._styled_button(no_clan_card, "Browse Clans", show_browse_clans,
                                    style="primary", width=16).pack(pady=5)
                return
            
            # Show current clan info
            clan = self.clans_data.get("clans", {}).get(self.player_clan, {})
            level, xp_cur, xp_max = self._get_clan_level(self.player_clan)
            members = clan.get("members", [])
            contributions = clan.get("contributions", {})
            
            # Clan header
            info_outer, info_card = self._styled_card(content_frame, f"🏰 {self.player_clan}")
            info_outer.pack(fill=tk.X, padx=15, pady=(10, 5))
            
            stats_row = tk.Frame(info_card, bg=ui["bg_card"])
            stats_row.pack(fill=tk.X)
            
            for label_text, value_text, color in [
                ("Level", str(level), ui["accent_light"]),
                ("XP", f"{xp_cur}/{xp_max}", ui["xp_color"]),
                ("Members", f"{len(members)}/20", ui["info"]),
                ("Total Wins", str(clan.get("total_wins", 0)), ui["success"]),
                ("Leader", clan.get("leader", "?"), ui["gold"]),
            ]:
                pill = tk.Frame(stats_row, bg=ui["bg_secondary"], padx=10, pady=6)
                pill.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
                tk.Label(pill, text=label_text, font=ui["font_small"], bg=ui["bg_secondary"],
                         fg=ui["text_muted"]).pack()
                tk.Label(pill, text=value_text, font=ui["font_body_bold"], bg=ui["bg_secondary"],
                         fg=color).pack()
            
            # XP progress bar
            bar_frame = tk.Frame(info_card, bg=ui["bg_secondary"], height=12)
            bar_frame.pack(fill=tk.X, padx=5, pady=(8, 5))
            bar_frame.pack_propagate(False)
            pct = xp_cur / max(1, xp_max)
            fill = tk.Frame(bar_frame, bg=ui["xp_color"], width=int(pct * 600))
            fill.place(x=0, y=0, relheight=1.0)
            
            # Motto
            motto = clan.get("motto", "No motto set")
            tk.Label(info_card, text=f'"{motto}"', font=("Segoe UI", 10, "italic"),
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(pady=5)
            
            # Members list
            members_outer, members_card = self._styled_card(content_frame, "Members & Contributions")
            members_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
            
            scroll_out, scroll_inner = self._styled_scrollable(members_card, ui["bg_card"])
            scroll_out.pack(fill=tk.BOTH, expand=True)
            
            sorted_members = sorted(members, key=lambda m: contributions.get(m, 0), reverse=True)
            for i, member in enumerate(sorted_members):
                mf = tk.Frame(scroll_inner, bg=ui["bg_card"], pady=4)
                mf.pack(fill=tk.X, padx=5)
                rank = "👑" if member == clan.get("leader") else f"#{i+1}"
                contrib = contributions.get(member, 0)
                is_you = " (You)" if member == self.current_username else ""
                tk.Label(mf, text=f"{rank}  {member}{is_you}", font=ui["font_body"],
                         bg=ui["bg_card"], fg=ui["text_primary"], anchor="w").pack(side=tk.LEFT)
                tk.Label(mf, text=f"{contrib} XP contributed", font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["xp_color"], anchor="e").pack(side=tk.RIGHT)
            
            # Leave button
            btn_frame = tk.Frame(content_frame, bg=ui["bg_primary"])
            btn_frame.pack(fill=tk.X, padx=15, pady=10)
            
            def do_leave():
                if messagebox.askyesno("Leave Clan", f"Leave '{self.player_clan}'?"):
                    success, msg = self._leave_clan()
                    if success:
                        messagebox.showinfo("Left", msg)
                        show_my_clan()
                    else:
                        self._show_popup_error("Error", msg)
            
            self._styled_button(btn_frame, "Leave Clan", do_leave, style="danger", width=12).pack(side=tk.RIGHT)
        
        def show_browse_clans():
            clear_content()
            current_tab[0] = 1
            update_tab_styles()
            
            browse_outer, browse_card = self._styled_card(content_frame, "Available Clans")
            browse_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            scroll_out, scroll_inner = self._styled_scrollable(browse_card, ui["bg_card"])
            scroll_out.pack(fill=tk.BOTH, expand=True)
            
            clans = self.clans_data.get("clans", {})
            if not clans:
                tk.Label(scroll_inner, text="No clans exist yet. Be the first to create one!",
                         font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_muted"]).pack(pady=20)
                return
            
            sorted_clans = sorted(clans.items(), key=lambda x: x[1].get("total_xp", 0), reverse=True)
            for clan_name, clan_info in sorted_clans:
                level, _, _ = self._get_clan_level(clan_name)
                members_count = len(clan_info.get("members", []))
                
                cf = tk.Frame(scroll_inner, bg=ui["bg_card"], pady=8, padx=10)
                cf.pack(fill=tk.X, padx=5, pady=3)
                
                left = tk.Frame(cf, bg=ui["bg_card"])
                left.pack(side=tk.LEFT, fill=tk.Y)
                
                tk.Label(left, text=f"🏰 {clan_name}", font=ui["font_body_bold"],
                         bg=ui["bg_card"], fg=ui["accent_light"], anchor="w").pack(anchor="w")
                tk.Label(left, text=f"Level {level} • {members_count}/20 members • {clan_info.get('total_wins', 0)} wins",
                         font=ui["font_small"], bg=ui["bg_card"], fg=ui["text_secondary"]).pack(anchor="w")
                tk.Label(left, text=f'Leader: {clan_info.get("leader", "?")}',
                         font=ui["font_small"], bg=ui["bg_card"], fg=ui["gold"]).pack(anchor="w")
                
                right = tk.Frame(cf, bg=ui["bg_card"])
                right.pack(side=tk.RIGHT, fill=tk.Y)
                
                if self.player_clan == clan_name:
                    tk.Label(right, text="✅ Your Clan", font=ui["font_small_bold"],
                             bg=ui["bg_card"], fg=ui["success"]).pack(anchor="e", pady=5)
                elif not self.player_clan and members_count < 20:
                    def do_join(cn=clan_name):
                        success, msg = self._join_clan(cn)
                        if success:
                            messagebox.showinfo("🏰 Joined!", msg)
                            show_my_clan()
                        else:
                            self._show_popup_error("Error", msg)
                    self._styled_button(right, "Join", do_join, style="success", width=6, small=True).pack(anchor="e", pady=5)
                elif members_count >= 20:
                    tk.Label(right, text="FULL", font=ui["font_small_bold"],
                             bg=ui["bg_card"], fg=ui["danger"]).pack(anchor="e", pady=5)
                
                sep = tk.Frame(scroll_inner, bg=ui["border"], height=1)
                sep.pack(fill=tk.X, padx=10)
        
        def show_clan_leaderboard():
            clear_content()
            current_tab[0] = 2
            update_tab_styles()
            
            lb_outer, lb_card = self._styled_card(content_frame, "🏆 Clan Leaderboard")
            lb_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            scroll_out, scroll_inner = self._styled_scrollable(lb_card, ui["bg_card"])
            scroll_out.pack(fill=tk.BOTH, expand=True)
            
            clans = self.clans_data.get("clans", {})
            sorted_clans = sorted(clans.items(), key=lambda x: x[1].get("total_xp", 0), reverse=True)
            
            medals = ["🥇", "🥈", "🥉"]
            for i, (clan_name, clan_info) in enumerate(sorted_clans):
                level, _, _ = self._get_clan_level(clan_name)
                medal = medals[i] if i < 3 else f"#{i+1}"
                is_mine = " ⭐" if clan_name == self.player_clan else ""
                
                row_bg = "#1a1a3a" if clan_name == self.player_clan else ui["bg_card"]
                rf = tk.Frame(scroll_inner, bg=row_bg, pady=6, padx=10)
                rf.pack(fill=tk.X, padx=5, pady=2)
                
                tk.Label(rf, text=f"{medal}  🏰 {clan_name}{is_mine}", font=ui["font_body_bold"],
                         bg=row_bg, fg=ui["text_primary"], anchor="w").pack(side=tk.LEFT)
                
                stats_text = f"Lv.{level} • {clan_info.get('total_xp', 0)} XP • {clan_info.get('total_wins', 0)} wins • {len(clan_info.get('members', []))} members"
                tk.Label(rf, text=stats_text, font=ui["font_small"],
                         bg=row_bg, fg=ui["text_secondary"], anchor="e").pack(side=tk.RIGHT)
        
        def show_clan_perks():
            clear_content()
            current_tab[0] = 3
            update_tab_styles()
            
            perks_outer, perks_card = self._styled_card(content_frame, "🎁 Clan Perks")
            perks_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            my_level = 0
            if self.player_clan:
                my_level, _, _ = self._get_clan_level(self.player_clan)
            
            scroll_out, scroll_inner = self._styled_scrollable(perks_card, ui["bg_card"])
            scroll_out.pack(fill=tk.BOTH, expand=True)
            
            for perk_level in sorted(self.clan_perks.keys()):
                perk = self.clan_perks[perk_level]
                unlocked = my_level >= perk_level
                
                pf = tk.Frame(scroll_inner, bg=ui["bg_card"], pady=8, padx=10)
                pf.pack(fill=tk.X, padx=5, pady=3)
                
                icon = "✅" if unlocked else "🔒"
                color = ui["success"] if unlocked else ui["text_muted"]
                
                tk.Label(pf, text=f"{icon}  Level {perk_level}: {perk['name']}", font=ui["font_body_bold"],
                         bg=ui["bg_card"], fg=color, anchor="w").pack(anchor="w")
                tk.Label(pf, text=perk["desc"], font=ui["font_small"],
                         bg=ui["bg_card"], fg=ui["text_secondary"] if unlocked else ui["text_muted"],
                         anchor="w").pack(anchor="w")
                
                sep = tk.Frame(scroll_inner, bg=ui["border"], height=1)
                sep.pack(fill=tk.X, padx=10)
        
        # Tab buttons
        tab_buttons = []
        tab_actions = [show_my_clan, show_browse_clans, show_clan_leaderboard, show_clan_perks]
        tab_labels = ["🏰 My Clan", "🔍 Browse", "🏆 Leaderboard", "🎁 Perks"]
        
        def update_tab_styles():
            for i, btn in enumerate(tab_buttons):
                if i == current_tab[0]:
                    btn.config(bg=ui["accent"], fg="#ffffff")
                else:
                    btn.config(bg=ui["bg_secondary"], fg=ui["text_secondary"])
        
        for i, label in enumerate(tab_labels):
            btn = tk.Label(tab_frame, text=label, font=ui["font_btn_sm"],
                           bg=ui["bg_secondary"], fg=ui["text_secondary"],
                           padx=18, pady=8, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=1)
            btn.bind("<Button-1>", lambda e, action=tab_actions[i]: action())
            tab_buttons.append(btn)
        
        show_my_clan()
    
    # ===== STRING POKÉDEX WINDOW =====
    
    def show_pokedex_window(self):
        """Show the String Pokédex collection window"""
        ui = self._ui
        pdx_win = self._styled_toplevel("📚 String Pokédex", 880, 740)
        self._styled_header(pdx_win, "String Pokédex",
                            "Every winning string collected and catalogued", icon="📚")
        
        # Stats bar
        stats = self._get_pokedex_stats()
        stats_outer, stats_card = self._styled_card(pdx_win, "Collection Stats")
        stats_outer.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        stats_row = tk.Frame(stats_card, bg=ui["bg_card"])
        stats_row.pack(fill=tk.X)
        
        for label_text, value_text, color in [
            ("Total Caught", str(stats["total_caught"]), ui["accent_light"]),
            ("Stored", str(stats["entries_stored"]), ui["info"]),
            ("Unique Combos", f"{stats['unique_combos']}/{stats['total_possible_combos']}", ui["gold"]),
        ]:
            pill = tk.Frame(stats_row, bg=ui["bg_secondary"], padx=10, pady=6)
            pill.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            tk.Label(pill, text=label_text, font=ui["font_small"], bg=ui["bg_secondary"],
                     fg=ui["text_muted"]).pack()
            tk.Label(pill, text=value_text, font=ui["font_body_bold"], bg=ui["bg_secondary"],
                     fg=color).pack()
        
        # Rarity distribution
        rc = stats["rarity_counts"]
        rarity_row = tk.Frame(stats_card, bg=ui["bg_card"])
        rarity_row.pack(fill=tk.X, pady=(5, 0))
        
        rarity_display = [
            ("⬜", "Common", rc.get("Common", 0), "#b0bec5"),
            ("🟩", "Uncommon", rc.get("Uncommon", 0), "#66bb6a"),
            ("🟦", "Rare", rc.get("Rare", 0), "#42a5f5"),
            ("🟪", "Epic", rc.get("Epic", 0), "#ab47bc"),
            ("🟧", "Legendary", rc.get("Legendary", 0), "#ffa726"),
            ("💜", "Mythic", rc.get("Mythic", 0), "#ff4081"),
        ]
        for icon, name, count, color in rarity_display:
            rf = tk.Frame(rarity_row, bg=ui["bg_secondary"], padx=6, pady=3)
            rf.pack(side=tk.LEFT, padx=3)
            tk.Label(rf, text=f"{icon} {count}", font=ui["font_small_bold"],
                     bg=ui["bg_secondary"], fg=color).pack()
        
        # Filter buttons
        filter_frame = tk.Frame(pdx_win, bg=ui["bg_primary"])
        filter_frame.pack(fill=tk.X, padx=15, pady=5)
        
        current_filter = ["All"]
        
        def refresh_entries():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            rarity_filter = current_filter[0]
            entries = list(reversed(self.pokedex_entries))
            
            if rarity_filter != "All":
                entries = [e for e in entries if e.get("rarity") == rarity_filter]
            
            if not entries:
                tk.Label(scrollable_frame, text="No entries found. Win matches to collect strings!",
                         font=ui["font_body"], bg=ui["bg_card"], fg=ui["text_muted"]).pack(pady=20)
                return
            
            for entry in entries[:100]:  # Show last 100
                entry_bg = ui["bg_card"]
                ef = tk.Frame(scrollable_frame, bg=entry_bg, pady=6, padx=12)
                ef.pack(fill=tk.X, padx=5, pady=2)
                
                # Header row: ID + rarity
                top_row = tk.Frame(ef, bg=entry_bg)
                top_row.pack(fill=tk.X)
                
                rarity_color = entry.get("rarity_color", "#b0bec5")
                rarity_icon = entry.get("rarity_icon", "⬜")
                stars = entry.get("stars", "★")
                
                tk.Label(top_row, text=f"#{entry.get('id', '?')}", font=ui["font_body_bold"],
                         bg=entry_bg, fg=ui["text_muted"], anchor="w").pack(side=tk.LEFT)
                tk.Label(top_row, text=f"  {rarity_icon} {entry.get('rarity', 'Common')} {stars}",
                         font=ui["font_small_bold"], bg=entry_bg, fg=rarity_color).pack(side=tk.LEFT, padx=10)
                
                if entry.get("is_new_combo"):
                    tk.Label(top_row, text="🆕 NEW COMBO", font=ui["font_small_bold"],
                             bg=entry_bg, fg=ui["gold"]).pack(side=tk.LEFT, padx=5)
                
                # Timestamp
                ts = entry.get("timestamp", "")[:16].replace("T", " ")
                tk.Label(top_row, text=ts, font=ui["font_small"],
                         bg=entry_bg, fg=ui["text_muted"]).pack(side=tk.RIGHT)
                
                # String display
                display_str = entry.get("string", "")
                if len(display_str) > 80:
                    display_str = display_str[:77] + "..."
                tk.Label(ef, text=f'"{display_str}"', font=ui["font_mono"],
                         bg=entry_bg, fg=rarity_color, anchor="w", wraplength=700).pack(anchor="w", pady=(2, 0))
                
                # Properties
                props = entry.get("properties", [])
                props_text = " • ".join(props)
                tk.Label(ef, text=props_text, font=ui["font_small"],
                         bg=entry_bg, fg=ui["text_secondary"], anchor="w", wraplength=700).pack(anchor="w")
                
                sep = tk.Frame(scrollable_frame, bg=ui["border"], height=1)
                sep.pack(fill=tk.X, padx=10)
        
        def set_filter(f):
            current_filter[0] = f
            for b in filter_btns:
                b.config(bg=ui["bg_secondary"], fg=ui["text_secondary"])
            filter_btns[filter_names.index(f)].config(bg=ui["accent"], fg="#ffffff")
            refresh_entries()
        
        filter_names = ["All", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        filter_icons = ["🔎", "⬜", "🟩", "🟦", "🟪", "🟧", "💜"]
        filter_btns = []
        for i, (name, icon) in enumerate(zip(filter_names, filter_icons)):
            lbl = f"{icon} {name}"
            btn = tk.Label(filter_frame, text=lbl, font=ui["font_small_bold"],
                           bg=ui["accent"] if i == 0 else ui["bg_secondary"],
                           fg="#ffffff" if i == 0 else ui["text_secondary"],
                           padx=10, pady=4, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, n=name: set_filter(n))
            filter_btns.append(btn)
        
        # Scrollable entries
        entries_outer, entries_card = self._styled_card(pdx_win, "Collection")
        entries_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        scroll_outer, scrollable_frame = self._styled_scrollable(entries_card, ui["bg_card"])
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        refresh_entries()
    
    def show_dev_console(self):
        """Show developer console (only for DeMarcusThe2nd)"""
        if self.current_username != "DeMarcusThe2nd":
            self._show_popup_error("Access Denied", "Developer Console is restricted to DeMarcusThe2nd only.")
            return
        
        dev_window = self._styled_toplevel("🔧 Developer Console", 900, 700)
        
        # Header
        self._styled_header(dev_window, "DEVELOPER CONSOLE", subtitle="Terminal access for DeMarcusThe2nd", icon="⚙️")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dev_window, style="Modern.TNotebook")
        notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # ===== COMMANDS TAB =====
        commands_frame = tk.Frame(notebook, bg="#161625")
        notebook.add(commands_frame, text="📖 Commands")
        
        # Commands display with scrollbar
        cmd_canvas = tk.Canvas(commands_frame, bg="#12121f", highlightthickness=0)
        cmd_scrollbar = ttk.Scrollbar(commands_frame, orient="vertical", command=cmd_canvas.yview)
        cmd_scrollable_frame = tk.Frame(cmd_canvas, bg="#12121f")
        
        cmd_scrollable_frame.bind("<Configure>", lambda e: cmd_canvas.configure(scrollregion=cmd_canvas.bbox("all")))
        cmd_canvas.create_window((0, 0), window=cmd_scrollable_frame, anchor="nw")
        cmd_canvas.configure(yscrollcommand=cmd_scrollbar.set)
        
        def _mw_cmd(event):
            try: cmd_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        cmd_canvas.bind("<Enter>", lambda e: cmd_canvas.bind_all("<MouseWheel>", _mw_cmd))
        cmd_canvas.bind("<Leave>", lambda e: (cmd_canvas.unbind_all("<MouseWheel>") if cmd_canvas.winfo_exists() else None))
        cmd_scrollable_frame.bind("<Enter>", lambda e: cmd_canvas.bind_all("<MouseWheel>", _mw_cmd))
        
        commands_list = [
            ("help", "Display all available commands"),
            ("stats", "Show game statistics (wins, rolls, level, XP, SP values)"),
            ("reset", "Reset current game to initial state"),
            ("addsp <n>", "Add N amount of SP (regular currency)"),
            ("addsp+ <n>", "Add N amount of SP+ (10-character currency)"),
            ("addspx <n>", "Add N amount of SPx (20-character currency)"),
            ("addsp^ <n>", "Add N amount of SP^ (40+ character currency)"),
            ("setlevel <n>", "Set player level to N"),
            ("setxp <n>", "Set player XP to N"),
            ("setwin <n>", "Set total wins count to N"),
            ("setroll <n>", "Set total rolls count to N"),
            ("clearach", "Clear all achievements (unlock them all)"),
            ("unlockach <id>", "Unlock specific achievement by ID"),
            ("giveitem <id>", "Add equipment item to inventory"),
            ("clearinv", "Clear all equipment from inventory"),
            ("togglemode <mode>", "Switch to game mode (Classic, Speed Run, Hardcore, etc)"),
            ("listmodes", "List all available game modes"),
            ("saveforce", "Force save all game data immediately"),
            ("time <hh:mm>", "Simulate time (for testing midnight mode)"),
            ("reveal", "Reveal the current target properties"),
            ("addxp <n>", "Add N amount of XP to current total"),
            ("addwins <n>", "Add N wins without rolling"),
            ("addrolls <n>", "Add N to total roll count"),
            ("setelo <n>", "Set PvP ELO rating to N"),
            ("setstreak <n>", "Set current winning streak to N"),
            ("setpvpwins <n>", "Set PvP wins count to N"),
            ("setpvplosses <n>", "Set PvP losses count to N"),
            ("resetpvp", "Reset all PvP stats to defaults"),
            ("unlockachall", "Unlock ALL achievements at once"),
            ("listach", "List all achievements and their unlock status"),
            ("setkarma <n>", "Set karma level to N"),
            ("addluck <n>", "Add N luck tokens"),
            ("whoami", "Show full player profile dump"),
            ("cls", "Clear the console output"),
            ("echo <text>", "Print text to the console"),
            ("tp <n>", "Set target property count for next round to N"),
            ("rename <name>", "Change your display username"),
            ("speed <n>", "Set game animation speed multiplier (1-10)"),
            ("listtournaments", "Show all tournament personal bests"),
            ("setplaytime <h>", "Set total play time in hours"),
            ("exportstats", "Dump full stats JSON to console"),
            ("reload", "Reload all player data from disk files"),
            ("listprops", "List all 15 possible string properties"),
            ("filecheck", "Verify all user data files exist and are valid JSON"),
            ("meminfo", "Show memory usage and object counts"),
            ("eventlog", "Show last 20 game events from this session"),
            ("spectateuser <user>", "Open live read-only spectator view of a player's game"),
            ("startbot [name]", "Start a bot player that simulates real gameplay (default: BotPlayer)"),
            ("stopbot [name]", "Stop a running bot player"),
            ("listbots", "List all currently running bot players"),
        ]
        
        for cmd, desc in commands_list:
            cmd_frame = tk.Frame(cmd_scrollable_frame, bg="#161625", relief=tk.RIDGE, bd=1)
            cmd_frame.pack(fill=tk.X, padx=5, pady=3)
            
            cmd_label = tk.Label(cmd_frame, text=f"$ {cmd}", bg="#161625", fg="#00e676", 
                                font=("Courier New", 10, "bold"), anchor="w", padx=5)
            cmd_label.pack(fill=tk.X)
            
            desc_label = tk.Label(cmd_frame, text=f"  ⤷ {desc}", bg="#161625", fg="#9aa0a6", 
                                 font=("Segoe UI", 9), anchor="w", padx=10)
            desc_label.pack(fill=tk.X, pady=(2, 5))
        
        cmd_canvas.pack(side="left", fill="both", expand=True)
        cmd_scrollbar.pack(side="right", fill="y")
        
        # ===== CONSOLE TAB =====
        console_frame = tk.Frame(notebook, bg="#161625")
        notebook.add(console_frame, text="🖥️ Console")
        
        # Console Output
        console_text = scrolledtext.ScrolledText(console_frame, height=20, width=100, bg="#12121f", fg="#00e676", 
                                                font=("Courier New", 8))
        console_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        console_info = f"""
>>> DEVELOPER CONSOLE ACTIVE
>>> Session User: {self.current_username}
>>> Timestamp: {datetime.datetime.now()}

[DEBUG] Game State:
  - Wins: {self.wins_count}
  - Rolls: {self.roll_count}
  - Level: {self.player_level}
  - XP: {self.player_xp}/{self.xp_to_level_up}
  - SP Values: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}
  
[DEBUG] Game Mode: {self.current_game_mode}
[DEBUG] April Fools Active: {self.is_april_fools}

[SYSTEM] Type 'help' or check the Commands tab for available commands
>>> Ready for input
"""
        console_text.insert(tk.END, console_info)
        console_text.config(state=tk.DISABLED)
        
        # Command input frame
        cmd_input_frame = tk.Frame(console_frame, bg="#0f0f1a")
        cmd_input_frame.pack(padx=10, pady=10, fill=tk.X)
        tk.Label(cmd_input_frame, text=">>> ", bg="#0f0f1a", fg="#00e676", font=("Courier New", 10)).pack(side=tk.LEFT)
        
        cmd_entry = tk.Entry(cmd_input_frame, bg="#12121f", fg="#00e676", font=("Courier New", 10))
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def execute_command():
            cmd = cmd_entry.get().strip().lower()
            if cmd:
                console_text.config(state=tk.NORMAL)
                console_text.insert(tk.END, f"\n>>> {cmd}")
                
                if cmd == "help":
                    help_text = """
[AVAILABLE COMMANDS]
  stats         : Show current game statistics
  reset         : Reset game to initial state
  addsp <n>     : Add SP (regular) - usage: addsp 100
  addsp+ <n>    : Add SP+ (10-char) - usage: addsp+ 50
  addspx <n>    : Add SPx (20-char) - usage: addspx 25
  addsp^ <n>    : Add SP^ (40+-char) - usage: addsp^ 10
  setlevel <n>  : Set player level - usage: setlevel 50
  setxp <n>     : Set player XP - usage: setxp 5000
  setwin <n>    : Set wins count - usage: setwin 100
  setroll <n>   : Set rolls count - usage: setroll 500
  clearach      : Clear/reset all achievements
  unlockach <id>: Unlock specific achievement
  giveitem <id> : Add equipment to inventory
  clearinv      : Clear equipment inventory
  togglemode <m>: Switch game mode - usage: togglemode hardcore
  listmodes     : Show all available game modes
  saveforce     : Force save all game data
  time <hh:mm>  : Simulate time - usage: time 23:59
  reveal        : Reveal current target properties
  addxp <n>     : Add XP - usage: addxp 1000
  addwins <n>   : Add wins - usage: addwins 50
  addrolls <n>  : Add rolls - usage: addrolls 100
  setelo <n>    : Set PvP ELO - usage: setelo 1500
  setstreak <n> : Set win streak - usage: setstreak 20
  setpvpwins <n>: Set PvP wins - usage: setpvpwins 50
  setpvplosses <n>: Set PvP losses - usage: setpvplosses 10
  resetpvp      : Reset all PvP stats to defaults
  unlockachall  : Unlock ALL achievements
  listach       : List achievements & status
  setkarma <n>  : Set karma level - usage: setkarma 100
  addluck <n>   : Add luck tokens - usage: addluck 5
  whoami        : Full player profile dump
  cls / clear   : Clear console output
  echo <text>   : Print text to console
  tp <n>        : Set target property count (1-15)
  rename <name> : Change display username
  speed <n>     : Set animation speed multiplier (1-10)
  listtournaments: Show tournament personal bests
  setplaytime <h>: Set play time in hours
  exportstats   : Dump full stats JSON to console
  reload        : Reload all data from disk
  listprops     : List all 15 possible string properties
  filecheck     : Verify user data files
  meminfo       : Show memory & object counts
  eventlog      : Show last 20 session events
  spectateuser <u>: Open live spectator view of a player's game
  startbot [name]: Start a bot player (default: BotPlayer)
  stopbot [name] : Stop a running bot player
  listbots       : List all running bots

Type 'help' to see this again.
"""
                    console_text.insert(tk.END, help_text)
                elif cmd == "stats":
                    console_text.insert(tk.END, f"\n[STATS] Wins: {self.wins_count} | Rolls: {self.roll_count} | Level: {self.player_level} | XP: {self.player_xp}/{self.xp_to_level_up}\nSP: {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}")
                elif cmd == "reset":
                    console_text.insert(tk.END, "\n[OK] Game reset")
                    self.reset_game()
                elif cmd.startswith("addsp "):
                    try:
                        amount = int(cmd.split()[1])
                        self.sp += amount
                        console_text.insert(tk.END, f"\n[OK] Added {amount} SP. Total: {self.sp}")
                        self._update_sp_label()
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addsp <number>")
                elif cmd.startswith("addsp+ "):
                    try:
                        amount = int(cmd.split()[1])
                        self.sp_plus += amount
                        console_text.insert(tk.END, f"\n[OK] Added {amount} SP+. Total: {self.sp_plus}")
                        self._update_sp_label()
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addsp+ <number>")
                elif cmd.startswith("addspx "):
                    try:
                        amount = int(cmd.split()[1])
                        self.sp_x += amount
                        console_text.insert(tk.END, f"\n[OK] Added {amount} SPx. Total: {self.sp_x}")
                        self._update_sp_label()
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addspx <number>")
                elif cmd.startswith("addsp^ "):
                    try:
                        amount = int(cmd.split()[1])
                        self.sp_caret += amount
                        console_text.insert(tk.END, f"\n[OK] Added {amount} SP^. Total: {self.sp_caret}")
                        self._update_sp_label()
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addsp^ <number>")
                elif cmd.startswith("setlevel "):
                    try:
                        level = int(cmd.split()[1])
                        self.player_level = level
                        console_text.insert(tk.END, f"\n[OK] Level set to {level}")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setlevel <number>")
                elif cmd.startswith("setxp "):
                    try:
                        xp = int(cmd.split()[1])
                        self.player_xp = xp
                        console_text.insert(tk.END, f"\n[OK] XP set to {xp}")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setxp <number>")
                elif cmd.startswith("setwin "):
                    try:
                        wins = int(cmd.split()[1])
                        self.wins_count = wins
                        console_text.insert(tk.END, f"\n[OK] Wins set to {wins}")
                        self.wins_label.config(text=str(self.wins_count))
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setwin <number>")
                elif cmd.startswith("setroll "):
                    try:
                        rolls = int(cmd.split()[1])
                        self.roll_count = rolls
                        console_text.insert(tk.END, f"\n[OK] Rolls set to {rolls}")
                        self.roll_label.config(text=str(self.roll_count))
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setroll <number>")
                elif cmd == "clearach":
                    self.achievements = {k: {**v, "unlocked": False} for k, v in self.achievements.items()}
                    console_text.insert(tk.END, "\n[OK] All achievements cleared")
                elif cmd.startswith("unlockach "):
                    try:
                        ach_id = cmd.split()[1]
                        if ach_id in self.achievements:
                            self.achievements[ach_id]["unlocked"] = True
                            console_text.insert(tk.END, f"\n[OK] Achievement '{ach_id}' unlocked")
                        else:
                            console_text.insert(tk.END, f"\n[ERROR] Achievement '{ach_id}' not found")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: unlockach <achievement_id>")
                elif cmd.startswith("giveitem "):
                    try:
                        item_id = cmd.split()[1]
                        if item_id in self.equipment_recipes:
                            if "owned" not in self.equipment_inventory:
                                self.equipment_inventory["owned"] = []
                            self.equipment_inventory["owned"].append(item_id)
                            console_text.insert(tk.END, f"\n[OK] Item '{item_id}' added to inventory")
                        else:
                            console_text.insert(tk.END, f"\n[ERROR] Item '{item_id}' not found")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: giveitem <item_id>")
                elif cmd == "clearinv":
                    self.equipment_inventory["owned"] = []
                    console_text.insert(tk.END, "\n[OK] Equipment inventory cleared")
                elif cmd.startswith("togglemode "):
                    try:
                        mode = " ".join(cmd.split()[1:]).title()
                        self.current_game_mode = mode
                        console_text.insert(tk.END, f"\n[OK] Switched to {mode} mode")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: togglemode <mode_name>")
                elif cmd == "listmodes":
                    modes = ["Classic", "Speed Run", "Hardcore", "Chaos", "Midnight", "Tournament"]
                    console_text.insert(tk.END, f"\n[MODES] {', '.join(modes)}")
                elif cmd == "saveforce":
                    self._save_stats()
                    self._save_achievements()
                    self._save_equipment()
                    console_text.insert(tk.END, "\n[OK] All data saved forcefully")
                elif cmd.startswith("time "):
                    try:
                        time_str = cmd.split()[1]
                        console_text.insert(tk.END, f"\n[OK] Simulating time: {time_str} (for testing midnight mode)")
                    except:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: time <hh:mm>")
                elif cmd == "reveal":
                    if self.target_properties:
                        props = ", ".join(sorted(self.target_properties))
                        console_text.insert(tk.END, f"\n[REVEAL] Target properties ({len(self.target_properties)}): {props}")
                    else:
                        console_text.insert(tk.END, "\n[WARN] No active round — target properties not set")
                elif cmd.startswith("addxp "):
                    try:
                        amount = int(cmd.split()[1])
                        self.player_xp += amount
                        console_text.insert(tk.END, f"\n[OK] Added {amount} XP. Total: {self.player_xp}/{self.xp_to_level_up}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addxp <number>")
                elif cmd.startswith("addwins "):
                    try:
                        amount = int(cmd.split()[1])
                        self.wins_count += amount
                        self.stats["total_wins"] = self.wins_count
                        self.wins_label.config(text=str(self.wins_count))
                        console_text.insert(tk.END, f"\n[OK] Added {amount} wins. Total: {self.wins_count}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addwins <number>")
                elif cmd.startswith("addrolls "):
                    try:
                        amount = int(cmd.split()[1])
                        self.roll_count += amount
                        self.stats["total_rolls"] = self.roll_count
                        self.roll_label.config(text=str(self.roll_count))
                        console_text.insert(tk.END, f"\n[OK] Added {amount} rolls. Total: {self.roll_count}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addrolls <number>")
                elif cmd.startswith("setelo "):
                    try:
                        elo = int(cmd.split()[1])
                        self.pvp_elo = elo
                        rn, rc = self._pvp_rank_for_elo(elo)
                        console_text.insert(tk.END, f"\n[OK] ELO set to {elo} ({rn})")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setelo <number>")
                elif cmd.startswith("setstreak "):
                    try:
                        s = int(cmd.split()[1])
                        self.winning_streak = s
                        if s > self.max_winning_streak:
                            self.max_winning_streak = s
                        console_text.insert(tk.END, f"\n[OK] Streak set to {s} (best: {self.max_winning_streak})")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setstreak <number>")
                elif cmd.startswith("setpvpwins "):
                    try:
                        n = int(cmd.split()[1])
                        self.pvp_wins = n
                        console_text.insert(tk.END, f"\n[OK] PvP wins set to {n}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setpvpwins <number>")
                elif cmd.startswith("setpvplosses "):
                    try:
                        n = int(cmd.split()[1])
                        self.pvp_losses = n
                        console_text.insert(tk.END, f"\n[OK] PvP losses set to {n}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setpvplosses <number>")
                elif cmd == "resetpvp":
                    self.pvp_elo = 1000
                    self.pvp_wins = 0
                    self.pvp_losses = 0
                    self.pvp_draws = 0
                    self.pvp_streak = 0
                    self.pvp_best_streak = 0
                    console_text.insert(tk.END, "\n[OK] All PvP stats reset to defaults (ELO 1000)")
                elif cmd == "unlockachall":
                    count = 0
                    for k in self.achievements:
                        if not self.achievements[k].get("completed") and not self.achievements[k].get("unlocked"):
                            count += 1
                        self.achievements[k]["completed"] = True
                        self.achievements[k]["unlocked"] = True
                    console_text.insert(tk.END, f"\n[OK] All {len(self.achievements)} achievements unlocked ({count} newly unlocked)")
                elif cmd == "listach":
                    console_text.insert(tk.END, "\n[ACHIEVEMENTS]")
                    for aid, ach in self.achievements.items():
                        done = ach.get("completed") or ach.get("unlocked")
                        icon = "✅" if done else "❌"
                        name = ach.get("name", aid)
                        console_text.insert(tk.END, f"\n  {icon} {aid}: {name}")
                elif cmd.startswith("setkarma "):
                    try:
                        k = int(cmd.split()[1])
                        self.rng_influence["karma_system"]["karma_level"] = k
                        console_text.insert(tk.END, f"\n[OK] Karma level set to {k}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: setkarma <number>")
                elif cmd.startswith("addluck "):
                    try:
                        n = int(cmd.split()[1])
                        lt = self.rng_influence.get("luck_tokens", {})
                        lt["current"] = lt.get("current", 0) + n
                        console_text.insert(tk.END, f"\n[OK] Added {n} luck tokens. Total: {lt['current']}/{lt.get('max', '?')}")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Invalid format. Usage: addluck <number>")
                elif cmd == "whoami":
                    title = self._get_player_title_for_wins(self.wins_count)
                    rn, _ = self._pvp_rank_for_elo(getattr(self, 'pvp_elo', 1000))
                    ach_done = sum(1 for a in self.achievements.values() if a.get("completed") or a.get("unlocked"))
                    spec = self.current_specialization or "None"
                    prest = self.prestige_system.get("current_level", 0)
                    info = (f"\n[PROFILE] {self.current_username}"
                            f"\n  Title:    {title}"
                            f"\n  Level:    {self.player_level}  (XP: {self.player_xp}/{self.xp_to_level_up})"
                            f"\n  Wins:     {self.wins_count}  |  Rolls: {self.roll_count}"
                            f"\n  Streak:   {self.winning_streak} (best: {self.max_winning_streak})"
                            f"\n  SP:       {self.sp} | SP+: {self.sp_plus} | SPx: {self.sp_x} | SP^: {self.sp_caret}"
                            f"\n  PvP ELO:  {getattr(self, 'pvp_elo', 1000)} ({rn})  W:{getattr(self, 'pvp_wins', 0)} L:{getattr(self, 'pvp_losses', 0)}"
                            f"\n  Achieve:  {ach_done}/{len(self.achievements)}"
                            f"\n  Spec:     {spec}"
                            f"\n  Prestige: Lv{prest}")
                    console_text.insert(tk.END, info)
                elif cmd == "nuke":
                    self.wins_count = 0
                    self.roll_count = 0
                    self.player_level = 1
                    self.player_xp = 0
                    self.winning_streak = 0
                    self.max_winning_streak = 0
                    self.sp = 0
                    self.sp_plus = 0
                    self.sp_x = 0
                    self.sp_caret = 0
                    self.pvp_elo = 1000
                    self.pvp_wins = 0
                    self.pvp_losses = 0
                    self.pvp_draws = 0
                    self.pvp_streak = 0
                    self.pvp_best_streak = 0
                    self.prestige_system["current_level"] = 0
                    self.prestige_system["prestige_points"] = 0
                    self.prestige_system["total_prestiges"] = 0
                    self.achievements = {k: {**v, "completed": False, "unlocked": False} for k, v in self.achievements.items()}
                    self.stats["total_wins"] = 0
                    self.stats["total_rolls"] = 0
                    self.stats["best_streak"] = 0
                    self.wins_label.config(text="0")
                    self.roll_label.config(text="0")
                    self._update_sp_label()
                    console_text.insert(tk.END, "\n[☢️ NUKE] ALL player data has been factory reset.")
                elif cmd in ("cls", "clear"):
                    console_text.delete("1.0", tk.END)
                    console_text.insert(tk.END, ">>> Console cleared.\n>>> Ready for input")
                elif cmd.startswith("echo "):
                    text = cmd[5:]
                    console_text.insert(tk.END, f"\n{text}")
                elif cmd.startswith("tp "):
                    try:
                        n = int(cmd.split()[1])
                        if 1 <= n <= 15:
                            self._dev_target_prop_count = n
                            console_text.insert(tk.END, f"\n[OK] Next round will have {n} target properties")
                        else:
                            console_text.insert(tk.END, "\n[ERROR] Must be 1-15")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Usage: tp <number 1-15>")
                elif cmd.startswith("rename "):
                    new_name = cmd[7:].strip()
                    if new_name:
                        old = self.current_username
                        self.current_username = new_name
                        console_text.insert(tk.END, f"\n[OK] Display name changed: {old} \u2192 {new_name}")
                    else:
                        console_text.insert(tk.END, "\n[ERROR] Usage: rename <new_name>")
                elif cmd.startswith("speed "):
                    try:
                        n = int(cmd.split()[1])
                        if 1 <= n <= 10:
                            self._dev_speed_mult = n
                            console_text.insert(tk.END, f"\n[OK] Animation speed multiplier set to {n}x")
                        else:
                            console_text.insert(tk.END, "\n[ERROR] Must be 1-10")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Usage: speed <1-10>")
                elif cmd == "listtournaments":
                    t_scores = self.tournament_data.get("scores", {})
                    console_text.insert(tk.END, "\n[TOURNAMENTS]")
                    for mode, icon, unit in [("speed", "\u26a1", "rolls"), ("survival", "\U0001f6e1\ufe0f", "rounds"), ("blitz", "\U0001f525", "pts")]:
                        ms = t_scores.get(mode, {})
                        best = ms.get("best", "\u2014")
                        plays = ms.get("plays", 0)
                        console_text.insert(tk.END, f"\n  {icon} {mode.title():10s}  Best: {best} {unit}  |  Played: {plays}x")
                elif cmd.startswith("setplaytime "):
                    try:
                        hours = float(cmd.split()[1])
                        self.stats["play_time"] = hours * 3600
                        console_text.insert(tk.END, f"\n[OK] Play time set to {hours:.1f} hours")
                    except Exception:
                        console_text.insert(tk.END, "\n[ERROR] Usage: setplaytime <hours>")
                elif cmd == "exportstats":
                    import pprint
                    dump = {"wins": self.wins_count, "rolls": self.roll_count, "level": self.player_level,
                            "xp": self.player_xp, "sp": self.sp, "sp_plus": self.sp_plus,
                            "sp_x": self.sp_x, "sp_caret": self.sp_caret,
                            "streak": self.winning_streak, "best_streak": self.max_winning_streak,
                            "pvp_elo": getattr(self, "pvp_elo", 1000),
                            "pvp_wins": getattr(self, "pvp_wins", 0),
                            "pvp_losses": getattr(self, "pvp_losses", 0),
                            "prestige": self.prestige_system.get("current_level", 0),
                            "achievements_done": sum(1 for a in self.achievements.values() if a.get("completed") or a.get("unlocked")),
                            "play_time_hours": round(self.stats.get("play_time", 0) / 3600, 2),
                            "stats": self.stats}
                    console_text.insert(tk.END, f"\n[EXPORT]\n{pprint.pformat(dump, width=60)}")
                elif cmd == "reload":
                    try:
                        self.stats = self._load_stats()
                        self.achievements = self._load_achievements()
                        self.equipment_inventory = self._load_equipment()
                        self.rolls_history = self._load_history()
                        self.roll_count = self.stats.get("total_rolls", 0)
                        self.wins_count = self.stats.get("total_wins", 0)
                        self.roll_label.config(text=str(self.roll_count))
                        self.wins_label.config(text=str(self.wins_count))
                        self._update_sp_label()
                        console_text.insert(tk.END, "\n[OK] Reloaded: stats, achievements, equipment, history from disk")
                    except Exception as e:
                        console_text.insert(tk.END, f"\n[ERROR] Reload failed: {e}")
                elif cmd == "listprops":
                    console_text.insert(tk.END, "\n[PROPERTIES] All 15 possible string properties:")
                    for i, prop in enumerate(sorted(self.possible_properties), 1):
                        display = self._property_name_display(prop) if hasattr(self, '_property_name_display') else prop
                        console_text.insert(tk.END, f"\n  {i:2d}. {prop:25s} {display}")
                elif cmd == "filecheck":
                    user = self.current_username
                    files_to_check = [
                        f"user_{user}_stats.json", f"user_{user}_data.json",
                        f"user_{user}_achievements.json", f"user_{user}_equipment.json",
                        f"user_{user}_history.json", f"user_{user}_pvp.json",
                        f"user_{user}_progression.json", f"user_{user}_strategy.json",
                        f"user_{user}_tournament.json",
                        "accounts.json", "shop_inventory.json", "game_settings.json",
                    ]
                    console_text.insert(tk.END, f"\n[FILECHECK] Checking data files for '{user}':")
                    ok_count = 0
                    for fp in files_to_check:
                        if os.path.exists(fp):
                            try:
                                with open(fp, 'r') as f:
                                    json.load(f)
                                console_text.insert(tk.END, f"\n  \u2705 {fp} (valid JSON)")
                                ok_count += 1
                            except json.JSONDecodeError as e:
                                console_text.insert(tk.END, f"\n  \u26a0\ufe0f {fp} (CORRUPT: {e})")
                        else:
                            console_text.insert(tk.END, f"\n  \u274c {fp} (missing)")
                    console_text.insert(tk.END, f"\n  --- {ok_count}/{len(files_to_check)} files OK")
                elif cmd == "meminfo":
                    import sys
                    obj_sizes = {
                        "achievements": sys.getsizeof(self.achievements),
                        "stats": sys.getsizeof(self.stats),
                        "equipment_inventory": sys.getsizeof(self.equipment_inventory),
                        "rolls_history": sys.getsizeof(getattr(self, 'rolls_history', [])),
                        "specialization_trees": sys.getsizeof(self.specialization_trees),
                        "prestige_system": sys.getsizeof(self.prestige_system),
                        "rng_influence": sys.getsizeof(self.rng_influence),
                        "investment_system": sys.getsizeof(self.investment_system),
                        "tournament_data": sys.getsizeof(self.tournament_data),
                    }
                    total = sum(obj_sizes.values())
                    console_text.insert(tk.END, f"\n[MEMORY] Top-level object sizes (shallow):")
                    for name, size in sorted(obj_sizes.items(), key=lambda x: -x[1]):
                        console_text.insert(tk.END, f"\n  {name:25s} {size:>8,} bytes")
                    console_text.insert(tk.END, f"\n  {'TOTAL':25s} {total:>8,} bytes")
                    console_text.insert(tk.END, f"\n  Python process: {sys.getsizeof(self):,} bytes (self)")
                elif cmd == "eventlog":
                    log = getattr(self, '_dev_event_log', [])
                    if not log:
                        console_text.insert(tk.END, "\n[EVENTLOG] No events recorded this session.")
                    else:
                        console_text.insert(tk.END, f"\n[EVENTLOG] Last {min(20, len(log))} events:")
                        for entry in log[-20:]:
                            console_text.insert(tk.END, f"\n  {entry}")
                elif cmd.startswith("spectateuser "):
                    try:
                        target = cmd.split(None, 1)[1].strip()
                        if not target:
                            raise ValueError("empty")
                        # Check if the account exists
                        accounts = self.account_manager._load_accounts()
                        if target not in accounts:
                            console_text.insert(tk.END, f"\n[ERROR] User '{target}' does not exist.")
                        elif target == self.current_username:
                            console_text.insert(tk.END, "\n[ERROR] You can't spectate yourself. Just look at your own screen.")
                        else:
                            # Check if they have data files
                            stats_file = f"user_{target}_stats.json"
                            if not os.path.exists(stats_file):
                                console_text.insert(tk.END, f"\n[WARN] User '{target}' has no saved data yet (never played).")
                            else:
                                console_text.insert(tk.END, f"\n[OK] Opening spectator view for '{target}'...")
                                self._spectate_user(target)
                    except (IndexError, ValueError):
                        console_text.insert(tk.END, "\n[ERROR] Usage: spectateuser <username>")
                elif cmd == "startbot" or cmd.startswith("startbot "):
                    parts = cmd.split(None, 1)
                    bot_name = parts[1].strip() if len(parts) > 1 else "BotPlayer"
                    ok, msg = self._start_bot_player(bot_name)
                    tag = "[OK]" if ok else "[ERROR]"
                    console_text.insert(tk.END, f"\n{tag} {msg}")
                elif cmd == "stopbot" or cmd.startswith("stopbot "):
                    parts = cmd.split(None, 1)
                    bot_name = parts[1].strip() if len(parts) > 1 else "BotPlayer"
                    ok, msg = self._stop_bot_player(bot_name)
                    tag = "[OK]" if ok else "[ERROR]"
                    console_text.insert(tk.END, f"\n{tag} {msg}")
                elif cmd == "listbots":
                    bots = getattr(self, '_bot_threads', {})
                    if not bots:
                        console_text.insert(tk.END, "\n[BOTS] No bots are currently running.")
                    else:
                        console_text.insert(tk.END, f"\n[BOTS] {len(bots)} bot(s) running:")
                        for name in bots:
                            sf = f"user_{name}_stats.json"
                            bs = self._load_json(sf, {})
                            console_text.insert(tk.END, f"\n  🤖 {name}  —  Rolls: {bs.get('total_rolls', 0):,}  Wins: {bs.get('total_wins', 0):,}")
                else:
                    console_text.insert(tk.END, f"\n[ERROR] Unknown command: '{cmd}'. Type 'help' for available commands")
                
                console_text.config(state=tk.DISABLED)
                console_text.see(tk.END)
                cmd_entry.delete(0, tk.END)
        
        execute_btn = self._styled_button(cmd_input_frame, "Execute", execute_command, style="success", width=10, small=True)
        execute_btn.pack(side=tk.LEFT, padx=5)
    
    def _spectate_user(self, target_username):
        """Open a LIVE spectator window showing every single action a user takes in real-time.
        Compares snapshots every second and logs every roll, win, SP gain, achievement,
        equipment purchase, PvP match, level up, and streak change."""
        ui = self._ui
        spec_win = self._styled_toplevel(f"👁️ LIVE SPECTATING: {target_username}", 960, 800,
                                          min_width=850, min_height=650)
        
        # Header
        self._styled_header(spec_win, f"LIVE SPECTATING — {target_username}",
                            subtitle="Real-time player surveillance · Every action logged · Read-only",
                            icon="👁️")
        
        # ── Live indicator bar with pulse ──────────────────────────────────
        live_bar = tk.Frame(spec_win, bg="#ff1744", height=30)
        live_bar.pack(fill=tk.X)
        live_bar.pack_propagate(False)
        live_label = tk.Label(live_bar, text="🔴 LIVE  —  Connecting to player feed...",
                              font=("Segoe UI", 9, "bold"), bg="#ff1744", fg="#ffffff")
        live_label.pack(expand=True)
        
        # ── Top: Compact live stats dashboard ──────────────────────────────
        dash_frame = tk.Frame(spec_win, bg=ui["bg_secondary"], pady=6)
        dash_frame.pack(fill=tk.X, padx=0)
        
        # Stats pill widgets (will be updated live)
        dash_inner = tk.Frame(dash_frame, bg=ui["bg_secondary"])
        dash_inner.pack(fill=tk.X, padx=12)
        
        def _pill(parent, icon, label, initial="—", color=None):
            """Create a compact stat pill, return the value label for updates"""
            pill = tk.Frame(parent, bg=ui["bg_card"], padx=8, pady=3)
            pill.pack(side=tk.LEFT, padx=3)
            tk.Label(pill, text=f"{icon} {label}", font=("Segoe UI", 8),
                     bg=ui["bg_card"], fg=ui["text_secondary"]).pack(side=tk.LEFT)
            val = tk.Label(pill, text=initial, font=("Segoe UI", 8, "bold"),
                           bg=ui["bg_card"], fg=color or ui["text_primary"])
            val.pack(side=tk.LEFT, padx=(4, 0))
            return val
        
        pill_rolls = _pill(dash_inner, "🎲", "Rolls", "0", ui["gold"])
        pill_wins = _pill(dash_inner, "🏆", "Wins", "0", ui["success"])
        pill_level = _pill(dash_inner, "⭐", "Lv", "1", ui["xp_color"])
        pill_sp = _pill(dash_inner, "💎", "SP", "0", ui["sp_color"])
        pill_streak = _pill(dash_inner, "🔥", "Streak", "0", ui["warning"])
        pill_elo = _pill(dash_inner, "⚔️", "ELO", "1000", ui["info"])
        pill_ach = _pill(dash_inner, "🏅", "Ach", "0", ui["gold"])
        pill_items = _pill(dash_inner, "🛡️", "Items", "0", ui["accent_light"])
        
        # Thin divider
        tk.Frame(spec_win, bg=ui["accent"], height=2).pack(fill=tk.X)
        
        # ── Bottom: Live action feed (scrolling text log) ─────────────────
        feed_frame = tk.Frame(spec_win, bg=ui["bg_primary"])
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Feed header
        feed_hdr = tk.Frame(feed_frame, bg=ui["bg_card"])
        feed_hdr.pack(fill=tk.X)
        tk.Frame(feed_hdr, bg="#ff1744", width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(feed_hdr, text="  📡  LIVE ACTION FEED  —  Every move, every second",
                 font=ui["font_subhead"], bg=ui["bg_card"], fg="#ff1744").pack(side=tk.LEFT, padx=8, pady=6)
        
        # Event counter
        event_count_var = tk.StringVar(value="Events: 0")
        tk.Label(feed_hdr, textvariable=event_count_var, font=ui["font_small"],
                 bg=ui["bg_card"], fg=ui["text_muted"]).pack(side=tk.RIGHT, padx=12)
        
        # Scrollable text widget for the feed
        feed_text = tk.Text(feed_frame, bg="#0a0a14", fg=ui["text_primary"],
                           font=("Consolas", 9), wrap=tk.WORD, state=tk.DISABLED,
                           relief=tk.FLAT, bd=0, padx=12, pady=8,
                           insertbackground=ui["text_primary"],
                           selectbackground=ui["accent"], selectforeground=ui["text_bright"])
        feed_scroll = tk.Scrollbar(feed_frame, orient="vertical", command=feed_text.yview)
        feed_text.configure(yscrollcommand=feed_scroll.set)
        feed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        feed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mousewheel scroll
        def _mw_feed(event):
            try: feed_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError: pass
        feed_text.bind("<Enter>", lambda e: feed_text.bind_all("<MouseWheel>", _mw_feed))
        feed_text.bind("<Leave>", lambda e: (feed_text.unbind_all("<MouseWheel>") if feed_text.winfo_exists() else None))
        
        # Configure text tags for colored output
        feed_text.tag_configure("time", foreground="#5f6368")
        feed_text.tag_configure("roll", foreground="#9aa0a6")
        feed_text.tag_configure("roll_string", foreground="#b388ff")
        feed_text.tag_configure("match_info", foreground="#00b0ff")
        feed_text.tag_configure("win", foreground="#00e676", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("critical", foreground="#ffd740", font=("Consolas", 10, "bold"))
        feed_text.tag_configure("sp_gain", foreground="#ea80fc", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("xp_gain", foreground="#69f0ae")
        feed_text.tag_configure("level_up", foreground="#ffd740", font=("Consolas", 10, "bold"))
        feed_text.tag_configure("achievement", foreground="#ffab00", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("equipment", foreground="#00b0ff", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("pvp_win", foreground="#00e676", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("pvp_loss", foreground="#ff1744", font=("Consolas", 9, "bold"))
        feed_text.tag_configure("streak", foreground="#ff6d00")
        feed_text.tag_configure("milestone", foreground="#ffd740", font=("Consolas", 10, "bold"))
        feed_text.tag_configure("separator", foreground="#2a2a4a")
        feed_text.tag_configure("system", foreground="#7c4dff")
        feed_text.tag_configure("loss", foreground="#5f6368")
        
        # ── Helper to load target data ────────────────────────────────────
        def _load_target_data():
            data = {}
            sf = f"user_{target_username}_stats.json"
            data["stats"] = self._load_json(sf, {
                "total_rolls": 0, "total_wins": 0, "best_streak": 0,
                "current_streak": 0, "fastest_win": None, "slowest_win": 0,
                "avg_rolls_per_win": 0, "property_discoveries": {}, "play_time": 0
            })
            df = f"user_{target_username}_data.json"
            data["user_data"] = self._load_json(df, {})
            af = f"user_{target_username}_achievements.json"
            data["achievements"] = self._load_json(af, {})
            ef = f"user_{target_username}_equipment.json"
            data["equipment"] = self._load_json(ef, {"owned": [], "equipped": {}})
            hf = f"user_{target_username}_history.json"
            data["history"] = self._load_json(hf, [])
            pf = f"user_{target_username}_pvp.json"
            data["pvp"] = self._load_json(pf, {})
            pgf = f"user_{target_username}_progression.json"
            data["progression"] = self._load_json(pgf, {})
            return data
        
        # ── State tracking for diff detection ─────────────────────────────
        prev = {
            "total_rolls": 0, "total_wins": 0, "level": 1, "xp": 0,
            "sp": 0, "sp_plus": 0, "sp_x": 0, "sp_caret": 0,
            "current_streak": 0, "best_streak": 0,
            "elo": 1000, "pvp_wins": 0, "pvp_losses": 0,
            "ach_unlocked": set(), "owned_items": [],
            "history_len": 0, "history_entries": [],
        }
        event_counter = [0]
        initialized = [False]
        
        def _log(text, tag="roll"):
            """Append a line to the feed"""
            feed_text.config(state=tk.NORMAL)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            feed_text.insert(tk.END, f"[{ts}] ", "time")
            feed_text.insert(tk.END, f"{text}\n", tag)
            feed_text.config(state=tk.DISABLED)
            feed_text.see(tk.END)
            event_counter[0] += 1
            event_count_var.set(f"Events: {event_counter[0]:,}")
        
        def _log_separator():
            feed_text.config(state=tk.NORMAL)
            feed_text.insert(tk.END, "─" * 80 + "\n", "separator")
            feed_text.config(state=tk.DISABLED)
        
        # ── Main refresh / diff engine ────────────────────────────────────
        def _tick():
            if not spec_win.winfo_exists():
                return
            
            try:
                data = _load_target_data()
            except Exception:
                if spec_win.winfo_exists():
                    spec_win.after(1000, _tick)
                return
            
            stats = data["stats"]
            user_data = data["user_data"]
            achievements = data["achievements"]
            equipment = data["equipment"]
            history = data["history"]
            pvp_data = data["pvp"]
            
            # Extract current values
            cur_rolls = stats.get("total_rolls", 0)
            cur_wins = stats.get("total_wins", 0)
            cur_level = user_data.get("player_level", user_data.get("level", 1))
            cur_xp = user_data.get("player_xp", user_data.get("xp", 0))
            cur_sp = equipment.get("sp", user_data.get("sp", 0))
            cur_sp_plus = equipment.get("sp_plus", user_data.get("sp_plus", 0))
            cur_sp_x = equipment.get("sp_x", user_data.get("sp_x", 0))
            cur_sp_caret = equipment.get("sp_caret", user_data.get("sp_caret", 0))
            cur_streak = stats.get("current_streak", 0)
            cur_best_streak = stats.get("best_streak", 0)
            cur_elo = pvp_data.get("elo", pvp_data.get("pvp_elo", 1000))
            cur_pvp_wins = pvp_data.get("wins", pvp_data.get("pvp_wins", 0))
            cur_pvp_losses = pvp_data.get("losses", pvp_data.get("pvp_losses", 0))
            cur_owned = equipment.get("owned", [])
            cur_ach_unlocked = set()
            for k, v in achievements.items():
                if isinstance(v, dict) and (v.get("unlocked") or v.get("completed")):
                    cur_ach_unlocked.add(k)
            cur_history_len = len(history) if isinstance(history, list) else 0
            
            # ── Update dashboard pills ────────────────────────────────
            try:
                pill_rolls.config(text=f"{cur_rolls:,}")
                pill_wins.config(text=f"{cur_wins:,}")
                pill_level.config(text=str(cur_level))
                total_sp = cur_sp + cur_sp_plus + cur_sp_x + cur_sp_caret
                pill_sp.config(text=f"{cur_sp}|{cur_sp_plus}|{cur_sp_x}|{cur_sp_caret}")
                pill_streak.config(text=str(cur_streak))
                pill_elo.config(text=str(cur_elo))
                pill_ach.config(text=f"{len(cur_ach_unlocked)}")
                pill_items.config(text=str(len(cur_owned)))
            except tk.TclError:
                return
            
            # ── First tick: initialize baseline, don't log ────────────
            if not initialized[0]:
                initialized[0] = True
                prev["total_rolls"] = cur_rolls
                prev["total_wins"] = cur_wins
                prev["level"] = cur_level
                prev["xp"] = cur_xp
                prev["sp"] = cur_sp
                prev["sp_plus"] = cur_sp_plus
                prev["sp_x"] = cur_sp_x
                prev["sp_caret"] = cur_sp_caret
                prev["current_streak"] = cur_streak
                prev["best_streak"] = cur_best_streak
                prev["elo"] = cur_elo
                prev["pvp_wins"] = cur_pvp_wins
                prev["pvp_losses"] = cur_pvp_losses
                prev["ach_unlocked"] = cur_ach_unlocked.copy()
                prev["owned_items"] = list(cur_owned)
                prev["history_len"] = cur_history_len
                prev["history_entries"] = list(history) if isinstance(history, list) else []
                
                _log(f"📡 Connected to {target_username}'s game feed", "system")
                _log(f"📊 Current state: Lv.{cur_level} | {cur_rolls:,} rolls | {cur_wins:,} wins | Streak: {cur_streak} | ELO: {cur_elo}", "system")
                _log(f"💎 Currency: SP={cur_sp} | SP+={cur_sp_plus} | SPx={cur_sp_x} | SP^={cur_sp_caret}", "system")
                _log(f"🏅 Achievements: {len(cur_ach_unlocked)} unlocked | 🛡️ Items: {len(cur_owned)} owned", "system")
                _log_separator()
                _log("👁️ Watching for activity...", "system")
                
                live_label.config(text=f"🔴 LIVE  —  Spectating {target_username}  —  Watching for moves...")
                
                if spec_win.winfo_exists():
                    spec_win.after(1000, _tick)
                return
            
            # ── Detect new history entries (each = a roll) ────────────
            new_entries = []
            if cur_history_len > prev["history_len"]:
                # Get only the new entries
                new_count = cur_history_len - prev["history_len"]
                if isinstance(history, list) and new_count > 0:
                    new_entries = history[-new_count:]
            
            anything_happened = False
            
            # ── Log each new roll individually ────────────────────────
            for entry in new_entries:
                anything_happened = True
                s = entry.get("string", "???")
                display_s = s if len(s) <= 50 else s[:47] + "..."
                matches = entry.get("matches", 0)
                total_needed = entry.get("total_needed", 0)
                match_pct = entry.get("match_pct", 0)
                won = entry.get("won", False)
                is_critical = entry.get("is_critical", False)
                sp_earned = entry.get("sp_earned", 0)
                xp_earned = entry.get("xp_earned", 0)
                roll_num = entry.get("number", "?")
                
                # The roll itself
                if won and is_critical:
                    _log(f"⚡ CRITICAL WIN!  Roll #{roll_num:,}  \"{display_s}\"", "critical")
                    _log(f"   ⚡ PERFECT MATCH [{matches}/{total_needed}] — CRITICAL HIT × 3 BONUS!", "critical")
                elif won:
                    _log(f"✅ WIN!  Roll #{roll_num:,}  \"{display_s}\"", "win")
                    _log(f"   🎯 PERFECT MATCH [{matches}/{total_needed}] — Round complete!", "win")
                else:
                    # Regular roll — show match progress
                    if match_pct >= 75:
                        _log(f"🎲 Roll #{roll_num:,}  \"{display_s}\"  [{matches}/{total_needed}] ({match_pct:.0f}%) — SO CLOSE!", "match_info")
                    elif match_pct >= 50:
                        _log(f"🎲 Roll #{roll_num:,}  \"{display_s}\"  [{matches}/{total_needed}] ({match_pct:.0f}%) — halfway", "roll")
                    elif matches > 0:
                        _log(f"🎲 Roll #{roll_num:,}  \"{display_s}\"  [{matches}/{total_needed}] ({match_pct:.0f}%)", "roll")
                    else:
                        _log(f"🎲 Roll #{roll_num:,}  \"{display_s}\"  [{matches}/{total_needed}] — no match", "loss")
                
                # SP earned on win
                if sp_earned > 0:
                    _log(f"   💰 +{sp_earned} SP earned{' (CRITICAL ×3!)' if is_critical else ''}", "sp_gain")
                
                # XP earned on win
                if xp_earned > 0:
                    _log(f"   ✨ +{xp_earned} XP gained{' (CRITICAL ×3!)' if is_critical else ''}", "xp_gain")
            
            # ── Detect level up ───────────────────────────────────────
            if cur_level > prev["level"]:
                anything_happened = True
                for lv in range(prev["level"] + 1, cur_level + 1):
                    _log_separator()
                    _log(f"🎉🎉🎉 LEVEL UP! {target_username} reached Level {lv}! 🎉🎉🎉", "level_up")
                    _log_separator()
            
            # ── Detect streak changes ─────────────────────────────────
            if cur_streak > prev["current_streak"] and cur_streak > 1:
                _log(f"🔥 Win streak: {cur_streak} in a row!", "streak")
            elif cur_streak == 0 and prev["current_streak"] > 2:
                _log(f"💔 Streak broken! Was {prev['current_streak']} — back to 0", "pvp_loss")
            
            if cur_best_streak > prev["best_streak"]:
                anything_happened = True
                _log(f"⭐ NEW BEST STREAK RECORD: {cur_best_streak}!", "milestone")
            
            # ── Detect SP changes (spending = negative) ───────────────
            sp_diff = cur_sp - prev["sp"]
            sp_plus_diff = cur_sp_plus - prev["sp_plus"]
            sp_x_diff = cur_sp_x - prev["sp_x"]
            sp_caret_diff = cur_sp_caret - prev["sp_caret"]
            
            if sp_diff < 0:
                _log(f"   🛒 Spent {abs(sp_diff)} SP (now {cur_sp})", "equipment")
            if sp_plus_diff < 0:
                _log(f"   🛒 Spent {abs(sp_plus_diff)} SP+ (now {cur_sp_plus})", "equipment")
            if sp_x_diff < 0:
                _log(f"   🛒 Spent {abs(sp_x_diff)} SPx (now {cur_sp_x})", "equipment")
            if sp_caret_diff < 0:
                _log(f"   🛒 Spent {abs(sp_caret_diff)} SP^ (now {cur_sp_caret})", "equipment")
            
            # ── Detect new equipment ──────────────────────────────────
            prev_items_set = set(prev["owned_items"])
            cur_items_set = set(cur_owned)
            new_items = cur_items_set - prev_items_set
            for item_id in new_items:
                anything_happened = True
                recipe = self.equipment_recipes.get(item_id, {})
                item_name = recipe.get("desc", item_id)
                # Check if it's a bot-exclusive item (not in normal recipes)
                is_bot_item = not recipe
                tag = "🤖🛡️ BOT-EXCLUSIVE ITEM" if is_bot_item else "🛡️ BOUGHT ITEM"
                _log_separator()
                _log(f"{tag}: {item_name} ({item_id})", "equipment")
                _log_separator()
            
            # ── Detect new achievements ───────────────────────────────
            new_achs = cur_ach_unlocked - prev["ach_unlocked"]
            for ach_id in new_achs:
                anything_happened = True
                ach_data = achievements.get(ach_id, {})
                ach_name = ach_data.get("name", ach_id)
                ach_rarity = ach_data.get("rarity", "common").upper()
                ach_desc = ach_data.get("desc", "")
                reward = ach_data.get("reward", 0)
                _log_separator()
                _log(f"🏆 ACHIEVEMENT UNLOCKED: {ach_name} [{ach_rarity}]", "achievement")
                _log(f"   📝 {ach_desc}", "achievement")
                if reward:
                    _log(f"   🎁 Reward: +{reward} SP", "sp_gain")
                _log_separator()
            
            # ── Detect PvP matches ────────────────────────────────────
            if cur_pvp_wins > prev["pvp_wins"]:
                anything_happened = True
                elo_change = cur_elo - prev["elo"]
                _log_separator()
                _log(f"⚔️ PVP MATCH: {target_username} WON! (+{elo_change} ELO → {cur_elo})", "pvp_win")
                _log_separator()
            if cur_pvp_losses > prev["pvp_losses"]:
                anything_happened = True
                elo_change = prev["elo"] - cur_elo
                _log_separator()
                _log(f"⚔️ PVP MATCH: {target_username} LOST! (-{elo_change} ELO → {cur_elo})", "pvp_loss")
                _log_separator()
            
            # ── Detect win milestones ─────────────────────────────────
            milestones = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
            for m in milestones:
                if cur_wins >= m and prev["total_wins"] < m:
                    _log_separator()
                    _log(f"🌟 MILESTONE: {target_username} reached {m:,} WINS!", "milestone")
                    _log_separator()
            
            roll_milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
            for m in roll_milestones:
                if cur_rolls >= m and prev["total_rolls"] < m:
                    _log(f"📊 ROLL MILESTONE: {cur_rolls:,} total rolls!", "milestone")
            
            # ── Update live bar ───────────────────────────────────────
            if anything_happened:
                now_str = datetime.datetime.now().strftime('%H:%M:%S')
                live_label.config(
                    text=f"🔴 LIVE  —  {target_username} active at {now_str}  —  Lv.{cur_level} | {cur_wins:,}W | Streak {cur_streak} | ELO {cur_elo}",
                    bg="#ff1744")
            else:
                live_label.config(
                    text=f"🔴 LIVE  —  Spectating {target_username}  —  Waiting for next move...",
                    bg="#b71c1c")
            
            # ── Save current as previous ──────────────────────────────
            prev["total_rolls"] = cur_rolls
            prev["total_wins"] = cur_wins
            prev["level"] = cur_level
            prev["xp"] = cur_xp
            prev["sp"] = cur_sp
            prev["sp_plus"] = cur_sp_plus
            prev["sp_x"] = cur_sp_x
            prev["sp_caret"] = cur_sp_caret
            prev["current_streak"] = cur_streak
            prev["best_streak"] = cur_best_streak
            prev["elo"] = cur_elo
            prev["pvp_wins"] = cur_pvp_wins
            prev["pvp_losses"] = cur_pvp_losses
            prev["ach_unlocked"] = cur_ach_unlocked.copy()
            prev["owned_items"] = list(cur_owned)
            prev["history_len"] = cur_history_len
            prev["history_entries"] = list(history) if isinstance(history, list) else []
            
            # ── Schedule next tick (1 second) ─────────────────────────
            if spec_win.winfo_exists():
                spec_win.after(1000, _tick)
        
        # Initial tick
        _tick()
    
    def _start_bot_player(self, bot_name="BotPlayer"):
        """Start a SUPERCHARGED bot that plays insanely fast with boosted luck, massive SP,
        and access to an exclusive bot-only mega shop. Runs in background thread."""
        import threading
        
        # Prevent duplicate bots
        if hasattr(self, '_bot_threads') and bot_name in self._bot_threads:
            return False, f"Bot '{bot_name}' is already running."
        if not hasattr(self, '_bot_threads'):
            self._bot_threads = {}
        
        # Register bot account if it doesn't exist
        accounts = self.account_manager._load_accounts()
        if bot_name not in accounts:
            accounts[bot_name] = {
                "password_hash": self.account_manager._hash_password("bot_password_123"),
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_played": None,
                "play_time": 0,
                "title": "🤖 Bot"
            }
            self.account_manager.accounts = accounts
            self.account_manager._save_accounts()
        
        # Stop flag
        stop_event = threading.Event()
        self._bot_threads[bot_name] = stop_event
        
        def _bot_loop():
            """Background bot simulation loop — SUPERCHARGED"""
            possible_properties = [
                "has_numbers", "has_symbols", "has_uppercase", "has_lowercase", "is_long",
                "has_spaces", "has_operators", "has_multiple_words", "has_repeats",
                "starts_with_letter", "ends_with_symbol", "has_punctuation", "has_vowels",
                "is_very_long", "has_consecutive_letters"
            ]
            
            rarity_tiers = ["common", "rare", "epic", "legendary"]
            
            # Default achievements catalogue (same as main game)
            default_achievements = {
                "first_win":       {"unlocked": False, "name": "First Victory",     "desc": "Win your first sequence",            "rarity": "common",    "category": "wins",       "reward": 5,    "goal": 1},
                "ten_wins":        {"unlocked": False, "name": "Dedicated Player",  "desc": "Win 10 sequences",                   "rarity": "common",    "category": "wins",       "reward": 15,   "goal": 10},
                "fifty_wins":      {"unlocked": False, "name": "Master Deductor",   "desc": "Win 50 sequences",                   "rarity": "rare",      "category": "wins",       "reward": 50,   "goal": 50},
                "hundred_wins":    {"unlocked": False, "name": "Centurion",         "desc": "Win 100 sequences",                  "rarity": "epic",      "category": "wins",       "reward": 150,  "goal": 100},
                "fivehundred_wins":{"unlocked": False, "name": "Unstoppable Force", "desc": "Win 500 sequences",                  "rarity": "legendary", "category": "wins",       "reward": 500,  "goal": 500},
                "hundred_rolls":   {"unlocked": False, "name": "Getting Started",   "desc": "Make 100 rolls",                     "rarity": "common",    "category": "rolls",      "reward": 5,    "goal": 100},
                "fivehundred_rolls":{"unlocked": False,"name": "Automation Expert", "desc": "Make 500 rolls",                     "rarity": "common",    "category": "rolls",      "reward": 10,   "goal": 500},
                "thousand_rolls":  {"unlocked": False, "name": "Obsessed",          "desc": "Make 1,000 rolls",                   "rarity": "rare",      "category": "rolls",      "reward": 30,   "goal": 1000},
                "perfectionist":   {"unlocked": False, "name": "Perfectionist",     "desc": "Win 3 in a row",                     "rarity": "common",    "category": "streaks",    "reward": 10,   "goal": 3},
                "streak_breaker":  {"unlocked": False, "name": "Streak Breaker",    "desc": "Win 5 in a row",                     "rarity": "rare",      "category": "streaks",    "reward": 30,   "goal": 5},
                "on_fire":         {"unlocked": False, "name": "On Fire",           "desc": "Win 10 in a row",                    "rarity": "epic",      "category": "streaks",    "reward": 75,   "goal": 10},
                "speed_demon":     {"unlocked": False, "name": "Speed Demon",       "desc": "Win in under 30 rolls",              "rarity": "common",    "category": "speed",      "reward": 10,   "goal": 30},
                "lightning":       {"unlocked": False, "name": "Lightning Fast",    "desc": "Win in under 10 rolls",              "rarity": "rare",      "category": "speed",      "reward": 40,   "goal": 10},
                "sp_collector":    {"unlocked": False, "name": "SP Collector",      "desc": "Accumulate 50 SP",                   "rarity": "common",    "category": "currency",   "reward": 10,   "goal": 50},
                "sp_hoarder":      {"unlocked": False, "name": "SP Hoarder",        "desc": "Accumulate 500 SP",                  "rarity": "rare",      "category": "currency",   "reward": 25,   "goal": 500},
                "property_master": {"unlocked": False, "name": "Property Spotter",  "desc": "Discover 10 unique properties",      "rarity": "common",    "category": "exploration","reward": 10,   "goal": 10},
                "explorer":        {"unlocked": False, "name": "Property Explorer", "desc": "Discover all 15 properties",         "rarity": "epic",      "category": "exploration","reward": 75,   "goal": 15},
                "first_craft":     {"unlocked": False, "name": "Apprentice Smith",  "desc": "Craft your first equipment",         "rarity": "common",    "category": "equipment",  "reward": 10,   "goal": 1},
                "pvp_debut":       {"unlocked": False, "name": "Arena Debut",       "desc": "Win your first PvP duel",            "rarity": "common",    "category": "pvp",        "reward": 15,   "goal": 1},
                "night_owl":       {"unlocked": False, "name": "Night Owl",         "desc": "Play between 12 AM and 6 AM",        "rarity": "rare",      "category": "special",    "reward": 20,   "goal": 1},
            }
            
            # ═══════════════════════════════════════════════════════════
            # 🤖 MASSIVE BOT-EXCLUSIVE ITEM CATALOGUE
            # Normal players CANNOT access these — bot_exclusive = True
            # ═══════════════════════════════════════════════════════════
            bot_exclusive_items = {
                # ── QUANTUM GAUNTLETS ─────────────────────────────────
                "quantum_gauntlet_mk1":    {"type": "gauntlet", "cost": {"sp": 20},       "effect": "quantum_luck_10",     "desc": "🔮 Quantum Gauntlet Mk.I — +10% luck",          "bot_exclusive": True},
                "quantum_gauntlet_mk2":    {"type": "gauntlet", "cost": {"sp": 50},       "effect": "quantum_luck_20",     "desc": "🔮 Quantum Gauntlet Mk.II — +20% luck",         "bot_exclusive": True},
                "quantum_gauntlet_mk3":    {"type": "gauntlet", "cost": {"sp": 120},      "effect": "quantum_luck_35",     "desc": "🔮 Quantum Gauntlet Mk.III — +35% luck",        "bot_exclusive": True},
                "quantum_gauntlet_omega":  {"type": "gauntlet", "cost": {"sp": 300},      "effect": "quantum_luck_50",     "desc": "🔮 Quantum Gauntlet Ω — +50% luck",             "bot_exclusive": True},
                # ── NEURAL DEVICES ────────────────────────────────────
                "neural_scanner_v1":       {"type": "device",   "cost": {"sp": 25},       "effect": "neural_scan_1",       "desc": "🧠 Neural Scanner v1 — Scan 1 property",        "bot_exclusive": True},
                "neural_scanner_v2":       {"type": "device",   "cost": {"sp": 60},       "effect": "neural_scan_2",       "desc": "🧠 Neural Scanner v2 — Scan 2 properties",      "bot_exclusive": True},
                "neural_scanner_v3":       {"type": "device",   "cost": {"sp": 150},      "effect": "neural_scan_all",     "desc": "🧠 Neural Scanner v3 — Full brain scan",        "bot_exclusive": True},
                "neural_overdrive":        {"type": "device",   "cost": {"sp": 400},      "effect": "neural_max",          "desc": "🧠 Neural Overdrive — 200% brain power",        "bot_exclusive": True},
                # ── TITANIUM ARMOR SET ────────────────────────────────
                "titanium_helmet":         {"type": "helmet",   "cost": {"sp": 30},       "effect": "armor_head_5",        "desc": "🪖 Titanium Helmet — +5 defense",               "bot_exclusive": True},
                "titanium_chestplate":     {"type": "chest",    "cost": {"sp": 45},       "effect": "armor_chest_8",       "desc": "🛡️ Titanium Chestplate — +8 defense",           "bot_exclusive": True},
                "titanium_leggings":       {"type": "legs",     "cost": {"sp": 35},       "effect": "armor_legs_6",        "desc": "🦿 Titanium Leggings — +6 defense",             "bot_exclusive": True},
                "titanium_boots":          {"type": "boots",    "cost": {"sp": 25},       "effect": "armor_feet_4",        "desc": "👢 Titanium Boots — +4 speed",                  "bot_exclusive": True},
                # ── NEON ARMOR SET ────────────────────────────────────
                "neon_helmet":             {"type": "helmet",   "cost": {"sp": 80},       "effect": "neon_head_10",        "desc": "💡 Neon Helmet — +10 glow defense",             "bot_exclusive": True},
                "neon_chestplate":         {"type": "chest",    "cost": {"sp": 120},      "effect": "neon_chest_15",       "desc": "💡 Neon Chestplate — +15 glow defense",         "bot_exclusive": True},
                "neon_leggings":           {"type": "legs",     "cost": {"sp": 100},      "effect": "neon_legs_12",        "desc": "💡 Neon Leggings — +12 glow defense",           "bot_exclusive": True},
                "neon_boots":              {"type": "boots",    "cost": {"sp": 70},       "effect": "neon_feet_8",         "desc": "💡 Neon Boots — +8 glow speed",                 "bot_exclusive": True},
                # ── VOID ARMOR SET ────────────────────────────────────
                "void_helmet":             {"type": "helmet",   "cost": {"sp": 200},      "effect": "void_head_20",        "desc": "🌑 Void Helmet — +20 shadow defense",           "bot_exclusive": True},
                "void_chestplate":         {"type": "chest",    "cost": {"sp": 300},      "effect": "void_chest_30",       "desc": "🌑 Void Chestplate — +30 shadow defense",       "bot_exclusive": True},
                "void_leggings":           {"type": "legs",     "cost": {"sp": 250},      "effect": "void_legs_25",        "desc": "🌑 Void Leggings — +25 shadow defense",         "bot_exclusive": True},
                "void_boots":              {"type": "boots",    "cost": {"sp": 180},      "effect": "void_feet_18",        "desc": "🌑 Void Boots — +18 shadow speed",              "bot_exclusive": True},
                # ── COSMIC WEAPONS ────────────────────────────────────
                "plasma_sword":            {"type": "weapon",   "cost": {"sp": 40},       "effect": "dmg_plasma_12",       "desc": "⚔️ Plasma Sword — 12 energy damage",            "bot_exclusive": True},
                "photon_blade":            {"type": "weapon",   "cost": {"sp": 90},       "effect": "dmg_photon_25",       "desc": "⚔️ Photon Blade — 25 light damage",             "bot_exclusive": True},
                "antimatter_lance":        {"type": "weapon",   "cost": {"sp": 200},      "effect": "dmg_anti_50",         "desc": "⚔️ Antimatter Lance — 50 void damage",          "bot_exclusive": True},
                "singularity_hammer":      {"type": "weapon",   "cost": {"sp": 350},      "effect": "dmg_gravity_75",      "desc": "🔨 Singularity Hammer — 75 gravity damage",     "bot_exclusive": True},
                "supernova_axe":           {"type": "weapon",   "cost": {"sp": 500},      "effect": "dmg_nova_100",        "desc": "🪓 Supernova Axe — 100 stellar damage",         "bot_exclusive": True},
                # ── SP MULTIPLIER CHIPS ───────────────────────────────
                "sp_chip_x2":              {"type": "chip",     "cost": {"sp": 30},       "effect": "sp_mult_2x",          "desc": "💎 SP Chip ×2 — Double SP earnings",            "bot_exclusive": True},
                "sp_chip_x3":              {"type": "chip",     "cost": {"sp": 80},       "effect": "sp_mult_3x",          "desc": "💎 SP Chip ×3 — Triple SP earnings",            "bot_exclusive": True},
                "sp_chip_x5":              {"type": "chip",     "cost": {"sp": 200},      "effect": "sp_mult_5x",          "desc": "💎 SP Chip ×5 — Quintuple SP earnings",         "bot_exclusive": True},
                "sp_chip_x10":             {"type": "chip",     "cost": {"sp": 500},      "effect": "sp_mult_10x",         "desc": "💎 SP Chip ×10 — MEGA SP multiplier",           "bot_exclusive": True},
                # ── XP ACCELERATORS ───────────────────────────────────
                "xp_injector_v1":          {"type": "implant",  "cost": {"sp": 25},       "effect": "xp_boost_50",         "desc": "💉 XP Injector v1 — +50% XP gain",              "bot_exclusive": True},
                "xp_injector_v2":          {"type": "implant",  "cost": {"sp": 70},       "effect": "xp_boost_100",        "desc": "💉 XP Injector v2 — +100% XP gain",             "bot_exclusive": True},
                "xp_injector_v3":          {"type": "implant",  "cost": {"sp": 180},      "effect": "xp_boost_200",        "desc": "💉 XP Injector v3 — +200% XP gain",             "bot_exclusive": True},
                "xp_injector_max":         {"type": "implant",  "cost": {"sp": 450},      "effect": "xp_boost_500",        "desc": "💉 XP Injector MAX — +500% XP gain",            "bot_exclusive": True},
                # ── LUCK ENHANCERS ────────────────────────────────────
                "lucky_clover":            {"type": "trinket",  "cost": {"sp": 15},       "effect": "luck_crit_5",         "desc": "🍀 Lucky Clover — +5% crit chance",             "bot_exclusive": True},
                "rabbits_foot":            {"type": "trinket",  "cost": {"sp": 35},       "effect": "luck_crit_10",        "desc": "🐾 Rabbit's Foot — +10% crit chance",           "bot_exclusive": True},
                "golden_horseshoe":        {"type": "trinket",  "cost": {"sp": 75},       "effect": "luck_crit_20",        "desc": "🧲 Golden Horseshoe — +20% crit chance",        "bot_exclusive": True},
                "chaos_dice":              {"type": "trinket",  "cost": {"sp": 150},      "effect": "luck_crit_35",        "desc": "🎲 Chaos Dice — +35% crit chance",              "bot_exclusive": True},
                "fate_manipulator":        {"type": "trinket",  "cost": {"sp": 300},      "effect": "luck_crit_50",        "desc": "🌀 Fate Manipulator — +50% crit chance",        "bot_exclusive": True},
                # ── PVP GEAR ──────────────────────────────────────────
                "pvp_badge_bronze":        {"type": "badge",    "cost": {"sp": 20},       "effect": "pvp_elo_boost_5",     "desc": "🥉 Bronze PvP Badge — +5 ELO per win",          "bot_exclusive": True},
                "pvp_badge_silver":        {"type": "badge",    "cost": {"sp": 50},       "effect": "pvp_elo_boost_10",    "desc": "🥈 Silver PvP Badge — +10 ELO per win",         "bot_exclusive": True},
                "pvp_badge_gold":          {"type": "badge",    "cost": {"sp": 120},      "effect": "pvp_elo_boost_20",    "desc": "🥇 Gold PvP Badge — +20 ELO per win",           "bot_exclusive": True},
                "pvp_badge_diamond":       {"type": "badge",    "cost": {"sp": 250},      "effect": "pvp_elo_boost_35",    "desc": "💠 Diamond PvP Badge — +35 ELO per win",        "bot_exclusive": True},
                "pvp_badge_champion":      {"type": "badge",    "cost": {"sp": 500},      "effect": "pvp_elo_boost_50",    "desc": "👑 Champion PvP Badge — +50 ELO per win",       "bot_exclusive": True},
                # ── STREAK SHIELDS ────────────────────────────────────
                "streak_shield_wood":      {"type": "shield",   "cost": {"sp": 20},       "effect": "streak_protect_10",   "desc": "🪵 Wood Streak Shield — 10% streak protection", "bot_exclusive": True},
                "streak_shield_iron":      {"type": "shield",   "cost": {"sp": 50},       "effect": "streak_protect_25",   "desc": "⬛ Iron Streak Shield — 25% streak protection",  "bot_exclusive": True},
                "streak_shield_diamond":   {"type": "shield",   "cost": {"sp": 130},      "effect": "streak_protect_50",   "desc": "💎 Diamond Streak Shield — 50% streak save",    "bot_exclusive": True},
                "streak_shield_unbreakable":{"type": "shield",  "cost": {"sp": 300},      "effect": "streak_protect_80",   "desc": "🔒 Unbreakable Shield — 80% streak save",       "bot_exclusive": True},
                # ── SPEED MODULES ─────────────────────────────────────
                "turbo_module_v1":         {"type": "module",   "cost": {"sp": 15},       "effect": "speed_10",            "desc": "⚡ Turbo Module v1 — 10% faster rolls",         "bot_exclusive": True},
                "turbo_module_v2":         {"type": "module",   "cost": {"sp": 40},       "effect": "speed_25",            "desc": "⚡ Turbo Module v2 — 25% faster rolls",         "bot_exclusive": True},
                "turbo_module_v3":         {"type": "module",   "cost": {"sp": 100},      "effect": "speed_50",            "desc": "⚡ Turbo Module v3 — 50% faster rolls",         "bot_exclusive": True},
                "warp_drive":              {"type": "module",   "cost": {"sp": 250},      "effect": "speed_75",            "desc": "🚀 Warp Drive — 75% faster rolls",              "bot_exclusive": True},
                "hyperdrive":              {"type": "module",   "cost": {"sp": 500},      "effect": "speed_max",           "desc": "🌌 Hyperdrive — MAXIMUM SPEED",                 "bot_exclusive": True},
                # ── RESOURCE GENERATORS ───────────────────────────────
                "sp_generator_basic":      {"type": "generator","cost": {"sp": 30},       "effect": "passive_sp_1",        "desc": "🔋 Basic SP Generator — +1 SP/roll",            "bot_exclusive": True},
                "sp_generator_adv":        {"type": "generator","cost": {"sp": 80},       "effect": "passive_sp_3",        "desc": "🔋 Advanced SP Generator — +3 SP/roll",         "bot_exclusive": True},
                "sp_generator_ultra":      {"type": "generator","cost": {"sp": 200},      "effect": "passive_sp_5",        "desc": "🔋 Ultra SP Generator — +5 SP/roll",            "bot_exclusive": True},
                "sp_generator_quantum":    {"type": "generator","cost": {"sp": 500},      "effect": "passive_sp_10",       "desc": "🔋 Quantum SP Generator — +10 SP/roll",         "bot_exclusive": True},
                # ── AURA EFFECTS ──────────────────────────────────────
                "aura_fire":               {"type": "aura",     "cost": {"sp": 40},       "effect": "aura_fire",           "desc": "🔥 Fire Aura — Blazing presence",               "bot_exclusive": True},
                "aura_ice":                {"type": "aura",     "cost": {"sp": 40},       "effect": "aura_ice",            "desc": "❄️ Ice Aura — Frozen presence",                 "bot_exclusive": True},
                "aura_lightning":          {"type": "aura",     "cost": {"sp": 60},       "effect": "aura_lightning",      "desc": "⚡ Lightning Aura — Electrifying",              "bot_exclusive": True},
                "aura_void":               {"type": "aura",     "cost": {"sp": 100},      "effect": "aura_void",           "desc": "🌑 Void Aura — Darkness surrounds",             "bot_exclusive": True},
                "aura_cosmic":             {"type": "aura",     "cost": {"sp": 200},      "effect": "aura_cosmic",         "desc": "🌌 Cosmic Aura — Stars orbit you",              "bot_exclusive": True},
                "aura_divine":             {"type": "aura",     "cost": {"sp": 400},      "effect": "aura_divine",         "desc": "👼 Divine Aura — Heavenly glow",                "bot_exclusive": True},
                "aura_glitch":             {"type": "aura",     "cost": {"sp": 600},      "effect": "aura_glitch",         "desc": "👾 Glitch Aura — Reality bends",                "bot_exclusive": True},
                # ── PET COMPANIONS ────────────────────────────────────
                "pet_robot_dog":           {"type": "pet",      "cost": {"sp": 25},       "effect": "pet_luck_3",          "desc": "🐕 Robot Dog — +3% luck, good boy",             "bot_exclusive": True},
                "pet_cyber_cat":           {"type": "pet",      "cost": {"sp": 25},       "effect": "pet_sp_2",            "desc": "🐱 Cyber Cat — +2 SP per win",                  "bot_exclusive": True},
                "pet_plasma_parrot":       {"type": "pet",      "cost": {"sp": 50},       "effect": "pet_xp_5",            "desc": "🦜 Plasma Parrot — +5 XP per roll",             "bot_exclusive": True},
                "pet_quantum_fox":         {"type": "pet",      "cost": {"sp": 80},       "effect": "pet_crit_5",          "desc": "🦊 Quantum Fox — +5% crit chance",              "bot_exclusive": True},
                "pet_void_serpent":        {"type": "pet",      "cost": {"sp": 150},      "effect": "pet_all_5",           "desc": "🐍 Void Serpent — +5% everything",              "bot_exclusive": True},
                "pet_phoenix":             {"type": "pet",      "cost": {"sp": 300},      "effect": "pet_rebirth",         "desc": "🔥 Phoenix — Resurrects streaks",               "bot_exclusive": True},
                "pet_galaxy_dragon":       {"type": "pet",      "cost": {"sp": 600},      "effect": "pet_ultimate",        "desc": "🐉 Galaxy Dragon — ULTIMATE companion",         "bot_exclusive": True},
                # ── TITLE CARDS ───────────────────────────────────────
                "title_the_machine":       {"type": "title",    "cost": {"sp": 50},       "effect": "title",               "desc": "📛 Title: The Machine",                         "bot_exclusive": True},
                "title_algorithm":         {"type": "title",    "cost": {"sp": 50},       "effect": "title",               "desc": "📛 Title: The Algorithm",                        "bot_exclusive": True},
                "title_binary_beast":      {"type": "title",    "cost": {"sp": 100},      "effect": "title",               "desc": "📛 Title: Binary Beast",                         "bot_exclusive": True},
                "title_digital_overlord":  {"type": "title",    "cost": {"sp": 200},      "effect": "title",               "desc": "📛 Title: Digital Overlord",                     "bot_exclusive": True},
                "title_neural_god":        {"type": "title",    "cost": {"sp": 400},      "effect": "title",               "desc": "📛 Title: Neural God",                           "bot_exclusive": True},
                "title_singularity":       {"type": "title",    "cost": {"sp": 800},      "effect": "title",               "desc": "📛 Title: The Singularity",                      "bot_exclusive": True},
                # ── MYSTERY BOXES ─────────────────────────────────────
                "mystery_box_common":      {"type": "box",      "cost": {"sp": 10},       "effect": "random_common",       "desc": "📦 Common Mystery Box",                          "bot_exclusive": True},
                "mystery_box_rare":        {"type": "box",      "cost": {"sp": 30},       "effect": "random_rare",         "desc": "📦 Rare Mystery Box",                            "bot_exclusive": True},
                "mystery_box_epic":        {"type": "box",      "cost": {"sp": 80},       "effect": "random_epic",         "desc": "📦 Epic Mystery Box",                            "bot_exclusive": True},
                "mystery_box_legendary":   {"type": "box",      "cost": {"sp": 200},      "effect": "random_legendary",    "desc": "📦 Legendary Mystery Box",                       "bot_exclusive": True},
                "mystery_box_mythic":      {"type": "box",      "cost": {"sp": 500},      "effect": "random_mythic",       "desc": "📦✨ MYTHIC Mystery Box",                        "bot_exclusive": True},
                # ── CONSUMABLE BOOSTERS ───────────────────────────────
                "booster_luck_1h":         {"type": "booster",  "cost": {"sp": 15},       "effect": "boost_luck_1h",       "desc": "🧪 1h Luck Potion — Boosted luck",              "bot_exclusive": True},
                "booster_sp_1h":           {"type": "booster",  "cost": {"sp": 15},       "effect": "boost_sp_1h",         "desc": "🧪 1h SP Potion — Double SP",                   "bot_exclusive": True},
                "booster_xp_1h":           {"type": "booster",  "cost": {"sp": 15},       "effect": "boost_xp_1h",         "desc": "🧪 1h XP Potion — Double XP",                   "bot_exclusive": True},
                "booster_mega_30m":        {"type": "booster",  "cost": {"sp": 40},       "effect": "boost_mega_30m",      "desc": "🧪 30m MEGA Potion — Everything boosted",        "bot_exclusive": True},
                "booster_ultra_10m":       {"type": "booster",  "cost": {"sp": 100},      "effect": "boost_ultra_10m",     "desc": "🧪 10m ULTRA Potion — INSANE boosts",            "bot_exclusive": True},
                # ── COSMETIC SKINS ────────────────────────────────────
                "skin_chrome":             {"type": "skin",     "cost": {"sp": 30},       "effect": "skin",                "desc": "🪞 Chrome Skin",                                "bot_exclusive": True},
                "skin_holographic":        {"type": "skin",     "cost": {"sp": 60},       "effect": "skin",                "desc": "🌈 Holographic Skin",                           "bot_exclusive": True},
                "skin_galaxy":             {"type": "skin",     "cost": {"sp": 100},      "effect": "skin",                "desc": "🌌 Galaxy Skin",                                "bot_exclusive": True},
                "skin_matrix":             {"type": "skin",     "cost": {"sp": 150},      "effect": "skin",                "desc": "💚 Matrix Skin",                                "bot_exclusive": True},
                "skin_golden":             {"type": "skin",     "cost": {"sp": 250},      "effect": "skin",                "desc": "✨ Golden Skin",                                 "bot_exclusive": True},
                "skin_diamond":            {"type": "skin",     "cost": {"sp": 400},      "effect": "skin",                "desc": "💎 Diamond Skin",                               "bot_exclusive": True},
                "skin_glitch_reality":     {"type": "skin",     "cost": {"sp": 700},      "effect": "skin",                "desc": "👾 Glitched Reality Skin",                      "bot_exclusive": True},
                # ── EMOTE PACKS ───────────────────────────────────────
                "emote_pack_basic":        {"type": "emote",    "cost": {"sp": 10},       "effect": "emotes_basic",        "desc": "😀 Basic Emote Pack (5 emotes)",                "bot_exclusive": True},
                "emote_pack_rare":         {"type": "emote",    "cost": {"sp": 30},       "effect": "emotes_rare",         "desc": "😎 Rare Emote Pack (8 emotes)",                 "bot_exclusive": True},
                "emote_pack_epic":         {"type": "emote",    "cost": {"sp": 70},       "effect": "emotes_epic",         "desc": "🤩 Epic Emote Pack (12 emotes)",                "bot_exclusive": True},
                "emote_pack_legendary":    {"type": "emote",    "cost": {"sp": 150},      "effect": "emotes_legendary",    "desc": "🤯 Legendary Emote Pack (20 emotes)",           "bot_exclusive": True},
                # ── ULTIMATE ITEMS ────────────────────────────────────
                "infinity_core":           {"type": "core",     "cost": {"sp": 1000},     "effect": "infinite_power",      "desc": "♾️ Infinity Core — Unlimited power source",     "bot_exclusive": True},
                "time_manipulator":        {"type": "core",     "cost": {"sp": 1500},     "effect": "time_warp",           "desc": "⏰ Time Manipulator — Bend time itself",         "bot_exclusive": True},
                "reality_engine":          {"type": "core",     "cost": {"sp": 2000},     "effect": "reality_bend",        "desc": "🌀 Reality Engine — Rewrite the rules",          "bot_exclusive": True},
                "omega_protocol":          {"type": "core",     "cost": {"sp": 3000},     "effect": "omega",               "desc": "Ω Omega Protocol — The final upgrade",           "bot_exclusive": True},
                "god_mode_chip":           {"type": "core",     "cost": {"sp": 5000},     "effect": "god_mode",            "desc": "🌟 GOD MODE CHIP — Transcend everything",       "bot_exclusive": True},
            }
            
            # Sorted item catalogue by cost for progressive buying
            bot_shop_order = sorted(bot_exclusive_items.keys(), 
                                     key=lambda x: bot_exclusive_items[x]["cost"].get("sp", 0))
            
            # ── Load or initialize bot state ─────────────────────────────
            stats_file = f"user_{bot_name}_stats.json"
            data_file = f"user_{bot_name}_data.json"
            ach_file = f"user_{bot_name}_achievements.json"
            equip_file = f"user_{bot_name}_equipment.json"
            history_file = f"user_{bot_name}_history.json"
            pvp_file = f"user_{bot_name}_pvp.json"
            progression_file = f"user_{bot_name}_progression.json"
            
            stats = self._load_json(stats_file, {
                "total_rolls": 0, "total_wins": 0, "best_streak": 0,
                "current_streak": 0, "fastest_win": None, "slowest_win": 0,
                "avg_rolls_per_win": 0, "property_discoveries": {}, "play_time": 0,
                "start_time": time.time()
            })
            
            user_data = self._load_json(data_file, {
                "player_level": 1, "player_xp": 0, "sp": 0, "sp_plus": 0,
                "sp_x": 0, "sp_caret": 0, "difficulty": "normal",
                "current_specialization": None, "current_game_mode": "Classic",
                "challenges": {}
            })
            
            achievements = self._load_json(ach_file, default_achievements)
            # Merge any missing achievements
            for k, v in default_achievements.items():
                if k not in achievements:
                    achievements[k] = v
            
            equipment = self._load_json(equip_file, {"owned": [], "equipped": {}, "sp": 0,
                                                      "sp_plus": 0, "sp_x": 0, "sp_caret": 0})
            
            history = self._load_json(history_file, [])
            if not isinstance(history, list):
                history = []
            
            pvp_data = self._load_json(pvp_file, {
                "elo": 1000, "wins": 0, "losses": 0, "draws": 0,
                "streak": 0, "best_streak": 0, "history": []
            })
            
            progression = self._load_json(progression_file, {
                "prestige_level": 0, "prestige_points": 0,
                "specialization": None, "mechanic_unlocks": {}
            })
            
            # Sync currency from equipment file (that's where it's stored)
            sp = equipment.get("sp", user_data.get("sp", 0))
            sp_plus = equipment.get("sp_plus", user_data.get("sp_plus", 0))
            sp_x = equipment.get("sp_x", user_data.get("sp_x", 0))
            sp_caret = equipment.get("sp_caret", user_data.get("sp_caret", 0))
            
            total_rolls = stats.get("total_rolls", 0)
            total_wins = stats.get("total_wins", 0)
            current_streak = stats.get("current_streak", 0)
            best_streak = stats.get("best_streak", 0)
            fastest_win = stats.get("fastest_win")
            slowest_win = stats.get("slowest_win", 0)
            level = user_data.get("player_level", 1)
            xp = user_data.get("player_xp", 0)
            xp_needed = 50 + (level - 1) * 25
            discoveries = stats.get("property_discoveries", {})
            pvp_elo = pvp_data.get("elo", 1000)
            pvp_wins = pvp_data.get("wins", 0)
            pvp_losses = pvp_data.get("losses", 0)
            pvp_streak = pvp_data.get("streak", 0)
            pvp_best_streak = pvp_data.get("best_streak", 0)
            owned_items = equipment.get("owned", [])
            equipped_items = equipment.get("equipped", {})
            
            round_rolls = 0  # rolls in current "round"
            
            # Generate initial target
            num_target_props = min(2 + total_wins // 15, 6)
            target = set(random.sample(possible_properties, min(num_target_props, len(possible_properties))))
            
            # ═══════════════════════════════════════════════════════════
            # 🤖 BOT SUPERCHARGE CONSTANTS
            # ═══════════════════════════════════════════════════════════
            BOT_WIN_CHANCE = 0.35           # 35% chance to FORCE a win each roll (vs ~2-5% normal)
            BOT_CRITICAL_CHANCE = 0.18      # 18% crit chance (vs 3% for normal players)
            BOT_SP_MULTIPLIER = 8           # 8x SP earnings
            BOT_XP_MULTIPLIER = 5           # 5x XP earnings
            BOT_PVP_WIN_CHANCE = 0.75       # 75% PvP win rate (vs 50/50)
            BOT_PVP_FREQUENCY = 8           # PvP every 8 wins (vs 50)
            BOT_SHOP_FREQUENCY = 5          # Shop every 5 wins (vs 20)
            BOT_SAVE_EVERY = 2              # Save every 2 rolls for max spectator visibility
            BOT_ROLL_DELAY_MIN = 0.04       # Minimum delay between rolls (FAST)
            BOT_ROLL_DELAY_MAX = 0.15       # Maximum delay between rolls (FAST)
            
            def _save_all():
                """Persist all bot state to disk"""
                stats["total_rolls"] = total_rolls
                stats["total_wins"] = total_wins
                stats["current_streak"] = current_streak
                stats["best_streak"] = best_streak
                stats["fastest_win"] = fastest_win
                stats["slowest_win"] = slowest_win
                stats["property_discoveries"] = discoveries
                if total_wins > 0:
                    stats["avg_rolls_per_win"] = round(total_rolls / total_wins, 1)
                stats["play_time"] = stats.get("play_time", 0) + 1
                
                user_data["player_level"] = level
                user_data["player_xp"] = xp
                user_data["sp"] = sp
                user_data["sp_plus"] = sp_plus
                user_data["sp_x"] = sp_x
                user_data["sp_caret"] = sp_caret
                user_data["current_game_mode"] = "Classic"
                user_data["difficulty"] = "normal"
                
                equipment["sp"] = sp
                equipment["sp_plus"] = sp_plus
                equipment["sp_x"] = sp_x
                equipment["sp_caret"] = sp_caret
                equipment["owned"] = owned_items
                equipment["equipped"] = equipped_items
                
                self._save_json(stats_file, stats)
                self._save_json(data_file, user_data)
                self._save_json(ach_file, achievements)
                self._save_json(equip_file, equipment)
                self._save_json(pvp_file, pvp_data)
                self._save_json(progression_file, progression)
                # Trim history to last 500
                self._save_json(history_file, history[-500:])
                
                # Update last played
                accts = self.account_manager._load_accounts()
                if bot_name in accts:
                    accts[bot_name]["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    accts[bot_name]["play_time"] = accts[bot_name].get("play_time", 0) + 1
                    self.account_manager.accounts = accts
                    self.account_manager._save_accounts()
            
            # ── Main bot loop — SUPERCHARGED ──────────────────────────────
            roll_batch = 0  # count rolls between saves
            
            while not stop_event.is_set():
                try:
                    # === SIMULATE A ROLL ===
                    s = self._generate_random_string()
                    properties = self._analyze_string(s)
                    total_rolls += 1
                    round_rolls += 1
                    
                    # Track property discoveries
                    prop_display_map = {
                        "has_numbers": "Has Numbers", "has_symbols": "Has Symbols",
                        "has_uppercase": "Has Uppercase", "has_lowercase": "Has Lowercase",
                        "is_long": "Is Long", "has_spaces": "Has Spaces",
                        "has_operators": "Has Operators", "has_multiple_words": "Has Multiple Words",
                        "has_repeats": "Has Repeats", "starts_with_letter": "Starts With Letter",
                        "ends_with_symbol": "Ends With Symbol", "has_punctuation": "Has Punctuation",
                        "has_vowels": "Has Vowels", "is_very_long": "Is Very Long",
                        "has_consecutive_letters": "Has Consecutive Letters"
                    }
                    for prop in properties:
                        dn = prop_display_map.get(prop, prop)
                        discoveries[dn] = discoveries.get(dn, 0) + 1
                    
                    matches = len(properties & target)
                    
                    # 🤖 BOT SUPER LUCK: Force wins way more often!
                    # Normal win = exact property match. Bot can just FORCE it.
                    natural_win = (properties == target)
                    forced_win = (not natural_win) and (random.random() < BOT_WIN_CHANCE)
                    won = natural_win or forced_win
                    
                    if forced_win:
                        # Fake the match — pretend properties matched perfectly
                        matches = len(target)
                        properties = set(target)  # Override so history looks legit
                    
                    # Calculate SP type
                    str_len = len(s)
                    if str_len >= 40:
                        sp_type, sp_display = "sp_caret", "SP^"
                    elif str_len >= 30:
                        sp_type, sp_display = "sp_x", "SPx"
                    elif str_len >= 15:
                        sp_type, sp_display = "sp_plus", "SP+"
                    else:
                        sp_type, sp_display = "sp", "SP"
                    
                    sp_earned = 0
                    xp_earned = 0
                    # 🤖 BOT SUPER CRIT: Way higher crit chance
                    is_critical = random.random() < BOT_CRITICAL_CHANCE
                    
                    # Record history entry
                    entry = {
                        "number": total_rolls, "string": s,
                        "properties": list(properties), "target_properties": list(target),
                        "matches": matches, "total_needed": len(target),
                        "timestamp": datetime.datetime.now().isoformat(),
                        "won": won, "sp_earned": 0, "xp_earned": 0,
                        "is_critical": is_critical,
                        "match_pct": round(matches / max(1, len(target)) * 100, 1)
                    }
                    
                    if won:
                        total_wins += 1
                        current_streak += 1
                        if current_streak > best_streak:
                            best_streak = current_streak
                        
                        # Track fastest/slowest win
                        if fastest_win is None or round_rolls < fastest_win:
                            fastest_win = round_rolls
                        if round_rolls > slowest_win:
                            slowest_win = round_rolls
                        
                        # 🤖 BOT MEGA SP: Massively boosted earnings
                        base_sp = {"sp": 5, "sp_plus": 10, "sp_x": 15, "sp_caret": 20}.get(sp_type, 5)
                        streak_mult = 1.0 + min(current_streak, 10) * 0.05
                        sp_earned = int(base_sp * streak_mult * BOT_SP_MULTIPLIER)
                        if is_critical:
                            sp_earned *= 3
                        
                        if sp_type == "sp":
                            sp += sp_earned
                        elif sp_type == "sp_plus":
                            sp_plus += sp_earned
                        elif sp_type == "sp_x":
                            sp_x += sp_earned
                        elif sp_type == "sp_caret":
                            sp_caret += sp_earned
                        
                        # 🤖 BOT MEGA XP: Way faster leveling
                        xp_earned = int((10 + (sp_earned // 5)) * BOT_XP_MULTIPLIER)
                        if is_critical:
                            xp_earned *= 3
                        xp += xp_earned
                        
                        # Level up check (bots level up FAST)
                        while xp >= xp_needed:
                            xp -= xp_needed
                            level += 1
                            xp_needed = 50 + (level - 1) * 25
                        
                        entry["sp_earned"] = sp_earned
                        entry["xp_earned"] = xp_earned
                        
                        # === UNLOCK ACHIEVEMENTS ===
                        ach_checks = {
                            "first_win": total_wins >= 1,
                            "ten_wins": total_wins >= 10,
                            "fifty_wins": total_wins >= 50,
                            "hundred_wins": total_wins >= 100,
                            "fivehundred_wins": total_wins >= 500,
                            "hundred_rolls": total_rolls >= 100,
                            "fivehundred_rolls": total_rolls >= 500,
                            "thousand_rolls": total_rolls >= 1000,
                            "perfectionist": best_streak >= 3,
                            "streak_breaker": best_streak >= 5,
                            "on_fire": best_streak >= 10,
                            "speed_demon": round_rolls <= 30,
                            "lightning": round_rolls <= 10,
                            "sp_collector": sp >= 50,
                            "sp_hoarder": sp >= 500,
                            "property_master": len(discoveries) >= 10,
                            "explorer": len(discoveries) >= 15,
                            "first_craft": len(owned_items) >= 1,
                            "pvp_debut": pvp_wins >= 1,
                        }
                        now_hour = datetime.datetime.now().hour
                        if 0 <= now_hour < 6:
                            ach_checks["night_owl"] = True
                        
                        for ach_id, condition in ach_checks.items():
                            if ach_id in achievements and condition:
                                if not achievements[ach_id].get("unlocked"):
                                    achievements[ach_id]["unlocked"] = True
                                    achievements[ach_id]["unlock_time"] = datetime.datetime.now().isoformat()
                        
                        # === 🤖 BOT MEGA SHOP — Buy from exclusive catalogue frequently ===
                        if total_wins % BOT_SHOP_FREQUENCY == 0 and total_wins > 0:
                            # Try to buy the next cheapest item we don't own
                            bought_something = False
                            for item_id in bot_shop_order:
                                if item_id not in owned_items:
                                    item_data = bot_exclusive_items[item_id]
                                    cost = item_data["cost"].get("sp", 0)
                                    if sp >= cost:
                                        sp -= cost
                                        owned_items.append(item_id)
                                        # Equip by type
                                        item_type = item_data["type"]
                                        equipped_items[item_type] = item_id
                                        bought_something = True
                                        break
                            
                            # Also check normal equipment catalogue if nothing exclusive to buy
                            if not bought_something:
                                normal_catalogue = [
                                    "iron_gauntlet", "basic_device", "steel_gauntlet", "analysis_device",
                                    "fortune_device", "silver_gauntlet", "gold_gauntlet", "mastery_device",
                                ]
                                for item_id in normal_catalogue:
                                    if item_id not in owned_items:
                                        recipe = self.equipment_recipes.get(item_id)
                                        if recipe:
                                            cost = recipe.get("cost", {})
                                            can_buy = True
                                            if cost.get("sp", 0) > sp: can_buy = False
                                            if cost.get("sp_plus", 0) > sp_plus: can_buy = False
                                            if cost.get("sp_x", 0) > sp_x: can_buy = False
                                            if cost.get("sp_caret", 0) > sp_caret: can_buy = False
                                            if can_buy:
                                                sp -= cost.get("sp", 0)
                                                sp_plus -= cost.get("sp_plus", 0)
                                                sp_x -= cost.get("sp_x", 0)
                                                sp_caret -= cost.get("sp_caret", 0)
                                                owned_items.append(item_id)
                                                item_type = recipe.get("type", "device")
                                                equipped_items[item_type] = item_id
                                        break
                        
                        # === 🤖 BOT PVP — Way more frequent, way better win rate ===
                        if total_wins % BOT_PVP_FREQUENCY == 0 and total_wins > 0:
                            pvp_won = random.random() < BOT_PVP_WIN_CHANCE
                            if pvp_won:
                                pvp_wins += 1
                                pvp_elo += random.randint(20, 45)
                                pvp_streak += 1
                                if pvp_streak > pvp_best_streak:
                                    pvp_best_streak = pvp_streak
                            else:
                                pvp_losses += 1
                                pvp_elo = max(100, pvp_elo - random.randint(5, 15))
                                pvp_streak = 0
                            pvp_data["elo"] = pvp_elo
                            pvp_data["wins"] = pvp_wins
                            pvp_data["losses"] = pvp_losses
                            pvp_data["streak"] = pvp_streak
                            pvp_data["best_streak"] = pvp_best_streak
                        
                        # New round — pick new target
                        num_target_props = min(2 + total_wins // 15, 6)
                        target = set(random.sample(possible_properties, min(num_target_props, len(possible_properties))))
                        round_rolls = 0
                    else:
                        # Loss — break streak sometimes (realistic)
                        if round_rolls > 100 and random.random() < 0.01:
                            current_streak = 0
                    
                    history.append(entry)
                    if len(history) > 500:
                        history = history[-500:]
                    
                    # 🤖 Save very frequently for max spectator visibility
                    roll_batch += 1
                    if roll_batch >= BOT_SAVE_EVERY:
                        roll_batch = 0
                        _save_all()
                    
                    # 🤖 SUPER FAST — barely any delay between rolls
                    delay = random.uniform(BOT_ROLL_DELAY_MIN, BOT_ROLL_DELAY_MAX)
                    stop_event.wait(delay)
                    
                except Exception as e:
                    # Don't crash the bot on errors, just skip and continue
                    time.sleep(0.5)
            
            # Final save when stopping
            _save_all()
        
        # Start the bot thread
        t = threading.Thread(target=_bot_loop, daemon=True, name=f"bot_{bot_name}")
        t.start()
        return True, f"🤖 SUPERCHARGED Bot '{bot_name}' started! 35% win rate | 8x SP | 18% crit | 100+ exclusive items"
    
    def _stop_bot_player(self, bot_name="BotPlayer"):
        """Stop a running bot player"""
        if not hasattr(self, '_bot_threads') or bot_name not in self._bot_threads:
            return False, f"Bot '{bot_name}' is not running."
        self._bot_threads[bot_name].set()  # Signal stop
        del self._bot_threads[bot_name]
        return True, f"Bot '{bot_name}' stopped."
        """Calculate SP type and display name based on string length"""
        if string_length >= 40:
            return ("sp_caret", "SP^")
        elif string_length >= 30:
            return ("sp_x", "SPx")
        elif string_length >= 15:
            return ("sp_plus", "SP+")
        else:
            return ("sp", "SP")
    
    def _update_sp_label(self):
        """Update the SP label with current SP values"""
        sp_text = f"{self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}"
        if hasattr(self, 'sp_label'):
            self.sp_label.config(text=sp_text)
    
    def _setup_game_after_login(self):
        """Setup game GUI and start mainloop after successful login"""
        # Reload stats for the logged-in user
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        self.roll_count = self.stats.get("total_rolls", 0)
        self.wins_count = self.stats.get("total_wins", 0)
        self.rolls_history = self._load_history()
        self.equipment_inventory = self._load_equipment()
        
        self._setup_gui()
        try:
            self._play_startup_sound()
        except Exception as e:
            print(f"Error playing startup sound: {e}")
        
        # Update labels with loaded stats
        self.roll_label.config(text=str(self.roll_count))
        self.wins_label.config(text=str(self.wins_count))
        self._update_sp_label()
        
        # Start the event loop
        self.root.mainloop()


if __name__ == "__main__":
    RollingGame()
