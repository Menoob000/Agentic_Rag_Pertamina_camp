import re

with open('RAG/docx_exporter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific broken lines
replacements = [
    ('config.get("elemen_formal") or {}.get("page_border", True)', '(config.get("elemen_formal") or {}).get("page_border", True)'),
    ('config.get("perusahaan") or {}.get("nama_default"', '(config.get("perusahaan") or {}).get("nama_default"'),
    ('config.get("styling") or {}.get("font_heading", "Arial")', '(config.get("styling") or {}).get("font_heading", "Arial")'),
    ('draft_data.get("cover_page") or {}.get(', '(draft_data.get("cover_page") or {}).get(')
]

for old, new in replacements:
    content = content.replace(old, new)

with open('RAG/docx_exporter.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed parentheses.")

