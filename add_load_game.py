# Read the file
with open('questionmark.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find first save_game and insert load_game after it
result_lines = []
inserted = False

for i, line in enumerate(lines):
    result_lines.append(line)
    
    # Look for the messagebox.showinfo("Save" pattern
    if not inserted and 'messagebox.showinfo("Save"' in line and i > 0 and 'def save_game' in ''.join(lines[max(0,i-10):i]):
        # Add load_game method
        load_game_code = '''    
    def load_game(self):
        """Load the game state from saved files"""
        try:
            self.stats = self._load_stats()
            self.roll_count = self.stats.get("total_rolls", 0)
            self.wins_count = self.stats.get("total_wins", 0)
            self.sp = self.stats.get("sp", 0)
            self.level = self.stats.get("level", 1)
            self.rolls_history = self._load_history()
            self.equipment_inventory = self._load_equipment()
            self.achievements = self._load_achievements()
            self.game_settings = self._load_game_settings()
            
            # Update UI labels
            self.roll_label.config(text=str(self.roll_count))
            self.wins_label.config(text=str(self.wins_count))
            self._update_sp_label()
            
            messagebox.showinfo("Load", "Game loaded successfully!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load game: {e}")
'''
        result_lines.append(load_game_code)
        inserted = True

# Write back
with open('questionmark.py', 'w', encoding='utf-8') as f:
    f.writelines(result_lines)

print("✅ load_game method added!")
