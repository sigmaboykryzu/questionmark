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
        self.current_user = None
        self.accounts = self._load_accounts()
    
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
        self.wins_count = 0
        self.current_theme = "dark"
        self.sound_enabled = True
        self.animations_enabled = True
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        self.tutorial_mode = False
        self.tutorial_step = 0
        
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
            "infinity_device": {"type": "device", "cost": {"sp_caret": 1}, "effect": "perfect_vision", "desc": "See all target properties"}
        }
    
    def _init_daily_challenges(self):
        """Initialize daily challenges system"""
        return {
            "challenge_1": {"name": "Quick Thinker", "desc": "Win 3 sequences", "target": 3, "reward_sp": 5, "icon": "⚡"},
            "challenge_2": {"name": "Accuracy Master", "desc": "Win 5 sequences", "target": 5, "reward_sp": 8, "icon": "🎯"},
            "challenge_3": {"name": "SP+ Collector", "desc": "Earn 3 SP+", "target": 3, "reward_sp": 10, "icon": "⬆"},
            "challenge_4": {"name": "SPx Collector", "desc": "Earn 2 SPx", "target": 2, "reward_sp": 15, "icon": "✕"},
            "challenge_5": {"name": "SP^ Collector", "desc": "Earn 1 SP^", "target": 1, "reward_sp": 25, "icon": "▲"},
            "challenge_6": {"name": "Grinding Session", "desc": "Roll 50 times", "target": 50, "reward_sp": 12, "icon": "🔄"},
            "challenge_7": {"name": "Perfect Series", "desc": "Win 3 in a row", "target": 3, "reward_sp": 20, "icon": "🔥"},
            "challenge_8": {"name": "Long String Master", "desc": "Win with 25+ char string", "target": 1, "reward_sp": 18, "icon": "📝"}
        }
    
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
        
        # Randomly select 2-4 target properties (balanced difficulty)
        num_targets = random.randint(2, 4)
        self.target_properties = set(random.sample(possible_properties, num_targets))
    
    def show_login_screen(self):
        """Show account login/register screen"""
        login_root = tk.Tk()
        login_root.title("🎮 Account Login")
        login_root.geometry("400x350")
        login_root.configure(bg="#2b2b2b")
        login_root.resizable(False, False)
        
        title_label = tk.Label(login_root, text="🎲 Property Deduction", font=("Arial", 16, "bold"),
                              bg="#2b2b2b", fg="#00ff00")
        title_label.pack(pady=20)
        
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
        self.root.title("🎲 Property Deduction Rolling Game")
        self.root.geometry("900x750")
        self.root.configure(bg="#2b2b2b")
        
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
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings_window)
        tools_menu.add_command(label="Equipment Crafting", command=self.show_equipment_window)
        tools_menu.add_command(label="Mini-Game", command=self.play_mini_game)
        tools_menu.add_command(label="Tutorial", command=self.start_tutorial)
        
        # Title
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(title_frame, text="🎲 PROPERTY DEDUCTION ROLLING GAME", 
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
        
        self.quit_button = tk.Button(button_frame, text="❌ QUIT", font=("Arial", 12, "bold"),
                                     bg="#cc0000", fg="#ffffff", padx=20, pady=10,
                                     activebackground="#cc0000", activeforeground="#ffffff",
                                     command=self.quit_game, width=15)
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
        # Info text
        info = tk.Label(self.root, text="Deduce the hidden properties by analyzing roll results. Auto-roll unlocks at 50,000 rolls.",
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
        if self.stats.get('fastest_win', float('inf')) <= 30 and not self.achievements["speed_demon"]["unlocked"]:
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
        settings_win.title("⚙️ Settings & Account")
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
            "Welcome to Property Deduction! Click ROLL to generate random strings.",
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
            "rolls_history": self.rolls_history[-100:],  # Save last 100 rolls
            "achievements": self.achievements,
            "stats": self.stats,
            "theme": self.current_theme,
            "sound_enabled": self.sound_enabled,
            "animations_enabled": self.animations_enabled
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
        ach_win.title("🏆 Achievements")
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
        stats_win.title("📊 Statistics")
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
        mini_win.title("🎮 Mini-Game: Property Match")
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
        leaderboard_win.title("🏅 Global Leaderboard")
        leaderboard_win.geometry("500x400")
        leaderboard_win.configure(bg="#2b2b2b")
        
        tk.Label(leaderboard_win, text="🏅 GLOBAL LEADERBOARD", font=("Arial", 16, "bold"), 
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
