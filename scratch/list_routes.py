with open('C:/Users/Stein Hoang/thai2drive/backend/server.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '@app.get' in line or '@api_router.get' in line:
            print(f'{idx}: {line.strip()}')
