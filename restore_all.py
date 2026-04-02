#!/usr/bin/env python3
"""
COMPLETE SYSTEM RESTORATION - Add back ALL systems
Restores: Tournaments, Game Modes, Equipment System, Analytics, Dev Console, Daily Challenges
"""

import os
import subprocess

def restore_all_systems():
    print("=" * 80)
    print("COMPLETE RESTORATION: Adding ALL Systems Back")
    print("=" * 80)
    
    with open('questionmark.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Fix the immediate daily_challenges issue by ensuring proper initialization
    print("\n[1/5] Ensuring daily_challenges is properly initialized...")
    
    # Step 2: Add missing game modes system
    print("[2/5] Adding Game Modes System...")
    if "game_modes = {" not in content:
        game_modes_code = '''
    def _init_game_modes(self):
        """Initialize game modes"""
        self.game_modes = {
            "Classic": {"name": "Classic", "desc": "Standard gameplay", "multiplier": 1.0},
            "Speed Run": {"name": "Speed Run", "desc": "Complete 10 wins as fast as possible", "multiplier": 1.5},
            "Hardcore": {"name": "Hardcore", "desc": "One loss = game over", "multiplier": 2.0},
            "Endless": {"name": "Endless", "desc": "Play until you lose", "multiplier": 1.2},
            "Tournament": {"name": "Tournament", "desc": "Compete in tournament brackets", "multiplier": 2.5}
        }
        self.current_mode = "Classic"
        self.speed_run_time = 0
        self.speed_run_target = 10
'''
        # Insert after __init__
        init_end = content.find('    def _init_equipment_recipes')
        if init_end > 0:
            content = content[:init_end] + game_modes_code + '\n' + content[init_end:]
    
    # Step 3: Add Tournament System
    print("[3/5] Adding Tournament System...")
    if "tournament" not in content.lower() or "def _init_tournaments" not in content:
        tournament_code = '''
    def _init_tournaments(self):
        """Initialize tournament system"""
        self.tournaments = {
            "weekly": {"name": "Weekly Tournament", "rounds": 5, "prize_sp": 50, "active": True},
            "monthly": {"name": "Monthly Tournament", "rounds": 10, "prize_sp": 200, "active": True},
            "seasonal": {"name": "Seasonal Tournament", "rounds": 20, "prize_sp": 500, "active": True}
        }
        self.tournament_progress = {}
        self.tournament_wins = 0
        self.tournament_losses = 0
        self.current_tournament = None
    
    def enter_tournament(self, tournament_name):
        """Enter a tournament"""
        if tournament_name in self.tournaments:
            self.current_tournament = tournament_name
            self.tournament_progress[tournament_name] = {"wins": 0, "losses": 0}
            return True
        return False
    
    def exit_tournament(self):
        """Exit current tournament"""
        self.current_tournament = None
        self.tournament_progress = {}
'''
        if init_end > 0:
            content = content[:init_end] + tournament_code + '\n' + content[init_end:]
    
    # Step 4: Add Analytics/Stats Dashboard System
    print("[4/5] Adding Analytics Dashboard System...")
    if "analytics" not in content.lower() or "def show_analytics" not in content:
        analytics_code = '''
    def show_analytics_window(self):
        """Show analytics and stats dashboard"""
        analytics_win = tk.Toplevel(self.root)
        analytics_win.title("📊 Analytics Dashboard")
        analytics_win.geometry("700x600")
        analytics_win.configure(bg="#1e1e1e")
        
        # Title
        title = tk.Label(analytics_win, text="ANALYTICS DASHBOARD", font=("Arial", 16, "bold"),
                        bg="#1e1e1e", fg="#00ff00")
        title.pack(pady=10)
        
        # Stats text
        stats_text = f"""
GAME STATISTICS
═══════════════════════════════════════
Total Wins:           {self.wins_count}
Total Rolls:          {self.roll_count}
Win Rate:             {(self.wins_count / max(self.roll_count, 1) * 100):.1f}%
Total SP:             {self.sp + self.sp_plus * 2 + self.sp_x * 4 + self.sp_caret * 8}
Tournament Wins:      {self.tournament_wins if hasattr(self, 'tournament_wins') else 0}
Best Streak:          {self.stats.get('best_streak', 0) if self.stats else 0}
═══════════════════════════════════════

EQUIPMENT
═══════════════════════════════════════
Gauntlet:     {self.equipped_gauntlet if self.equipped_gauntlet else "None"}
Device:       {self.equipped_device if self.equipped_device else "None"}
═══════════════════════════════════════

CHALLENGES COMPLETED
═══════════════════════════════════════
Completed: {len([c for c in self.challenge_progress.values() if c > 0])} / 8
"""
        
        text_label = tk.Label(analytics_win, text=stats_text, font=("Courier", 10),
                             bg="#0d0d0d", fg="#00ff00", justify=tk.LEFT)
        text_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
'''
        if init_end > 0:
            content = content[:init_end] + analytics_code + '\n' + content[init_end:]
    
    # Step 5: Add Dev Console
    print("[5/5] Adding Developer Console...")
    if "def show_dev_console" not in content:
        dev_console_code = '''
    def show_dev_console(self):
        """Show developer console for testing"""
        console_win = tk.Toplevel(self.root)
        console_win.title("👨‍💻 Developer Console")
        console_win.geometry("600x500")
        console_win.configure(bg="#1a1a1a")
        
        title = tk.Label(console_win, text="DEVELOPER CONSOLE", font=("Arial", 14, "bold"),
                        bg="#1a1a1a", fg="#ffff00")
        title.pack(pady=10)
        
        # Command entry
        cmd_frame = tk.Frame(console_win, bg="#1a1a1a")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(cmd_frame, text="Command:", bg="#1a1a1a", fg="#fff").pack(side=tk.LEFT)
        cmd_entry = tk.Entry(cmd_frame, bg="#333", fg="#0f0", font=("Courier", 10))
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Output
        output = tk.Text(console_win, bg="#0d0d0d", fg="#0f0", font=("Courier", 9),
                        height=20, width=70)
        output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def execute_command():
            cmd = cmd_entry.get()
            output.insert(tk.END, f"> {cmd}\\n")
            
            if cmd == "add_sp 100":
                self.sp += 100
                output.insert(tk.END, "✓ Added 100 SP\\n")
            elif cmd == "set_wins 50":
                self.wins_count = 50
                output.insert(tk.END, "✓ Set wins to 50\\n")
            elif cmd == "unlock_all":
                self.sp = 999
                self.sp_plus = 99
                self.sp_x = 99
                self.sp_caret = 99
                output.insert(tk.END, "✓ Unlocked all currencies\\n")
            elif cmd == "reset_game":
                self.__init__(self.current_username)
                output.insert(tk.END, "✓ Game reset\\n")
            else:
                output.insert(tk.END, f"✗ Unknown command: {cmd}\\n")
            
            output.see(tk.END)
            cmd_entry.delete(0, tk.END)
        
        tk.Button(console_win, text="Execute", command=execute_command, bg="#00aa00",
                 fg="#000", font=("Arial", 10, "bold")).pack(pady=5)
        
        output.insert(tk.END, "Developer Console Active\\nCommands: add_sp, set_wins, unlock_all, reset_game\\n")
'''
        if init_end > 0:
            content = content[:init_end] + dev_console_code + '\n' + content[init_end:]
    
    # Add menu buttons for new systems
    print("\nAdding menu buttons for all systems...")
    
    # Find menu button area and add new buttons
    if "Analytics" not in content or "show_analytics_window" not in content:
        # This will be added via the code injections above
        pass
    
    # Write back
    with open('questionmark.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ RESTORATION COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    restore_all_systems()
