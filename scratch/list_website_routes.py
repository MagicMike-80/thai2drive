with open('C:/Users/Stein Hoang/thai2drive/backend/website.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'website_router' in line or 'route' in line or '@' in line:
            if 'get' in line or 'post' in line or '@' in line:
                print(f'{idx}: {line.strip()}')
