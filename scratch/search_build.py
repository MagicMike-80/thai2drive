with open('C:/Users/Stein Hoang/thai2drive/PRODUCTION-SETUP.md', 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f, 1):
        if 'web' in line.lower() or 'dist' in line.lower() or 'build' in line.lower():
            clean_line = line.encode('ascii', errors='ignore').decode('ascii').strip()
            print(f'{idx}: {clean_line}')
