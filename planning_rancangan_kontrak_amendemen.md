# 🗺️ Roadmap Pengembangan — `Agentic_Rag_Pertamina_camp`

> Disusun berdasarkan seluruh pembahasan: fitur baru (Rancangan Kontrak & Amendemen), isolasi dari production (ITec-Ai), Qdrant Cloud, dan ingestion via browser.

---

## 🧭 Prinsip Dasar

- **Folder ini = Prototype / Development** → self-contained, tidak boleh bergantung pada kode `ITec-Ai/dapur-ai`
- **Folder ITec-Ai = Production** → tidak disentuh sama sekali
- **Qdrant Cloud** → dipilih agar tidak perlu Docker, bisa akses dari mana saja, data persisten
- **Ingestion via browser** → user upload PDF langsung dari UI Streamlit ke vector store

---

## 📊 Gambaran Arsitektur Target

```
Agentic_Rag_Pertamina_camp/  (self-contained)
│
├── app.py                   ← Streamlit UI (4 halaman)
│     ├── 📋 Dokumen RKS
│     ├── 📄 Dokumen Tender
│     ├── 📝 Rancangan Kontrak  ← BARU
│     ├── 📎 Draft Amendemen    ← BARU
│     └── 🗄️ Knowledge Base    ← BARU
│
├── api.py                   ← FastAPI (4 endpoint)
│     ├── POST /api/generate-rks       (sudah ada)
│     ├── POST /api/generate-tender    (sudah ada)
│     ├── POST /api/generate-kontrak   ← BARU
│     ├── POST /api/generate-amendemen ← BARU
│     └── POST/GET/DELETE /api/kb/*    ← BARU
│
├── RAG/
│     └── vector_store.py     ← Ditulis ulang (self-contained, multi-collection, bytes input)
│
├── contract/                 ← Modul BARU
│     ├── schema.py
│     ├── generator.py
│     ├── docx_builder.py
│     ├── amendment_schema.py
│     └── amendment_generator.py
│
├── tender/                   (sudah ada, tidak diubah besar)
└── .env                      ← Qdrant Cloud credential (terpisah dari ITec-Ai)
```

---

## ✅ FASE 0 — Setup Infrastruktur
**Estimasi: 0.5 hari | Prasyarat: semua fase berikutnya**

### Step 0.1 — Daftar & Konfigurasi Qdrant Cloud
- [ ] Daftar di [cloud.qdrant.io](https://cloud.qdrant.io) (free tier, 1 cluster)
- [ ] Buat cluster baru → catat `Endpoint URL` dan `API Key`
- [ ] Update `.env` di `Agentic_Rag_Pertamina_camp`:
  ```env
  # Qdrant Cloud (proto — terpisah dari ITec-Ai)
  QDRANT_CLUSTER_ENDPOINT=https://xxxx.us-east4-0.gcp.cloud.qdrant.io:6333
  QDRANT_API_KEY=your-cloud-api-key

  # OpenRouter (sudah ada)
  OPENROUTER_API_KEY=...

  # Embedding
  EMBEDDING_MODEL=sentence-transformers/all-minilm-l6-v2
  ```
- [ ] Pastikan `.env.example` diupdate juga (tanpa nilai asli)

### Step 0.2 — Rencana Collections Qdrant
```
rks_kb         ← dokumen referensi RKS (sudah berjalan)
contract_kb    ← template & referensi Rancangan Kontrak
amendment_kb   ← contoh Addendum / Amendemen
```

---

## ✅ FASE 1 — Tulis Ulang `RAG/vector_store.py` (Self-Contained)
**Estimasi: 1 hari | Dasar untuk semua fitur RAG**

> ⚠️ **Tidak mengcopy dari `dapur-ai`** — ditulis ulang mandiri.

### Step 1.1 — Desain Interface
```python
class Vector_Store:
    def __init__(self, collection_name: str)
    def ingest_bytes(self, file_bytes: bytes, filename: str) -> int
    # Input bytes bukan path — karena Streamlit upload ke memory
    def list_sources(self) -> dict[str, int]
    # Return {filename: chunk_count}
    def delete_source(self, filename: str) -> None
    def retrieve(self, query: str, k: int = 4) -> list[Document]
    def as_retriever(self) -> BaseRetriever
```

### Step 1.2 — Implementasi
- [ ] Koneksi ke Qdrant Cloud via `QDRANT_CLUSTER_ENDPOINT` + `QDRANT_API_KEY`
- [ ] Auto-create collection jika belum ada
- [ ] `ingest_bytes()`: tulis temp file → Docling parse → chunk → embed → push ke Qdrant
- [ ] Chunk ID deterministik (`uuid5`) → idempotent (re-upload file sama tidak duplikat)
- [ ] `list_sources()` + `delete_source()` untuk manajemen KB
- [ ] Gunakan `HuggingFaceEmbeddings` (lokal, tidak perlu API)

### Step 1.3 — Update `config.py`
- [ ] Tambah `QDRANT_CLUSTER_ENDPOINT`, `QDRANT_API_KEY`, `EMBEDDING_MODEL`
- [ ] Semua konfigurasi baca dari `.env`

---

## ✅ FASE 2 — Halaman Knowledge Base di Streamlit + API
**Estimasi: 1 hari | Bergantung pada: FASE 1**

> Fitur ingestion dokumen via browser — user tidak perlu akses server.

### Step 2.1 — API Endpoints Knowledge Base (`api.py`)
```
POST   /api/kb/ingest     ← Upload PDF, pilih collection, ingest
GET    /api/kb/list        ← List dokumen per collection
DELETE /api/kb/delete      ← Hapus dokumen dari collection
```

### Step 2.2 — Halaman `🗄️ Knowledge Base` di `app.py`
- [ ] Dropdown pilih collection: `rks_kb | contract_kb | amendment_kb`
- [ ] File uploader (PDF, multi-file)
- [ ] Tombol **Upload & Ingest** → progress spinner → konfirmasi sukses + jumlah chunks
- [ ] Tabel daftar dokumen yang sudah terindex (nama file + jumlah chunk)
- [ ] Tombol **🗑️ Hapus** per dokumen
- [ ] Catatan: halaman ini bisa dijadikan tab terpisah atau halaman sidebar sendiri

---

## ✅ FASE 3 — Schema Rancangan Kontrak & Amendemen
**Estimasi: 1 hari | Fondasi sebelum coding generator**

### Step 3.1 — Buat folder & file baru `contract/`
```
contract/
├── __init__.py
├── schema.py            ← Model Pydantic kontrak definitif
├── amendment_schema.py  ← Model Pydantic amendemen/addendum
├── generator.py         ← LLM generator kontrak
├── amendment_generator.py
└── docx_builder.py      ← Renderer DOCX mandiri
```

### Step 3.2 — `contract/schema.py`
Pydantic models untuk 20+ pasal kontrak:
- [ ] `IdentitasPihak` (Pemberi Kerja & Penyedia)
- [ ] `NilaiKontrak` (nilai, mata uang, sistem pembayaran, retensi)
- [ ] `JangkaWaktu` (durasi, masa pemeliharaan, tanggal mulai)
- [ ] `Pasal` (nomor, judul, konten — bisa paragraf/list/tabel)
- [ ] `KontrakDefinitif` (cover + identitas + 20 pasal + TTD)
- [ ] JSON Schema string untuk prompt LLM

Susunan 20 pasal minimal:
```
Pasal  1  Definisi & Interpretasi
Pasal  2  Lingkup Pekerjaan
Pasal  3  Jangka Waktu Pelaksanaan
Pasal  4  Nilai Kontrak & Pembayaran
Pasal  5  Hak & Kewajiban Para Pihak
Pasal  6  Personel & Peralatan
Pasal  7  HSSE & CSMS
Pasal  8  Subkontraktor
Pasal  9  Perubahan Pekerjaan (Change Order)
Pasal 10  Denda & Penalti Keterlambatan
Pasal 11  Jaminan (Pelaksanaan, Pemeliharaan, TKDN)
Pasal 12  Force Majeure
Pasal 13  Penghentian & Pemutusan Kontrak
Pasal 14  Penyelesaian Perselisihan
Pasal 15  Kerahasiaan
Pasal 16  Integritas & Anti-Suap
Pasal 17  Ketentuan TKDN
Pasal 18  Garansi & Masa Pemeliharaan
Pasal 19  Serah Terima Pekerjaan
Pasal 20  Ketentuan Lain-Lain
```

### Step 3.3 — `contract/amendment_schema.py`
- [ ] `JenisPerubahan` enum: `NILAI_KONTRAK | WAKTU | LINGKUP | PERSONEL | LAINNYA`
- [ ] `ItemPerubahan` (pasal yang diubah, isi lama, isi baru, alasan/justifikasi)
- [ ] `DraftAmendemen` (nomor addendum, tanggal, referensi kontrak asal, list perubahan, TTD)

---

## ✅ FASE 4 — LLM Generator Kontrak & Amendemen
**Estimasi: 2 hari | Bergantung pada: FASE 1 & 3**

### Step 4.1 — `contract/generator.py`
- [ ] `GenerateKontrakTool.invoke(kwargs)`: terima input form → RAG retrieve dari `contract_kb` → prompt LLM → JSON pasal → simpan ke active store
- [ ] Prompt engineering: instruksikan LLM untuk mengisi setiap pasal secara spesifik berdasarkan jenis pekerjaan, bukan template generik
- [ ] Context injection: jika ada PDF RKS/BOQ di-upload, ekstrak teks → masukkan ke prompt sebagai konteks lingkup pekerjaan

### Step 4.2 — `contract/amendment_generator.py`
- [ ] Input: referensi kontrak asal (nomor + upload PDF opsional) + jenis perubahan + detail perubahan
- [ ] RAG retrieve dari `amendment_kb` → contoh amendemen serupa
- [ ] LLM generate: konsideran hukum, narasi perubahan per pasal, klausa restatement
- [ ] Output JSON → siap render ke DOCX

---

## ✅ FASE 5 — DOCX Builder Kontrak & Amendemen
**Estimasi: 2 hari | Bergantung pada: FASE 3 & 4**

### Step 5.1 — `contract/docx_builder.py` (Rancangan Kontrak)
- [ ] Cover: Logo Pertamina, judul `KONTRAK PEKERJAAN`, nomor kontrak, tanggal
- [ ] Halaman pembuka: Identitas Para Pihak
- [ ] Body: render 20 pasal dengan heading terformat `PASAL 1`, `PASAL 2`, dst.
- [ ] Tabel di dalam pasal (jika diperlukan — misal daftar personel, milestone pembayaran)
- [ ] Footer setiap halaman: nomor halaman + nomor kontrak
- [ ] Halaman tanda tangan: kolom TTD Pertamina & Vendor
- [ ] Watermark / disclaimer `DRAFT AI — PERLU REVIEW LEGAL` di setiap halaman

### Step 5.2 — DOCX Builder Amendemen
- [ ] Cover: `ADDENDUM KE-[N] ATAS KONTRAK NOMOR [XXX]`
- [ ] Konsideran (Menimbang, Mengingat, Memperhatikan)
- [ ] Pasal perubahan: format `"Pasal X semula berbunyi: [...] diubah menjadi: [...]"`
- [ ] Pasal penutup: ketentuan lain tetap berlaku, tanggal berlaku efektif
- [ ] Halaman tanda tangan: Pertamina & Vendor

---

## ✅ FASE 6 — API Endpoints Baru (`api.py`)
**Estimasi: 0.5 hari | Bergantung pada: FASE 4 & 5**

### Step 6.1 — Tambah 2 endpoint

```python
POST /api/generate-kontrak
# Input Form:
#   nama_pekerjaan, nomor_kontrak, tanggal, nama_vendor,
#   npwp_vendor, nilai_kontrak, durasi_hari, masa_pemeliharaan,
#   resiko_csms, sistem_pembayaran, pejabat_ttd_pertamina
#   file (PDF RKS opsional untuk konteks lingkup)
# Output: FileResponse .docx

POST /api/generate-amendemen
# Input Form:
#   nomor_addendum, nomor_kontrak_asal, nama_pekerjaan,
#   nama_vendor, tanggal_berlaku, alasan_perubahan,
#   jenis_perubahan[], detail_perubahan
#   file (PDF kontrak asal opsional)
# Output: FileResponse .docx
```

---

## ✅ FASE 7 — UI Streamlit (2 Halaman Baru)
**Estimasi: 1.5 hari | Bergantung pada: FASE 6**

### Step 7.1 — Update navigasi sidebar `app.py`
```python
options=[
    "📋 Dokumen RKS",
    "📄 Dokumen Tender (IKPP & Kontrak)",
    "📝 Rancangan Kontrak Definitif",   # BARU
    "📎 Draft Amendemen / Addendum",     # BARU
    "🗄️ Knowledge Base",               # BARU (dari Fase 2)
]
```

### Step 7.2 — Halaman `📝 Rancangan Kontrak Definitif`
Tab-based input:
- **Tab 1 — Identitas Kontrak:** Nomor, Judul Pekerjaan, Tanggal, Jenis Kontrak
- **Tab 2 — Para Pihak:** Unit Pertamina, Data Vendor (nama, NPWP, alamat, direktur)
- **Tab 3 — Nilai & Pembayaran:** Nilai kontrak (Rp), sistem pembayaran, retensi, TKDN
- **Tab 4 — Waktu & HSSE:** Durasi (hari), masa pemeliharaan, tingkat risiko CSMS
- **Tab 5 — Dokumen Pendukung:** Upload RKS/BOQ PDF (konteks lingkup pekerjaan untuk LLM)
- Tombol: **🚀 Generate Rancangan Kontrak (.docx)**

### Step 7.3 — Halaman `📎 Draft Amendemen / Addendum`
- Input Referensi: Nomor Kontrak Asal, Tanggal Kontrak, Para Pihak
- Input Amendemen: Nomor Addendum, Tanggal Berlaku Efektif
- Multi-select Jenis Perubahan: `Nilai Kontrak | Waktu | Lingkup | Personel | Lainnya`
- Per jenis: Nilai/kondisi **lama** → Nilai/kondisi **baru** → Alasan/justifikasi
- Upload kontrak asal (PDF opsional) → AI baca konteks pasal yang berubah
- Tombol: **🚀 Generate Draft Amendemen (.docx)**

---

## ✅ FASE 8 — Testing & QA
**Estimasi: 1 hari**

- [ ] Test end-to-end: Rancangan Kontrak → DOCX (berbagai jenis pekerjaan)
- [ ] Test end-to-end: Amendemen dengan upload kontrak asal → DOCX
- [ ] Test Knowledge Base: upload PDF → ingest → retrieve → hapus
- [ ] Validasi DOCX: cek nomor pasal, header/footer, kolom TTD
- [ ] Test error handling: file rusak, LLM timeout, Qdrant tidak terhubung
- [ ] Update `README.md` dengan instruksi endpoint dan halaman baru

---

## 📅 Timeline Ringkas

```
Hari 1      │ FASE 0: Setup Qdrant Cloud + konfigurasi .env
Hari 1-2    │ FASE 1: Tulis ulang RAG/vector_store.py (self-contained)
Hari 2-3    │ FASE 2: KB Management UI + API endpoints KB
Hari 3-4    │ FASE 3: Schema contract/ (kontrak & amendemen)
Hari 4-6    │ FASE 4: LLM Generator (kontrak & amendemen)
Hari 6-8    │ FASE 5: DOCX Builder (kontrak & amendemen)
Hari 8      │ FASE 6: API Endpoints baru di api.py
Hari 9-10   │ FASE 7: Streamlit UI (2 halaman baru)
Hari 10-11  │ FASE 8: Testing & QA + update README
```

**Total: ~11 hari kerja**

---

## ⚠️ Batasan & Aturan Selama Pengembangan

| Aturan | Keterangan |
|---|---|
| ❌ Jangan import dari `ITec-Ai/dapur-ai` | Folder ini harus self-contained |
| ❌ Jangan pakai `http://qdrant-db:6333` | Itu URL Docker production, bukan untuk proto |
| ✅ Semua config dari `.env` lokal | Tidak ada hardcode credentials |
| ✅ Output selalu ke folder `output/` | Konsisten dengan pola yang sudah ada |
| ✅ Tambahkan watermark DRAFT di DOCX baru | Rancangan Kontrak & Amendemen belum final |


> Berdasarkan analisis mendalam terhadap arsitektur `Agentic_Rag_Pertamina_camp`

---

## 🔍 Analisis Kondisi Saat Ini

### Yang Sudah Ada (Tapi Belum Lengkap)
Sistem saat ini sudah memiliki *fondasi* untuk Rancangan Kontrak:
- **`tender/schema.py`** → `RancanganKontrakData` (model dasar, hanya 6 field: judul, nomor, durasi, pemeliharaan, sistem bayar, denda, lingkup)
- **`tender/docx.py`** → Pasti ada fungsi `render_tender_to_docx` yang merender kontrak sebagai **Bagian B** dari dokumen tender
- **`tender/generator.py`** → LLM mengisi `rancangan_kontrak` sebagai sub-bagian dari JSON tender

**Masalah:** Rancangan Kontrak yang ada saat ini hanya *embedded* di dalam dokumen tender, bukan dokumen mandiri yang lengkap. Draft Amendemen **belum ada sama sekali**.

---

## 🚧 GAP Analysis

| Komponen | Kondisi Saat Ini | Target |
|---|---|---|
| Rancangan Kontrak | Bagian B embedded di Dokumen Tender (minimal) | Dokumen mandiri 20+ pasal (definitif) |
| Pasal-pasal kontrak | Hanya `lingkup_pekerjaan`, durasi, denda | Lengkap: Hak & Kewajiban, Force Majeure, Garansi, Penyelesaian Sengketa, dll. |
| Draft Amendemen | ❌ Tidak ada | Dokumen perubahan kontrak berbasis referensi kontrak asal |
| UI Generator Kontrak | ❌ Tidak ada halaman terpisah | Form input + generate + preview |
| UI Generator Amendemen | ❌ Tidak ada | Form input perubahan + diff visual |

---

## ⚙️ Yang Perlu Disiapkan

### A. Persiapan Data & Referensi (Knowledge Base)

1. **Kumpulkan template kontrak Pertamina Patra Niaga**
   - Template Kontrak Definitif standar (PDF/Word dari pengadaan nyata)
   - Template Amendemen / Addendum (contoh perubahan kontrak yang pernah dibuat)
   - Pedoman: `A03-001/PNG200000/2024-S9 Rev.1` (sudah ada di sistem prompt)
   
2. **Indexing ke Qdrant Vector Store**
   - Tambah collection baru: `contract_knowledge` dan `amendment_knowledge`
   - Parse PDF referensi menggunakan Docling → embed → push ke Qdrant

3. **Pelajari struktur pasal kontrak Pertamina:**
   Minimal 20 pasal yang harus ada di Rancangan Kontrak Definitif:
   - Pasal 1: Definisi & Interpretasi
   - Pasal 2: Lingkup Pekerjaan
   - Pasal 3: Jangka Waktu Pelaksanaan
   - Pasal 4: Nilai Kontrak & Pembayaran
   - Pasal 5: Hak & Kewajiban Para Pihak
   - Pasal 6: Personel & Peralatan
   - Pasal 7: HSSE & CSMS
   - Pasal 8: Subkontraktor
   - Pasal 9: Perubahan Pekerjaan (Change Order)
   - Pasal 10: Denda & Penalti
   - Pasal 11: Jaminan Pelaksanaan & Pemeliharaan
   - Pasal 12: Force Majeure
   - Pasal 13: Penghentian & Pemutusan Kontrak
   - Pasal 14: Penyelesaian Perselisihan
   - Pasal 15: Kerahasiaan
   - Pasal 16: Integritas & Anti-Suap
   - Pasal 17: Ketentuan TKDN
   - Pasal 18: Garansi & Masa Pemeliharaan
   - Pasal 19: Serah Terima Pekerjaan
   - Pasal 20: Ketentuan Lain-Lain (Governing Law, Amandemen, dll.)

---

### B. Persiapan Infrastruktur Kode

#### File Baru yang Perlu Dibuat:

```
Agentic_Rag_Pertamina_camp/
├── contract/                          # 📁 Modul baru
│   ├── __init__.py
│   ├── schema.py                      # Pydantic models pasal kontrak lengkap
│   ├── generator.py                   # LLM generator (contract & amendment)
│   ├── docx_builder.py                # python-docx renderer kontrak mandiri
│   └── amendment_schema.py            # Schema khusus amendemen/addendum
├── RAG/
│   └── contract_retriever.py          # RAG retriever untuk knowledge kontrak
└── api.py                             # Tambah 2 endpoint baru
```

#### File yang Perlu Dimodifikasi:

```
├── app.py                             # Tambah 2 menu baru di sidebar
├── tender/schema.py                   # Perluas RancanganKontrakData (20+ pasal)
├── tender/docx.py                     # Sinkronisasi dengan schema baru
└── RAG/vector_store.py                # Support multi-collection
```

---

## 🗺️ Planning Eksekusi (Fase per Fase)

---

### 📌 FASE 1 — Foundation & Schema Design
**Estimasi: 1–2 hari**

**Tujuan:** Buat blueprint data (schema) yang solid sebelum coding apapun.

- [ ] **1.1** Buat `contract/schema.py`
  - Model Pydantic untuk setiap pasal: `Pasal`, `KontrakDefinitif`
  - Model untuk `AmendemenKontrak`: berisi referensi ke kontrak asal + perubahan per pasal
  - JSON Schema string untuk prompt LLM

- [ ] **1.2** Buat `contract/amendment_schema.py`
  - `JenisPerubahan` enum: `NILAI_KONTRAK`, `LINGKUP_PEKERJAAN`, `WAKTU_PELAKSANAAN`, `PERSONEL`, `LAIN_LAIN`
  - `ItemPerubahan`: pasal yang diubah, isi lama, isi baru, alasan
  - `DraftAmendemen`: nomor addendum, tanggal, referensi kontrak asal, list perubahan, pejabat penandatangan

- [ ] **1.3** Review & validasi schema dengan tim (apakah sudah sesuai format Pertamina)

---

### 📌 FASE 2 — LLM Generator & RAG
**Estimasi: 2–3 hari**

**Tujuan:** LLM bisa generate konten pasal yang relevan dan kontekstual.

- [ ] **2.1** Buat `contract/generator.py`
  - `GenerateKontrakDefinitifTool.invoke()`: terima input form → prompt LLM → return JSON pasal lengkap
  - Prompt engineering: pasal harus spesifik ke jenis pekerjaan, bukan template generik
  - RAG injection: retrieve kontrak referensi dari vector store untuk grounding

- [ ] **2.2** Buat `contract/amendment_generator.py`
  - Input: **kontrak asal** (bisa upload docx/PDF, atau pilih dari database kontrak) + **parameter perubahan** (jenis, alasan, nilai baru)
  - LLM generate: narasi pasal lama vs baru, konsideran hukum, klausa restatement
  - Output JSON → siap render ke DOCX

- [ ] **2.3** Setup RAG untuk kontrak (opsional, jika ada data referensi)
  - Buat collection `contract_kb` di Qdrant
  - `RAG/contract_retriever.py` untuk query klausul kontrak serupa

---

### 📌 FASE 3 — DOCX Builder (Renderer)
**Estimasi: 2–3 hari**

**Tujuan:** Output DOCX harus sesuai format resmi Pertamina (header, footer, nomor pasal, format tabel, dll.).

- [ ] **3.1** Buat `contract/docx_builder.py`
  - **Cover page** kontrak: logo Pertamina, judul "KONTRAK PEKERJAAN", nomor kontrak, tanggal
  - **Halaman Pembuka**: Identitas Para Pihak (Pertamina sebagai Pemberi Kerja, Vendor sebagai Penyedia)
  - **Body**: Render 20+ pasal dengan numbering `Pasal 1`, `Pasal 2`, dst.
  - **Footer** setiap halaman: nomor halaman + nomor kontrak
  - **Halaman Tanda Tangan**: kolom TTD Pertamina & Vendor

- [ ] **3.2** Buat `contract/amendment_docx_builder.py`
  - Cover: "ADDENDUM KE-[N] ATAS KONTRAK NOMOR [XXX]"
  - **Konsideran** (Menimbang, Mengingat, Memperhatikan)
  - **Pasal Perubahan**: Tampilkan pasal yang diubah dengan format "Pasal X sebelumnya berbunyi... diubah menjadi..."
  - **Pasal Penutup**: ketentuan lain tetap berlaku, tanggal berlaku, tanda tangan

---

### 📌 FASE 4 — API Endpoints
**Estimasi: 1 hari**

**Tujuan:** Expose fitur baru melalui FastAPI.

- [ ] **4.1** Tambah di `api.py`:
  ```
  POST /api/generate-kontrak
  POST /api/generate-amendemen
  ```

- [ ] **4.2** `POST /api/generate-kontrak`
  - Input Form: `nama_pekerjaan`, `nomor_kontrak`, `nama_vendor`, `nilai_kontrak`, `durasi_hari`, `jenis_kontrak`, `resiko_csms`, `sistem_pembayaran`, file RKS (PDF opsional)
  - Process: extract context → LLM generate → export DOCX
  - Output: file `.docx` (FileResponse)

- [ ] **4.3** `POST /api/generate-amendemen`
  - Input Form: `nomor_addendum`, `referensi_nomor_kontrak`, `nama_pekerjaan`, `nama_vendor`, `jenis_perubahan[]`, `alasan_perubahan`, `tanggal_berlaku`, file kontrak asal (PDF opsional)
  - Process: parse kontrak asal → LLM draft perubahan → export DOCX
  - Output: file `.docx`

---

### 📌 FASE 5 — Frontend (Streamlit UI)
**Estimasi: 1–2 hari**

**Tujuan:** User experience yang intuitif, konsisten dengan desain existing.

- [ ] **5.1** Modifikasi `app.py` — tambah 2 menu di sidebar:
  ```
  📋 Dokumen RKS
  📄 Dokumen Tender (IKPP & Kontrak)
  📝 Rancangan Kontrak Definitif      ← BARU
  📎 Draft Amendemen / Addendum        ← BARU
  ```

- [ ] **5.2** Halaman **Rancangan Kontrak** (Tab-based form):
  - **Tab 1** — Identitas Kontrak: Nomor, Judul, Tanggal, Jenis Kontrak
  - **Tab 2** — Para Pihak: Data Pertamina (unit) & Data Vendor (nama, NPWP, alamat, wakil sah)
  - **Tab 3** — Nilai & Pembayaran: Nilai kontrak (Rp), Sistem pembayaran (Milestone/Monthly), Retensi
  - **Tab 4** — Waktu & HSSE: Durasi, Masa Pemeliharaan, Tingkat Risiko CSMS
  - **Tab 5** — Dokumen Pendukung: Upload RKS / BOQ PDF sebagai konteks lingkup pekerjaan

- [ ] **5.3** Halaman **Draft Amendemen** (Form terstruktur):
  - Input Referensi Kontrak Asal: Nomor Kontrak, Tanggal, Para Pihak
  - Input Nomor Addendum & Tanggal
  - Pilih Jenis Perubahan (multi-select): Nilai, Waktu, Lingkup, Personel, Lainnya
  - Untuk setiap jenis: input nilai lama → nilai baru → alasan/justifikasi
  - Upload kontrak asal (PDF) untuk AI baca konteks pasal yang berubah
  - Tombol: 🚀 Generate Draft Amendemen

---

### 📌 FASE 6 — Testing & QA
**Estimasi: 1 hari**

- [ ] **6.1** Test end-to-end: Rancangan Kontrak dari input form → DOCX download
- [ ] **6.2** Test end-to-end: Draft Amendemen dengan upload kontrak asal → DOCX
- [ ] **6.3** Validasi format DOCX: apakah nomor pasal, header/footer, TTD sudah benar
- [ ] **6.4** Test dengan berbagai jenis pekerjaan (konstruksi, jasa operasi, maintenance, dll.)

---

## 📊 Timeline Ringkas

```
Hari 1-2  │ FASE 1: Schema Design (contract & amendment Pydantic models)
Hari 3-5  │ FASE 2: LLM Generator + RAG contract retriever
Hari 6-8  │ FASE 3: DOCX Builder (kontrak + amendemen renderer)
Hari 9    │ FASE 4: API Endpoints (2 endpoint baru di api.py)
Hari 10-11│ FASE 5: Streamlit UI (2 halaman baru)
Hari 12   │ FASE 6: Testing & QA
```

**Total estimasi: ~12 hari kerja**

---

## ⚠️ Risiko & Mitigasi

| Risiko | Tingkat | Mitigasi |
|---|---|---|
| Tidak ada data referensi kontrak Pertamina untuk RAG | 🔴 Tinggi | Buat LLM prompt yang sangat detail dengan pedoman kontrak yang ada. RAG bisa ditambahkan belakangan. |
| Format DOCX tidak sesuai standar Pertamina | 🟡 Sedang | Minta template Word asli dari tim pengadaan untuk dijadikan basis `docx_builder` |
| LLM menghasilkan pasal yang tidak akurat secara hukum | 🟡 Sedang | Tambahkan disclaimer "DRAFT AI - Perlu Review Legal" di cover DOCX. Human-in-the-loop review. |
| Amendemen membutuhkan parsing kontrak asal yang akurat | 🟡 Sedang | Gunakan Docling untuk parse DOCX/PDF kontrak asal, beri ke LLM sebagai konteks penuh |

---

## 💡 Rekomendasi Urutan Eksekusi

> Mulai dari yang memberikan value paling cepat:

1. **Kerjakan FASE 1 & 3 (Schema + DOCX Builder) dulu** → karena ini fondasi
2. **Lanjut FASE 2 (LLM Generator)** → ini bagian paling complex
3. **FASE 4 & 5 (API + UI)** → relatif cepat karena tinggal "pasang" komponen yang sudah ada
4. **FASE 6 (Testing)** → iteratif, bisa disambi saat development

> **Saran:** Mulai dari `contract/schema.py` dan minta contoh/template Rancangan Kontrak Pertamina yang asli untuk dijadikan acuan struktur pasal sebelum coding apapun.
