import glob, os

files = glob.glob('C:/Users/Stein Hoang/thai2drive/**/*.bat', recursive=True) + \
        glob.glob('C:/Users/Stein Hoang/thai2drive/**/*.sh', recursive=True) + \
        glob.glob('C:/Users/Stein Hoang/thai2drive/**/*.js', recursive=True) + \
        glob.glob('C:/Users/Stein Hoang/thai2drive/**/*.json', recursive=True) + \
        glob.glob('C:/Users/Stein Hoang/thai2drive/**/*.md', recursive=True)

for fpath in files:
    if 'node_modules' in fpath or '.expo' in fpath or '.git' in fpath:
        continue
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'export' in content and 'web' in content:
                print(f'Match: {fpath}')
    except Exception:
        pass
