with open("backend/server.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace('\n                {"bildeUrl": {"$regex": "T2D_", "$options": "i"}},', '')
text = text.replace('\r\n                {"bildeUrl": {"$regex": "T2D_", "$options": "i"}},', '')

with open("backend/server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated server.py successfully!")
