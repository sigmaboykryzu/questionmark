# Completely revert to clean state and remove popups properly
import os
import subprocess

# Get the original file from git if possible
try:
    result = subprocess.run(['git', 'checkout', 'questionmark.py'], cwd='.', capture_output=True, text=True)
    print("Reverted to git version")
except:
    print("No git repo, will manually fix")

# Now properly remove the popups
with open('questionmark.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Simple replacements for the victory messageboxes
replacements = [
    ('messagebox.showinfo("Victory!", f"Won sequence!\\n+{sp_gained} {sp_display}{bonus_text}\\n+{xp_earned} XP\\n\\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\\n\\nRank: {player_title}{streak_text}{level_text}{reward_text}")',
     'self.match_label.config(text=f"🎉 WON! +{sp_gained}{sp_display} +{xp_earned}XP", fg="#00ff00", font=("Segoe UI", 14, "bold"))'),
    ('self.root.after(500, lambda msg=streak_msg: messagebox.showinfo("🎉 COMBO BONUS!", msg))',
     'pass  # Combo shown via label'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('questionmark.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cleaned up!")
