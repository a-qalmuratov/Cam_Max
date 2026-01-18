import re
import os

files_to_clean = [
    'bot/handlers/ai_search.py',
    'bot/handlers/camera_management.py',
    'bot/handlers/settings.py',
    'bot/handlers/statistics.py',
    'bot/handlers/video_view.py',
    'bot/handlers/quick_actions.py'
]

for filepath in files_to_clean:
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove box characters
    content = content.replace('┏', '')
    content = content.replace('┃', '')
    content = content.replace('┗', '')
    content = content.replace('━', '─')  # Replace with normal dash
    content = content.replace('┓', '')
    content = content.replace('┛', '')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Cleaned: {filepath}")

print("\n🎉 All menus cleaned!")
