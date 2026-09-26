# Panduan Deployment & Setup Lokal (Simple RAG Agent)

Panduan ini berisi langkah-langkah *step-by-step* untuk melakukan kloning repository dari GitHub hingga menjalankan aplikasi RAG Agent di lingkungan lokal.

---

## 📋 Prasyarat Sistem

1. **Git** terinstall di komputer.
2. **Python** (versi 3.10 ke atas direkomendasikan).
3. **uv** (Package & Project Manager cepat untuk Python).

---

## 🚀 Langkah-Langkah Installation & Setup

### 1. Clone Repository
Buka terminal (PowerShell / Command Prompt / Bash) dan jalankan:

```bash
git clone <URL_REPOSITORY_GITHUB_ANDA>
cd Simple_rag
```

---

### 2. Install Package Manager (`uv`)
Jika Anda belum menginstall `uv`, jalankan perintah berikut:

- **Windows (PowerShell):**
  ```powershell
  powershell -executionpolicy bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Linux / macOS:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

> ⚠️ **Penting untuk Windows (PowerShell):**  
> Setelah instalasi `uv` selesai, refresh sesi environment PATH terminal Anda dengan menjalankan:
> ```powershell
> $env:Path = "C:\Users\furqo\.local\bin;$env:Path"
> ```
> *(Atau tutup dan buka kembali jendela PowerShell Anda)*.

---

### 3. Sinkronisasi & Install Dependency Project (`uv sync`)
Jalankan perintah berikut di direktori utama project (`Simple_rag`):

```bash
uv sync
```

*Perintah ini akan membuat Virtual Environment (`.venv`) secara otomatis dan menginstall 131+ package yang terdaftar pada `pyproject.toml` & `uv.lock`.*

---

### 4. Konfigurasi `config.py`
Buka file [`config.py`](config.py) dan sesuaikan URL remote LLM server Anda (misalnya tunnel ngrok dari Kaggle/Colab/Ollama server):

```python
# Remote Inference Endpoint (sesuai URL ngrok / endpoint aktif Anda)
REMOTE_LLM_URL = "https://pamperer-handbook-dock.ngrok-free.dev/v1"
LLM_MODEL_NAME = "qwen3.5:9b"

# Configuration Vector Database & Embeddings (Local)
EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "qwen_knowledge_base"
```

---

### 5. Ingest Dokumen PDF ke Vector Database (Opsional / Otomatis)

1. Taruh file-file dokumen PDF yang ingin dijadikan basis pengetahuan (*knowledge base*) di folder:
   ```text
   ./RAG/Data/
   ```
2. Untuk memproses dan memasukkan dokumen PDF ke ChromaDB secara manual, jalankan:
   ```bash
   uv run python -m RAG.store
   ```
   *(Catatan: Jika folder `./chroma_db` belum ada, sistem akan otomatis melakukan ekstraksi dokumen PDF saat agent pertama kali dijalankan).*

---

### 6. Menjalankan Agent RAG

Eksekusi program utama menggunakan `uv`:

```bash
uv run python agent.py
```

---

## 🛠️ Ringkasan Perintah Cepat (Quick Commands)

| Aksi | Perintah |
| :--- | :--- |
| **Refresh Path `uv` (Windows)** | `$env:Path = "C:\Users\furqo\.local\bin;$env:Path"` |
| **Install / Sync Dependency** | `uv sync` |
| **Ingest PDF Data** | `uv run python -m RAG.store` |
| **Run Agent RAG** | `uv run python agent.py` |

---

## ❓ Troubleshoot / Kendala Umum

1. **`uv : The term 'uv' is not recognized...`**  
   - Solusi: Jalankan `$env:Path = "C:\Users\furqo\.local\bin;$env:Path"` di PowerShell atau restart terminal Anda.
2. **`Failed to connect to Remote LLM` / Connection Error**  
   - Solusi: Pastikan endpoint ngrok pada `config.py` dalam kondisi aktif dan dapat diakses.
