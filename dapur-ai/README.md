# 🍳 Dapur AI — V2 (OpenRouter + Qdrant)

> Backend AI Microservice untuk sistem Pertamina RKS & Tender Document Generator.

## 🏗️ Arsitektur

| Komponen | Teknologi |
|----------|-----------|
| **API Framework** | FastAPI + Uvicorn |
| **LLM Provider** | OpenRouter (`qwen/qwen3.7-flash`) |
| **Vector Store** | Qdrant Cloud |
| **Embedding** | `sentence-transformers/all-minilm-l6-v2` (lokal) |
| **Agent Framework** | LangGraph (10-node graph with interrupts) |
| **Document Export** | python-docx |

## 📁 Struktur Folder

```
dapur-ai/
├── api.py              # FastAPI endpoints (RKS + Tender + Ingest)
├── agent.py            # LangGraph multi-node agent
├── main.py             # CLI interactive runner
├── config.py           # Konfigurasi (baca dari .env)
├── Dockerfile          # Container setup
├── pyproject.toml      # Dependencies (uv)
├── RAG/                # Retrieval-Augmented Generation
│   ├── vector_store.py # Qdrant vector store wrapper
│   ├── tools.py        # RKS generate & export tools
│   ├── summarizer.py   # PDF text extraction + summarization
│   ├── docx_exporter.py# DOCX rendering engine
│   └── Data/           # PDF source documents
└── tender/             # Dokumen Tender generator
    ├── generator.py    # Tender generate & export logic
    ├── schema.py       # Tender document schema
    ├── docx.py         # Tender DOCX export
    └── static_content.py # Template konten statis
```

## 🔌 API Endpoints

| Method | Endpoint | Keterangan |
|--------|----------|-----------|
| `GET` | `/` | Health check |
| `POST` | `/api/ingest-pdf` | Upload & ingest PDF ke knowledge base |
| `POST` | `/api/generate-rks` | Generate dokumen RKS (.docx) |
| `POST` | `/api/generate-tender` | Generate dokumen Tender (.docx) |

## ⚙️ Environment Variables

```env
# Wajib diisi:
OPENROUTER_API_KEY=sk-or-v1-xxxxx        # API key OpenRouter
QDRANT_CLUSTER_ENDPOINT=https://xxx.qdrant.io:6333
QDRANT_API_KEY=xxxxx                      # API key Qdrant Cloud

# Opsional (sudah ada default):
LLM_MODEL_NAME=qwen/qwen3.7-flash
EMBEDDING_MODEL=sentence-transformers/all-minilm-l6-v2
```

## 🚀 Menjalankan Lokal

```bash
# Install dependencies
uv sync

# Jalankan API server
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Atau jalankan CLI agent
uv run python main.py
```

## 🐳 Menjalankan via Docker

```bash
docker build -t dapur-ai .
docker run -p 8000:8000 --env-file ../.env dapur-ai
```

## 📝 Perubahan dari V1

- ~~Ollama + ngrok~~ → **OpenRouter** (cloud, tanpa setup server)
- ~~ChromaDB (lokal)~~ → **Qdrant Cloud** (managed, scalable)
- ~~Agent 2-node~~ → **Agent 10-node** (router, KB, clarify, BoQ upload, review, export)
- ~~RKS only~~ → **RKS + Dokumen Tender**
- ~~Blocking API calls~~ → **Async `run_in_threadpool`**
