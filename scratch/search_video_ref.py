with open('C:/Users/Stein Hoang/thai2drive/backend/webapp.py', 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f, 1):
        if 'video' in line.lower() or 'film' in line.lower() or 'bibliotek' in line.lower():
            if 'html' in line or 'function' in line or 'const' in line or 'div' in line or 'button' in line or 'route' in line:
                clean_line = line.encode('ascii', errors='ignore').decode('ascii').strip()
                print(f'{idx}: {clean_line}')
