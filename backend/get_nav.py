import re
content = open('webapp.py', 'r', encoding='utf-8').read()
match = re.search(r'<nav.*?nav>', content, re.DOTALL | re.IGNORECASE)
if match:
    print(match.group(0))
else:
    print("Nav not found")
