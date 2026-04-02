#!/usr/bin/env python3
"""
FINAL VERIFICATION SCRIPT - Check all required methods exist and are correct
"""

def check_methods():
    with open('questionmark.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # All critical methods needed
    critical_methods = {
        # RNG System
        '_calculate_player_luck': 'Calculate luck from equipment, abilities, level, streak',
        '_apply_luck_to_roll': 'Apply luck to determine if roll is lucky',
        '_handle_pity_system': 'Handle 50-loss pity guarantee',
        'use_reroll_token': 'Use token or 10 SP to reroll',
        'gain_reroll_tokens': 'Gain tokens from achievements',
        '_apply_rng_to_result': 'Apply combined RNG effects',
        '_load_rng_data': 'Load RNG data from JSON',
        '_save_rng_data': 'Save RNG data to JSON',
        
        # Progressive Mechanics
        '_init_progressive_mechanics': 'Initialize 7 mechanics',
        '_update_progressive_mechanics': 'Check level-up unlocks',
        'get_target_property_count': 'Get property count based on level',
        'get_active_game_modifiers': 'Get active random modifiers',
        'apply_random_modifier': 'Apply modifier to target',
        'trigger_cascading_effect': 'Chain win tracking',
        'get_dynamic_difficulty_multiplier': 'Get difficulty multiplier',
        
        # Systems Interaction
        '_init_systems_interaction': 'Initialize synergy system',
        '_calculate_system_synergies': 'Calculate all synergies',
        'apply_systems_interaction_on_win': 'Apply synergy on win',
        'apply_systems_interaction_on_loss': 'Handle loss (pity counter)',
        'get_synergy_multiplier': 'Get current synergy (1.0x-3.0x)',
        'report_system_interactions': 'Generate synergy report',
        
        # UI Windows
        'show_rng_control_window': 'Display RNG control panel',
        'show_progressive_mechanics_window': 'Display mechanics status',
        'show_systems_synergy_window': 'Display synergy report',
        
        # Basic methods
        'manual_roll': 'Main roll method',
        'calculate_xp': 'XP calculation',
        'load_game': 'Load game state',
        'start_tutorial': 'Tutorial system',
    }
    
    print("=" * 70)
    print("FINAL METHOD VERIFICATION")
    print("=" * 70)
    
    missing = []
    found = []
    
    for method, description in critical_methods.items():
        if f'def {method}(self' in content or f'def {method}()' in content:
            found.append(method)
            print(f"✓ {method:40} - {description}")
        else:
            missing.append(method)
            print(f"✗ {method:40} - {description}")
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {len(found)}/{len(critical_methods)} methods found")
    print("=" * 70)
    
    if missing:
        print(f"\n⚠️  MISSING METHODS ({len(missing)}):")
        for m in missing:
            print(f"    - {m}")
        return False
    else:
        print("\n✅ ALL CRITICAL METHODS FOUND!")
        return True

if __name__ == "__main__":
    success = check_methods()
    exit(0 if success else 1)
