# Changelog

Semua perubahan penting pada proyek **ITec-Ai (Sistem RKS & Tender)** akan didokumentasikan dalam file ini.

Format penulisan berpedoman pada [Keep a Changelog](https://keepachangelog.com/id/1.0.0/) dan mengikuti kaidah [Semantic Versioning](https://semver.org/lang/id/).

---

## [0.4.0] - 2026-10-08

### 🚀 Ditambahkan (Added)
- **Integrasi Qdrant Vector DB Lokal**:
  - Pengaktifan container `itec-qdrant` berbasis bridge network internal (`http://qdrant-db:6333`).
  - Pembuatan koleksi `Documents` otomatis dengan vektor 384 dimensi (Cosine distance) untuk model embedding MiniLM.
- **API Knowledge Base (Dapur-AI)**:
  - `GET /api/knowledge`: Melihat daftar PDF referensi, status ingest (`done`, `processing`, `not_ingested`), dan jumlah chunk di Qdrant.
  - `POST /api/ingest-pdf`: Ingest file PDF satuan yang diunggah ke Qdrant secara asinkron (background task).
  - `POST /api/ingest-all`: Ingest seluruh PDF di folder server secara otomatis di latar belakang.
  - `DELETE /api/knowledge/{filename}`: Menghapus data dokumen dari disk sekaligus membersihkan chunk terkait di Qdrant.
- **UI Manajemen Knowledge Base (Web Wadah)**:
  - Tabel dokumen interaktif di halaman `/knowledge` yang menampilkan daftar file, status ekstraksi, dan jumlah chunk.
  - Tombol aksi *"Ingest Semua PDF"* dan tombol *"Hapus"* dokumen.
  - Live auto-polling via AJAX untuk memperbarui status baris tabel secara real-time saat AI memproses dokumen.
- **Persistensi Data Dokumen**:
  - Volume Docker `dapur-rag-data:/app/RAG/Data` agar file PDF referensi yang diunggah tidak hilang saat container dibuat ulang (*recreate*).

### ⚡ Performa & Optimasi (Performance)
- **Non-blocking UI Rendering**:
  - Mengubah alur pemuatan halaman `/knowledge` dari *blocking PHP cURL* menjadi pemanggilan *asynchronous* via AJAX (`/knowledge/status`).
  - Memangkas waktu muat halaman awal (Largest Contentful Paint / LCP) dari **14,6 detik menjadi < 100 milidetik**.
- **Singleton & Lazy Loading Model AI**:
  - Menerapkan caching singleton pada koneksi Qdrant dan instance model `HuggingFaceEmbeddings` di `vector_store.py`.
  - Model embedding PyTorch hanya dimuat sekali di RAM, menghilangkan beban CPU berlebih dan mencegah server *freeze* saat diakses banyak pengguna.
- **Perbaikan Docker Caching**:
  - Menambahkan file `dapur-ai/.dockerignore` untuk mengecualikan `.venv` Windows agar tidak menimpa virtual environment Linux container.
  - Waktu start-up container `itec-dapur` terpangkas dari **~7 menit menjadi 1,6 detik** tanpa pernah mendownload ulang paket library saat restart.
  - Menambahkan `uv.lock` pada `dapur-ai/Dockerfile` untuk instalasi dependensi yang deterministik dan konsisten.

### 🛠️ Diperbaiki (Fixed)
- **Autentikasi OpenRouter**:
  - Memperbaiki issue `User not found` pada `itec-dapur` dengan menyelaraskan `OPENROUTER_API_KEY` dan model `qwen/qwen3.7-flash` dari environment host.
- **Idempotensi Ingest RAG**:
  - Mengganti mekanisme pemrosesan batch acak dengan fungsi `ingest_file()` berbasis ID deterministik (`uuid5`). File yang di-ingest ulang akan otomatis memperbarui chunk lama tanpa menimbulkan data duplikat di Qdrant.
- **Validasi Otomasi Testing**:
  - Pengujian end-to-end Playwright untuk skenario **TC-RKS-01** (Generate RKS lengkap) terverifikasi **100% Passed**.

### 🔒 Keamanan & Pembersihan Repositori (Security & Chore)
- Memperbarui `.gitignore` untuk mengabaikan:
  - File environment kredensial rahasia (`.env`).
  - Folder draft dan hasil generate dokumen (`dapur-ai/output/`, `dapur-ai/drafts/`).
  - Folder legacy `dapur-ai-old/` dan duplikat aset.
  - Artefak pengujian Playwright (`scenario-test/node_modules/`, `test-results/`, dan file `.docx` hasil robot).

---

## [1.0.0] - 2026-09-24

### 🚀 Rilis Awal (Initial Release)
- Sistem pembuatan dokumen RKS dan Tender awal menggunakan model OpenRouter.
- Dashboard Web berbasis Laravel 11 (Zona Wadah) dan backend AI berbasis FastAPI (Zona Dapur).
- Modul autentikasi pengguna dan riwayat generasi dokumen dasar.
