# Fix indentation issues
with open('questionmark.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the problematic section - lines with improper indentation
for i, line in enumerate(lines):
    # Check if this is the misaligned match_label line
    if 'self.match_label.config(text=victory_text' in line and not line.startswith('                    '):
        # Add proper indentation (20 spaces = 5 indents of 4 spaces)
        lines[i] = '                    ' + line.lstrip()
    
    # Remove extra try/except wrappers that aren't needed
    if line.strip() == 'try:' and i > 0 and '# Combo bonus shown' in lines[i+1]:
        lines[i] = ''
    if line.strip() == 'except:' and i > 0 and 'pass' in lines[i+1]:
        lines[i] = ''
    if line.strip() == 'pass' and i > 0 and 'except:' in lines[i-1]:
        lines[i] = ''

with open('questionmark.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed indentation!")
