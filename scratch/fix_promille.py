import os

path = 'C:/Users/Stein Hoang/thai2drive/content/quiz_extra_questions.json'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace 0.2
text = text.replace(
    '"text_no": "0.2 promille",\n        "text_th": "0.2 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.2 promille"',
    '"text_no": "0.2 promille",\n        "text_th": "0.2 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.2 blood alcohol limit (BAC)"'
)

# Replace 0.5
text = text.replace(
    '"text_no": "0.5 promille",\n        "text_th": "0.5 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.5 promille"',
    '"text_no": "0.5 promille",\n        "text_th": "0.5 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.5 blood alcohol limit (BAC)"'
)

# Replace 0.0
text = text.replace(
    '"text_no": "0.0 promille",\n        "text_th": "0.0 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.0 promille"',
    '"text_no": "0.0 promille",\n        "text_th": "0.0 \u0e42\u0e1b\u0e23\u0e21\u0e34\u0e25\u0e40\u0e25\u0e48",\n        "text_en": "0.0 blood alcohol limit (BAC)"'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Promille question updated successfully!")
