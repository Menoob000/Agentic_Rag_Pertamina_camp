# 📝 Change Log: Pengembangan Modul Kontrak & Amendemen
**Tanggal:** 11 Oktober 2026

Dokumen ini mencatat pembaruan dan penambahan fitur baru pada proyek `Agentic_Rag_Pertamina_camp`. Fokus utama pembaruan ini adalah penambahan fitur otomatisasi **Rancangan Kontrak Definitif** dan **Draft Amendemen / Addendum** yang berjalan terpisah (standalone) dari modul Tender/RKS, dan mengandalkan sistem RAG dengan basis Qdrant Cloud.

## 🚀 Fitur Baru
1. **Generator Rancangan Kontrak Definitif:**
   - Menyusun draft lengkap kontrak pemborongan pekerjaan (20 Pasal).
   - Menghasilkan file output berbentuk `.docx` dengan format korporat Pertamina, lengkap dengan penempatan nama pihak dan tanda tangan.
2. **Generator Draft Amendemen / Addendum:**
   - Menyusun draft addendum berdasarkan perubahan spesifik yang disepakati (misal: perubahan nilai kontrak atau waktu).
   - Merumuskan konsideran secara otomatis (Mengingat, Memperhatikan, Menimbang) menggunakan gaya bahasa Legal Drafting.
   - Menyajikan tabel komparasi "Kondisi Lama" vs "Kondisi Baru" di dalam output `.docx`.
3. **Qdrant Cloud Integration & Knowledge Base Management:**
   - Beralih menggunakan Qdrant Cloud (memisahkan environment ini dari folder production lokal `ITec-Ai`).
   - Menyediakan UI Khusus di Streamlit untuk mengunggah dokumen referensi (PDF) yang akan diserap oleh *vector database* dan dikategorikan ke dalam *collection* yang spesifik (`rks_kb`, `contract_kb`, `amendment_kb`).

## 📁 Perubahan File (Struktur Direktori)

Berikut adalah ringkasan hierarki file (*file tree*) yang ditambahkan atau diubah (ditandai dengan 🟢 Baru, 🟡 Dimodifikasi):

```text
Agentic_Rag_Pertamina_camp/
├── 🟡 .env                  # Penambahan Qdrant Cloud API & URL
├── 🟡 config.py             # Penambahan variabel konstanta KB baru
├── 🟡 app.py                # Penambahan UI Streamlit untuk 2 mode baru + UI KB
├── 🟡 api.py                # Penambahan endpoint FastAPI (/generate-kontrak, dll)
├── RAG/
│   └── 🟡 vector_store.py   # Refactor koneksi Qdrant Cloud & memori upload
└── contract/                # 🟢 DIREKTORI MODUL BARU
    ├── 🟢 schema.py             # Skema Pydantic Kontrak Definitif
    ├── 🟢 generator.py          # LLM Agent Generator Kontrak
    ├── 🟢 amendment_schema.py   # Skema Pydantic Draft Amendemen
    ├── 🟢 amendment_generator.py# LLM Agent Generator Amendemen
    └── 🟢 docx_builder.py       # Renderer dokumen word
```

### 1. Penambahan Modul Baru (`contract/`)
- `contract/schema.py`: Mendefinisikan struktur output JSON Pydantic yang sangat ketat untuk 20 pasal Kontrak Definitif.
- `contract/amendment_schema.py`: Mendefinisikan struktur output JSON Pydantic untuk konsideran dan rumusan pasal Addendum.
- `contract/generator.py`: Menyimpan *Agent* berbasis LLM (Qwen via OpenRouter) untuk mengekstrak informasi dan mem-parsing output menjadi draft Kontrak menggunakan *System Prompt* spesifik.
- `contract/amendment_generator.py`: Menyimpan *Agent* berbasis LLM untuk merumuskan bahasa Addendum.
- `contract/docx_builder.py`: Skrip *renderer* menggunakan `python-docx` untuk menyatukan draft JSON ke dalam dokumen word siap cetak dengan XML Styling Pertamina (warna navy, tabel khusus, header).

### 2. Modifikasi File Utama
- `RAG/vector_store.py`: Dirombak (di-refactor) agar mendukung koneksi ke Qdrant Cloud dan menggunakan `all-minilm-l6-v2` untuk *embeddings*. Menambahkan metode `ingest_bytes` sehingga file dari *browser* bisa langsung diindeks tanpa disimpan ke *disk* lokal.
- `api.py`: 
  - Penambahan *endpoint* FastAPI `POST /api/generate-kontrak` dan `POST /api/generate-amendemen`.
  - Penambahan *endpoint* manajemen KB (Knowledge Base) seperti `/api/kb/ingest`, `/api/kb/list`, dan `/api/kb/delete`.
- `app.py`:
  - Penambahan tab/mode navigasi "📝 Rancangan Kontrak Definitif" pada Streamlit Sidebar.
  - Penambahan tab/mode navigasi "📎 Draft Amendemen / Addendum".
  - Penambahan halaman "🗄️ Knowledge Base Management" untuk manajemen RAG secara visual.
- `config.py` & `.env`: Menyimpan kredensial `QDRANT_CLOUD_URL` dan `QDRANT_API_KEY`.

---
*Dokumen ini dibuat secara otomatis sebagai catatan serah terima (handover) pengembangan fitur.*
