import os
from dotenv import load_dotenv

load_dotenv()

# ========================
# Embedding Model
# ========================
# Default: sentence-transformers/all-minilm-l6-v2 (runs locally, no API needed)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-minilm-l6-v2")

# ========================
# Qdrant Cloud Vector Store
# ========================
QDRANT_CLUSTER_ENDPOINT = os.getenv("QDRANT_CLUSTER_ENDPOINT", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# ========================
# OpenRouter LLM (replaces Ollama + ngrok)
# ========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen/qwen3.7-flash")