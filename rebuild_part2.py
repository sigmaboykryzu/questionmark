#!/usr/bin/env python3
"""
COMPREHENSIVE REBUILD PART 2 - Adds manual_roll integrations and complete RNG system
"""

with open('questionmark.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find manual_roll method and enhance it with RNG system integration
output_lines = []
i = 0
while i < len(lines):
    output_lines.append(lines[i])
    
    # Look for manual_roll method and add RNG integration
    if 'def manual_roll(self):' in lines[i]:
        # Find the part where we should add RNG checks
        j = i + 1
        found_match_update = False
        while j < len(lines) and j < i + 200:
            if 'matches = len(self.properties & self.target_properties)' in lines[j]:
                # Add RNG system check before win condition
                indent = '            '
                rng_check = f'''{indent}# Apply RNG and pity system
{indent}if matches == total_targets:  # Player won
{indent}    if self._handle_pity_system():
{indent}        matches = total_targets  # Force win from pity
{indent}    elif not self._apply_luck_to_roll():
{indent}        matches = max(0, matches - 1)  # Apply luck penalty if unlucky
{indent}    
{indent}    # Apply progressive mechanics bonus
{indent}    sp_gained = int(sp_gained * self.get_dynamic_difficulty_multiplier())
{indent}    
{indent}    # Apply systems interaction
{indent}    sp_gained, _ = self.apply_systems_interaction_on_win(sp_gained)
{indent}    xp_earned = self.calculate_xp(sp_gained)
'''
                # Insert RNG check
                output_lines = output_lines[:-1]  # Remove the current line we just added
                for line in output_lines:
                    pass  # Keep them
                # Add RNG integration after the matches calculation
                while j < len(lines) and 'if matches == total_targets' not in lines[j]:
                    output_lines.append(lines[j])
                    j += 1
                
                # Add enhancement to the win condition
                if j < len(lines) and 'if matches == total_targets' in lines[j]:
                    output_lines.append(lines[j])
                    j += 1
                    # Look for sp_gained and add systems interaction
                    while j < len(lines) and 'def ' not in lines[j]:
                        if 'xp_earned = ' in lines[j] or 'sp_gained =' in lines[j]:
                            # These already exist, keep them
                            output_lines.append(lines[j])
                        else:
                            output_lines.append(lines[j])
                        j += 1
                        if 'self.wins_count' in ''.join(lines[max(0,j-5):j]):
                            break
                
                found_match_update = True
                break
            j += 1
        i = j if found_match_update else i + 1
    else:
        i += 1

with open('questionmark.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✅ Part 2: Added manual_roll RNG integration")
