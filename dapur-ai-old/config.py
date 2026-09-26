import os
from dotenv import load_dotenv

load_dotenv()

# Remote Inference Endpoint
# Supports injection via environment variable (for Docker) or falls back to hardcoded default
REMOTE_LLM_URL = os.getenv("REMOTE_LLM_URL", "https://pamperer-handbook-dock.ngrok-free.dev/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen3.5:9b")

# Local Embedding & Vector Store Configurations
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "Qwen/Qwen3-Embedding-0.6B")
OLLAMA_EMBEDDING = os.getenv("OLLAMA_EMBEDDING", "qwen3-embedding:4b")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "qwen_knowledge_base")

# Retrieval Settings
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "2"))
