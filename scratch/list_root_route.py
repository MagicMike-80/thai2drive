import glob

files = glob.glob('C:/Users/Stein Hoang/thai2drive/backend/*.py')
for fpath in files:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f, 1):
            if '@app.get("/")' in line or '@app.get(\'/\')' in line:
                print(f'{fpath} L{idx}: {line.strip()}')
