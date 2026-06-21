import re

with open('C:/Users/Stein Hoang/thai2drive/backend/website.py', 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f, 1):
        matches = re.findall(r'href="[^"]+"', line)
        if matches:
            # strip emojis or replace unicode
            clean_line = line.encode('ascii', errors='ignore').decode('ascii').strip()
            print(f'{idx}: {clean_line}')
