with open('C:/Users/Stein Hoang/thai2drive/backend/website.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'web' in line or 'quiz-app' in line:
            print(f'{idx}: {line.strip()}')
