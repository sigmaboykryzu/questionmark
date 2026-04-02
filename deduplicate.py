#!/usr/bin/env python3
"""
DEDUPLICATION SCRIPT: Remove duplicate method definitions
"""

def deduplicate():
    with open('questionmark.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track where duplicates occur
    method_defs = {}
    duplicates_to_remove = []
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            if method_name in method_defs:
                # Found a duplicate!
                duplicates_to_remove.append((method_name, method_defs[method_name], i))
                print(f"Found duplicate: {method_name} at lines {method_defs[method_name]+1} and {i+1}")
            else:
                method_defs[method_name] = i
    
    # Remove duplicates (start from the end so indices don't shift)
    for method, first_line, second_line in reversed(duplicates_to_remove):
        print(f"Removing duplicate {method} definition starting at line {second_line+1}")
        
        # Find the end of the method (next def or class or double newline)
        end_line = second_line + 1
        while end_line < len(lines):
            if lines[end_line].strip().startswith('def ') or lines[end_line].strip().startswith('class '):
                break
            if end_line < len(lines) - 1 and lines[end_line].strip() == '' and lines[end_line+1].strip().startswith('def '):
                break
            end_line += 1
        
        # Remove the duplicate method
        del lines[second_line:end_line]
        print(f"  Removed lines {second_line+1} to {end_line}")
    
    # Write the file
    with open('questionmark.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ DEDUPLICATION COMPLETE!")

if __name__ == "__main__":
    deduplicate()
