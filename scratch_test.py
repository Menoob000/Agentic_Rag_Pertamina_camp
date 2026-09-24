import sys, io, warnings
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

from agent import extractor_llm

last_ai_msg = 'Berapa level risiko CSMS? (HIGH / MIDDLE / LOW)'
user_text = 'HIGH'

extracted = extractor_llm.invoke(f'''
Extract any RKS document metadata from the user message below.
Return null for fields not mentioned.

The agent previously asked this question (use this context to understand short answers):
"{last_ai_msg}"

User message: {user_text}

Return valid JSON matching the schema.
''')
print('Extracted:', extracted)

