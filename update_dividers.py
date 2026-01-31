#!/usr/bin/env python3
"""Script to update all box-character dividers to clean design."""
import re
from pathlib import Path

# Files to update
files = [
    'bot/handlers/ai_search.py',
    'bot/handlers/settings.py',
    'bot/handlers/statistics.py',
]

# Pattern to match long dividers
pattern = r'─{10,}'
replacement = '━━━━━━━━━━━━'

for file_path in files:
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        continue
    
    # Read file
    content = path.read_text(encoding='utf-8')
    
    # Count matches
    matches = len(re.findall(pattern, content))
    
    if matches == 0:
        print(f"✅ {file_path} - No dividers to update")
        continue
    
    # Replace dividers
    new_content = re.sub(pattern, replacement, content)
    
    # Write back
    path.write_text(new_content, encoding='utf-8')
    print(f"✅ {file_path} - Updated {matches} dividers")

print("\n✨ All dividers updated!")
