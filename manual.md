# ITec-Ai - Manual Penggunaan & Panduan Arsitektur

Selamat datang di proyek **ITec-Ai**! Sistem AI Pembuat Dokumen RKS Tender Terdekopel ini dibangun dengan arsitektur *microservices* berbasis Docker dan sistem pemrosesan latar belakang (*Asynchronous Queue*).

Dokumen ini memandu Anda (dan tim pengembang) mengenai struktur sistem, tata cara menjalankan, konfigurasi API AI, serta pemeliharaan aplikasi.

---

## 🏗️ Arsitektur & Struktur Proyek

Proyek ini terdiri dari **4 Layanan Utama (Services)** yang berjalan di dalam jaringan Docker internal (`itec-rks-network`):

1. **ZONA WADAH (`web-app` / `itec-wadah`)**:
   - Framework: Laravel 11 (PHP 8.2 + Nginx)
   - Akses: [http://localhost](http://localhost) (Port `80`)
   - Peran: Antarmuka pengguna (UI/UX), manajemen user, riwayat dokumen, dan penerima input form tender.
2. **QUEUE WORKER (`queue-worker` / `itec-queue-worker`)**:
   - Service: Worker Latar Belakang Laravel (`php artisan queue:work`)
   - Peran: Mengisi permintaan pemrosesan AI secara asinkron dari *queue* database agar web utama tetap kencang dan tidak mengalami *504 Timeout*.
3. **ZONA DAPUR (`dapur-ai` / `itec-dapur`)**:
   - Framework: Python FastAPI + LangChain / AI Agent
   - Akses API: [http://localhost:8000](http://localhost:8000) (Port `8000`)
   - Peran: Mesin pemrosesan AI (membaca BOQ PDF, interaksi LLM, dan *generate* dokumen `.docx`).
4. **DATABASE (`db` / `itec-db`)**:
   - Engine: PostgreSQL 16
   - Port Internal: `5432`
   - Peran: Menyimpan data pengguna, *audit log*, tabel `jobs` (queue), dan riwayat dokumen.

---

## ⚡ Alur Pemrosesan Dokumen (Asynchronous Flow)

1. **User mengisi Form Tender** di Zona Wadah (`web-app`).
2. Server menerima input dan **langsung mengembalikan respon dalam < 0.1 detik** ke pengguna (User langsung di-redirect ke halaman Riwayat).
3. Permintaan pembuatan dokumen dimasukkan ke dalam daftar antrean database (*Jobs*).
4. **`queue-worker`** secara otomatis mengambil antrean tersebut di latar belakang, memanggil API `dapur-ai` (`POST /api/generate-tender`), lalu mengunduh & menyimpan hasil `.docx` ke penyimpanan lokal.
5. Pengguna dapat memantau status *(Processing / Completed)* dan **mengunduh dokumen langsung dari halaman Riwayat**.

---

## 🔑 Konfigurasi Kredensial & API Mesin AI

Semua variabel lingkungan penting dikelola melalui file **`.env`** di root folder proyek.

### 1. Pengaturan Kredensial AI (`dapur-ai`)
Jika Anda perlu mengganti API Key LLM (OpenRouter), nama model, atau konfigurasi Vector DB:

Buka file `.env` di root proyek dan ubah variabel berikut:
```env
# Kredensial API AI (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
LLM_MODEL_NAME=qwen/qwen3.7-flash

# Konfigurasi Vector Database (Opsional / Qdrant)
QDRANT_CLUSTER_ENDPOINT=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
```

### 2. Pengaturan Koneksi Antar Kontainer
Secara default, `web-app` dan `queue-worker` terhubung ke `dapur-ai` melalui jaringan internal Docker:
```env
DAPUR_AI_URL=http://dapur-ai:8000
DAPUR_AI_TIMEOUT=300
QUEUE_CONNECTION=database
```

> **Catatan:** Setelah mengubah isi `.env`, selalu jalankan `docker-compose up -d` untuk menerapkan perubahan pada kontainer.

---

## 🚀 Menjalankan & Mengelola Proyek

### 1. Menjalankan Semua Layanan
Navigasikan ke folder utama proyek `ITec-Ai`, lalu jalankan:
```bash
docker-compose up -d
```
*Perintah ini akan menyalakan `web-app`, `queue-worker`, `dapur-ai`, dan `db` sekaligus di latar belakang.*

### 2. Jalankan Migrasi Database (Jika Pertama Kali / Reset)
```bash
docker exec -it itec-wadah php artisan migrate --seed
```

### 3. Kredensial Login Default (Web App)
- **URL**: [http://localhost](http://localhost)
- **Email**: `admin@itec.ai`
- **Password**: `password`

---

## 🛠️ Perintah Pemeliharaan (Maintenance)

### Memeriksa Status Kontainer
```bash
docker-compose ps
```

### Memeriksa Log Aplikasi Realtime
```bash
# Melihat log semua layanan
docker-compose logs -f

# Melihat aktivitas Queue Worker (Proses background AI)
docker-compose logs -f queue-worker

# Melihat log Mesin AI (FastAPI / LLM)
docker-compose logs -f dapur-ai

# Melihat log Web Laravel
docker-compose logs -f web-app
```

### Restart Queue Worker (Wajib dilakukan jika ada perubahan kode Laravel Job)
```bash
docker-compose restart queue-worker
```

### Menghentikan Sistem
```bash
# Mematikan kontainer tanpa menghapus data
docker-compose stop

# Mematikan dan menghapus kontainer (Data volume tetap aman)
docker-compose down
```

---

## 📂 Lokasi File Penting untuk Pengembang

- **Integrasi API AI di Laravel**: [`wadah-web/app/Services/DapurApiService.php`](file:///d:/Backup/Kuliah/Sems%207%2026%20-%2027/pertaminav2/ITec-Ai/wadah-web/app/Services/DapurApiService.php)
- **Background Job Generator**: [`wadah-web/app/Jobs/ProcessTenderGeneration.php`](file:///d:/Backup/Kuliah/Sems%207%2026%20-%2027/pertaminav2/ITec-Ai/wadah-web/app/Jobs/ProcessTenderGeneration.php)
- **FastAPI Endpoint (Dapur AI)**: [`dapur-ai/api.py`](file:///d:/Backup/Kuliah/Sems%207%2026%20-%2027/pertaminav2/ITec-Ai/dapur-ai/api.py)
- **Orkestrasi Docker**: [`docker-compose.yml`](file:///d:/Backup/Kuliah/Sems%207%2026%20-%2027/pertaminav2/ITec-Ai/docker-compose.yml)

---
*Manual ini telah diperbarui untuk mendukung arsitektur Asynchronous Queue Worker & Microservices ITec-Ai.*

## Kredensial
Silakan masuk menggunakan kredensial berikut:

Alamat Email: admin@itec.ai
Kata Sandi: password