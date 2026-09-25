# Pertamina Procurement AI System (V2)

Sistem berbasis AI untuk otomatisasi penyusunan dokumen pengadaan PT Pertamina Patra Niaga:
1. **Dokumen RKS (Rencana Kerja dan Syarat-Syarat):** Penyusunan spesifikasi teknis dan ruang lingkup pekerjaan berbasis LLM & RAG Vector Store.
2. **Dokumen Tender (IKPP & Rancangan Kontrak):** Paket dokumen tender lengkap Versi 2.0 (Cover, Bagian A: IKPP 40 Poin & Ketentuan Umum, Lampiran 1A s.d. 8, dan Bagian B: Rancangan Kontrak Definitif, PI-07, SP3MK).

---

## 📋 Daftar Isi
- [Prasyarat](#-prasyarat)
- [Konfigurasi Lingkungan (.env)](#-konfigurasi-lingkungan-env)
- [Instalasi Dependensi](#-instalasi-dependensi)
- [Menjalankan Backend (FastAPI)](#-menjalankan-backend-fastapi)
- [Menjalankan Frontend (Streamlit)](#-menjalankan-frontend-streamlit)
- [Alur Penggunaan Aplikasi](#-alur-penggunaan-aplikasi)
- [Daftar Endpoint API](#-daftar-endpoint-api)
- [Troubleshooting](#-troubleshooting)

---

## ⚙️ Prasyarat

Pastikan perangkat Anda sudah terinstal:
- **Python 3.12+**
- **uv** (Package & environment manager yang direkomendasikan):
  ```bash
  # Instalasi uv (jika belum terpasang di Windows PowerShell):
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  *(Atau dapat menggunakan Python venv & pip biasa)*

---

## 🔑 Konfigurasi Lingkungan (`.env`)

Pastikan file `.env` berada di direktori `AI_System_V2/` dengan variabel konfigurasi berikut:

```env
# OpenRouter / LLM
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Qdrant Vector Store
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_CLUSTER_ENDPOINT=https://your-cluster-url.qdrant.io

# HuggingFace (Embedding)
HF_TOKEN=your_huggingface_token

# (Opsional) Tavily & LangSmith Tracing
TAVILY_API_KEY=your_tavily_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT="Pertamina_AI"
```

---

## 📦 Instalasi Dependensi

Masuk ke direktori `AI_System_V2`:

```bash
cd "d:\Coding practice\Pertamina\AI_System_V2"
```

### Menggunakan `uv` (Direkomendasikan)
```bash
uv sync
```

### Menggunakan `pip` standar (Alternatif)
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

pip install -r pyproject.toml
```

---

## 🚀 Menjalankan Backend (FastAPI)

Backend FastAPI bertugas memproses ekstraksi file PDF (Docling), query RAG vector store, inferensi LLM via OpenRouter, serta mengekspor dokumen ke format `.docx`.

Buka terminal pertama di folder `AI_System_V2`:

```bash
# Menjalankan server FastAPI dengan auto-reload di port 8000
uv run uvicorn api:app --reload --port 8000
```

* **Swagger API Documentation:** Buka [http://localhost:8000/docs](http://localhost:8000/docs) di browser untuk melihat dan menguji endpoint API secara interaktif.
* **Redoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 💻 Menjalankan Frontend (Streamlit)

Frontend Streamlit menyediakan antarmuka web yang interaktif dengan navigasi sidebar untuk memilih dokumen yang ingin dibuat.

Buka terminal kedua di folder `AI_System_V2`:

```bash
uv run streamlit run app.py
```

Setelah dijalankan, browser Anda akan otomatis membuka:
* **Web UI:** [http://localhost:8501](http://localhost:8501)

> **Catatan:** Pastikan Backend FastAPI sudah aktif di port `8000` sebelum menekan tombol *Generate* pada Streamlit.

---

## 🧭 Alur Penggunaan Aplikasi

Setelah membuka aplikasi Streamlit ([http://localhost:8501](http://localhost:8501)):

1. **Gunakan Navigasi di Sidebar Kiri:**
   * Pilih **📋 Dokumen RKS** jika ingin membuat dokumen teknis Rencana Kerja & Syarat.
   * Pilih **📄 Dokumen Tender (IKPP & Kontrak)** jika ingin membuat paket dokumen tender formal lengkap.

2. **Jika Memilih Dokumen RKS:**
   * Isi Judul Pekerjaan, Detail Ruang Lingkup, Lokasi, dan Kategori Risiko CSMS.
   * Unggah dokumen acuan BoQ / TOR (PDF).
   * Klik **🚀 Generate Dokumen RKS**.
   * Unduh file `.docx` yang dihasilkan.

3. **Jika Memilih Dokumen Tender:**
   * **Tab 1 (Informasi Tender & Pejabat):** Masukkan Nama Pengadaan, Nomor Dokumen Tender, Tanggal, Metode Pemenuhan (Tender Terbatas/Terbuka), Jenis Kontrak, serta data Pejabat Pengadaan & Pengawas.
   * **Tab 2 (HPS/OE, CSMS & TKDN):** Masukkan Nilai *Prime Cost*, Total HPS (+ Keuntungan & Risiko), Kategori Risiko HSSE/CSMS, dan Komitmen Minimal TKDN (%).
   * **Tab 3 (Jadwal & Pelaksanaan):** Tentukan jadwal Pre-Bid Meeting (hari/tanggal, waktu, platform Microsoft Teams) dan batas waktu pemasukan dokumen penawaran di SmartGEP.
   * **Tab 4 (Dokumen Pendukung - Opsional):** Unggah file RKS atau BOQ (PDF) agar AI dapat merumuskan kriteria teknis Lampiran 2A dan pasal kontrak Bagian B secara spesifik.
   * Klik **🚀 Generate Paket Dokumen Tender Lengkap (.docx)**.
   * Unduh file Dokumen Tender lengkap yang langsung siap pakai.

---

## 📡 Daftar Endpoint API

| Method | Endpoint | Deskripsi | Input Utama | Output |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/generate-rks` | Generate Dokumen RKS | `jenis_pekerjaan`, `detail_pekerjaan`, `resiko_csms`, file PDF | File `.docx` (Direct Download) |
| `POST` | `/api/generate-tender` | Generate Dokumen Tender Lengkap | `nama_pengadaan`, `nomor_tender`, `hps_oe`, `csms`, `tkdn`, dll. | File `.docx` (Direct Download) |

---

## 🛠️ Troubleshooting

1. **Error: `Gagal terhubung ke API backend` pada Streamlit:**
   * Pastikan server FastAPI di terminal pertama sudah berjalan dan menampilkan log `Application startup complete`.
   * Periksa apakah port `8000` tidak terblokir firewall atau sedang digunakan oleh aplikasi lain.

2. **Proses Generate Memakan Waktu Lama:**
   * Dokumen tender memiliki lebih dari 70 halaman dan matriks tabel yang padat, serta ekstraksi PDF menggunakan Docling membutuhkan komputasi.
   * Waktu generate normal berkisar antara 30 detik s.d. 2 menit tergantung ukuran file konteks yang diunggah dan respons LLM.

3. **Dokumen Hasil Download:**
   * Semua file yang digenerate tersimpan secara lokal di folder `output/` dalam direktori proyek.
