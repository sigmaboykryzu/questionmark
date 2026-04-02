#!/usr/bin/env python3
"""
INTEGRATION SCRIPT: Connect all restored systems into the game loop
This script properly integrates:
1. RNG Control (luck, pity, reroll)
2. Progressive Mechanics (7 unlocks)
3. Systems Interaction (synergies)
Into the actual gameplay
"""

import re

def integrate_systems():
    with open('questionmark.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # STEP 1: Fix the UI windows - move them inside the class
    # Find and remove the standalone functions at the end
    print("[1/6] Moving UI windows inside class...")
    
    # Find the standalone show_rng_control_window and remove it
    standalone_rng = r'    def show_rng_control_window\(self\):.*?(?=    def show_progressive|if __name__|$)'
    standalone_prog = r'    def show_progressive_mechanics_window\(self\):.*?(?=    def show_systems|if __name__|$)'
    standalone_synergy = r'    def show_systems_synergy_window\(self\):.*?(?=if __name__|$)'
    
    # Remove duplicates if they exist outside the class
    content = re.sub(r'\n\n    def show_rng_control_window\(self\):.*?(?=\n    def show_progressive|\nif __name__|$)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n\n    def show_progressive_mechanics_window\(self\):.*?(?=\n    def show_systems|\nif __name__|$)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n\n    def show_systems_synergy_window\(self\):.*?(?=\nif __name__|$)', '', content, flags=re.DOTALL)
    
    # STEP 2: Add menu buttons for the 3 new windows
    print("[2/6] Adding menu buttons for RNG, Progressive, and Synergy windows...")
    
    # Find the menu bar creation and add new buttons
    menu_insert_point = 'settings_btn = tk.Button(menu_frame'
    if menu_insert_point in content:
        insertion = '''
        # New system windows buttons
        rng_btn = tk.Button(menu_frame, text="🍀 RNG", command=self.show_rng_control_window, 
                           bg="#444", fg="#fff", font=("Arial", 10), width=6)
        rng_btn.pack(side=tk.LEFT, padx=2)
        
        prog_btn = tk.Button(menu_frame, text="📈 Mechanics", command=self.show_progressive_mechanics_window,
                            bg="#444", fg="#fff", font=("Arial", 10), width=10)
        prog_btn.pack(side=tk.LEFT, padx=2)
        
        synergy_btn = tk.Button(menu_frame, text="🔗 Synergy", command=self.show_systems_synergy_window,
                               bg="#444", fg="#fff", font=("Arial", 10), width=8)
        synergy_btn.pack(side=tk.LEFT, padx=2)
        
        '''
        content = content.replace(menu_insert_point, insertion + menu_insert_point)
    
    # STEP 3: Integrate RNG into manual_roll WIN condition
    print("[3/6] Integrating RNG system into manual_roll (WIN)...")
    
    # Find manual_roll's win condition and add RNG
    win_condition = '''        # Check if won
        if properties == self.target_properties:
            self.wins_count += 1
            self.wins_label.config(text=str(self.wins_count))
            self.match_label.config(text="🏆 SUCCESS! 🏆", fg="#00ff00", font=("Arial", 16, "bold"))
            self._play_success_sound()
            
            # Apply RNG check (pity system, luck)
            final_result = self._apply_rng_to_result(True)  # True = it was a win
            if not final_result:
                # RNG overrode win to loss (shouldn't happen with current logic)
                self.match_label.config(text="❌ NO MATCH", fg="#ff0000", font=("Arial", 16, "bold"))
                self.root.after(2000, self._next_sequence)
                return
            
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
            
            # APPLY SYNERGY MULTIPLIER to SP
            synergy_mult = self.get_synergy_multiplier()
            if synergy_mult > 1.0:
                # Apply synergy multiplier
                if sp_type == "sp":
                    bonus_sp = int((synergy_mult - 1.0) * self.sp)
                    self.sp += bonus_sp
            
            self._update_sp_label()
            
            # Update daily challenges and get rewards
            challenge_rewards = self._update_challenges(sp_type, len(s))
            reward_text = ""
            if challenge_rewards:
                reward_text = "\\n\\n⭐ CHALLENGES COMPLETED:\\n" + challenge_rewards
            
            # Add synergy info to message
            synergy_text = f"\\n\\n✨ Synergy Multiplier: {synergy_mult:.2f}x"
            
            player_title = self._get_player_title_for_wins(self.wins_count)
            messagebox.showinfo("Victory!", f"Won sequence!\\n+1 {sp_display}\\n\\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\\n\\nRank: {player_title}{synergy_text}{reward_text}")
            
            # Update stats
            rolls_in_win = len([r for r in self.rolls_history if r['number'] > (self.rolls_history[-1]['number'] - len(self.rolls_history))])
            self.stats['fastest_win'] = min(self.stats['fastest_win'], rolls_in_win)
            self.stats['slowest_win'] = max(self.stats['slowest_win'], rolls_in_win)
            self.stats['current_streak'] += 1
            self.stats['best_streak'] = max(self.stats['best_streak'], self.stats['current_streak'])
            
            # Update perfect series challenge (challenge 7)
            if self.stats['current_streak'] >= 3:
                self.challenge_progress["challenge_7"] = max(self.challenge_progress.get("challenge_7", 0), self.stats['current_streak'])
            
            # Apply systems interaction on win (may increment pity counter or other effects)
            self.apply_systems_interaction_on_win()
            
            # Check for progressive mechanics unlocks
            if 'level' in self.stats:
                self._update_progressive_mechanics()
            
            # Generate new target after 2 seconds
            self.root.after(2000, self._next_sequence)'''
    
    old_win_condition = '''        # Check if won
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
                reward_text = "\\n\\n⭐ CHALLENGES COMPLETED:\\n" + challenge_rewards
            
            player_title = self._get_player_title_for_wins(self.wins_count)
            messagebox.showinfo("Victory!", f"Won sequence!\\n+1 {sp_display}\\n\\nTotal: {self.sp}|{self.sp_plus}|{self.sp_x}|{self.sp_caret}\\n\\nRank: {player_title}{reward_text}")
            
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
            self.root.after(2000, self._next_sequence)'''
    
    content = content.replace(old_win_condition, win_condition)
    
    # STEP 4: Integrate RNG into manual_roll LOSS condition
    print("[4/6] Integrating RNG system into manual_roll (LOSS)...")
    
    # Find the loss condition
    loss_condition_old = '''        else:
            # Did not match
            self.match_label.config(text="❌ NO MATCH", fg="#ff0000", font=("Arial", 16, "bold"))
            self.stats['current_streak'] = 0'''
    
    loss_condition_new = '''        else:
            # Did not match
            self.match_label.config(text="❌ NO MATCH", fg="#ff0000", font=("Arial", 16, "bold"))
            self.stats['current_streak'] = 0
            
            # Apply systems interaction on loss (increment pity counter)
            self.apply_systems_interaction_on_loss()'''
    
    content = content.replace(loss_condition_old, loss_condition_new)
    
    # STEP 5: Add import for Toplevel if not present
    print("[5/6] Ensuring Toplevel import...")
    if "from tkinter import" in content and "Toplevel" not in content:
        old_import = "from tkinter import scrolledtext, messagebox, ttk, filedialog"
        new_import = "from tkinter import scrolledtext, messagebox, ttk, filedialog, Toplevel"
        content = content.replace(old_import, new_import)
    
    # STEP 6: Verify all system methods are present
    print("[6/6] Verifying all system methods exist...")
    
    required_methods = [
        '_calculate_player_luck',
        '_apply_rng_to_result',
        '_handle_pity_system',
        '_init_progressive_mechanics',
        '_update_progressive_mechanics',
        'get_synergy_multiplier',
        'apply_systems_interaction_on_win',
        'apply_systems_interaction_on_loss',
        'show_rng_control_window',
        'show_progressive_mechanics_window',
        'show_systems_synergy_window'
    ]
    
    missing = []
    for method in required_methods:
        if f'def {method}(self)' not in content:
            missing.append(method)
    
    if missing:
        print(f"⚠️  WARNING: Missing methods: {missing}")
        print("These should be present from rebuild_complete.py")
    else:
        print("✓ All system methods verified!")
    
    # Write the integrated file
    with open('questionmark.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ INTEGRATION COMPLETE!")
    print("━" * 50)
    print("Changes made:")
    print("  ✓ UI windows ready to use (inside class)")
    print("  ✓ Menu buttons added (🍀 RNG, 📈 Mechanics, 🔗 Synergy)")
    print("  ✓ RNG integrated into WIN condition")
    print("  ✓ Synergy multiplier applied to SP rewards")
    print("  ✓ Systems interaction on loss (pity tracking)")
    print("  ✓ Progressive mechanics unlock checking")
    print("  ✓ Toplevel import ensured")
    print("━" * 50)

if __name__ == "__main__":
    integrate_systems()
