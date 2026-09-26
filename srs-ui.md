# 📐 SRS — UI/UX Design System & Interface Specification
## ITec-Ai · Sistem AI Pembuat Dokumen RKS & Tender · PT Pertamina Patra Niaga
> Versi 2.0 — Disesuaikan dengan arsitektur proyek aktual

---

## 1. KONTEKS PROYEK

### 1.1 Target User
- Karyawan korporat divisi Procurement & Engineering (usia 30–50 tahun)
- Mengurus dokumentasi berat (RKS, Tender, BOQ)
- Membutuhkan antarmuka yang **efisien, minim kebingungan, dan tidak intimidatif**

### 1.2 Prinsip Desain Utama
| # | Prinsip | Implementasi |
|---|---------|-------------|
| 1 | **Don't Make Me Think** | Label jelas, placeholder informatif, flow linier |
| 2 | **Forgiving UI** | Undo, konfirmasi sebelum aksi destruktif, default value |
| 3 | **High Contrast / WCAG AA** | Rasio kontras minimal 4.5:1, font besar |
| 4 | **Progressive Disclosure** | Tampilkan yang penting dulu, detail di balik akordion |

### 1.3 Tech Stack (Existing — Tidak Diubah)
```
Frontend Framework : Laravel 11 + Blade Template Engine
Styling            : Vanilla CSS dengan Design Token System (CSS Custom Properties)
Interaktivitas     : Alpine.js (ringan, deklaratif, tanpa build step)
Icons              : Inline SVG (Lucide-style, stroke-based)
Font               : Inter (Google Fonts, sudah terpasang)
Backend API        : FastAPI (Python) — via internal Docker network
```

---

## 2. DESIGN TOKEN SYSTEM

Design token adalah **satu-satunya sumber kebenaran** untuk seluruh visual. Semua komponen **wajib** menggunakan CSS variable, **bukan** hardcoded value.

### 2.1 Warna (Sudah Didefinisikan di `app.css`)
```css
/* Brand — Pertamina Corporate */
--color-primary:        #C41E3A;   /* Merah Pertamina */
--color-primary-dark:   #9E1830;
--color-primary-light:  #E8475E;
--color-secondary:      #003366;   /* Biru Korporat */
--color-accent:         #D4A843;   /* Emas / Aksen */

/* Status */
--color-success:        #059669;   /* Hijau — Approved, Berhasil */
--color-warning:        #D97706;   /* Kuning — Review, Menunggu */
--color-danger:         #DC2626;   /* Merah — Error, Gagal */
--color-info:           #2563EB;   /* Biru — Info, Draft */

/* Neutral */
--color-bg:             #F5F6FA;
--color-surface:        #FFFFFF;
--color-text:           #1F2937;
--color-text-secondary: #6B7280;
--color-border:         #D1D5DB;
```

### 2.2 Tipografi
```css
--font-family:    'Inter', system-ui, sans-serif;
--font-size-sm:   0.875rem;    /* 14px — helper text, caption */
--font-size-base: 1rem;        /* 16px — body text, form input */
--font-size-lg:   1.125rem;    /* 18px — subheading */
--font-size-xl:   1.375rem;    /* 22px — section title */
--font-size-2xl:  1.75rem;     /* 28px — page title */
```
> **Catatan penting:** Form input WAJIB menggunakan `font-size: 16px` minimum agar tidak trigger zoom di mobile Safari.

### 2.3 Spacing
```css
--space-xs:  0.25rem;   /* 4px */
--space-sm:  0.5rem;    /* 8px */
--space-md:  1rem;      /* 16px */
--space-lg:  1.5rem;    /* 24px */
--space-xl:  2rem;      /* 32px */
--space-2xl: 3rem;      /* 48px */
```

### 2.4 Elevasi & Radius
```css
--radius-sm:    6px;    /* Tombol kecil, input */
--radius-md:    10px;   /* Card, panel */
--radius-lg:    16px;   /* Modal, dialog */
--shadow-sm:    0 1px 3px rgba(0,0,0,0.08);
--shadow-md:    0 4px 12px rgba(0,0,0,0.1);
--shadow-lg:    0 8px 30px rgba(0,0,0,0.15);
```

### 2.5 Dark Mode (Fase Lanjutan)
Dark mode **belum menjadi prioritas** pada iterasi ini. Namun, karena seluruh warna menggunakan CSS variable, implementasinya nanti hanya perlu menambahkan blok `[data-theme="dark"]` yang meng-override token di atas. Tidak ada perubahan pada HTML atau JS.

---

## 3. GLOBAL LAYOUT

### 3.1 Struktur Halaman
```
┌─────────────────────────────────────────────────┐
│  TOP NAVBAR (fixed)                             │
│  [Logo] [Nav Items...        ] [User] [Logout]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  MAIN CONTENT AREA                              │
│  ┌─────────────────────────────────────────┐    │
│  │  Page Header (Title + Description)      │    │
│  ├─────────────────────────────────────────┤    │
│  │                                         │    │
│  │  @yield('content')                      │    │
│  │                                         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
├─────────────────────────────────────────────────┤
│  FOOTER (© ITec-Ai · Pertamina Patra Niaga)     │
└─────────────────────────────────────────────────┘
```

### 3.2 Top Navbar
- **Posisi:** Fixed top, lebar penuh, z-index tinggi
- **Kiri:** Logo + Brand ("ITec-Ai · Sistem RKS")
- **Tengah:** Menu navigasi horizontal (lihat §3.3)
- **Kanan:** Nama user + role + tombol Logout
- **Tinggi:** ~64px, background `--color-surface` dengan `--shadow-sm`

### 3.3 Navigasi — Item Menu
Menu navigasi **harus mencerminkan semua fitur aktual** yang tersedia:

| # | Label Menu | Route | Icon (Lucide) | Akses |
|---|-----------|-------|---------------|-------|
| 1 | **Buat RKS** | `/` | `file-text` | Semua user |
| 2 | **Buat Tender** | `/tender` | `gavel` / `file-signature` | Semua user |
| 3 | **Knowledge Base** | `/knowledge` | `database` / `book-open` | Semua user |
| 4 | **Riwayat** | `/riwayat` | `clock` / `history` | Semua user |
| 5 | **Audit Trail** | `/audit` | `shield` | Admin only |

> **State aktif:** Item menu yang sedang dipilih mendapat underline tebal `--color-primary` dan font-weight 600.

---

## 4. HALAMAN — SPESIFIKASI PER VIEW

### 4.1 Halaman: Buat Dokumen RKS (`/`) — ✅ SUDAH ADA
**Status:** Sudah diimplementasikan di `rks/form.blade.php`

**Layout:** Single-column centered form di dalam `.card`

**Form Fields:**
| Field | Tipe | Required | Keterangan |
|-------|------|----------|-----------|
| Jenis Pekerjaan | `text` | ✅ | Placeholder informatif |
| Detail Pekerjaan | `textarea` (4 rows) | ✅ | Deskripsi lengkap lingkup |
| Lokasi | `text` | ❌ | Opsional |
| Risiko CSMS | `select` | ✅ | LOW / MEDIUM / HIGH |
| Nomor Dokumen | `text` | ✅ | Format: `RKS-[KODE]-[TAHUN]` |
| Nama Perusahaan | `text` | ✅ | Default: PT PERTAMINA |
| Upload PDF (BOQ) | `file` (drag & drop) | ✅ | Format PDF, maks 50MB |

**Submit Flow:**
1. User klik "Generate Dokumen RKS"
2. Tampilkan **Loading Overlay** dengan stepper animasi (4 tahap)
3. Setelah selesai → Auto-download file `.docx`
4. Redirect ke halaman Riwayat dengan flash message sukses

**Loading Overlay Spec:**
- Full-screen semi-transparent overlay (`rgba(0,0,0,0.5)`)
- Card putih di tengah dengan spinner + 4 step indicator
- Pesan: "Mohon jangan tutup halaman ini. Proses berlangsung 2–5 menit."

---

### 4.2 Halaman: Buat Dokumen Tender (`/tender`) — 🔴 BELUM ADA
**Status:** Backend API sudah siap (`POST /api/generate-tender`), halaman frontend belum dibuat.

**Layout:** Single-column centered form, **dipecah menjadi 3 section** menggunakan akordion/fieldset agar tidak overwhelm user.

**Section 1 — Informasi Umum:**
| Field | Tipe | Required | Default Value |
|-------|------|----------|--------------|
| Nama Pengadaan | `text` | ✅ | — |
| Nomor Tender | `text` | ✅ | `No.Project/DT/PND970000/2026-S7` |
| Tanggal Dokumen | `date` / `text` | ✅ | Hari ini |
| Metode Pemenuhan | `select` | ✅ | Tender Terbatas |
| Jenis Kontrak | `select` | ✅ | Gabungan Harga Satuan & Lumpsum |

**Section 2 — Data Finansial & Teknis:**
| Field | Tipe | Required | Default Value |
|-------|------|----------|--------------|
| Prime Cost (Rp) | `number` | ✅ | 13.283.434.534 |
| Total dengan K&R (Rp) | `number` | ✅ | 14.346.100.000 |
| Risiko CSMS | `select` | ✅ | Tinggi |
| TKDN Minimal (%) | `number` (step 0.01) | ✅ | 20.12 |

**Section 3 — Pejabat & Jadwal:**
| Field | Tipe | Required | Default Value |
|-------|------|----------|--------------|
| Pejabat Procurement (Nama) | `text` | ✅ | Rigga Widar Atmagi |
| Pejabat Procurement (Jabatan) | `text` | ✅ | Area Manager Procurement Kalimantan |
| Pejabat Berwenang | `text` | ✅ | Sr. Manager Opt. & Maint. Regional Kalimantan |
| Pengawas Pekerjaan | `text` | ✅ | Region Manager RPD Regional Kalimantan |
| Pre-bid (Tanggal) | `text` | ✅ | Senin, 08 Desember 2025 |
| Pre-bid (Waktu) | `text` | ✅ | 10.00 WITA |
| Pre-bid (Tempat) | `textarea` | ✅ | Microsoft Teams Meeting... |
| Pemasukan Mulai | `text` | ✅ | Senin, 08 Desember 2025 |
| Pemasukan Selesai | `text` | ✅ | Senin, 15 Desember 2025 |

**File Upload:** Upload file BOQ/RKS (opsional) untuk konteks tambahan AI.

**Submit Flow:** Identik dengan RKS — Loading Overlay → Auto-download `.docx`

---

### 4.3 Halaman: Knowledge Base Management (`/knowledge`) — ✅ SUDAH ADA
**Status:** Sudah diimplementasikan di `knowledge/index.blade.php`

**Fitur:**
- Upload file PDF ke knowledge base AI (via `/api/ingest-pdf`)
- List file yang sudah diupload (jika tersedia)
- Feedback: Toast notification "File berhasil diupload dan sedang diproses"

---

### 4.4 Halaman: Riwayat Generasi (`/riwayat`) — ✅ SUDAH ADA
**Status:** Sudah diimplementasikan di `rks/history.blade.php`

**Layout:** Data table di dalam `.card`

**Tabel Kolom:**
| Kolom | Keterangan |
|-------|-----------|
| ID | Auto-increment |
| Jenis Dokumen | "RKS" atau "Tender" (badge berwarna) |
| Nama Proyek | Judul pekerjaan |
| Dibuat Oleh | Nama user |
| Tanggal | Format: dd MMM yyyy, HH:mm |
| Status | Badge pill (Draft=Abu, Selesai=Hijau, Gagal=Merah) |
| Aksi | Tombol Download (jika file tersedia) |

**Fitur Tabel:**
- Sticky header
- Zebra-striping pada baris genap
- Empty state: Ilustrasi + teks "Belum ada dokumen yang digenerate"
- Pagination (jika jumlah > 15 baris)

---

### 4.5 Halaman: Audit Trail (`/audit`) — ✅ SUDAH ADA (Admin Only)
**Status:** Sudah diimplementasikan di `audit/index.blade.php`

**Akses:** Hanya user dengan role `admin`

**Fitur:** Log seluruh aktivitas sistem (siapa melakukan apa, kapan)

---

## 5. COMPONENT LIBRARY — Spesifikasi Reusable

### 5.1 Button (`.btn`)
```
Variant       | Background           | Text     | Use Case
─────────────┼──────────────────────┼──────────┼─────────────────
.btn-primary  | --color-primary      | white    | Aksi utama (Generate, Submit)
.btn-secondary| --color-secondary    | white    | Aksi alternatif
.btn-outline  | transparent          | primary  | Aksi sekunder (Cancel, Back)
.btn-ghost    | transparent          | text     | Aksi minor (Reset)
.btn-danger   | --color-danger       | white    | Aksi destruktif (Hapus)
```
- **Minimum hitbox:** 44×44px (WCAG touch target)
- **States:** Default → Hover (darken 10%) → Active (darken 15%) → Disabled (opacity 0.5, cursor: not-allowed)
- **Loading state:** Spinner SVG menggantikan teks, tombol disabled

### 5.2 Form Input (`.form-input`)
- **Height:** 48px (nyaman untuk usia 30–50 tahun)
- **Font size:** `--font-size-base` (16px)
- **Border:** 1.5px solid `--color-border`
- **Focus:** Border berubah ke `--color-primary`, shadow ring biru transparan
- **Error:** Border merah `--color-danger` + ikon peringatan + pesan error inline di bawah

### 5.3 Card (`.card`)
- **Background:** `--color-surface`
- **Border-radius:** `--radius-md` (10px)
- **Shadow:** `--shadow-sm`
- **Padding:** `--space-xl` (32px)

### 5.4 Alert / Flash Message (`.alert`)
```
Variant        | Border-left Color | Background         | Icon
──────────────┼───────────────────┼────────────────────┼──────
.alert-success | --color-success   | --color-success-bg | ✓ Check
.alert-error   | --color-danger    | --color-danger-bg  | ✕ X-circle
.alert-warning | --color-warning   | --color-warning-bg | ⚠ Alert
.alert-info    | --color-info      | --color-info-bg    | ℹ Info
```
- **Dismissible:** Tombol × di kanan atas
- **Auto-dismiss:** 5 detik untuk pesan sukses/info

### 5.5 Badge / Status Pill (`.badge`)
```
Status     | Background       | Text Color
───────────┼──────────────────┼───────────
Draft      | #F3F4F6 (Abu)    | #374151
Review     | #FEF3C7 (Kuning) | #92400E
Approved   | #D1FAE5 (Hijau)  | #065F46
Rejected   | #FEE2E2 (Merah)  | #991B1B
```
- **Border-radius:** 999px (pill shape)
- **Padding:** 4px 12px
- **Font-size:** `--font-size-sm`

### 5.6 File Upload Area (`.file-upload-area`)
- **Style:** Dashed border, background `--color-surface-alt`
- **States:** Default → Drag-over (border solid biru) → Has-file (border hijau + nama file)
- **Interaction:** Click to browse + Drag & drop

### 5.7 Loading Overlay (`.loading-overlay`)
- **Backdrop:** `rgba(0, 0, 0, 0.5)`, blur 2px
- **Card:** Centered, max-width 480px
- **Spinner:** CSS animation (rotate 360°), warna `--color-primary`
- **Step indicator:** Numbered list, step aktif mendapat highlight

### 5.8 Empty State
- **Ilustrasi:** SVG sederhana (opsional)
- **Heading:** "Belum ada data"
- **Deskripsi:** Teks penjelasan + CTA button
- **Contoh:** "Belum ada dokumen. [Buat RKS Pertama →]"

### 5.9 Data Table (`.data-table`)
- **Header:** Sticky, background `--color-surface-alt`, font-weight 600
- **Rows:** Zebra-striping (`:nth-child(even)` dengan background `--color-surface-alt`)
- **Hover:** Baris highlight dengan background lebih gelap
- **Responsive:** Horizontal scroll pada layar kecil

---

## 6. UX FEEDBACK & MICRO-INTERACTIONS

### 6.1 Toast Notification
- **Posisi:** Bottom-right, stack ke atas jika multiple
- **Duration:** Success/Info = 3 detik, Warning = 5 detik, Error = manual dismiss
- **Animasi:** Slide-in dari kanan + fade-out

### 6.2 Form Validation
- **Timing:** Inline, langsung setelah field kehilangan fokus (onblur)
- **Visual:** Ikon ⚠ + teks merah di bawah field (`--color-danger`)
- **Jangan:** Jangan gunakan pop-up/modal untuk validasi error

### 6.3 Konfirmasi Aksi Destruktif
- **Kapan:** Sebelum menghapus dokumen, menghapus file knowledge base
- **Implementasi:** Modal dialog sederhana ("Apakah Anda yakin?") dengan 2 tombol: Cancel (outline) + Confirm (danger)

### 6.4 Loading States
- **Data fetch:** Skeleton loader (kotak abu-abu animasi pulse)
- **Submit form:** Loading overlay full-screen dengan stepper
- **Button:** Spinner inline menggantikan teks button

---

## 7. RESPONSIVE BREAKPOINTS

```css
/* Mobile first — jarang dipakai karena target user desktop */
@media (max-width: 768px)  { /* Tablet: sidebar collapse, form full-width */ }
@media (max-width: 480px)  { /* Mobile: nav menjadi hamburger menu */ }
```

> **Catatan:** Target utama adalah **desktop browser** (Chrome/Edge). Responsive mobile adalah bonus, bukan prioritas.

---

## 8. EXECUTION PLAN — Fase Implementasi

### FASE 1 — ✅ SELESAI
> Scaffold Layout, CSS Design Token System, Halaman Buat RKS, Riwayat, Audit, Knowledge Base

Semua sudah diimplementasikan dan berjalan di Docker.

### FASE 2 — 🔴 BERIKUTNYA
> Halaman Buat Dokumen Tender + Navigasi Baru

- [ ] Buat `TenderController.php` (controller)
- [ ] Buat `tender/form.blade.php` (view)
- [ ] Tambah route `GET /tender` dan `POST /generate-tender` di `web.php`
- [ ] Tambah menu "Buat Tender" di `layouts/app.blade.php`
- [ ] Tambah menu "Knowledge Base" di `layouts/app.blade.php`
- [ ] Update `DapurApiService.php` untuk memanggil `/api/generate-tender`

### FASE 3 — POLISH & ENHANCEMENT
> Refinement interaksi dan kualitas

- [ ] Toast notification system (Alpine.js)
- [ ] Inline form validation (onblur)
- [ ] Skeleton loaders pada halaman Riwayat & Audit
- [ ] Empty state illustrations
- [ ] Dark mode toggle (opsional)
- [ ] Animasi transisi halaman (subtle)

### FASE 4 — ADVANCED (Opsional)
> Fitur tambahan jika waktu tersedia

- [ ] Dashboard dengan metrics card (Total Drafts, Selesai, Gagal)
- [ ] Search & filter pada tabel Riwayat
- [ ] Export riwayat ke CSV
- [ ] Auto-save draft form (localStorage)

---

## 9. FILE MAP — Lokasi Implementasi

```
wadah-web/
├── public/css/
│   └── app.css                    ← Design tokens + seluruh styling
├── resources/views/
│   ├── layouts/
│   │   └── app.blade.php          ← Global layout (navbar, footer)
│   ├── auth/
│   │   └── login.blade.php        ← Halaman login
│   ├── rks/
│   │   ├── form.blade.php         ← Form Generate RKS ✅
│   │   └── history.blade.php      ← Riwayat Generasi ✅
│   ├── tender/
│   │   └── form.blade.php         ← Form Generate Tender 🔴 BELUM
│   ├── knowledge/
│   │   └── index.blade.php        ← Knowledge Base ✅
│   └── audit/
│       └── index.blade.php        ← Audit Trail ✅
├── app/Http/Controllers/
│   ├── RksController.php          ← ✅
│   ├── TenderController.php       ← 🔴 BELUM
│   ├── KnowledgeController.php    ← ✅
│   └── AuditController.php        ← ✅
├── app/Services/
│   └── DapurApiService.php        ← HTTP client ke Dapur AI ✅
└── routes/
    └── web.php                    ← Route definitions ✅
```