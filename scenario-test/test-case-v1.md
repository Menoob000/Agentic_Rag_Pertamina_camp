# Scenario Test Case - ITec-Ai RKS & Tender System
**Version:** v1.0
**Date:** 2026-10-08

## 1. Modul Autentikasi (Authentication)

| Test Case ID | Skenario Pengujian | Langkah-Langkah (Steps) | Hasil yang Diharapkan (Expected Result) | Status (Pass/Fail) |
|---|---|---|---|---|
| TC-AUTH-01 | Login dengan kredensial valid | 1. Buka halaman `/login`<br>2. Masukkan username dan password valid<br>3. Klik tombol Login | Pengguna berhasil masuk dan diarahkan ke Dashboard/Form RKS (`/`) | |
| TC-AUTH-02 | Login dengan kredensial tidak valid | 1. Buka halaman `/login`<br>2. Masukkan password salah<br>3. Klik tombol Login | Muncul pesan error "Kredensial tidak valid" dan pengguna tetap di halaman login | |
| TC-AUTH-03 | Logout dari sistem | 1. Klik tombol Logout di navigasi | Sesi berakhir dan pengguna diarahkan kembali ke halaman `/login` | |

## 2. Modul Knowledge Base (RAG Ingestion)

| Test Case ID | Skenario Pengujian | Langkah-Langkah (Steps) | Hasil yang Diharapkan (Expected Result) | Status (Pass/Fail) |
|---|---|---|---|---|
| TC-KB-01 | Upload file PDF referensi valid | 1. Buka halaman `/knowledge`<br>2. Pilih file PDF referensi (contoh RKS.pdf)<br>3. Klik Upload | Notifikasi sukses. Background task berjalan untuk ingest ke Qdrant | |
| TC-KB-02 | Upload file non-PDF | 1. Buka halaman `/knowledge`<br>2. Pilih file .docx atau .txt<br>3. Klik Upload | Sistem menolak dengan pesan error "Hanya file PDF yang diizinkan" | |
| TC-KB-03 | Mengecek integrasi API Ingest | 1. Melakukan upload PDF<br>2. Periksa log API `/api/ingest-pdf` di terminal `dapur-ai` | API menerima request dengan status 200 dan memulai Background Task | |

## 3. Modul Pembuatan RKS (RKS Generation)

| Test Case ID | Skenario Pengujian | Langkah-Langkah (Steps) | Hasil yang Diharapkan (Expected Result) | Status (Pass/Fail) |
|---|---|---|---|---|
| TC-RKS-01 | Generate RKS dengan parameter lengkap | 1. Buka form RKS (`/`)<br>2. Isi parameter pengadaan dan upload dokumen BOQ/pendukung<br>3. Klik Generate | Sistem memproses (loading), memanggil API `dapur-ai`, dan mengunduh RKS `.docx` | |
| TC-RKS-02 | Generate RKS tanpa dokumen wajib | 1. Buka form RKS (`/`)<br>2. Kosongkan dokumen wajib<br>3. Klik Generate | Validasi form mencegah submit, muncul peringatan wajib isi | |
| TC-RKS-03 | Penanganan Timeout dari AI | 1. Request Generate RKS<br>2. Simulasikan respon AI > 300 detik | Web tidak *crash*, menampilkan pesan error koneksi timeout ke pengguna dengan baik | |

## 4. Modul Pembuatan Dokumen Tender (Tender Generation)

| Test Case ID | Skenario Pengujian | Langkah-Langkah (Steps) | Hasil yang Diharapkan (Expected Result) | Status (Pass/Fail) |
|---|---|---|---|---|
| TC-TND-01 | Generate Dokumen Tender dengan RKS valid | 1. Buka form Tender (`/tender`)<br>2. Upload RKS (.docx) yang valid<br>3. Klik Generate | Sistem mengekstrak metadata dari RKS dan menghasilkan dokumen Tender `.docx` | |
| TC-TND-02 | Generate Dokumen Tender dengan file non-RKS | 1. Buka form Tender (`/tender`)<br>2. Upload file docx sembarangan<br>3. Klik Generate | AI gagal mengekstrak metadata RKS, muncul error gagal generate tender | |

## 5. Modul Riwayat & Audit Log

| Test Case ID | Skenario Pengujian | Langkah-Langkah (Steps) | Hasil yang Diharapkan (Expected Result) | Status (Pass/Fail) |
|---|---|---|---|---|
| TC-AUD-01 | Melihat riwayat pembuatan dokumen | 1. Masuk ke halaman `/riwayat` | Daftar dokumen RKS dan Tender yang pernah digenerate tampil sesuai user | |
| TC-AUD-02 | Mengakses Audit Trail | 1. Masuk ke halaman `/audit` | Muncul tabel log aktivitas sistem (waktu, user, aksi, dan IP) | |
| TC-AUD-03 | Batasan Hak Akses Audit | 1. Login sebagai Staff biasa (jika ada)<br>2. Akses `/audit` | Ditolak oleh sistem dengan halaman 403 Forbidden (jika role diterapkan) | |
