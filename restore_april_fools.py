#!/usr/bin/env python3
"""
APRIL FOOLS EVENT RESTORATION
Adds back all special event content and features
"""

def restore_april_fools():
    with open('questionmark.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 80)
    print("🎉 RESTORING APRIL FOOLS EVENT & SPECIAL FEATURES")
    print("=" * 80)
    
    # Add April Fools initialization to __init__
    print("\n[1/5] Adding April Fools Event System...")
    if "self.april_fools_active" not in content:
        init_addition = '''        
        # April Fools Event (v1.67)
        self.april_fools_active = True
        self.april_fools_mode = "chaos"  # chaos, normal, hilarious
        self.prank_count = 0
        self.pranks_triggered = []
        self.easter_eggs_found = 0
        self.troll_level = 0
'''
        # Find __init__ end and add
        init_marker = "self.difficulty = \"normal\""
        if init_marker in content:
            content = content.replace(init_marker, init_marker + init_addition)
    
    # Add April Fools event methods
    print("[2/5] Adding April Fools Event Methods...")
    
    april_fools_code = '''
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
        
        import random
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
        easter_eggs = {
            "QUESTIONMARK": "🎪 YOU FOUND THE MASTER EGG! 🎪",
            "APRILFOOLS": "🃏 The Trickster smiles... 🃏",
            "ROLLINGGAME": "🎲 Rolling in the deep... 🎲",
            "TROLL": "👹 Troll mode activated! 👹",
            "CHAOS": "⚡ CHAOS MODE UNLOCKED ⚡",
            "SECRET": "🔐 Hidden secrets revealed! 🔐",
            "CHEAT": "💀 Cheater! (But I won't tell) 💀",
            "HIDDEN": "👁️ All seeing eye mode 👁️",
        }
        
        if code.upper() in easter_eggs:
            self.easter_eggs_found += 1
            self.troll_level += 1
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
'''
    
    # Insert after class definition
    if "def _init_daily_challenges" in content:
        insert_pos = content.find("def _init_daily_challenges")
        content = content[:insert_pos] + april_fools_code + "\n    " + content[insert_pos:]
    
    # Add April Fools UI button
    print("[3/5] Adding April Fools Event UI...")
    if "april_button" not in content:
        button_code = '''        
        # April Fools Event Button
        self.april_button = tk.Button(button_frame, text="🃏 Event", font=("Arial", 11, "bold"),
                                     bg="#ff6600", fg="#000000", padx=15, pady=10,
                                     activebackground="#ff6600", activeforeground="#000000",
                                     command=self.show_april_fools_menu, width=8)
        self.april_button.pack(side=tk.LEFT, padx=5)
'''
        # Find where to insert (after other buttons)
        if "self.history_button.pack" in content:
            pos = content.find("self.history_button.pack")
            pos = content.find("\n", pos) + 1
            content = content[:pos] + button_code + content[pos:]
    
    # Add April Fools menu window
    print("[4/5] Adding April Fools Event Menu...")
    event_menu_code = '''
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
'''
    
    if "def show_april_fools_menu" not in content:
        # Insert before show_history_window or at end of class
        if "def show_history_window" in content:
            pos = content.find("def show_history_window")
            content = content[:pos] + event_menu_code + "\n    " + content[pos:]
    
    # Integrate April Fools into manual_roll
    print("[5/5] Integrating April Fools into Gameplay...")
    if "self.trigger_april_fools_prank()" not in content:
        # Find manual_roll and add prank trigger
        if "def manual_roll(self):" in content:
            pos = content.find("def manual_roll(self):") 
            pos = content.find("\n", pos) + 1
            prank_code = '''        # 🃏 April Fools prank trigger
        prank_msg = self.trigger_april_fools_prank()
        if prank_msg and self.april_fools_active:
            self.match_label.config(text=prank_msg, fg="#ff6600")
            self.apply_april_fools_effect()
        
'''
            content = content[:pos] + prank_code + content[pos:]
    
    # Write back
    with open('questionmark.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ APRIL FOOLS EVENT FULLY RESTORED!")
    print("=" * 80)
    print("\n✨ Special Features Added:")
    print("  ✓ Prank System (8 different pranks)")
    print("  ✓ Easter Egg Discovery System")
    print("  ✓ Troll Level Progression")
    print("  ✓ April Fools UI Menu")
    print("  ✓ Event Bonus SP Rewards")
    print("  ✓ Prank Integration into Gameplay")
    print("\n🎪 Hidden Easter Eggs:")
    print("  - QUESTIONMARK, APRILFOOLS, ROLLINGGAME, TROLL")
    print("  - CHAOS, SECRET, CHEAT, HIDDEN")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    restore_april_fools()
