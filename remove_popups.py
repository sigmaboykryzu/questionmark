# Replace all victory messageboxes with in-game labels
with open('questionmark.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the victory messagebox pattern with in-game label update
replacements = [
    # Pattern 1: Victory messagebox with reward text
    (
        'messagebox.showinfo("Victory!", f"Won sequence!\\n+{sp_gained} {sp_display}{bonus_text}\\n+{xp_earned} XP\\n\\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\\n\\nRank: {player_title}{streak_text}{level_text}{reward_text}")',
        'victory_text = f"🎉 WON! +{sp_gained}{sp_display} +{xp_earned}XP {player_title}{streak_text}{level_text}"\n            self.match_label.config(text=victory_text, fg="#00ff00", font=("Segoe UI", 14, "bold"))'
    ),
    # Pattern 2: Combo bonus messagebox with delay
    (
        'self.root.after(500, lambda msg=streak_msg: messagebox.showinfo("🎉 COMBO BONUS!", msg))',
        '# Combo bonus shown via match_label'
    ),
    # Pattern 3: Remove try/except wrapper around combo bonus
    (
        '                try:\n                    self.root.after(500, lambda msg=streak_msg: messagebox.showinfo("🎉 COMBO BONUS!", msg))\n                    # Flash screen on big streaks\n                    if self.winning_streak % 5 == 0 and self.animations_enabled:\n                        self._flash_screen()\n                except:\n                    pass',
        '# Flash screen on big streaks\n                if self.winning_streak % 5 == 0 and self.animations_enabled:\n                    self._flash_screen()'
    ),
]

for old, new in replacements:
    content = content.replace(old, new)

# Remove time.sleep calls that aren't essential
content = content.replace('                time.sleep(0.001)  # Tiny sleep to let UI update\n', '')
content = content.replace('                time.sleep(0.001)  # Yield to allow UI thread to process events\n', '')

with open('questionmark.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removed popup messageboxes and delays!")
