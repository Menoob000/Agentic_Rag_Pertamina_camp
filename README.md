# ITec-Ai (AI-Powered RKS Tender Document Generator)

![ITec-Ai Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Laravel](https://img.shields.io/badge/Laravel-11.x-FF2D20?style=flat&logo=laravel)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker)

**ITec-Ai** adalah sebuah sistem pintar berbasis *Artificial Intelligence* (AI) yang dirancang untuk mengotomatiskan pembuatan dokumen **RKS (Rencana Kerja dan Syarat-syarat) Tender** dan spesifikasi teknis berdasarkan input berupa dokumen Bill of Quantities (BOQ) berformat PDF. 

Sistem ini membantu perusahaan dan konsultan teknik untuk mempercepat penyusunan dokumen tender yang sebelumnya memakan waktu berhari-hari menjadi hanya dalam hitungan menit, dengan tingkat akurasi dan standar industri yang tinggi berkat dukungan Large Language Models (LLM).

---

## 🎯 Tujuan Proyek

1. **Efisiensi Waktu**: Mengurangi waktu pembuatan draft dokumen RKS secara signifikan.
2. **Standardisasi Output**: Menjaga kualitas dan format dokumen teknis (.docx) yang konsisten dan siap pakai.
3. **Pengalaman Pengguna yang Cepat (Asynchronous)**: Mencegah *bottleneck* atau *timeout* pada aplikasi web saat AI sedang berpikir dengan menggunakan arsitektur pemrosesan di latar belakang (*background jobs*).
4. **Terdekopel (Decoupled)**: Memisahkan beban kerja antarmuka web (UI) dan mesin kecerdasan buatan (AI) agar sistem lebih *scalable* (mudah diperbesar skalanya) dan *maintainable* (mudah dikelola).

---

## 🛠️ Tech Stack & Tools yang Dipakai

Proyek ini dibangun menggunakan arsitektur *microservices* modern yang dipisahkan dalam *container* Docker:

### 1. Zona Wadah (Web Application)
*Bertugas menangani antarmuka pengguna, manajemen data, dan alur kerja (workflow).*
- **Framework**: Laravel 11 (PHP 8.2)
- **Frontend**: Blade Templating, Alpine.js (opsional untuk interaktivitas), Vanilla CSS / Tailwind.
- **Web Server**: Nginx & PHP-FPM
- **Queue System**: Database Queue (Laravel Jobs)

### 2. Zona Dapur (AI Engine / Backend Microservice)
*Bertugas sebagai "otak" sistem yang membaca PDF, berinteraksi dengan LLM, dan menulis dokumen `.docx`.*
- **Framework**: Python FastAPI
- **AI/LLM Tools**: LangChain, OpenRouter API (Qwen, GPT-4, dll), `sentence-transformers` (untuk *embedding*).
- **Vector Database**: Qdrant (Disiapkan untuk Fase 2 / RAG System).

### 3. Infrastruktur & Database
- **Database Utama**: PostgreSQL 16 (Relasional Database)
- **Orkestrasi**: Docker & Docker Compose
- **Penyimpanan (Storage)**: Docker Volumes (Lokal)

---

## 🏗️ Arsitektur Sistem

Sistem terdiri dari **4 Layanan (Services)** utama yang saling berkomunikasi secara internal melalui jaringan Docker (`itec-rks-network`):

1. **`web-app` (Wadah)**: Menerima *request* HTTP dari pengguna, memvalidasi form tender, dan meneruskannya ke antrean (*queue*).
2. **`queue-worker`**: Mengambil pekerjaan dari tabel antrean database dan melakukan panggilan API *HTTP Request* yang memakan waktu lama ke layanan AI di latar belakang.
3. **`dapur-ai` (Mesin AI)**: Menerima *request* dari *queue worker*, membaca isi PDF, mengirim *prompt* ke LLM eksternal, memformat hasilnya menjadi *file* `.docx`, lalu merespons dengan URL *file* tersebut.
4. **`db` (PostgreSQL)**: Menyimpan kredensial pengguna, riwayat dokumen, dan manajemen status *queue/jobs*.

---

## ⚙️ Persyaratan Sistem (Prerequisites)

Sebelum menjalankan proyek ini, pastikan mesin Anda telah menginstal:
- [Docker](https://www.docker.com/products/docker-desktop/) (Desktop / Engine)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

---

## 🚀 Instalasi & Konfigurasi

### 1. Clone Repositori (Jika belum)
```bash
git clone <url-repositori-anda>
cd ITec-Ai
```

### 2. Konfigurasi Environment (`.env`)
Salin file konfigurasi bawaan (jika belum ada) dan sesuaikan nilainya.
```bash
cp .env.example .env
```
Buka `.env` dan pastikan Anda mengatur kredensial penting, terutama **API Key untuk AI**:
```env
# Kredensial Database
DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE=itec_rks
DB_USERNAME=itec_admin
DB_PASSWORD=password_database_anda

# Konfigurasi AI (Zona Dapur)
OPENROUTER_API_KEY=sk-or-v1-kunci-api-anda-di-sini
LLM_MODEL_NAME=qwen/qwen3.7-flash
DAPUR_AI_URL=http://dapur-ai:8000
```

### 3. Jalankan Aplikasi dengan Docker
Sistem sudah dirancang agar dapat di-*build* dan dijalankan hanya dengan satu perintah:
```bash
docker-compose up -d --build
```
*(Proses ini akan mengunduh image sistem operasi, dependensi Python, library AI, dan mengatur volume penyimpanan. Mungkin membutuhkan waktu yang lumayan pada build pertama.)*

### 4. Menyiapkan Database Laravel (Migrasi)
Setelah semua *container* berstatus `Up` / `Healthy`, jalankan migrasi tabel ke dalam PostgreSQL:
```bash
docker exec -it itec-wadah php artisan migrate --seed
```
*(Opsi `--seed` akan membuatkan akun default `admin@itec.ai` dengan sandi `password`).*

---

## 🌐 Akses Penggunaan (Usage)

Setelah instalasi selesai, layanan dapat diakses pada:

- **Web Dashboard (User)**: [http://localhost](http://localhost) (atau [http://localhost:80](http://localhost:80))
- **Dokumentasi API AI (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Alur Singkat:
1. Login menggunakan akun yang terdaftar.
2. Navigasi ke menu **"Buat Tender Baru"**.
3. Isi informasi pekerjaan (Jenis, Detail, Lokasi) dan *upload* dokumen dasar (PDF BOQ).
4. Tekan **"Generate Dokumen"**.
5. Anda akan dialihkan ke halaman **Riwayat**. Status akan menunjukkan *"Processing"* dengan ikon berputar.
6. Tunggu beberapa saat (AI sedang bekerja di belakang layar). Segarkan halaman (atau tunggu update) dan status akan berubah menjadi *"Completed"*.
7. Tekan **"Download RKS (.docx)"** untuk mendapatkan hasilnya.

---

## 🛠️ Perintah Pemeliharaan (Maintenance Commands)

Bagi pengembang yang perlu melakukan perbaikan kode atau mengecek status sistem (*Troubleshooting*):

- **Melihat Status Service**: `docker-compose ps`
- **Melihat Log Mesin AI**: `docker-compose logs -f dapur-ai`
- **Melihat Log Queue Worker (Penting untuk cek progres AI)**: `docker-compose logs -f queue-worker`
- **Merestart Queue Worker (setelah ganti kode Job di Laravel)**: `docker-compose restart queue-worker`
- **Mematikan Sistem**: `docker-compose down`

---

## 📜 Lisensi
Dikembangkan untuk kebutuhan internal proyek.
