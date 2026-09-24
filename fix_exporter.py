import re

with open('RAG/docx_exporter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Match `.get("some_key", {})` or `.get('some_key', {})`
content = re.sub(r'\.get\((["\'].*?["\']),\s*\{\}\)', r'.get(\1) or {}', content)
# Match `.get("some_key", [])` or `.get('some_key', [])`
content = re.sub(r'\.get\((["\'].*?["\']),\s*\[\]\)', r'.get(\1) or []', content)

with open('RAG/docx_exporter.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated docx_exporter.py safely.")

