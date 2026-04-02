import random
import string
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import threading
import winsound
import json
import os
from datetime import datetime
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

class AccountManager:
    """Handles user account management"""
    def __init__(self):
        self.accounts_file = "accounts.json"
        self.remembered_accounts_file = "remembered_accounts.json"
        self.current_user = None
        self.accounts = self._load_accounts()
        self.remembered_accounts = self._load_remembered_accounts()
    
    def _load_accounts(self):
        """Load all accounts from file"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_accounts(self):
        """Save all accounts to file"""
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f, indent=2)
    
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
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        account["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_accounts()
        self._remember_account(username)  # Remember this account
        return True, "Login successful"
    
    def _load_remembered_accounts(self):
        """Load remembered accounts list"""
        if os.path.exists(self.remembered_accounts_file):
            try:
                with open(self.remembered_accounts_file, 'r') as f:
                    data = json.load(f)
                    return data.get("remembered", [])
            except:
                return []
        return []
    
    def _save_remembered_accounts(self):
        """Save remembered accounts list"""
        with open(self.remembered_accounts_file, 'w') as f:
            json.dump({"remembered": self.remembered_accounts}, f, indent=2)
    
    def _remember_account(self, username):
        """Add username to remembered accounts"""
        if username not in self.remembered_accounts:
            self.remembered_accounts.insert(0, username)
            # Keep only last 5 remembered accounts
            self.remembered_accounts = self.remembered_accounts[:5]
            self._save_remembered_accounts()
    
    def forget_account(self, username):
        """Remove username from remembered accounts"""
        if username in self.remembered_accounts:
            self.remembered_accounts.remove(username)
            self._save_remembered_accounts()
    
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

class RollingGame:
    def __init__(self, username=None):
        # Account system
        self.account_manager = AccountManager()
        self.current_username = username
        
        self.roll_count = 0
        self.rolls_history = []
        self.target_properties = set()
        self.game_won = False
        self.auto_rolling = False
        
        # Auto-roll Speed Control (NO DELAYS!)
        self.autoroll_speed = 100  # Speed in ms (lower = faster)
        self.autoroll_min_speed = 10  # Minimum 10ms
        self.autoroll_max_speed = 2000  # Maximum 2000ms
        self.wins_count = 0
        self.current_theme = "dark"
        self.sound_enabled = True
        self.animations_enabled = True
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        self.tutorial_mode = False
        self.tutorial_step = 0
        
        # Difficulty setting
        self.difficulty = "normal"        
        # April Fools Event (v1.67)
        self.april_fools_active = True
        self.april_fools_mode = "chaos"  # chaos, normal, hilarious
        self.prank_count = 0
        self.pranks_triggered = []
        self.easter_eggs_found = 0
        self.troll_level = 0
        
        # v1.67 Special Items & Features
        self.john_pork_elixir = {"count": 0, "sp_boost": 67}
        self.facebook_test_mode = False
        self.dev_console_open = False
        self.v167_language = "bussin"
        
        # v1.677676767... (EXTENDED VERSION - GENUINE THE MOST TUFF THING EVER) - INIT EARLY!
        self.version_1_67_mode = self._check_april_fools_or_v167_mode()
        self.v167_equipment_unlocked = self.version_1_67_mode
        self.purple_text_property = self.version_1_67_mode  # Purple text property active on April Fools
        self._init_april_fools_pranks()  # Initialize pranks before daily challenges
        self._init_skill_tree()
        self._init_tournaments()
        self._init_dungeons()
        self._init_seasonal_system()
        self._init_daily_quests()
        self._init_prestige_system()
        self._init_pvp_system()
        self._init_collection_system()
        self._init_cosmetics()
        self._init_marketplace()
        self._init_guilds()
        
        # Daily Challenge System (AFTER v1.67 mode is set)
        self.daily_challenges = self._init_daily_challenges()
        self.challenge_progress = self._load_challenge_progress()
        
        # Game Modes & Tournaments
        self.game_modes = {
            "Classic": {"name": "Classic", "desc": "Standard gameplay", "multiplier": 1.0},
            "Speed Run": {"name": "Speed Run", "desc": "10 wins fast", "multiplier": 1.5},
            "Hardcore": {"name": "Hardcore", "desc": "One loss = game over", "multiplier": 2.0},
            "Victory Royale 1.67": {"name": "Victory Royale 1.67", "desc": "Guess sequence is SUPER TUFF - JS PEAK ENERGY", "multiplier": 2.5},
        }
        self.current_mode = "Classic"
        self.tournaments = {
            "weekly": {"name": "Weekly", "rounds": 5, "prize": 50},
            "monthly": {"name": "Monthly", "rounds": 10, "prize": 200},
        }
        self.tournament_wins = 0
        self.current_tournament = None
        
        # Difficulty setting
        self.difficulty = "normal"
        
        # SP and Equipment System
        self.sp = 0  # Regular SP (5 characters)
        self.sp_plus = 0  # SP+ (10 characters)
        self.sp_x = 0  # SPx (20 characters)
        self.sp_caret = 0  # SP^ (40+ characters)
        self.equipped_gauntlet = None  # Left hand
        self.equipped_device = None  # Right hand
        self.equipment_inventory = self._load_equipment()
        self._init_equipment_recipes()

        
        # Analytics
        self.total_rolls_ever = 0
        self.total_wins_ever = 0
        
        # Initialize game
        self._generate_target()
        self.possible_properties = [
            "has_numbers", "has_symbols", "has_uppercase", "has_lowercase", "is_long",
            "has_spaces", "has_operators", "has_multiple_words", "has_repeats",
            "starts_with_letter", "ends_with_symbol", "has_punctuation", "has_vowels",
            "is_very_long", "has_consecutive_letters"
        ]
        self._setup_gui()
        self._play_startup_sound()

    
    def _init_equipment_recipes(self):
        """Initialize equipment crafting recipes"""
        self.equipment_recipes = {
            "iron_gauntlet": {"type": "gauntlet", "cost": {"sp": 3}, "effect": "roll_count - 1", "desc": "Reduce rolls by 1"},
            "steel_gauntlet": {"type": "gauntlet", "cost": {"sp_plus": 1}, "effect": "win_bonus + 3", "desc": "Gain 3 bonus rolls"},
            "silver_gauntlet": {"type": "gauntlet", "cost": {"sp_x": 1}, "effect": "accuracy + 10%", "desc": "+10% property accuracy"},
            "gold_gauntlet": {"type": "gauntlet", "cost": {"sp_x": 2}, "effect": "sp_gain + 25%", "desc": "+25% SP gained"},
            "obsidian_gauntlet": {"type": "gauntlet", "cost": {"sp_caret": 1}, "effect": "double_sp", "desc": "Double all SP earned"},
            "basic_device": {"type": "device", "cost": {"sp": 2}, "effect": "reroll_free", "desc": "1 free reroll per win"},
            "analysis_device": {"type": "device", "cost": {"sp_plus": 1}, "effect": "see_extra_prop", "desc": "See 1 extra property"},
            "fortune_device": {"type": "device", "cost": {"sp_plus": 2}, "effect": "luck_boost", "desc": "+15% luck in rolls"},
            "mastery_device": {"type": "device", "cost": {"sp_x": 1}, "effect": "fast_analysis", "desc": "Properties reveal 30% faster"},
            "infinity_device": {"type": "device", "cost": {"sp_caret": 1}, "effect": "perfect_vision", "desc": "See all target properties"},
            # v1.677676... LEGENDARY EQUIPMENT (LIMITED EDITION - APRIL FOOLS)
            "thors_hammer": {"type": "gauntlet", "cost": {"sp_caret": 2}, "effect": "ultimate_power", "desc": "⚡ THOR'S HAMMER - ULTRA BUSSIN POWER! +100 SP on hit!", "rarity": "LEGENDARY", "v167_only": True},
            "infinity_gauntlet": {"type": "gauntlet", "cost": {"sp_caret": 3}, "effect": "infinity_control", "desc": "♾️ INFINITY GAUNTLET - PEAK RIZZ ENERGY! Control all properties!", "rarity": "MYTHIC", "v167_only": True},
            "67_gauntlet": {"type": "gauntlet", "cost": {"sp_caret": 1}, "effect": "lucky_67", "desc": "67️⃣ THE 67 GAUNTLET - EZZZ MODE ACTIVATED! Math goes BUSSIN!", "rarity": "EPIC", "v167_only": True},
            "mathematical_gauntlet": {"type": "gauntlet", "cost": {"sp_caret": 1}, "effect": "math_power", "desc": "📐 MATHEMATICAL GAUNTLET - (67/67 + sqrt² + 67+71 - 67-65) = DUPER COOL!", "rarity": "EPIC", "v167_only": True},
        }
    
    def _check_april_fools_or_v167_mode(self):
        """Check if today is April Fools or if v1.67 mode is enabled"""
        from datetime import datetime
        today = datetime.now()
        is_april_fools = (today.month == 4 and today.day in [1, 2])
        return is_april_fools
    
    
    
    def _init_tournaments(self):
        """Initialize comprehensive tournament system"""
        self.tournaments = {
            "weekly": {
                "name": "Weekly Challenge",
                "desc": "5 rounds, win against progressively harder sequences",
                "rounds": 5,
                "prize": 50,
                "type": "elimination",
                "difficulty_multiplier": 1.5,
                "active": True,
                "reset_day": "Monday"
            },
            "monthly": {
                "name": "Monthly Championship",
                "desc": "10 rounds, compete for massive rewards",
                "rounds": 10,
                "prize": 200,
                "type": "bracket",
                "difficulty_multiplier": 2.0,
                "active": True,
                "reset_day": "1st"
            },
            "seasonal": {
                "name": "Seasonal Tournament",
                "desc": "Compete across 30 days for legendary rewards",
                "rounds": 30,
                "prize": 500,
                "type": "points_based",
                "difficulty_multiplier": 2.5,
                "active": True,
                "reset_day": "Monthly"
            },
            "speed_run": {
                "name": "Speed Run Championship",
                "desc": "Complete sequences in minimum rolls",
                "rounds": 10,
                "prize": 100,
                "type": "speed",
                "difficulty_multiplier": 1.8,
                "active": True,
                "reset_day": "Weekly"
            },
            "accuracy": {
                "name": "Accuracy Masters",
                "desc": "Highest accuracy across 20 rounds",
                "rounds": 20,
                "prize": 150,
                "type": "accuracy",
                "difficulty_multiplier": 1.6,
                "active": True,
                "reset_day": "Weekly"
            },
            "endurance": {
                "name": "Endurance Trial",
                "desc": "50 consecutive wins without resets",
                "rounds": 50,
                "prize": 300,
                "type": "endurance",
                "difficulty_multiplier": 2.2,
                "active": True,
                "reset_day": "Monthly"
            }
        }
        self.tournament_stats = {}
        self.current_tournament = None
        self.tournament_round = 0
        self.tournament_wins = 0
        self.tournament_scores = {}
        self.tournament_ranks = {}
        self._init_tournament_scores()
    
    def _init_tournament_scores(self):
        """Initialize tournament score tracking"""
        for t_name in self.tournaments:
            self.tournament_scores[t_name] = 0
            self.tournament_ranks[t_name] = 0
    
    
    def _init_skill_tree(self):
        """Initialize comprehensive skill tree"""
        self.skills = {
            # Offensive Skills
            "keen_eye": {"name": "Keen Eye", "level": 1, "max_level": 10, "cost_base": 5, "effect": "+2% property detection per level"},
            "pattern_master": {"name": "Pattern Master", "level": 1, "max_level": 10, "cost_base": 8, "effect": "+3% win chance per level"},
            "rapid_analysis": {"name": "Rapid Analysis", "level": 1, "max_level": 10, "cost_base": 10, "effect": "-5% rolls per level"},
            "perfect_strike": {"name": "Perfect Strike", "level": 1, "max_level": 5, "cost_base": 15, "effect": "15% chance to instantly win"},
            
            # Defensive Skills
            "shield_mind": {"name": "Shield Mind", "level": 1, "max_level": 10, "cost_base": 5, "effect": "+2% error recovery per level"},
            "stability": {"name": "Stability", "level": 1, "max_level": 10, "cost_base": 7, "effect": "+1% streak preservation per level"},
            "resilience": {"name": "Resilience", "level": 1, "max_level": 5, "cost_base": 12, "effect": "Second chance on loss (once per session)"},
            
            # Economy Skills
            "profit_master": {"name": "Profit Master", "level": 1, "max_level": 10, "cost_base": 6, "effect": "+5% SP gains per level"},
            "fortune_finder": {"name": "Fortune Finder", "level": 1, "max_level": 10, "cost_base": 8, "effect": "+3% rare item drop rate per level"},
            "wealth_accumulation": {"name": "Wealth Accumulation", "level": 1, "max_level": 10, "cost_base": 10, "effect": "+2% multiplier per level"},
            
            # Special Skills
            "legendary_aura": {"name": "Legendary Aura", "level": 1, "max_level": 5, "cost_base": 25, "effect": "Unlock legendary equipment"},
            "time_mastery": {"name": "Time Mastery", "level": 1, "max_level": 3, "cost_base": 30, "effect": "Slow down time (1 second)"},
            "chaos_control": {"name": "Chaos Control", "level": 1, "max_level": 3, "cost_base": 35, "effect": "Control sequence difficulty"},
        }
        self.skill_points = 10
        self.total_skill_points_earned = 10
    
    def upgrade_skill(self, skill_name):
        """Upgrade a skill"""
        if skill_name not in self.skills:
            return False, "Skill not found"
        
        skill = self.skills[skill_name]
        if skill["level"] >= skill["max_level"]:
            return False, "Skill already at max level"
        
        upgrade_cost = skill["cost_base"] * skill["level"]
        if self.sp < upgrade_cost:
            return False, f"Need {upgrade_cost} SP"
        
        self.sp -= upgrade_cost
        skill["level"] += 1
        self.total_skill_points_earned += 1
        return True, f"{skill_name} upgraded to level {skill['level']}"
    
    
    def _init_dungeons(self):
        """Initialize dungeon system"""
        self.dungeons = {
            "easy": {"name": "Training Grounds", "boss": "Training Dummy", "hp": 50, "reward": 25, "difficulty": 1.0},
            "medium": {"name": "Dark Forest", "boss": "Shadow Beast", "hp": 150, "reward": 75, "difficulty": 2.0},
            "hard": {"name": "Dragon's Lair", "boss": "Ancient Dragon", "hp": 300, "reward": 200, "difficulty": 3.0},
            "nightmare": {"name": "Abyss", "boss": "Void Entity", "hp": 500, "reward": 500, "difficulty": 5.0},
        }
        self.current_dungeon = None
        self.current_boss_hp = 0
        self.daily_dungeons_completed = 0
        self.dungeons_completed_total = 0
    
    def enter_dungeon(self, difficulty):
        """Enter a dungeon"""
        if difficulty not in self.dungeons:
            return False, "Dungeon not found"
        
        self.current_dungeon = difficulty
        dungeon = self.dungeons[difficulty]
        self.current_boss_hp = dungeon["hp"]
        return True, f"Entered {dungeon['name']}! Boss: {dungeon['boss']} (HP: {dungeon['hp']})"
    
    def attack_boss(self, damage):
        """Attack dungeon boss"""
        if not self.current_dungeon:
            return False, "Not in a dungeon"
        
        self.current_boss_hp = max(0, self.current_boss_hp - damage)
        dungeon = self.dungeons[self.current_dungeon]
        
        if self.current_boss_hp <= 0:
            reward = int(dungeon["reward"] * dungeon["difficulty"])
            self.sp += reward
            self.dungeons_completed_total += 1
            self.daily_dungeons_completed += 1
            result = f"Boss defeated! +{reward} SP!"
            self.current_dungeon = None
            return True, result
        
        return True, f"Boss HP: {self.current_boss_hp}/{dungeon['hp']}"
    
    def _init_marketplace(self):
        """Initialize player marketplace/trading"""
        self.marketplace_items = {}
        self.marketplace_listings = []
        self.trade_history = []
    
    
    def _init_seasonal_system(self):
        """Initialize seasonal content"""
        self.current_season = 1
        self.season_progress = 0
        self.season_rewards_claimed = []
        self.seasonal_challenges = {
            "win_100": {"name": "Century Wins", "target": 100, "reward": 100, "completed": False},
            "speedrun": {"name": "Lightning Fast", "target": 5, "reward": 50, "completed": False},
            "tournament": {"name": "Tournament Champion", "target": 1, "reward": 75, "completed": False},
            "boss_hunter": {"name": "Boss Slayer", "target": 10, "reward": 100, "completed": False},
        }
    
    def _init_daily_quests(self):
        """Initialize daily quest system"""
        self.daily_quests = {
            "quick_wins": {"name": "Quick Wins", "target": 10, "reward": 20, "progress": 0},
            "accuracy": {"name": "Accuracy Master", "target": 5, "reward": 15, "progress": 0},
            "equipment": {"name": "Equipment Crafter", "target": 1, "reward": 25, "progress": 0},
            "tournament": {"name": "Tournament Play", "target": 1, "reward": 30, "progress": 0},
            "dungeon": {"name": "Dungeon Explorer", "target": 2, "reward": 25, "progress": 0},
        }
        self.quest_completion_date = None
    
    def _init_prestige_system(self):
        """Initialize prestige/advancement system (not rebirth)"""
        self.prestige_level = 0
        self.prestige_points = 0
        self.total_prestige_points_earned = 0
        self.prestige_unlocks = {}
    
    def _init_pvp_system(self):
        """Initialize PvP battle system"""
        self.pvp_rating = 1000  # Elo rating
        self.pvp_wins = 0
        self.pvp_losses = 0
        self.pvp_streak = 0
        self.pvp_opponents = []
    
    def _init_collection_system(self):
        """Initialize collection/trophy system"""
        self.collection = {
            "rare_sequences": [],
            "achievements_earned": [],
            "equipment_collected": [],
            "bosses_defeated": [],
            "tournaments_won": [],
        }
    
    def simulate_pvp_battle(self, opponent_skill=50):
        """Simulate PvP battle"""
        player_score = self.wins_count + (self.skill_points * 5)
        opponent_score = opponent_skill + random.randint(10, 50)
        
        if player_score > opponent_score:
            self.pvp_wins += 1
            self.pvp_streak += 1
            self.pvp_rating = min(3000, self.pvp_rating + 25)
            reward = int(50 * (1 + self.pvp_streak * 0.1))
            self.sp += reward
            return True, f"Victory! +{reward} SP! Rating: {self.pvp_rating}"
        else:
            self.pvp_losses += 1
            self.pvp_streak = 0
            self.pvp_rating = max(800, self.pvp_rating - 15)
            return False, f"Defeat! Rating: {self.pvp_rating}"
    
    def complete_daily_quest(self, quest_name):
        """Complete a daily quest"""
        if quest_name not in self.daily_quests:
            return False, "Quest not found"
        
        quest = self.daily_quests[quest_name]
        if quest["progress"] >= quest["target"]:
            return False, "Quest already complete"
        
        quest["progress"] += 1
        if quest["progress"] >= quest["target"]:
            self.sp += quest["reward"]
            return True, f"Quest complete! +{quest['reward']} SP!"
        
        return True, f"{quest['name']}: {quest['progress']}/{quest['target']}"
    
    def _init_cosmetics(self):
        """Initialize cosmetic system"""
        self.cosmetics = {
            "themes": ["Dark", "Light", "Matrix", "Neon", "Forest", "Ocean"],
            "current_theme": "Dark",
            "titles": ["Novice", "Adept", "Expert", "Master", "Legend", "Mythic"],
            "current_title": "Novice",
            "particles": ["none", "stars", "fire", "ice", "lightning"],
            "current_particles": "none",
        }

    def _init_guilds(self):
        """Initialize guild system"""
        self.guilds = {}
        self.current_guild = None
        self.guild_level = 0
        self.guild_contribution = 0

    def earn_skill_points(self, amount=1):
        """Earn skill points from tournaments/achievements"""
        self.skill_points += amount
        self.total_skill_points_earned += amount

    def participate_in_tournament(self, tournament_name):
        """Start a tournament"""
        if tournament_name not in self.tournaments:
            return False, "Tournament not found"
        
        tournament = self.tournaments[tournament_name]
        if not tournament["active"]:
            return False, "Tournament is not active"
        
        self.current_tournament = tournament_name
        self.tournament_round = 0
        self.tournament_wins = 0
        return True, f"Joined {tournament['name']}!"
    
    def complete_tournament_round(self, rounds_taken):
        """Complete a tournament round"""
        if not self.current_tournament:
            return None
        
        tournament = self.tournaments[self.current_tournament]
        self.tournament_round += 1
        
        # Calculate points based on tournament type
        if tournament["type"] == "speed":
            points = max(0, 100 - rounds_taken * 2)
        elif tournament["type"] == "accuracy":
            points = 50 + self.roll_count
        elif tournament["type"] == "endurance":
            points = 100 + (self.tournament_round * 10)
        else:
            points = 50 + (tournament["difficulty_multiplier"] * 10)
        
        self.tournament_scores[self.current_tournament] += points
        self.tournament_wins += 1
        
        # Check if tournament complete
        if self.tournament_round >= tournament["rounds"]:
            reward = int(tournament["prize"] * tournament["difficulty_multiplier"])
            self.sp += reward
            result = f"Tournament Complete! +{reward} SP!"
            self.current_tournament = None
            return result
        
        return f"Round {self.tournament_round}/{tournament['rounds']} - +{points} pts"

    def _init_april_fools_pranks(self):
        """Initialize April Fools pranks"""
        self.pranks = {
            "reverse_colors": {"name": "Reverse Colors", "chance": 0.05, "active": False},
            "backwards_text": {"name": "Backwards Text", "chance": 0.08, "active": False},
            "upside_down": {"name": "Upside Down UI", "chance": 0.03, "active": False},
            "zalgo_text": {"name": "Zalgo Text", "chance": 0.06, "active": False},
            "invisible_buttons": {"name": "Invisible Buttons", "chance": 0.04, "active": False},
            "random_sounds": {"name": "Random Sounds", "chance": 0.07, "active": False},
            "exploding_text": {"name": "Exploding Text", "chance": 0.05, "active": False},
            "spinning_cursor": {"name": "Spinning Cursor", "chance": 0.06, "active": False},
        }
    
    def trigger_april_fools_prank(self):
        """Randomly trigger April Fools prank"""
        if not self.april_fools_active or random.random() > 0.15:
            return None
        
        prank_list = list(self.pranks.keys())
        selected_prank = random.choice(prank_list)
        self.pranks[selected_prank]["active"] = True
        self.prank_count += 1
        self.pranks_triggered.append(selected_prank)
        
        prank_messages = {
            "reverse_colors": "🎭 COLORS REVERSED! 🎭",
            "backwards_text": "txet sdrawkcab gnihtyreve!",
            "upside_down": "⊥hƃᴉɹ ǝɯoɔ ⅂I",
            "zalgo_text": "Z̸͓̰͎͎͔̭̘̦̻̟̗͔͎̦̹̪̓a̶̧̛̤̤̳̠͓͎̯̤̭̟͙̣̰͉̐̉̃̐̅l̶̬̖̞̓̈́̾͋g̴̝̗̹̤̻̯͎̎̐̉̈̈́o̸̡̭̪̞̼͚͖̘̣̒͐̀̒̓̆͘!",
            "invisible_buttons": "where did the buttons go? 👻",
            "random_sounds": "🔊 SOUND CHECK! 🔊",
            "exploding_text": "💥 TEXT OVERLOAD 💥",
            "spinning_cursor": "🌪️ SPINNING! 🌪️",
        }
        
        return prank_messages.get(selected_prank, f"Prank: {selected_prank}")
    
    def apply_april_fools_effect(self):
        """Apply active April Fools effects"""
        for prank_name, prank_data in self.pranks.items():
            if prank_data["active"]:
                if prank_name == "reverse_colors":
                    # Reverse color scheme
                    self.current_theme = "light" if self.current_theme == "dark" else "dark"
                
                elif prank_name == "zalgo_text":
                    # Add zalgo characters randomly
                    pass
                
                elif prank_name == "random_sounds":
                    # Play random sound effect
                    try:
                        import winsound
                        winsound.Beep(random.randint(100, 2000), random.randint(50, 200))
                    except:
                        pass
    
    def find_easter_egg(self, code):
        """Hidden Easter Egg system"""
        # v1.67 Special: Chocolate Bunny
        if code.upper() == "CHOCOLATE" or code.upper() == "CHOCOLATEBUNNY":
            self.easter_eggs_found += 1
            self.john_pork_elixir["count"] += 1
            self.sp += 67  # John Pork Elixir bonus
            self.troll_level += 2
            return "🐰 YO THIS CHOCOLATE BUNNY BUSSIN! +67 SP OMEGA TUFF!🐰"
        
        easter_eggs = {
            "QUESTIONMARK": "🎪 YO THIS PEAK RIZZ ENERGY! 🎪",
            "APRILFOOLS": "🃏 OGMGMGMGM THE TRICKSTER RIZZ EXTREME! 🃏",
            "ROLLINGGAME": "🎲 DUPER COOL ROLLING EZZZ! 🎲",
            "TROLL": "👹 ULTRA TROLL MODE ACTIVATED! 👹",
            "CHAOS": "⚡ OMEGA CHAOS MODE UNLOCKED TUFF! ⚡",
            "SECRET": "🔐 PEAK SECRET VIBES REVEALED! 🔐",
            "CHEAT": "💀 YO CHEATER RIZZ! (WE NOT SNITCHING THO) 💀",
            "HIDDEN": "👁️ DUPER EXTREME ALL SEEING BUSSIN MODE! 👁️",
            "JOHNPORK": "🍗 JOHN PORK ULTRA POWER! +67! 🍗",
        }
        
        if code.upper() in easter_eggs:
            self.easter_eggs_found += 1
            self.troll_level += 1
            # John Pork bonus
            if code.upper() == "JOHNPORK":
                self.john_pork_elixir["count"] += 1
                self.sp += 67
            return easter_eggs[code.upper()]
        return None
    
    def april_fools_bonus_sp(self):
        """Give bonus SP if April Fools pranks have been triggered"""
        bonus = self.prank_count * 2
        if self.easter_eggs_found > 0:
            bonus += self.easter_eggs_found * 5
        if self.troll_level > 5:
            bonus += 25
        return bonus
    
    def get_v167_feedback_message(self):
        """Get v1.677676... April Fools feedback message (GENUINE THE MOST TUFF THING EVER)"""
        messages = [
            "🐰 THIS IS BUSSIN FRFR! +67 SP POWER!",
            "⚡ JS PEAK ENERGY! EXTREME DUPER BTC MINER MODE!",
            "💜 PURPLE TEXT VIBES UNLOCKED! WHY NOT THO??",
            "👑 VICTORY ROYALE 1.67 - GUESS IS SUPER TUFF!",
            "🔧 THOR'S HAMMER ACTIVATED! OMEGA RIZZ!",
            "♾️ INFINITY GAUNTLET POWER! CONTROL ALL!",
            "67️⃣ THE 67 GAUNTLET MAKES THIS EZZZ!",
            "📐 MATHEMATICAL MAGIC: (67/67 + sqrt² + 67+71 - 67-65) = DUPER COOL!",
            "🎪 APRIL FOOLS MODE IS PEAK! OGMGMGMGM!",
            "💯 THIS UPDATE IS EZZZ CONFIRMED!"
        ]
        return random.choice(messages)

    def _init_daily_challenges(self):
        """Initialize daily challenges system"""
        challenges = {
            "challenge_1": {"name": "Quick Thinker", "desc": "Win 3 sequences", "target": 3, "reward_sp": 5, "icon": "⚡"},
            "challenge_2": {"name": "Accuracy Master", "desc": "Win 5 sequences", "target": 5, "reward_sp": 8, "icon": "🎯"},
            "challenge_3": {"name": "SP+ Collector", "desc": "Earn 3 SP+", "target": 3, "reward_sp": 10, "icon": "⬆"},
            "challenge_4": {"name": "SPx Collector", "desc": "Earn 2 SPx", "target": 2, "reward_sp": 15, "icon": "✕"},
            "challenge_5": {"name": "SP^ Collector", "desc": "Earn 1 SP^", "target": 1, "reward_sp": 25, "icon": "▲"},
            "challenge_6": {"name": "Grinding Session", "desc": "Roll 50 times", "target": 50, "reward_sp": 12, "icon": "🔄"},
            "challenge_7": {"name": "Perfect Series", "desc": "Win 3 in a row", "target": 3, "reward_sp": 20, "icon": "🔥"},
            "challenge_8": {"name": "Long String Master", "desc": "Win with 25+ char string", "target": 1, "reward_sp": 18, "icon": "📝"}
        }
        
        # April Fools Challenge Modifiers (v1.677676...)
        if self.version_1_67_mode:
            challenges["april_fools_1"] = {"name": "Victory Royale 1.67", "desc": "Win in Victory Royale 1.67 mode - SUPER TUFF", "target": 1, "reward_sp": 50, "icon": "👑", "modifier": "2x multiplier"}
            challenges["april_fools_2"] = {"name": "JS Peak Energy", "desc": "Use Victory Royale mode (EXTREME DUPER BTC MINER ENERGY)", "target": 3, "reward_sp": 35, "icon": "⚙️", "modifier": "unlock_v167_items"}
            challenges["april_fools_3"] = {"name": "Purple Text Master", "desc": "Identify purple text properties", "target": 5, "reward_sp": 40, "icon": "💜", "modifier": "feedback_messages"}
        
        return challenges
    
    def _load_challenge_progress(self):
        """Load daily challenge progress"""
        challenge_file = self.account_manager.get_user_data_file(self.current_username) if self.current_username else "challenge_progress.json"
        if os.path.exists(challenge_file):
            try:
                with open(challenge_file, 'r') as f:
                    data = json.load(f)
                    return data.get("challenges", {})
            except:
                return {}
        return {}
    
    def _save_challenge_progress(self):
        """Save daily challenge progress"""
        if not self.current_username:
            return
        challenge_file = self.account_manager.get_user_data_file(self.current_username)
        challenge_data = {"challenges": self.challenge_progress}
        try:
            with open(challenge_file, 'w') as f:
                json.dump(challenge_data, f, indent=2)
        except:
            pass
    
    def _update_challenges(self, sp_type, string_length):
        """Update daily challenge progress"""
        # Challenge 1: Win sequences (Quick Thinker - 3 wins)
        self.challenge_progress["challenge_1"] = self.challenge_progress.get("challenge_1", 0) + 1
        
        # Challenge 2: Win sequences (Accuracy Master - 5 wins)
        self.challenge_progress["challenge_2"] = self.challenge_progress.get("challenge_2", 0) + 1
        
        # Challenge 3-5: SP type collectors
        if sp_type == "sp_plus":
            self.challenge_progress["challenge_3"] = self.challenge_progress.get("challenge_3", 0) + 1
        elif sp_type == "sp_x":
            self.challenge_progress["challenge_4"] = self.challenge_progress.get("challenge_4", 0) + 1
        elif sp_type == "sp_caret":
            self.challenge_progress["challenge_5"] = self.challenge_progress.get("challenge_5", 0) + 1
        
        # Challenge 6: Rolling
        self.challenge_progress["challenge_6"] = self.challenge_progress.get("challenge_6", 0) + 1
        
        # Challenge 7: Perfect Series (tracked in win condition)
        # Challenge 8: Long string
        if string_length >= 25:  # Updated to match new SP^ threshold
            self.challenge_progress["challenge_8"] = self.challenge_progress.get("challenge_8", 0) + 1
    
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
        if os.path.exists(eq_file):
            try:
                with open(eq_file, 'r') as f:
                    data = json.load(f)
                    self.sp = data.get("sp", 0)
                    self.sp_plus = data.get("sp_plus", 0)
                    self.sp_x = data.get("sp_x", 0)
                    self.sp_caret = data.get("sp_caret", 0)
                    self.equipped_gauntlet = data.get("equipped", {}).get("gauntlet")
                    self.equipped_device = data.get("equipped", {}).get("device")
                    return data
            except:
                return {"sp": 0, "sp_plus": 0, "sp_x": 0, "sp_caret": 0, "owned": [], "equipped": {"gauntlet": None, "device": None}}
        return {"sp": 0, "sp_plus": 0, "sp_x": 0, "sp_caret": 0, "owned": [], "equipped": {"gauntlet": None, "device": None}}
    
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
        with open(eq_file, 'w') as f:
            json.dump(eq_data, f, indent=2)
    
    def _generate_target(self):
        """Generate random target properties"""
        possible_properties = [
            "has_numbers",
            "has_symbols",
            "has_uppercase",
            "has_lowercase",
            "is_long",
            "has_spaces",
            "has_operators",
            "has_multiple_words",
            "has_repeats",
            "starts_with_letter",
            "ends_with_symbol",
            "has_punctuation",
            "has_vowels",
            "is_very_long",
            "has_consecutive_letters"
        ]
        
        # v1.677676... April Fools: Add purple text property (WHY NOT??)
        if self.purple_text_property:
            possible_properties.append("has_purple_text_vibes")  # Feedback messages property
        
        # Randomly select target properties based on difficulty
        if self.difficulty == "easy":
            num_targets = random.randint(1, 2)
        elif self.difficulty == "hard":
            num_targets = random.randint(3, 5)
        else:  # normal
            num_targets = random.randint(2, 4)
        self.target_properties = set(random.sample(possible_properties, num_targets))
    
    def show_login_screen(self):
        """Show account login/register screen"""
        login_root = tk.Tk()
        login_root.title("Questionmark - Account Login")
        login_root.geometry("450x500")
        login_root.configure(bg="#2b2b2b")
        login_root.resizable(False, False)
        
        title_label = tk.Label(login_root, text="Questionmark", font=("Arial", 16, "bold"),
                              bg="#2b2b2b", fg="#00ff00")
        title_label.pack(pady=20)
        
        # Remembered accounts frame
        remembered_frame = tk.Frame(login_root, bg="#2b2b2b")
        remembered_frame.pack(pady=10, padx=10, fill=tk.X)
        
        if self.account_manager.remembered_accounts:
            tk.Label(remembered_frame, text="Recent Accounts:", bg="#2b2b2b", fg="#aaaaaa",
                    font=("Arial", 9, "italic")).pack(anchor="w")
            
            def quick_login(username):
                def inner():
                    username_entry.delete(0, tk.END)
                    username_entry.insert(0, username)
                    password_entry.focus()
                return inner
            
            for acc in self.account_manager.remembered_accounts:
                def create_forget(u):
                    def forget():
                        self.account_manager.forget_account(u)
                        login_root.destroy()
                        self.show_login_screen()
                    return forget
                
                acc_btn_frame = tk.Frame(remembered_frame, bg="#1e1e1e")
                acc_btn_frame.pack(fill=tk.X, pady=2)
                
                acc_btn = tk.Button(acc_btn_frame, text=f"  {acc}  ", command=quick_login(acc),
                                   bg="#333333", fg="#00ff00", font=("Arial", 10),
                                   anchor="w", justify=tk.LEFT)
                acc_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
                
                forget_btn = tk.Button(acc_btn_frame, text="✕", command=create_forget(acc),
                                      bg="#662222", fg="#ff6b6b", font=("Arial", 8), width=3)
                forget_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Username frame
        uname_frame = tk.Frame(login_root, bg="#2b2b2b")
        uname_frame.pack(pady=10)
        tk.Label(uname_frame, text="Username:", bg="#2b2b2b", fg="#ffffff", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        username_entry = tk.Entry(uname_frame, width=25, font=("Arial", 10))
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # Password frame
        pwd_frame = tk.Frame(login_root, bg="#2b2b2b")
        pwd_frame.pack(pady=10)
        tk.Label(pwd_frame, text="Password:", bg="#2b2b2b", fg="#ffffff", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        password_entry = tk.Entry(pwd_frame, width=25, font=("Arial", 10), show="•")
        password_entry.pack(side=tk.LEFT, padx=5)
        
        status_label = tk.Label(login_root, text="", bg="#2b2b2b", fg="#ffff00", font=("Arial", 9))
        status_label.pack(pady=5)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                status_label.config(text="Please enter username and password", fg="#ff6b6b")
                return
            success, msg = self.account_manager.login(username, password)
            if success:
                self.current_username = username
                login_root.destroy()
                self.root = None
                self._setup_gui()
                self.root.mainloop()
            else:
                status_label.config(text=msg, fg="#ff6b6b")
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                status_label.config(text="Please enter username and password", fg="#ff6b6b")
                return
            success, msg = self.account_manager.register(username, password)
            if success:
                status_label.config(text="Account created! Now login", fg="#00ff00")
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            else:
                status_label.config(text=msg, fg="#ff6b6b")
        
        # Button frame
        btn_frame = tk.Frame(login_root, bg="#2b2b2b")
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(btn_frame, text="Login", command=login, bg="#00cc00", fg="#000000",
                             font=("Arial", 11, "bold"), padx=15, pady=8)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        register_btn = tk.Button(btn_frame, text="Register", command=register, bg="#0099ff", fg="#000000",
                                font=("Arial", 11, "bold"), padx=15, pady=8)
        register_btn.pack(side=tk.LEFT, padx=10)
        
        guest_btn = tk.Button(btn_frame, text="Guest", command=lambda: login_root.destroy(),
                             bg="#666666", fg="#ffffff", font=("Arial", 11, "bold"), padx=15, pady=8)
        guest_btn.pack(side=tk.LEFT, padx=10)
        
        login_root.mainloop()
    
    def _setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title("Questionmark")
        self.root.geometry("900x750")
        self.root.configure(bg="#2b2b2b")
        
        # Developer Console Hotkey (v1.67)
        self.root.bind('<Control-Shift-d>', lambda e: self.toggle_dev_console())
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Save Game", command=self.save_game)
        game_menu.add_command(label="Load Game", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.quit_game)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="History", command=self.show_history_window)
        view_menu.add_command(label="Statistics", command=self.show_stats_window)
        view_menu.add_command(label="Achievements", command=self.show_achievements_window)
        view_menu.add_command(label="Leaderboard", command=self.show_leaderboard)
        
        # Systems menu - NEW!
        systems_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Systems", menu=systems_menu)
        systems_menu.add_command(label="💪 Skill Tree", command=self.show_skill_tree_screen)
        systems_menu.add_command(label="🏆 Tournaments", command=self.show_tournament_screen)
        systems_menu.add_command(label="🐉 Dungeons", command=self.show_dungeon_screen)
        systems_menu.add_command(label="⚔️ PvP Battles", command=self.show_pvp_screen)
        systems_menu.add_separator()
        systems_menu.add_command(label="📊 Prestige", command=lambda: messagebox.showinfo("Prestige", f"Prestige Level: {self.prestige_level}\nTotal Points: {self.total_prestige_points_earned}"))
        systems_menu.add_command(label="⚡ Seasonal", command=lambda: messagebox.showinfo("Seasonal", f"Season: {self.current_season}\nProgress: {self.season_progress}"))

        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings_screen)
        tools_menu.add_command(label="Equipment Crafting", command=self.show_equipment_window)
        tools_menu.add_command(label="Mini-Game", command=self.play_mini_game)
        tools_menu.add_command(label="Tutorial", command=self.start_tutorial)
        
        # Title
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(title_frame, text="QUESTIONMARK", 
                        font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#00ff00")
        title.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(self.root, bg="#2b2b2b")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats_frame, text="Roll Count:", font=("Arial", 11, "bold"), 
                bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.roll_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                   bg="#2b2b2b", fg="#ffff00")
        self.roll_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(stats_frame, text="  |  Sequences Won:", font=("Arial", 11, "bold"), 
                bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.wins_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                   bg="#2b2b2b", fg="#00ff00")
        self.wins_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(stats_frame, text="  |  SP: ", font=("Arial", 11, "bold"), 
                bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        self.sp_label = tk.Label(stats_frame, text="0|0|0|0", font=("Arial", 10, "bold"), 
                                 bg="#2b2b2b", fg="#ff00ff")
        self.sp_label.pack(side=tk.LEFT, padx=2)
        
        # Current roll display
        roll_frame = tk.LabelFrame(self.root, text="Current Roll", font=("Arial", 11, "bold"),
                                   bg="#2b2b2b", fg="#00ff00", padx=10, pady=10)
        roll_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        self.roll_text = tk.Label(roll_frame, text="(No rolls yet)", font=("Courier", 10),
                                  bg="#1e1e1e", fg="#ffffff", wraplength=850, 
                                  justify=tk.LEFT, pady=10)
        self.roll_text.pack(fill=tk.BOTH, expand=True)
        
        # Properties found
        props_frame = tk.LabelFrame(self.root, text="Properties Found", font=("Arial", 11, "bold"),
                                    bg="#2b2b2b", fg="#00ff00", padx=10, pady=10, height=120)
        props_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        props_frame.pack_propagate(False)
        
        self.props_text = tk.Label(props_frame, text="(Roll to analyze)", font=("Arial", 10),
                                   bg="#1e1e1e", fg="#ffffff", justify=tk.LEFT)
        self.props_text.pack(fill=tk.BOTH, expand=True)
        
        # Matches display
        match_frame = tk.LabelFrame(self.root, text="Target Match", font=("Arial", 11, "bold"),
                                    bg="#2b2b2b", fg="#00ff00", padx=10, pady=10, height=80)
        match_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        match_frame.pack_propagate(False)
        
        self.match_label = tk.Label(match_frame, text="0/0 matches", font=("Arial", 14, "bold"),
                                    bg="#1e1e1e", fg="#ff6b6b", pady=10)
        self.match_label.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#2b2b2b")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.roll_button = tk.Button(button_frame, text="🎲 ROLL", font=("Arial", 12, "bold"),
                                     bg="#00cc00", fg="#000000", padx=20, pady=10,
                                     activebackground="#00cc00", activeforeground="#000000",
                                     command=self.manual_roll, width=15)
        self.roll_button.pack(side=tk.LEFT, padx=5)
        
        self.auto_button = tk.Button(button_frame, text="⚡ AUTO-ROLL", font=("Arial", 12, "bold"),
                                     bg="#ff9900", fg="#000000", padx=20, pady=10,
                                     activebackground="#ff9900", activeforeground="#000000",
                                     command=self.toggle_auto_roll, state=tk.DISABLED, width=15)
        self.auto_button.pack(side=tk.LEFT, padx=5)
        
        self.history_button = tk.Button(button_frame, text="📊 HISTORY", font=("Arial", 12, "bold"),
                                        bg="#0099ff", fg="#000000", padx=20, pady=10,
                                        activebackground="#0099ff", activeforeground="#000000",
                                        command=self.show_history_window, width=15)
        self.history_button.pack(side=tk.LEFT, padx=5)
        
        # April Fools Event Button
        self.april_button = tk.Button(button_frame, text="🃏 Event", font=("Arial", 11, "bold"),
                                     bg="#ff6600", fg="#000000", padx=15, pady=10,
                                     activebackground="#ff6600", activeforeground="#000000",
                                     command=self.show_april_fools_menu, width=8)
        self.april_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(button_frame, text="❌ QUIT", font=("Arial", 12, "bold"),
                                     bg="#cc0000", fg="#ffffff", padx=20, pady=10,
                                     activebackground="#cc0000", activeforeground="#ffffff",
                                     command=self.quit_game, width=15)
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
        # Info text
        info = tk.Label(self.root, text="Deduce the hidden properties by analyzing roll results. Adjust difficulty in settings. Auto-roll unlocks at 500 rolls.",
                       font=("Arial", 10), bg="#2b2b2b", fg="#cccccc")
        info.pack(pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
    
    def _play_startup_sound(self):
        """Play startup sound"""
        if self.sound_enabled:
            try:
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(1000, 200)
            except:
                pass
    
    def _play_roll_sound(self):
        """Play roll sound"""
        if self.sound_enabled:
            try:
                winsound.Beep(600, 100)
            except:
                pass
    
    def _play_success_sound(self):
        """Play success sound"""
        if self.sound_enabled:
            try:
                winsound.Beep(1200, 150)
                time.sleep(0.1)
                winsound.Beep(1400, 150)
                time.sleep(0.1)
                winsound.Beep(1600, 200)
            except:
                pass
    
    def _load_achievements(self):
        """Load achievements from file (per-user)"""
        ach_file = self.account_manager.get_user_achievements_file(self.current_username) if self.current_username else "achievements.json"
        try:
            with open(ach_file, "r") as f:
                return json.load(f)
        except:
            return {
                "first_win": {"unlocked": False, "name": "First Victory", "desc": "Win your first sequence"},
                "ten_wins": {"unlocked": False, "name": "Dedicated Player", "desc": "Win 10 sequences"},
                "fifty_wins": {"unlocked": False, "name": "Master Deductor", "desc": "Win 50 sequences"},
                "hundred_rolls": {"unlocked": False, "name": "Persistent", "desc": "Make 100 rolls"},
                "thousand_rolls": {"unlocked": False, "name": "Obsessed", "desc": "Make 1000 rolls"},
                "auto_unlock": {"unlocked": False, "name": "Automation Expert", "desc": "Make 500 rolls"},  # Reduced from 50,000
                "speed_demon": {"unlocked": False, "name": "Speed Demon", "desc": "Win a sequence in under 30 rolls"},  # Reduced from 50
                "perfectionist": {"unlocked": False, "name": "Perfectionist", "desc": "Win 3 sequences in a row"},
                "explorer": {"unlocked": False, "name": "Property Explorer", "desc": "Discover all 15 properties"},
                "night_owl": {"unlocked": False, "name": "Night Owl", "desc": "Play between 12 AM and 6 AM"},
                "sp_collector": {"unlocked": False, "name": "SP Collector", "desc": "Earn 50 total SP"},
                "equipment_master": {"unlocked": False, "name": "Equipment Master", "desc": "Craft 5 pieces of equipment"}
            }
    
    def _save_achievements(self):
        """Save achievements to file (per-user)"""
        try:
            ach_file = self.account_manager.get_user_achievements_file(self.current_username) if self.current_username else "achievements.json"
            with open(ach_file, "w") as f:
                json.dump(self.achievements, f, indent=2)
        except:
            pass
    
    def _load_stats(self):
        """Load statistics from file (per-user)"""
        stats_file = self.account_manager.get_user_stats_file(self.current_username) if self.current_username else "stats.json"
        try:
            with open(stats_file, "r") as f:
                return json.load(f)
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
        try:
            self.stats["total_rolls"] = self.roll_count
            self.stats["total_wins"] = self.wins_count
            self.stats["play_time"] += time.time() - self.stats["start_time"]
            stats_file = self.account_manager.get_user_stats_file(self.current_username) if self.current_username else "stats.json"
            with open(stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        unlocked = []
        
        if self.wins_count >= 1 and not self.achievements["first_win"]["unlocked"]:
            self.achievements["first_win"]["unlocked"] = True
            unlocked.append("First Victory")
        
        if self.wins_count >= 10 and not self.achievements["ten_wins"]["unlocked"]:
            self.achievements["ten_wins"]["unlocked"] = True
            unlocked.append("Dedicated Player")
        
        if self.wins_count >= 50 and not self.achievements["fifty_wins"]["unlocked"]:
            self.achievements["fifty_wins"]["unlocked"] = True
            unlocked.append("Master Deductor")
        
        if self.roll_count >= 100 and not self.achievements["hundred_rolls"]["unlocked"]:
            self.achievements["hundred_rolls"]["unlocked"] = True
            unlocked.append("Persistent")
        
        if self.roll_count >= 1000 and not self.achievements["thousand_rolls"]["unlocked"]:
            self.achievements["thousand_rolls"]["unlocked"] = True
            unlocked.append("Obsessed")
        
        if self.roll_count >= 500 and not self.achievements["auto_unlock"]["unlocked"]:  # Reduced from 50,000
            self.achievements["auto_unlock"]["unlocked"] = True
            unlocked.append("Automation Expert")
        
        # Check for speed demon (win in under 30 rolls)
        fastest = self.stats.get('fastest_win')
        if fastest and isinstance(fastest, (int, float)) and fastest <= 30 and not self.achievements["speed_demon"]["unlocked"]:
            self.achievements["speed_demon"]["unlocked"] = True
            unlocked.append("Speed Demon")
        
        # Check for perfectionist (3 wins in a row)
        if self.stats.get('current_streak', 0) >= 3 and not self.achievements["perfectionist"]["unlocked"]:
            self.achievements["perfectionist"]["unlocked"] = True
            unlocked.append("Perfectionist")
        
        # Check for night owl
        current_hour = datetime.now().hour
        if 0 <= current_hour <= 6 and not self.achievements["night_owl"]["unlocked"]:
            self.achievements["night_owl"]["unlocked"] = True
            unlocked.append("Night Owl")
        
        # Check for SP collector (50 total SP)
        total_sp = self.sp + self.sp_plus + self.sp_x + self.sp_caret
        if total_sp >= 50 and not self.achievements["sp_collector"]["unlocked"]:
            self.achievements["sp_collector"]["unlocked"] = True
            unlocked.append("SP Collector")
        
        # Check for equipment master (5 crafted items)
        crafted_count = len(self.equipment_inventory.get("owned", []))
        if crafted_count >= 5 and not self.achievements["equipment_master"]["unlocked"]:
            self.achievements["equipment_master"]["unlocked"] = True
            unlocked.append("Equipment Master")
        
        # Check for explorer (all 15 properties discovered)
        discoveries = self.stats.get('property_discoveries', {})
        if len(discoveries) >= 15 and not self.achievements["explorer"]["unlocked"]:
            self.achievements["explorer"]["unlocked"] = True
            unlocked.append("Property Explorer")
        
        if unlocked:
            self._show_achievement_popup(unlocked)
            self._save_achievements()
    
    def _show_achievement_popup(self, achievements):
        """Show achievement unlocked popup"""
        popup = tk.Toplevel(self.root)
        popup.title("🏆 Achievement Unlocked!")
        popup.geometry("400x200")
        popup.configure(bg="#1e1e1e")
        
        tk.Label(popup, text="🏆 ACHIEVEMENT UNLOCKED!", font=("Arial", 14, "bold"), 
                bg="#1e1e1e", fg="#00ff00").pack(pady=10)
        
        for ach in achievements:
            tk.Label(popup, text=f"• {ach}", font=("Arial", 11), 
                    bg="#1e1e1e", fg="#ffffff").pack()
        
        tk.Button(popup, text="Awesome!", command=popup.destroy, 
                 bg="#00cc00", fg="#000000").pack(pady=10)
    
    def _apply_theme(self, theme):
        """Apply a theme to the GUI"""
        self.current_theme = theme
        
        if theme == "dark":
            colors = {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "accent": "#00ff00",
                "secondary": "#1e1e1e",
                "button_bg": "#00cc00",
                "button_fg": "#000000"
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
        self.auto_button.config(bg="#ff9900", fg="#000000")
        self.history_button.config(bg="#0099ff", fg="#000000")
        self.quit_button.config(bg="#cc0000", fg="#ffffff")
        
        # Update frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg"])
            elif isinstance(widget, tk.Label):
                if "bg" in widget.config():
                    widget.configure(bg=colors["bg"], fg=colors["fg"])
    
    def show_settings_window(self):
        """Show settings window with account management and daily challenges"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Questionmark - Settings & Account")
        settings_win.geometry("600x600")
        settings_win.configure(bg="#2b2b2b")
        
        notebook = ttk.Notebook(settings_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Account Tab
        account_frame = tk.Frame(notebook, bg="#2b2b2b")
        notebook.add(account_frame, text="👤 Account")
        
        if self.current_username:
            acc_info = self.account_manager.accounts.get(self.current_username, {})
            created = acc_info.get("created", "Unknown")
            title = self._get_player_title()
            
            info_text = f"Username: {self.current_username}\nTitle: {title}\nCreated: {created}"
            tk.Label(account_frame, text=info_text, font=("Arial", 11), bg="#2b2b2b", fg="#00ff00", justify=tk.LEFT).pack(pady=20, padx=20)
        else:
            tk.Label(account_frame, text="Playing as Guest\n(Create an account to save progress)", 
                    font=("Arial", 11), bg="#2b2b2b", fg="#ffff00").pack(pady=20, padx=20)
        
        # Daily Challenges Tab
        challenge_frame = tk.Frame(notebook, bg="#2b2b2b")
        notebook.add(challenge_frame, text="🎯 Daily Challenges")
        
        tk.Label(challenge_frame, text="📅 TODAY'S CHALLENGES", font=("Arial", 13, "bold"),
                bg="#2b2b2b", fg="#00ff00").pack(pady=10)
        
        challenges_scroll = scrolledtext.ScrolledText(challenge_frame, wrap=tk.WORD, height=20, width=70,
                                                      bg="#1e1e1e", fg="#ffffff", font=("Arial", 9))
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
        
        # Settings Tab
        settings_frame = tk.Frame(notebook, bg="#2b2b2b")
        notebook.add(settings_frame, text="⚙️ Game Settings")
        
        # Sound settings
        sound_frame = tk.LabelFrame(settings_frame, text="Audio", bg="#2b2b2b", fg="#00ff00")
        sound_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sound_var = tk.BooleanVar(value=self.sound_enabled)
        tk.Checkbutton(sound_frame, text="Enable Sound Effects", variable=sound_var,
                      command=lambda: setattr(self, 'sound_enabled', sound_var.get()),
                      bg="#2b2b2b", fg="#ffffff", selectcolor="#1e1e1e").pack(anchor=tk.W, padx=10, pady=5)
        
        # Animation settings
        anim_frame = tk.LabelFrame(settings_frame, text="Visual", bg="#2b2b2b", fg="#00ff00")
        anim_frame.pack(fill=tk.X, padx=10, pady=5)
        
        anim_var = tk.BooleanVar(value=self.animations_enabled)
        tk.Checkbutton(anim_frame, text="Enable Animations", variable=anim_var,
                      command=lambda: setattr(self, 'animations_enabled', anim_var.get()),
                      bg="#2b2b2b", fg="#ffffff", selectcolor="#1e1e1e").pack(anchor=tk.W, padx=10, pady=5)
        
        # Theme settings
        theme_frame = tk.LabelFrame(settings_frame, text="Theme", bg="#2b2b2b", fg="#00ff00")
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        theme_var = tk.StringVar(value=self.current_theme)
        themes = [("Dark", "dark"), ("Light", "light"), ("Neon", "neon")]
        
        for text, value in themes:
            tk.Radiobutton(theme_frame, text=text, variable=theme_var, value=value,
                          command=lambda v=value: self._apply_theme(v),
                          bg="#2b2b2b", fg="#ffffff", selectcolor="#1e1e1e").pack(anchor=tk.W, padx=10)
        
        # Difficulty settings
        diff_frame = tk.LabelFrame(settings_frame, text="Difficulty", bg="#2b2b2b", fg="#00ff00")
        diff_frame.pack(fill=tk.X, padx=10, pady=5)
        
        diff_var = tk.StringVar(value=self.difficulty)
        difficulties = [("Easy (1-2 properties)", "easy"), ("Normal (2-4 properties)", "normal"), ("Hard (3-5 properties)", "hard")]
        
        for text, value in difficulties:
            tk.Radiobutton(diff_frame, text=text, variable=diff_var, value=value,
                          command=lambda v=value: setattr(self, 'difficulty', v),
                          bg="#2b2b2b", fg="#ffffff", selectcolor="#1e1e1e").pack(anchor=tk.W, padx=10)
        
        # Save/Load
        save_frame = tk.LabelFrame(settings_frame, text="Save/Load", bg="#2b2b2b", fg="#00ff00")
        save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(save_frame, text="Save Game", command=self.save_game,
                 bg="#00cc00", fg="#000000").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(save_frame, text="Load Game", command=self.load_game,
                 bg="#ff9900", fg="#000000").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tutorial
        tutorial_frame = tk.LabelFrame(settings_frame, text="Help", bg="#2b2b2b", fg="#00ff00")
        tutorial_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(tutorial_frame, text="Start Tutorial", command=self.start_tutorial,
                 bg="#0099ff", fg="#ffffff").pack(pady=5)
    
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
            "Use the feedback (✓ marks) to deduce which properties are required.",
            "Keep rolling until you find a string with ALL target properties!",
            "Try auto-roll once you unlock it at 50,000 rolls.",
            "Check your achievements and statistics for more fun!"
        ]
        
        if self.tutorial_step < len(steps):
            messagebox.showinfo("Tutorial", steps[self.tutorial_step])
            self.tutorial_step += 1
        else:
            self.tutorial_mode = False
            messagebox.showinfo("Tutorial Complete", "You're ready to play!")
    
    def save_game(self):
        """Save current game state"""
        game_state = {
            "roll_count": self.roll_count,
            "wins_count": self.wins_count,
            "target_properties": list(self.target_properties),
            "rolls_history": self.rolls_history[-100:],
            "achievements": self.achievements,
            "stats": self.stats,
            "theme": self.current_theme,
            "sound_enabled": self.sound_enabled,
            "animations_enabled": self.animations_enabled,
            "difficulty": self.difficulty,
            # NEW SYSTEMS
            "autoroll_speed": self.autoroll_speed,
            "skills": self.skills,
            "skill_points": self.skill_points,
            "tournament_scores": self.tournament_scores,
            "pvp_rating": self.pvp_rating,
            "pvp_wins": self.pvp_wins,
            "pvp_losses": self.pvp_losses,
            "prestige_level": self.prestige_level,
            "prestige_points": self.prestige_points,
            "dungeons_completed_total": self.dungeons_completed_total,
            "daily_dungeons_completed": self.daily_dungeons_completed,
            "current_season": self.current_season,
            "seasonal_challenges": self.seasonal_challenges,
            "daily_quests": self.daily_quests,
        }
        
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, "w") as f:
                    json.dump(game_state, f, indent=2)
                messagebox.showinfo("Save", "Game saved successfully!")
            except:
                messagebox.showerror("Save Error", "Failed to save game.")
    
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
                # NEW SYSTEMS
                self.autoroll_speed = game_state.get("autoroll_speed", 100)
                self.skills = game_state.get("skills", self.skills)
                self.skill_points = game_state.get("skill_points", 10)
                self.tournament_scores = game_state.get("tournament_scores", self.tournament_scores)
                self.pvp_rating = game_state.get("pvp_rating", 1000)
                self.pvp_wins = game_state.get("pvp_wins", 0)
                self.pvp_losses = game_state.get("pvp_losses", 0)
                self.prestige_level = game_state.get("prestige_level", 0)
                self.prestige_points = game_state.get("prestige_points", 0)
                self.dungeons_completed_total = game_state.get("dungeons_completed_total", 0)
                self.daily_dungeons_completed = game_state.get("daily_dungeons_completed", 0)
                self.current_season = game_state.get("current_season", 1)
                self.seasonal_challenges = game_state.get("seasonal_challenges", self.seasonal_challenges)
                self.daily_quests = game_state.get("daily_quests", self.daily_quests)
                
                # Update UI
                self.roll_label.config(text=str(self.roll_count))
                self.wins_label.config(text=str(self.wins_count))
                self._apply_theme(self.current_theme)
                
                messagebox.showinfo("Load", "Game loaded successfully!")
            except:
                messagebox.showerror("Load Error", "Failed to load game.")
    
    def show_achievements_window(self):
        """Show achievements window"""
        ach_win = tk.Toplevel(self.root)
        ach_win.title("Questionmark - Achievements")
        ach_win.geometry("600x500")
        ach_win.configure(bg="#2b2b2b")
        
        canvas = tk.Canvas(ach_win, bg="#2b2b2b")
        scrollbar = tk.Scrollbar(ach_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2b2b2b")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        row = 0
        for ach_id, ach_data in self.achievements.items():
            status = "✅" if ach_data["unlocked"] else "❌"
            color = "#00ff00" if ach_data["unlocked"] else "#ff6b6b"
            
            tk.Label(scrollable_frame, text=f"{status} {ach_data['name']}", font=("Arial", 12, "bold"),
                    bg="#2b2b2b", fg=color).grid(row=row, column=0, sticky="w", padx=10, pady=2)
            tk.Label(scrollable_frame, text=ach_data['desc'], font=("Arial", 10),
                    bg="#2b2b2b", fg="#cccccc").grid(row=row, column=1, sticky="w", padx=10, pady=2)
            row += 1
    
    def show_stats_window(self):
        """Show statistics window"""
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Questionmark - Statistics")
        stats_win.geometry("700x600")
        stats_win.configure(bg="#2b2b2b")
        
        # Basic stats
        basic_frame = tk.LabelFrame(stats_win, text="Game Statistics", bg="#2b2b2b", fg="#00ff00")
        basic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_text = f"""
Total Rolls: {self.roll_count}
Total Wins: {self.wins_count}
Win Rate: {self.wins_count/max(1, self.roll_count)*100:.1f}%
Best Streak: {self.stats.get('best_streak', 0)}
Current Streak: {self.stats.get('current_streak', 0)}
Average Rolls per Win: {self.roll_count/max(1, self.wins_count):.1f}
Play Time: {self.stats.get('play_time', 0)/3600:.1f} hours
"""
        
        tk.Label(basic_frame, text=stats_text, font=("Courier", 10), bg="#1e1e1e", fg="#00ff00",
                justify=tk.LEFT).pack(fill=tk.X, padx=10, pady=10)
        
        # Property discoveries
        prop_frame = tk.LabelFrame(stats_win, text="Property Discoveries", bg="#2b2b2b", fg="#00ff00")
        prop_frame.pack(fill=tk.X, padx=10, pady=5)
        
        discoveries = self.stats.get('property_discoveries', {})
        prop_text = ""
        for prop in sorted(self._property_name_display(p) for p in self.possible_properties):
            count = discoveries.get(prop, 0)
            prop_text += f"{prop}: {count}\n"
        
        tk.Label(prop_frame, text=prop_text, font=("Courier", 9), bg="#1e1e1e", fg="#ffffff",
                justify=tk.LEFT).pack(fill=tk.X, padx=10, pady=10)
        
        # Charts section (if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            chart_frame = tk.LabelFrame(stats_win, text="Charts", bg="#2b2b2b", fg="#00ff00")
            chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Create a simple bar chart of property discoveries
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='#2b2b2b')
            ax.set_facecolor('#1e1e1e')
            
            props = list(discoveries.keys())
            counts = list(discoveries.values())
            
            bars = ax.bar(range(len(props)), counts, color='#00ff00')
            ax.set_xticks(range(len(props)))
            ax.set_xticklabels(props, rotation=45, ha='right', color='white')
            ax.set_ylabel('Discoveries', color='white')
            ax.set_title('Property Discoveries', color='white')
            ax.tick_params(colors='white')
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Show message about matplotlib not being available
            chart_frame = tk.LabelFrame(stats_win, text="Charts", bg="#2b2b2b", fg="#00ff00")
            chart_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(chart_frame, text="Install matplotlib for charts:\npip install matplotlib", 
                    font=("Arial", 10), bg="#1e1e1e", fg="#ff6b6b", justify=tk.LEFT).pack(pady=10)
        
        # Mini-game button
        tk.Button(stats_win, text="🎮 Play Mini-Game", command=self.play_mini_game,
                 bg="#ff00ff", fg="#ffffff", font=("Arial", 12, "bold")).pack(pady=10)
    
    def play_mini_game(self):
        """Play a simple mini-game - optimized for performance"""
        mini_win = tk.Toplevel(self.root)
        mini_win.title("Questionmark - Mini-Game")
        mini_win.geometry("500x400")
        mini_win.configure(bg="#2b2b2b")
        
        tk.Label(mini_win, text="Match the properties as fast as possible!", 
                font=("Arial", 14, "bold"), bg="#2b2b2b", fg="#00ff00").pack(pady=10)
        
        self.mini_score = 0
        self.mini_time_left = 30
        self.mini_target = random.choice(list(self.possible_properties))
        self.mini_running = True
        
        score_label = tk.Label(mini_win, text=f"Score: {self.mini_score}", 
                              font=("Arial", 12), bg="#2b2b2b", fg="#ffff00")
        score_label.pack()
        
        time_label = tk.Label(mini_win, text=f"Time: {self.mini_time_left}", 
                             font=("Arial", 12), bg="#2b2b2b", fg="#ff6b6b")
        time_label.pack()
        
        target_label = tk.Label(mini_win, text=f"Find: {self._property_name_display(self.mini_target)}", 
                               font=("Arial", 12, "bold"), bg="#2b2b2b", fg="#ffffff")
        target_label.pack(pady=10)
        
        roll_button = tk.Button(mini_win, text="🎲 ROLL", bg="#00cc00", fg="#000000", 
                               font=("Arial", 12, "bold"))
        roll_button.pack(pady=20)
        
        def roll_mini():
            if not self.mini_running:
                return
            s = self._generate_random_string()
            props = self._analyze_string(s)
            
            if self.mini_target in props:
                self.mini_score += 10
                score_label.config(text=f"Score: {self.mini_score}")
                self.mini_target = random.choice(list(self.possible_properties))
                target_label.config(text=f"Find: {self._property_name_display(self.mini_target)}")
                self._play_success_sound()
            else:
                self.mini_score = max(0, self.mini_score - 1)
                score_label.config(text=f"Score: {self.mini_score}")
        
        def update_timer():
            if not self.mini_running:
                return
            self.mini_time_left -= 1
            time_label.config(text=f"Time: {self.mini_time_left}")
            if self.mini_time_left <= 0:
                self.mini_running = False
                roll_button.config(state=tk.DISABLED)
                messagebox.showinfo("Time's Up!", f"Final Score: {self.mini_score}")
                mini_win.destroy()
            else:
                mini_win.after(1000, update_timer)
        
        roll_button.config(command=roll_mini)
        update_timer()
    
    def show_leaderboard(self):
        """Show real player leaderboard (no bots)"""
        leaderboard_win = tk.Toplevel(self.root)
        leaderboard_win.title("Questionmark - Leaderboard")
        leaderboard_win.geometry("500x400")
        leaderboard_win.configure(bg="#2b2b2b")
        
        tk.Label(leaderboard_win, text="QUESTIONMARK LEADERBOARD", font=("Arial", 16, "bold"), 
                bg="#2b2b2b", fg="#00ff00").pack(pady=10)
        
        # Get real player stats from accounts
        leaders = []
        for username in self.account_manager.accounts.keys():
            stats_file = self.account_manager.get_user_stats_file(username)
            try:
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        stats = json.load(f)
                        wins = stats.get("total_wins", 0)
                        account_info = self.account_manager.accounts[username]
                        title = self._get_player_title_for_wins(wins)
                        leaders.append((username, wins, title))
            except:
                pass
        
        # Sort by wins
        leaders.sort(key=lambda x: x[1], reverse=True)
        
        # Create scrolled frame for leaderboard
        scroll_frame = tk.Frame(leaderboard_win, bg="#1e1e1e")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(scroll_frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        medals = ["🥇", "🥈", "🥉"]
        
        if not leaders:
            tk.Label(scrollable_frame, text="No players yet! Be the first!", 
                    font=("Arial", 12), bg="#1e1e1e", fg="#ffff00").pack(pady=20)
        else:
            for i, (name, wins, title) in enumerate(leaders[:50], 1):
                medal = medals[i-1] if i <= 3 else f"{i}."
                color = "#ffff00" if name == self.current_username else "#ffffff"
                entry_text = f"{medal} {name:<15} | {wins} wins | {title}"
                tk.Label(scrollable_frame, text=entry_text, font=("Courier", 10), 
                        bg="#1e1e1e", fg=color, justify=tk.LEFT).pack(anchor="w", padx=10, pady=2)
    
    def _get_player_title_for_wins(self, wins):
        """Get title based on wins count"""
        if wins >= 100:
            return "Legend"
        elif wins >= 50:
            return "Master"
        elif wins >= 25:
            return "Expert"
        elif wins >= 10:
            return "Veteran"
        elif wins >= 5:
            return "Adept"
        return "Novice"
    
    def show_settings_screen(self):
        """Show comprehensive settings screen with auto-roll speed control"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("500x700")
        settings_window.config(bg="#1a1a1a")
        
        title = tk.Label(settings_window, text="⚙️ GAME SETTINGS", font=("Arial", 14, "bold"), fg="#00ff00", bg="#1a1a1a")
        title.pack(pady=10)
        
        # Auto-roll Speed Control
        speed_frame = tk.Frame(settings_window, bg="#2a2a2a")
        speed_frame.pack(fill=tk.X, padx=15, pady=10)
        
        speed_label = tk.Label(speed_frame, text="🎲 Auto-Roll Speed (No Delay!)", font=("Arial", 11, "bold"), fg="#00ff00", bg="#2a2a2a")
        speed_label.pack(anchor=tk.W)
        
        speed_info = tk.Label(speed_frame, text=f"Current: {self.autoroll_speed}ms | Range: {self.autoroll_min_speed}-{self.autoroll_max_speed}ms", 
                             font=("Arial", 9), fg="#888", bg="#2a2a2a")
        speed_info.pack(anchor=tk.W)
        
        def update_speed(val):
            self.autoroll_speed = int(float(val))
            speed_info.config(text=f"Current: {self.autoroll_speed}ms | Range: {self.autoroll_min_speed}-{self.autoroll_max_speed}ms")
        
        speed_slider = tk.Scale(speed_frame, from_=self.autoroll_min_speed, to=self.autoroll_max_speed, 
                               orient=tk.HORIZONTAL, bg="#3a3a3a", fg="#00ff00", command=update_speed)
        speed_slider.set(self.autoroll_speed)
        speed_slider.pack(fill=tk.X)
        
        # Skill Points Display
        skill_frame = tk.Frame(settings_window, bg="#2a2a2a")
        skill_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(skill_frame, text="💪 Skill Tree Overview", font=("Arial", 11, "bold"), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W)
        
        skill_text = f"Total Skills: {len(self.skills)}\n"
        for skill_name, skill in list(self.skills.items())[:5]:
            skill_text += f"  • {skill['name']}: Lvl {skill['level']}/{skill['max_level']}\n"
        skill_text += f"  ... ({len(self.skills)-5} more skills)"
        
        tk.Label(skill_frame, text=skill_text, font=("Arial", 9), fg="#aaa", bg="#2a2a2a", justify=tk.LEFT).pack(anchor=tk.W)
        
        # Tournament Status
        tournament_frame = tk.Frame(settings_window, bg="#2a2a2a")
        tournament_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(tournament_frame, text="🏆 Tournament Status", font=("Arial", 11, "bold"), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W)
        
        tour_text = f"Active Tournaments: {len([t for t in self.tournaments.values() if t['active']])}\n"
        tour_text += f"PvP Rating: {self.pvp_rating}\n"
        tour_text += f"Current Streak: {self.pvp_streak}"
        
        tk.Label(tournament_frame, text=tour_text, font=("Arial", 9), fg="#aaa", bg="#2a2a2a", justify=tk.LEFT).pack(anchor=tk.W)
        
        # Dungeon Progress
        dungeon_frame = tk.Frame(settings_window, bg="#2a2a2a")
        dungeon_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(dungeon_frame, text="🐉 Dungeon Progress", font=("Arial", 11, "bold"), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W)
        
        dungeon_text = f"Dungeons Completed: {self.dungeons_completed_total}\n"
        dungeon_text += f"Daily Completed: {self.daily_dungeons_completed}\n"
        dungeon_text += f"Current Prestige Level: {self.prestige_level}"
        
        tk.Label(dungeon_frame, text=dungeon_text, font=("Arial", 9), fg="#aaa", bg="#2a2a2a", justify=tk.LEFT).pack(anchor=tk.W)
        
        close_btn = tk.Button(settings_window, text="✓ Close Settings", command=settings_window.destroy, 
                            bg="#00ff00", fg="#000", font=("Arial", 10, "bold"))
        close_btn.pack(pady=10)

    def show_skill_tree_screen(self):
        """Display skill tree interface"""
        tree_window = tk.Toplevel(self.root)
        tree_window.title("💪 Skill Tree")
        tree_window.geometry("600x700")
        tree_window.config(bg="#1a1a1a")
        
        title = tk.Label(tree_window, text="💪 SKILL TREE", font=("Arial", 14, "bold"), fg="#00ff00", bg="#1a1a1a")
        title.pack(pady=10)
        
        canvas = tk.Canvas(tree_window, bg="#1a1a1a", highlightthickness=0)
        scrollbar = tk.Scrollbar(tree_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for skill_name, skill in self.skills.items():
            skill_frame = tk.Frame(scrollable_frame, bg="#2a2a2a")
            skill_frame.pack(fill=tk.X, padx=10, pady=3)
            
            info = f"{skill['name']} Lvl {skill['level']}/{skill['max_level']} | {skill['effect']}"
            tk.Label(skill_frame, text=info, font=("Arial", 9), fg="#aaa", bg="#2a2a2a").pack(anchor=tk.W, padx=5)
            
            def upgrade_callback(s=skill_name):
                success, msg = self.upgrade_skill(s)
                messagebox.showinfo("Skill Upgrade", msg)
                if success:
                    tree_window.destroy()
                    self.show_skill_tree_screen()
            
            upgrade_btn = tk.Button(skill_frame, text=f"Upgrade ({skill['cost_base'] * skill['level']} SP)", 
                                  command=upgrade_callback, bg="#666", fg="#fff", font=("Arial", 8))
            upgrade_btn.pack(anchor=tk.W, padx=5)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_tournament_screen(self):
        """Display tournament selection and participation"""
        tournament_window = tk.Toplevel(self.root)
        tournament_window.title("🏆 Tournaments")
        tournament_window.geometry("700x600")
        tournament_window.config(bg="#1a1a1a")
        
        title = tk.Label(tournament_window, text="🏆 TOURNAMENTS", font=("Arial", 14, "bold"), fg="#00ff00", bg="#1a1a1a")
        title.pack(pady=10)
        
        canvas = tk.Canvas(tournament_window, bg="#1a1a1a", highlightthickness=0)
        scrollbar = tk.Scrollbar(tournament_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for t_name, tournament in self.tournaments.items():
            t_frame = tk.Frame(scrollable_frame, bg="#2a2a2a")
            t_frame.pack(fill=tk.X, padx=10, pady=5)
            
            header = tk.Label(t_frame, text=f"{tournament['name']} - {tournament['desc']}", 
                            font=("Arial", 10, "bold"), fg="#00ff00", bg="#2a2a2a")
            header.pack(anchor=tk.W, padx=5, pady=3)
            
            stats = f"Rounds: {tournament['rounds']} | Reward: {tournament['prize']} SP | Type: {tournament['type'].upper()}"
            tk.Label(t_frame, text=stats, font=("Arial", 9), fg="#aaa", bg="#2a2a2a").pack(anchor=tk.W, padx=15)
            
            score_text = f"Your Score: {self.tournament_scores.get(t_name, 0)}"
            tk.Label(t_frame, text=score_text, font=("Arial", 9), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W, padx=15)
            
            def join_callback(tn=t_name):
                success, msg = self.participate_in_tournament(tn)
                messagebox.showinfo("Tournament", msg)
            
            join_btn = tk.Button(t_frame, text="▶ Join Tournament", command=join_callback, 
                               bg="#ff6600", fg="#000", font=("Arial", 9, "bold"))
            join_btn.pack(anchor=tk.W, padx=15, pady=3)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_dungeon_screen(self):
        """Display dungeon interface"""
        dungeon_window = tk.Toplevel(self.root)
        dungeon_window.title("🐉 Dungeons")
        dungeon_window.geometry("500x500")
        dungeon_window.config(bg="#1a1a1a")
        
        title = tk.Label(dungeon_window, text="🐉 DUNGEONS", font=("Arial", 14, "bold"), fg="#00ff00", bg="#1a1a1a")
        title.pack(pady=10)
        
        for difficulty, dungeon in self.dungeons.items():
            d_frame = tk.Frame(dungeon_window, bg="#2a2a2a")
            d_frame.pack(fill=tk.X, padx=10, pady=10)
            
            header = tk.Label(d_frame, text=f"{dungeon['name']} - {dungeon['boss']}", 
                            font=("Arial", 10, "bold"), fg="#ff6600", bg="#2a2a2a")
            header.pack(anchor=tk.W, padx=5, pady=3)
            
            stats = f"Boss HP: {dungeon['hp']} | Reward: {dungeon['reward']} SP | Difficulty: {dungeon['difficulty']}x"
            tk.Label(d_frame, text=stats, font=("Arial", 9), fg="#aaa", bg="#2a2a2a").pack(anchor=tk.W, padx=15)
            
            def enter_callback(diff=difficulty):
                success, msg = self.enter_dungeon(diff)
                messagebox.showinfo("Dungeon", msg)
            
            enter_btn = tk.Button(d_frame, text="⚔️ Enter Dungeon", command=enter_callback, 
                                bg="#ff0000", fg="#fff", font=("Arial", 9, "bold"))
            enter_btn.pack(anchor=tk.W, padx=15, pady=3)

    def show_pvp_screen(self):
        """Display PvP battle interface"""
        pvp_window = tk.Toplevel(self.root)
        pvp_window.title("⚔️ PvP Battles")
        pvp_window.geometry("500x400")
        pvp_window.config(bg="#1a1a1a")
        
        title = tk.Label(pvp_window, text="⚔️ PvP BATTLES", font=("Arial", 14, "bold"), fg="#00ff00", bg="#1a1a1a")
        title.pack(pady=10)
        
        stats_frame = tk.Frame(pvp_window, bg="#2a2a2a")
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        
        stats_text = f"Rating: {self.pvp_rating}\nWins: {self.pvp_wins} | Losses: {self.pvp_losses}\nStreak: {self.pvp_streak}"
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W)
        
        opponent_frame = tk.Frame(pvp_window, bg="#2a2a2a")
        opponent_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(opponent_frame, text="Find an Opponent", font=("Arial", 11, "bold"), fg="#00ff00", bg="#2a2a2a").pack(anchor=tk.W, pady=5)
        
        def simulate_battle():
            opponent_skill = random.randint(40, 80)
            result, msg = self.simulate_pvp_battle(opponent_skill)
            messagebox.showinfo("PvP Battle", msg)
            pvp_window.destroy()
            self.show_pvp_screen()
        
        battle_btn = tk.Button(opponent_frame, text="⚡ Battle!", command=simulate_battle, 
                             bg="#ff0000", fg="#fff", font=("Arial", 11, "bold"), height=2)
        battle_btn.pack(fill=tk.X)

    def toggle_dev_console(self):
        """Toggle developer console - v1.67 Feature (Ctrl+Shift+D)"""
        self.dev_console_open = not self.dev_console_open
        if self.dev_console_open:
            self.show_dev_console()
        else:
            if hasattr(self, 'dev_win') and self.dev_win.winfo_exists():
                self.dev_win.destroy()
    
    def show_dev_console(self):
        """Show developer console window"""
        if hasattr(self, 'dev_win') and self.dev_win.winfo_exists():
            self.dev_win.lift()
            return
        
        self.dev_win = tk.Toplevel(self.root)
        self.dev_win.title("🔧 v1.67 BUSSIN DEV CONSOLE - ULTRA TUFF EZZZ")
        self.dev_win.geometry("600x400")
        self.dev_win.configure(bg="#0a0a0a")
        
        tk.Label(self.dev_win, text="v1.67 BUSSIN DEV CONSOLE - PEAK RIZZ", font=("Courier", 12, "bold"),
                bg="#0a0a0a", fg="#00ff00").pack(pady=5)
        
        # Command input
        cmd_frame = tk.Frame(self.dev_win, bg="#0a0a0a")
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(cmd_frame, text=">", bg="#0a0a0a", fg="#00ff00", font=("Courier", 10)).pack(side=tk.LEFT)
        cmd_entry = tk.Entry(cmd_frame, bg="#1a1a1a", fg="#00ff00", font=("Courier", 10))
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Output area
        output = scrolledtext.ScrolledText(self.dev_win, bg="#0a0a0a", fg="#00ff00",
                                          font=("Courier", 9), height=15)
        output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Show help
        help_text = """BUSSIN v1.67 DEV COMMANDS - EZZZ MODE:
  add_sp <amount> - Add SP (SUPER TUFF)
  add_win - Add a win (DUPER COOL)
  set_mode <classic/speedrun/hardcore> - PEAK MODE (ULTRA)
  easter_egg <code> - Trigger BUSSIN egg (EXTREME)
  facebook - Enable BUSSIN Facebook mode (OGMGMGMGM)
  version - v1.67 BUSSIN UPDATE
  help - Show this RIZZ help
"""
        output.insert(tk.END, help_text)
        output.config(state=tk.DISABLED)
        
        def execute_command():
            cmd = cmd_entry.get().strip()
            output.config(state=tk.NORMAL)
            output.insert(tk.END, f"\n> {cmd}")
            
            try:
                if cmd.startswith("add_sp"):
                    parts = cmd.split()
                    amount = int(parts[1]) if len(parts) > 1 else 10
                    self.sp += amount
                    output.insert(tk.END, f"\n✓ YO BUSSIN! Added {amount} SP - ULTRA TUFF! (Total: {self.sp})")
                elif cmd == "add_win":
                    self.wins_count += 1
                    output.insert(tk.END, f"\n✓ PEAK WIN ADDED! EZZZ MODE! (Total: {self.wins_count})")
                elif cmd.startswith("set_mode"):
                    parts = cmd.split()
                    if len(parts) > 1:
                        self.current_mode = parts[1].capitalize()
                        output.insert(tk.END, f"\n✓ DUPER COOL MODE! {self.current_mode} BUSSIN ACTIVATED!")
                    else:
                        output.insert(tk.END, "\n✗ YO USE: set_mode <classic/speedrun/hardcore> - TUFF")
                elif cmd.startswith("easter_egg"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) > 1:
                        code = parts[1]
                        result = self.find_easter_egg(code)
                        output.insert(tk.END, f"\n{result if result else '✗ Invalid code'}")
                    else:
                        output.insert(tk.END, "\n✗ Usage: easter_egg <code>")
                elif cmd == "facebook":
                    self.facebook_test_mode = True
                    output.insert(tk.END, "\n✓ OGMGMGMGM FACEBOOK BUSSIN MODE ENABLED! ULTRA RIZZ!")
                elif cmd == "version":
                    output.insert(tk.END, "\nv1.67 BUSSIN APRIL FOOLS UPDATE - PEAK RIZZ! EZZZ! 67!")
                elif cmd == "help":
                    output.insert(tk.END, help_text)
                else:
                    output.insert(tk.END, "\n✗ YO THAT COMMAND NOT BUSSIN BRO! LLOLOLOL")
            except Exception as e:
                output.insert(tk.END, f"\n✗ YO ERROR TUFF! {e} - NOT BUSSIN!")
            
            output.see(tk.END)
            output.config(state=tk.DISABLED)
            cmd_entry.delete(0, tk.END)
        
        tk.Button(cmd_frame, text="Execute", command=execute_command, bg="#00aa00",
                 fg="#000", font=("Courier", 9)).pack(side=tk.LEFT, padx=5)
        
        cmd_entry.bind("<Return>", lambda e: execute_command())
        cmd_entry.focus()
    
    def calculate_xp(self, sp_gained):
        """Calculate XP earned based on SP gained"""
        # Base XP is roughly 1/10 of SP
        xp_earned = max(1, sp_gained // 10)
        return xp_earned
    
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
        
        # Update properties
        if properties:
            props_display = "\n".join([
                ("✓ " if prop in self.target_properties else "  ") + self._property_name_display(prop)
                for prop in sorted(properties)
            ])
        else:
            props_display = "(No notable properties)"
        self.props_text.config(text=props_display)
        
        # Update match count
        color = "#00ff00" if matches == total_targets else "#ff6b6b"
        self.match_label.config(text=f"{matches}/{total_targets} matches", fg=color)
        
        # Update roll count
        self.roll_label.config(text=str(self.roll_count))
        
        # Check auto-roll unlock
        if self.roll_count >= 50000 and self.auto_button.cget("state") == tk.DISABLED:
            self.auto_button.config(state=tk.NORMAL)
            self.match_label.config(text="⚡ AUTO-ROLL UNLOCKED! ⚡", fg="#00ff00", font=("Arial", 14, "bold"))
    
    def manual_roll(self):
        # 🃏 April Fools prank trigger
        prank_msg = self.trigger_april_fools_prank()
        if prank_msg and self.april_fools_active:
            self.match_label.config(text=prank_msg, fg="#ff6600")
            self.apply_april_fools_effect()
        
        """Perform a manual roll"""
        self.roll_count += 1
        s = self._generate_random_string()
        properties = self._analyze_string(s)
        
        # Update property discoveries
        for prop in properties:
            prop_name = self._property_name_display(prop)
            self.stats['property_discoveries'][prop_name] = self.stats['property_discoveries'].get(prop_name, 0) + 1
        
        self.rolls_history.append({
            'number': self.roll_count,
            'string': s,
            'properties': properties
        })
        
        self._update_display(s, properties)
        self._play_roll_sound()
        self._check_achievements()
        
        # Check if won
        if properties == self.target_properties:
            self.wins_count += 1
            self.wins_label.config(text=str(self.wins_count))
            self.match_label.config(text="🏆 SUCCESS! 🏆", fg="#00ff00", font=("Arial", 16, "bold"))
            self._play_success_sound()
            
            # Calculate SP based on string length
            sp_type, sp_display = self._calculate_sp(len(s))
            if sp_type == "sp":
                self.sp += 1
            elif sp_type == "sp_plus":
                self.sp_plus += 1
            elif sp_type == "sp_x":
                self.sp_x += 1
            elif sp_type == "sp_caret":
                self.sp_caret += 1
            
            self._update_sp_label()
            
            # Update daily challenges and get rewards
            challenge_rewards = self._update_challenges(sp_type, len(s))
            reward_text = ""
            if challenge_rewards:
                reward_text = "\n\n⭐ CHALLENGES COMPLETED:\n" + challenge_rewards
            
            player_title = self._get_player_title_for_wins(self.wins_count)
            messagebox.showinfo("Victory!", f"Won sequence!\n+1 {sp_display}\n\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\n\nRank: {player_title}{reward_text}")
            
            # Update stats
            rolls_in_win = len([r for r in self.rolls_history if r['number'] > (self.rolls_history[-1]['number'] - len(self.rolls_history))])
            self.stats['fastest_win'] = min(self.stats['fastest_win'], rolls_in_win)
            self.stats['slowest_win'] = max(self.stats['slowest_win'], rolls_in_win)
            self.stats['current_streak'] += 1
            self.stats['best_streak'] = max(self.stats['best_streak'], self.stats['current_streak'])
            
            # Update perfect series challenge (challenge 7)
            if self.stats['current_streak'] >= 3:
                self.challenge_progress["challenge_7"] = max(self.challenge_progress.get("challenge_7", 0), self.stats['current_streak'])
            
            # Generate new target after 2 seconds
            self.root.after(2000, self._next_sequence)
    
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
        self.match_label.config(text="0/0 matches", fg="#ff6b6b", font=("Arial", 14, "bold"))
        self.roll_text.config(text="(No rolls yet)")
        self.props_text.config(text="(Roll to analyze)")
        self.roll_button.config(state=tk.NORMAL)
        self.history_button.config(state=tk.NORMAL)
    
    
    def auto_roll_thread(self):
        """Auto-roll in a separate thread"""
        session_start = self.roll_count
        
        while self.auto_rolling:
            for _ in range(10):
                if not self.auto_rolling:
                    break
                
                self.roll_count += 1
                s = self._generate_random_string()
                properties = self._analyze_string(s)
                
                # Update property discoveries
                for prop in properties:
                    prop_name = self._property_name_display(prop)
                    self.stats['property_discoveries'][prop_name] = self.stats['property_discoveries'].get(prop_name, 0) + 1
                
                self.rolls_history.append({
                    'number': self.roll_count,
                    'string': s,
                    'properties': properties
                })
                
                self.root.after(0, self._update_display, s, properties)
                
                if properties == self.target_properties:
                    self.wins_count += 1
                    self.root.after(0, lambda: self.wins_label.config(text=str(self.wins_count)))
                    self.root.after(0, lambda: self.match_label.config(text="🏆 SUCCESS! 🏆", fg="#00ff00", font=("Arial", 16, "bold")))
                    self.root.after(0, self._play_success_sound)
                    
                    # Update stats
                    rolls_in_win = len([r for r in self.rolls_history if r['number'] > (self.rolls_history[-1]['number'] - len(self.rolls_history))])
                    self.stats['fastest_win'] = min(self.stats['fastest_win'], rolls_in_win)
                    self.stats['slowest_win'] = max(self.stats['slowest_win'], rolls_in_win)
                    self.stats['current_streak'] += 1
                    self.stats['best_streak'] = max(self.stats['best_streak'], self.stats['current_streak'])
                    
                    time.sleep(2)  # Pause before next sequence
                    self.root.after(0, self._next_sequence)
                    break
            
            time.sleep(0.1)  # 10 rolls per second
        
        # Auto-roll stopped
        self.root.after(0, self.stop_auto_roll_gui)
    
    def stop_auto_roll_gui(self):
        """Stop auto-roll GUI update"""
        self.auto_rolling = False
        self.auto_button.config(state=tk.NORMAL, text="⚡ AUTO-ROLL")
        self.roll_button.config(state=tk.NORMAL)
    
    
    def show_april_fools_menu(self):
        """Show April Fools event menu"""
        event_win = tk.Toplevel(self.root)
        event_win.title("🃏 April Fools Event 🃏")
        event_win.geometry("500x400")
        event_win.configure(bg="#2b2b2b")
        
        title = tk.Label(event_win, text="🎉 APRIL FOOLS EVENT 🎉", 
                        font=("Arial", 16, "bold"), bg="#2b2b2b", fg="#ff6600")
        title.pack(pady=10)
        
        info_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 APRIL FOOLS MODE ACTIVE 🎭
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pranks Triggered:    {self.prank_count}
Easter Eggs Found:   {self.easter_eggs_found}
Troll Level:         {self.troll_level}

Current Prank:       {self.pranks_triggered[-1] if self.pranks_triggered else 'None'}

Active Pranks:
{chr(10).join([f"  ✓ {p}: {'ACTIVE' if self.pranks[p]['active'] else 'off'}" for p in list(self.pranks.keys())[:4]])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event Bonus SP: +{self.april_fools_bonus_sp()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎪 Find all hidden Easter Eggs!
🎲 Survive the Pranks!
👹 Unlock Troll Mode!
"""
        
        info_label = tk.Label(event_win, text=info_text, font=("Courier", 9),
                             bg="#1e1e1e", fg="#00ff00", justify=tk.LEFT)
        info_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Easter egg code entry
        code_frame = tk.Frame(event_win, bg="#2b2b2b")
        code_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(code_frame, text="Secret Code:", bg="#2b2b2b", fg="#fff").pack(side=tk.LEFT)
        code_entry = tk.Entry(code_frame, bg="#333", fg="#0f0", font=("Courier", 10))
        code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        def check_code():
            code = code_entry.get()
            result = self.find_easter_egg(code)
            if result:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Easter Egg Found!", result)
                code_entry.delete(0, tk.END)
        
        tk.Button(code_frame, text="Check", command=check_code, bg="#00aa00", 
                 fg="#000", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

    def show_history_window(self):
        """Show roll history in new window"""
        if not self.rolls_history:
            self.match_label.config(text="No rolls yet!", fg="#ff6b6b", font=("Arial", 14, "bold"))
            return
        
        history_win = tk.Toplevel(self.root)
        history_win.title("Roll History")
        history_win.geometry("700x500")
        history_win.configure(bg="#2b2b2b")
        
        text_widget = scrolledtext.ScrolledText(history_win, font=("Courier", 9),
                                               bg="#1e1e1e", fg="#00ff00")
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add history text
        text_widget.insert(tk.END, f"ROLL HISTORY (Total: {len(self.rolls_history)} rolls)\n")
        text_widget.insert(tk.END, "="*70 + "\n\n")
        
        for entry in self.rolls_history[-50:]:
            matches = len(entry['properties'] & self.target_properties)
            total = len(self.target_properties)
            preview = entry['string'][:40] + "..." if len(entry['string']) > 40 else entry['string']
            text_widget.insert(tk.END, f"Roll {entry['number']:6d}: \"{preview}\" - {matches}/{total} match\n")
        
        if len(self.rolls_history) > 50:
            text_widget.insert(tk.END, f"\n... and {len(self.rolls_history) - 50} more rolls")
        
        text_widget.config(state=tk.DISABLED)
    
    def reset_game(self):
        """Reset for new game"""
        self.roll_count = 0
        self.rolls_history = []
        self.wins_count = 0
        self.game_won = False
        self.auto_rolling = False
        self.auto_button.config(state=tk.DISABLED, text="⚡ AUTO-ROLL")
        self.roll_button.config(state=tk.NORMAL)
        
        self._generate_target()
        
        self.roll_text.config(text="(No rolls yet)")
        self.props_text.config(text="(Roll to analyze)")
        self.match_label.config(text="0/0 matches")
        self.roll_label.config(text="0")
        self.wins_label.config(text="0")
    
    def quit_game(self):
        """Quit the game"""
        self.auto_rolling = False
        self._save_stats()
        self._save_achievements()
        self._save_equipment()
        self.root.destroy()
    
    def _update_sp_label(self):
        """Update SP label display with all SP types"""
        display = f"{self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}"
        self.sp_label.config(text=display)
    
    def _calculate_sp(self, string_length):
        """Calculate SP type gained based on string length and return (sp_type, display_name)"""
        if string_length >= 25:  # Reduced from 40 to 25 for SP^
            return ("sp_caret", "SP^")  # 4 SP
        elif string_length >= 15:  # Reduced from 20 to 15 for SPx
            return ("sp_x", "SPx")  # 3 SP
        elif string_length >= 8:  # Reduced from 10 to 8 for SP+
            return ("sp_plus", "SP+")  # 2 SP
        elif string_length >= 4:  # Reduced from 5 to 4 for SP
            return ("sp", "SP")  # 1 SP
        return ("none", "No SP")
    
    def show_equipment_window(self):
        """Show equipment crafting and equipping window"""
        eq_win = tk.Toplevel(self.root)
        eq_win.title("⚙️ Equipment Crafting")
        eq_win.geometry("900x650")
        eq_win.configure(bg="#2b2b2b")
        
        # Title
        tk.Label(eq_win, text="⚙️ EQUIPMENT CRAFTING & MANAGEMENT", font=("Arial", 14, "bold"),
                bg="#2b2b2b", fg="#00ff00").pack(pady=10)
        
        # SP display with all types
        sp_frame = tk.Frame(eq_win, bg="#1e1e1e")
        sp_frame.pack(fill=tk.X, padx=10, pady=5)
        sp_text = f"SP: {self.sp}  |  SP+: {self.sp_plus}  |  SPx: {self.sp_x}  |  SP^: {self.sp_caret}"
        tk.Label(sp_frame, text=sp_text, font=("Arial", 12, "bold"),
                bg="#1e1e1e", fg="#ff00ff").pack(pady=5)
        
        def check_cost(cost_dict):
            """Check if player has enough SP to craft"""
            for sp_type, amount in cost_dict.items():
                if sp_type == "sp" and self.sp < amount:
                    return False
                elif sp_type == "sp_plus" and self.sp_plus < amount:
                    return False
                elif sp_type == "sp_x" and self.sp_x < amount:
                    return False
                elif sp_type == "sp_caret" and self.sp_caret < amount:
                    return False
            return True
        
        def deduct_cost(cost_dict):
            """Deduct SP from player"""
            for sp_type, amount in cost_dict.items():
                if sp_type == "sp":
                    self.sp -= amount
                elif sp_type == "sp_plus":
                    self.sp_plus -= amount
                elif sp_type == "sp_x":
                    self.sp_x -= amount
                elif sp_type == "sp_caret":
                    self.sp_caret -= amount
            self._update_sp_label()
        
        def cost_str(cost_dict):
            """Convert cost dict to display string"""
            parts = []
            if "sp" in cost_dict:
                parts.append(f"{cost_dict['sp']} SP")
            if "sp_plus" in cost_dict:
                parts.append(f"{cost_dict['sp_plus']} SP+")
            if "sp_x" in cost_dict:
                parts.append(f"{cost_dict['sp_x']} SPx")
            if "sp_caret" in cost_dict:
                parts.append(f"{cost_dict['sp_caret']} SP^")
            return " + ".join(parts)
        
        # Gauntlets section
        gaunts_frame = tk.LabelFrame(eq_win, text="🧤 GAUNTLETS (Left Hand)", font=("Arial", 12, "bold"),
                                     bg="#2b2b2b", fg="#00ff00", padx=10, pady=10)
        gaunts_frame.pack(fill=tk.X, padx=10, pady=5)
        
        gauntlets = {k: v for k, v in self.equipment_recipes.items() if v["type"] == "gauntlet"}
        
        for eq_name, recipe in gauntlets.items():
            btn_frame = tk.Frame(gaunts_frame, bg="#2b2b2b")
            btn_frame.pack(fill=tk.X, pady=3)
            
            info_text = f"{eq_name}  |  Cost: {cost_str(recipe['cost'])}  |  {recipe['desc']}"
            tk.Label(btn_frame, text=info_text, font=("Arial", 9), bg="#2b2b2b", fg="#ffffff", 
                    justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
            
            def craft_gauntlet(en=eq_name):
                if check_cost(self.equipment_recipes[en]["cost"]):
                    deduct_cost(self.equipment_recipes[en]["cost"])
                    if en not in self.equipment_inventory.get("owned", []):
                        self.equipment_inventory.setdefault("owned", []).append(en)
                    self._save_equipment()
                    messagebox.showinfo("Crafted!", f"Created {en}!")
                    eq_win.destroy()
                    self.show_equipment_window()
                else:
                    cost_needed = cost_str(self.equipment_recipes[en]["cost"])
                    messagebox.showerror("Insufficient SP", f"Need: {cost_needed}")
            
            tk.Button(btn_frame, text="Buy", command=craft_gauntlet, bg="#00aa00", fg="#000000",
                     font=("Arial", 9, "bold"), padx=10).pack(side=tk.RIGHT, padx=5)
        
        # Devices section (with green buttons)
        devices_frame = tk.LabelFrame(eq_win, text="📱 DEVICES (Right Hand)", font=("Arial", 12, "bold"),
                                      bg="#2b2b2b", fg="#00ff00", padx=10, pady=10)
        devices_frame.pack(fill=tk.X, padx=10, pady=5)
        
        devices = {k: v for k, v in self.equipment_recipes.items() if v["type"] == "device"}
        
        for eq_name, recipe in devices.items():
            btn_frame = tk.Frame(devices_frame, bg="#2b2b2b")
            btn_frame.pack(fill=tk.X, pady=3)
            
            info_text = f"{eq_name}  |  Cost: {cost_str(recipe['cost'])}  |  {recipe['desc']}"
            tk.Label(btn_frame, text=info_text, font=("Arial", 9), bg="#2b2b2b", fg="#ffffff",
                    justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
            
            def craft_device(en=eq_name):
                if check_cost(self.equipment_recipes[en]["cost"]):
                    deduct_cost(self.equipment_recipes[en]["cost"])
                    if en not in self.equipment_inventory.get("owned", []):
                        self.equipment_inventory.setdefault("owned", []).append(en)
                    self._save_equipment()
                    messagebox.showinfo("Crafted!", f"Created {en}!")
                    eq_win.destroy()
                    self.show_equipment_window()
                else:
                    cost_needed = cost_str(self.equipment_recipes[en]["cost"])
                    messagebox.showerror("Insufficient SP", f"Need: {cost_needed}")
            
            tk.Button(btn_frame, text="Buy", command=craft_device, bg="#00ff00", fg="#000000",
                     font=("Arial", 9, "bold"), padx=10).pack(side=tk.RIGHT, padx=5)
        
        # Equipment tab
        equip_frame = tk.LabelFrame(eq_win, text="⚙️ EQUIPPED ITEMS", font=("Arial", 12, "bold"),
                                    bg="#2b2b2b", fg="#00ff00", padx=10, pady=10)
        equip_frame.pack(fill=tk.X, padx=10, pady=5)
        
        owned = self.equipment_inventory.get("owned", [])
        
        def equip_gauntlet(eq_name):
            self.equipped_gauntlet = eq_name if eq_name != "none" else None
            self._save_equipment()
            eq_win.destroy()
            self.show_equipment_window()
        
        def equip_device(eq_name):
            self.equipped_device = eq_name if eq_name != "none" else None
            self._save_equipment()
            eq_win.destroy()
            self.show_equipment_window()
        
        gauntlet_owned = [eq for eq in owned if self.equipment_recipes.get(eq, {}).get("type") == "gauntlet"]
        device_owned = [eq for eq in owned if self.equipment_recipes.get(eq, {}).get("type") == "device"]
        
        g_frame = tk.Frame(equip_frame, bg="#2b2b2b")
        g_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(g_frame, text="Left Hand (Gauntlet):", font=("Arial", 10, "bold"), bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        tk.Button(g_frame, text="None", command=lambda: equip_gauntlet("none"), bg="#666666", fg="#ffffff", width=12).pack(side=tk.LEFT, padx=2)
        for g in gauntlet_owned:
            tk.Button(g_frame, text=g, command=lambda gn=g: equip_gauntlet(gn), bg="#00aa00", fg="#000000", width=12).pack(side=tk.LEFT, padx=2)
        
        d_frame = tk.Frame(equip_frame, bg="#2b2b2b")
        d_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(d_frame, text="Right Hand (Device):", font=("Arial", 10, "bold"), bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT, padx=5)
        tk.Button(d_frame, text="None", command=lambda: equip_device("none"), bg="#666666", fg="#ffffff", width=12).pack(side=tk.LEFT, padx=2)
        for d in device_owned:
            tk.Button(d_frame, text=d, command=lambda dn=d: equip_device(dn), bg="#00ff00", fg="#000000", width=12).pack(side=tk.LEFT, padx=2)
    
    def run(self):
        """Run the game"""
        self.root.mainloop()


def main():
    """Main entry point - shows login screen then initializes game with authenticated user"""
    account_mgr = AccountManager()
    root = tk.Tk()
    root.title("Rolling Game - Login")
    root.geometry("420x350")
    root.configure(bg="#1a1a1a")
    root.resizable(False, False)
    
    login_result = {'username': None, 'logged_in': False}
    
    def on_login_success(username):
        """Callback when user successfully logs in or creates account"""
        login_result['username'] = username
        login_result['logged_in'] = True
        root.destroy()
    
    def on_cancel():
        """User cancelled - exit application"""
        root.destroy()
    
    # Main login frame
    main_frame = tk.Frame(root, bg="#1a1a1a")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, text="🎮 Rolling Game", font=("Arial", 22, "bold"), bg="#1a1a1a", fg="#00ff00")
    title_label.pack(pady=(0, 20))
    
    subtitle_label = tk.Label(main_frame, text="Account Login / Register", font=("Arial", 11), bg="#1a1a1a", fg="#888")
    subtitle_label.pack(pady=(0, 15))
    
    # Mode tracking
    mode_var = tk.StringVar(value="login")
    
    # Form container
    form_frame = tk.Frame(main_frame, bg="#1a1a1a")
    form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Entry fields
    tk.Label(form_frame, text="Username:", bg="#1a1a1a", fg="#cccccc", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 3))
    user_entry = tk.Entry(form_frame, width=35, bg="#2a2a2a", fg="#00ff00", insertbackground="#00ff00", font=("Arial", 10))
    user_entry.pack(fill=tk.X, pady=(0, 12))
    
    tk.Label(form_frame, text="Password:", bg="#1a1a1a", fg="#cccccc", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 3))
    pass_entry = tk.Entry(form_frame, width=35, show="•", bg="#2a2a2a", fg="#00ff00", insertbackground="#00ff00", font=("Arial", 10))
    pass_entry.pack(fill=tk.X, pady=(0, 15))
    
    # Status label
    status_label = tk.Label(form_frame, text="", bg="#1a1a1a", fg="#ff6600", font=("Arial", 9))
    status_label.pack(pady=(0, 10))
    
    def submit_auth():
        """Process login or registration"""
        username = user_entry.get().strip()
        password = pass_entry.get()
        
        if not username or not password:
            status_label.config(text="⚠️ Enter username and password", fg="#ff6600")
            return
        
        if mode_var.get() == "login":
            if account_mgr.login(username, password):
                on_login_success(username)
            else:
                status_label.config(text="❌ Invalid username or password", fg="#ff0000")
                pass_entry.delete(0, tk.END)
        else:  # register
            if len(username) < 3:
                status_label.config(text="⚠️ Username must be 3+ characters", fg="#ff6600")
                return
            if len(password) < 4:
                status_label.config(text="⚠️ Password must be 4+ characters", fg="#ff6600")
                return
            
            if account_mgr.register(username, password):
                status_label.config(text="✅ Account created! Logging in...", fg="#00ff00")
                root.after(500, lambda: on_login_success(username))
            else:
                status_label.config(text="❌ Username already exists", fg="#ff0000")
                user_entry.delete(0, tk.END)
    
    def toggle_mode():
        """Toggle between login and register"""
        if mode_var.get() == "login":
            mode_var.set("register")
            mode_btn.config(text="← Back to Login")
            title_label.config(text="📝 Create Account")
            submit_btn.config(text="Register")
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            status_label.config(text="")
        else:
            mode_var.set("login")
            mode_btn.config(text="Create Account →")
            title_label.config(text="🎮 Rolling Game")
            submit_btn.config(text="Login")
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            status_label.config(text="")
    
    def guest_login():
        """Login as guest"""
        guest_username = "Guest_" + str(int(time.time() * 1000) % 100000)
        on_login_success(guest_username)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#1a1a1a")
    button_frame.pack(fill=tk.X, pady=(15, 0))
    
    submit_btn = tk.Button(button_frame, text="Login", command=submit_auth, bg="#00ff00", fg="#000", font=("Arial", 10, "bold"), width=12)
    submit_btn.pack(side=tk.LEFT, padx=3)
    
    mode_btn = tk.Button(button_frame, text="Create Account →", command=toggle_mode, bg="#ff6600", fg="#000", font=("Arial", 10, "bold"), width=16)
    mode_btn.pack(side=tk.LEFT, padx=3)
    
    guest_btn = tk.Button(button_frame, text="👤 Guest", command=guest_login, bg="#555", fg="#fff", font=("Arial", 10), width=8)
    guest_btn.pack(side=tk.LEFT, padx=3)
    
    exit_btn = tk.Button(button_frame, text="✕", command=on_cancel, bg="#333", fg="#fff", font=("Arial", 10), width=2)
    exit_btn.pack(side=tk.RIGHT, padx=3)
    
    # Bind Enter key
    user_entry.bind('<Return>', lambda e: pass_entry.focus())
    pass_entry.bind('<Return>', lambda e: submit_auth())
    
    root.mainloop()
    
    # Start game if login successful
    if login_result['logged_in']:
        game = RollingGame(username=login_result['username'])
        game.run()


if __name__ == "__main__":
    main()
