#!/usr/bin/env python3
"""
RESTORE AUTHENTIC v1.67 APRIL FOOLS CONTENT
Adds back the REAL features from April 1, 2026 release
"""

def restore_v167_features():
    with open('questionmark.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("=" * 80)
    print("🍗 RESTORING AUTHENTIC v1.67 APRIL FOOLS FEATURES")
    print("=" * 80)
    
    # 1. Add John Pork Elixir to equipment
    print("\n[1/4] Adding John Pork Elixir (+67 SP item)...")
    if "john_pork" not in content:
        equipment_addition = '''        
        # John Pork Elixir (v1.67 Easter Egg)
        self.john_pork_elixir = {
            "name": "John Pork Elixir",
            "sp_boost": 67,
            "description": "A legendary elixir that grants +67 SP",
            "rarity": "LEGENDARY",
            "count": 0
        }
'''
        if "self.equipment =" in content:
            pos = content.find("self.equipment =")
            pos = content.find("\n", pos) + 1
            # Find the end of equipment initialization
            end_pos = content.find("self.", pos)
            content = content[:end_pos] + equipment_addition + content[end_pos:]
    
    # 2. Add Chocolate Bunny easter egg
    print("[2/4] Adding Chocolate Bunny easter egg...")
    if "chocolate" not in content:
        easter_eggs = '''        
        # Chocolate Bunny (v1.67 Easter Egg)
        if code.upper() == "CHOCOLATE" or code.upper() == "CHOCOLATEBUNNY":
            self.easter_eggs_found += 1
            self.john_pork_elixir["count"] += 1
            self.sp += 67  # John Pork Elixir bonus
            return "🐰 Chocolate Bunny Found! +67 SP! 🐰"
'''
        if "def find_easter_egg" in content:
            pos = content.find("if code.upper() in easter_eggs:")
            if pos > 0:
                content = content[:pos] + easter_eggs + "\n        " + content[pos:]
    
    # 3. Add Dev Console proper implementation
    print("[3/4] Adding Dev Console...")
    if "DEV_CONSOLE_OPEN" not in content or "dev_console" not in content.lower()[:5000]:
        dev_console = '''    
    def toggle_dev_console(self):
        """Toggle developer console - Easter egg access"""
        if not hasattr(self, 'dev_console_open'):
            self.dev_console_open = False
        
        self.dev_console_open = not self.dev_console_open
        
        if self.dev_console_open:
            self.show_dev_console()
        else:
            if hasattr(self, 'dev_win') and self.dev_win.winfo_exists():
                self.dev_win.destroy()
    
    def show_dev_console(self):
        """Show developer console window"""
        if not hasattr(self, 'dev_win'):
            self.dev_win = tk.Toplevel(self.root)
        else:
            if self.dev_win.winfo_exists():
                self.dev_win.lift()
                return
            self.dev_win = tk.Toplevel(self.root)
        
        self.dev_win.title("🔧 Developer Console")
        self.dev_win.geometry("600x400")
        self.dev_win.configure(bg="#0a0a0a")
        
        tk.Label(self.dev_win, text="Developer Console", font=("Courier", 12, "bold"),
                bg="#0a0a0a", fg="#00ff00").pack(pady=5)
        
        # Command input
        cmd_frame = tk.Frame(self.dev_win, bg="#0a0a0a")
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(cmd_frame, text">", bg="#0a0a0a", fg="#00ff00", font=("Courier", 10)).pack(side=tk.LEFT)
        cmd_entry = tk.Entry(cmd_frame, bg="#1a1a1a", fg="#00ff00", font=("Courier", 10))
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Output area
        output = scrolledtext.ScrolledText(self.dev_win, bg="#0a0a0a", fg="#00ff00",
                                          font=("Courier", 9), height=15)
        output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Available commands
        help_text = """Available Dev Commands:
  add_sp <amount> - Add SP
  add_win - Add a win
  set_mode <classic/speedrun/hardcore> - Change mode
  easter_egg <code> - Trigger easter egg
  facebook - Enable Facebook test mode
  version - Show version info
  help - Show this help
"""
        output.insert(tk.END, help_text)
        output.config(state=tk.DISABLED)
        
        def execute_command():
            cmd = cmd_entry.get()
            output.config(state=tk.NORMAL)
            output.insert(tk.END, f"\n> {cmd}")
            
            try:
                if cmd.startswith("add_sp"):
                    amount = int(cmd.split()[1])
                    self.sp += amount
                    output.insert(tk.END, f"\n✓ Added {amount} SP (Total: {self.sp})")
                elif cmd == "add_win":
                    self.wins_count += 1
                    output.insert(tk.END, f"\n✓ Added win (Total: {self.wins_count})")
                elif cmd.startswith("set_mode"):
                    mode = cmd.split()[1]
                    self.game_mode = mode
                    output.insert(tk.END, f"\n✓ Mode set to {mode}")
                elif cmd.startswith("easter_egg"):
                    code = cmd.split()[1]
                    result = self.find_easter_egg(code)
                    output.insert(tk.END, f"\n{result if result else 'Invalid code'}")
                elif cmd == "facebook":
                    self.facebook_test_mode = True
                    output.insert(tk.END, "\n✓ Facebook test mode enabled")
                elif cmd == "version":
                    output.insert(tk.END, "\nv1.67 April Fools + Restoration")
                elif cmd == "help":
                    output.insert(tk.END, help_text)
                else:
                    output.insert(tk.END, "\n✗ Unknown command")
            except Exception as e:
                output.insert(tk.END, f"\n✗ Error: {e}")
            
            output.see(tk.END)
            output.config(state=tk.DISABLED)
            cmd_entry.delete(0, tk.END)
        
        tk.Button(cmd_frame, text="Execute", command=execute_command, bg="#00aa00",
                 fg="#000", font=("Courier", 9)).pack(side=tk.LEFT, padx=5)
        
        cmd_entry.bind("<Return>", lambda e: execute_command())
    
    def enable_facebook_test_mode(self):
        """Facebook test mode - v1.67 feature"""
        self.facebook_test_mode = True
        self.ui_theme = "facebook"  # Blue theme
        return "Facebook Test Mode Enabled"
'''
        # Find where to insert - after show_leaderboard
        if "def show_leaderboard" in content:
            pos = content.find("def show_leaderboard")
            # Find the next def after this one
            next_def = content.find("\n    def ", pos + 100)
            if next_def > 0:
                content = content[:next_def] + dev_console + content[next_def:]
    
    # 4. Add Facebook test mode initialization
    print("[4/4] Initializing Facebook test mode...")
    if "self.facebook_test_mode" not in content:
        fb_init = '''        
        # Facebook Test Mode (v1.67)
        self.facebook_test_mode = False
        self.ui_theme = "default"
'''
        if "self.april_fools_active" in content:
            pos = content.find("self.april_fools_active")
            pos = content.find("\n", pos) + 1
            content = content[:pos] + fb_init + content[pos:]
    
    # 5. Add hotkey for dev console (Ctrl+Shift+D)
    print("[5/4] Adding developer hotkey...")
    if "bind('<Control-Shift-d>" not in content:
        hotkey_code = '''        
        # Developer Console Hotkey
        self.root.bind('<Control-Shift-d>', lambda e: self.toggle_dev_console())
'''
        if "self.root.bind" in content:
            # Find first bind and add after
            first_bind = content.find("self.root.bind")
            # Find next line after it
            next_line = content.find("\n", first_bind) + 1
            content = content[:next_line] + hotkey_code + content[next_line:]
    
    with open('questionmark.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ v1.67 AUTHENTIC FEATURES RESTORED!")
    print("=" * 80)
    print("\n🍗 Features Added:")
    print("  ✓ John Pork Elixir (+67 SP legendary item)")
    print("  ✓ Chocolate Bunny easter egg")
    print("  ✓ Developer Console (Ctrl+Shift+D)")
    print("  ✓ Facebook Test Mode")
    print("  ✓ Dev console commands")
    print("\n🔧 Dev Console Commands:")
    print("  • add_sp <amount> - Add SP")
    print("  • add_win - Add a win")
    print("  • set_mode <mode> - Change game mode")
    print("  • easter_egg <code> - Trigger easter egg")
    print("  • facebook - Enable Facebook mode")
    print("  • version - Show version")
    print("\n⌨️ Hotkey: Ctrl+Shift+D to open Developer Console")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    restore_v167_features()
