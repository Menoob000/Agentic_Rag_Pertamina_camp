import streamlit as st
import requests
import os

# FastAPI Backend URLs
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_RKS_URL = f"{BASE_URL}/api/generate-rks"
API_TENDER_URL = f"{BASE_URL}/api/generate-tender"

st.set_page_config(
    page_title="Pertamina Procurement AI System",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────
# Sidebar Navigation (Navbar)
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo_pertamina.png" if os.path.exists("assets/logo_pertamina.png") else "", use_container_width=True)
    st.title("Pertamina AI System")
    st.caption("Automated Procurement Document Generator")
    st.divider()

    st.subheader("📌 Navigasi Dokumen")
    doc_type = st.radio(
        "Pilih Jenis Dokumen yang Ingin Dibuat:",
        options=[
            "📋 Dokumen RKS",
            "📄 Dokumen Tender (IKPP & Kontrak)"
        ],
        index=1,
        help="Pilih antara pembuatan Dokumen RKS teknis atau Paket Dokumen Tender lengkap (IKPP + Rancangan Kontrak)."
    )

    st.divider()
    st.info(
        "💡 **Panduan Cepat:**\n\n"
        "• **RKS:** Menyusun Rencana Kerja & Syarat teknis.\n"
        "• **Dokumen Tender:** Menyusun paket tender resmi (IKPP Bab I-II, Lampiran 1A-8, dan Bagian B Rancangan Kontrak)."
    )


# ──────────────────────────────────────────────────────────────
# MODE 1: DOKUMEN RKS
# ──────────────────────────────────────────────────────────────
if doc_type == "📋 Dokumen RKS":
    st.title("📋 Pertamina RKS Generator")
    st.write(
        "Isi parameter pekerjaan dan unggah dokumen referensi (seperti BoQ / Spesifikasi Teknis) "
        "untuk menyusun draft RKS secara otomatis menggunakan LLM dan RAG Vector Store."
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Informasi Pekerjaan")
        rks_jenis = st.text_input("Judul Pekerjaan", placeholder="Contoh: Pembangunan Fasilitas Perpipaan...")
        rks_detail = st.text_area("Detail Pekerjaan / Lingkup", placeholder="Penjelasan singkat ruang lingkup pekerjaan...", height=120)
        rks_lokasi = st.text_input("Lokasi Pekerjaan", placeholder="Contoh: Fuel Terminal Balikpapan")

    with col2:
        st.subheader("🏢 Metadata Dokumen")
        rks_csms = st.selectbox("Risiko CSMS", options=["HIGH", "MIDDLE", "LOW"], index=0)
        rks_nomor = st.text_input("Nomor Dokumen", value="RKS-[KODE]-[TAHUN]")
        rks_perusahaan = st.text_input("Nama Perusahaan", value="PT PERTAMINA (PERSERO)")

        st.subheader("📎 Dokumen Referensi")
        rks_file = st.file_uploader("Unggah BoQ / Dokumen Acuan (PDF)", type=["pdf"], key="rks_uploader")
        st.caption("File PDF ini akan diekstrak menggunakan Docling dan diringkas oleh AI.")

    st.markdown("---")
    if st.button("🚀 Generate Dokumen RKS", type="primary", use_container_width=True):
        if not rks_jenis or not rks_detail or not rks_file:
            st.warning("⚠️ Mohon lengkapi Judul Pekerjaan, Detail Pekerjaan, dan unggah file PDF.")
        else:
            with st.spinner("⏳ Sedang memproses dokumen dan menyusun RKS dengan AI... (Mohon tunggu)"):
                files = {
                    "file": (rks_file.name, rks_file.getvalue(), "application/pdf")
                }
                data = {
                    "jenis_pekerjaan": rks_jenis,
                    "detail_pekerjaan": rks_detail,
                    "lokasi": rks_lokasi,
                    "resiko_csms": rks_csms,
                    "nomor_dokumen": rks_nomor,
                    "nama_perusahaan": rks_perusahaan
                }
                try:
                    res = requests.post(API_RKS_URL, data=data, files=files, timeout=600)
                    if res.status_code == 200:
                        st.success("✅ Dokumen RKS berhasil dibuat!")
                        filename = f"RKS_{rks_jenis.replace(' ', '_')}.docx"
                        cd = res.headers.get('content-disposition')
                        if cd and 'filename=' in cd:
                            filename = cd.split('filename=')[1].strip('"\'')

                        st.download_button(
                            label="📥 Unduh Dokumen RKS (.docx)",
                            data=res.content,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Terjadi kesalahan pada server (Status: {res.status_code})")
                        try:
                            st.json(res.json())
                        except Exception:
                            st.text(res.text)
                except requests.exceptions.RequestException as e:
                    st.error("❌ Gagal terhubung ke API backend.")
                    st.info("Pastikan server FastAPI sudah berjalan: `uv run uvicorn api:app --reload`")
                    st.caption(f"Error detail: {e}")


# ──────────────────────────────────────────────────────────────
# MODE 2: DOKUMEN TENDER (IKPP & KONTRAK)
# ──────────────────────────────────────────────────────────────
else:
    st.title("📄 Pertamina Dokumen Tender Generator")
    st.write(
        "Menghasilkan paket resmi **Dokumen Tender Pertamina Patra Niaga** (Versi 2.0) lengkap: "
        "**Bagian A** (IKPP Ketentuan Khusus 40 Poin, Bab II Ketentuan Umum, Lampiran 1 s.d. 8) "
        "dan **Bagian B** (Rancangan Kontrak Definitif, Pakta Integritas PI-07, Template SP3MK)."
    )
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 1. Informasi Tender & Pejabat",
        "💰 2. HPS/OE, CSMS & TKDN",
        "📅 3. Jadwal & Pelaksanaan",
        "📎 4. Dokumen Pendukung (Opsional)"
    ])

    with tab1:
        st.subheader("Data Pengadaan & Tender")
        t_nama = st.text_area(
            "Nama Pengadaan (Judul Lengkap)",
            value="PENGADAAN DAN PEMASANGAN PIPA TRANSMISI MINYAK DAN GAS REGIONAL KALIMANTAN",
            height=80,
            help="Judul pengadaan yang akan tertera di Cover Dokumen Tender, Bagian A, dan Bagian B."
        )

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_nomor = st.text_input("Nomor Dokumen Tender", value="No.Project/DT/PND970000/2026-S7")
            t_metode = st.selectbox(
                "Metode Pemenuhan Kebutuhan",
                options=["Tender Terbatas", "Tender Terbuka", "Pemilihan Langsung", "Penunjukan Langsung"],
                index=0
            )
        with col_t2:
            t_tanggal = st.text_input("Tanggal Dokumen Tender", value="04 Desember 2025")
            t_jenis_kontrak = st.selectbox(
                "Jenis Kontrak",
                options=["Gabungan Harga Satuan & Lumpsum", "Harga Satuan", "Harga Lumpsum"],
                index=0
            )

        st.subheader("Pejabat & Pengawas")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            t_proc_nama = st.text_input("Nama Pejabat Procurement", value="Rigga Widar Atmagi")
            t_proc_jabatan = st.text_input("Jabatan Pejabat Procurement", value="Area Manager Procurement Kalimantan")
        with col_p2:
            t_pejabat_wenang = st.text_input("Pejabat Berwenang", value="Sr. Manager Opt. & Maint. Regional Kalimantan")
            t_pengawas = st.text_input("Pengawas Pekerjaan / Direksi", value="Region Manager RPD Regional Kalimantan")

    with tab2:
        st.subheader("Harga Perkiraan Sendiri (HPS / OE)")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            t_prime_cost = st.number_input(
                "Total Nilai Prime Cost (Rp)",
                min_value=0.0,
                value=13283434534.0,
                step=1000000.0,
                format="%.2f"
            )
            st.caption(f"Prime Cost: Rp {int(t_prime_cost):,}".replace(",", "."))
        with col_h2:
            t_total_kr = st.number_input(
                "Total Nilai HPS Termasuk Keuntungan & Risiko (Rp)",
                min_value=0.0,
                value=14346100000.0,
                step=1000000.0,
                format="%.2f"
            )
            st.caption(f"Total (+K&R): Rp {int(t_total_kr):,}".replace(",", "."))

        st.divider()
        st.subheader("Aspek Kualifikasi & Kebijakan")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            t_csms = st.selectbox("Tingkat Risiko CSMS (HSSE)", options=["Tinggi", "Sedang", "Rendah"], index=0)
            st.caption("Menentukan ambang batas passing grade CSMS pada Lampiran 3A.")
        with col_q2:
            t_tkdn = st.number_input("Target Komitmen Minimal TKDN (%)", min_value=0.0, max_value=100.0, value=20.12, step=0.1)
            st.caption("Target pemenuhan TKDN yang wajib dipenuhi penyedia pada Form A3/A4/A5.")

    with tab3:
        st.subheader("Rapat Penjelasan (Pre-Bid Meeting)")
        col_pb1, col_pb2 = st.columns(2)
        with col_pb1:
            t_pb_tgl = st.text_input("Hari & Tanggal Pre-Bid", value="Senin, 08 Desember 2025")
            t_pb_waktu = st.text_input("Waktu Pre-Bid", value="10.00 WITA")
        with col_pb2:
            t_pb_tempat = st.text_input(
                "Tempat / Platform Pre-Bid",
                value="Microsoft Teams Meeting dengan link yang disampaikan melalui email Undangan Prebid Meeting"
            )

        st.divider()
        st.subheader("Pemasukan Dokumen Penawaran")
        col_pm1, col_pm2 = st.columns(2)
        with col_pm1:
            t_pm_mulai = st.text_input("Mulai Pemasukan Penawaran", value="Senin, 08 Desember 2025")
        with col_pm2:
            t_pm_selesai = st.text_input("Batas Akhir Pemasukan Penawaran", value="Senin, 15 Desember 2025")

    with tab4:
        st.subheader("Dokumen Konteks Tambahan")
        st.write(
            "Unggah dokumen RKS atau file BOQ (PDF) jika ada. LLM akan memanfaatkan konteks ini untuk "
            "menyusun kode KBUP/KBLI yang sangat akurat, kriteria teknis Lampiran 2A, dan ruang lingkup kontrak Bagian B."
        )
        t_file = st.file_uploader("Unggah RKS / BoQ (PDF) - Opsional", type=["pdf"], key="tender_uploader")
        if t_file:
            st.success(f"File terdeteksi: {t_file.name} ({len(t_file.getvalue()) / 1024:.1f} KB)")

    st.markdown("---")
    if st.button("🚀 Generate Paket Dokumen Tender Lengkap (.docx)", type="primary", use_container_width=True):
        if not t_nama:
            st.warning("⚠️ Mohon lengkapi Nama Pengadaan.")
        else:
            with st.spinner("⏳ AI sedang menyusun Dokumen Tender (IKPP 40 Poin, Lampiran 1-8 & Kontrak Bagian B)... Ini memerlukan waktu 1-2 menit."):
                form_payload = {
                    "nama_pengadaan": t_nama,
                    "nomor_tender": t_nomor,
                    "tanggal": t_tanggal,
                    "prime_cost": t_prime_cost,
                    "total_dengan_kr": t_total_kr,
                    "resiko_csms": t_csms,
                    "tkdn_minimal": t_tkdn,
                    "metode_pemenuhan": t_metode,
                    "jenis_kontrak": t_jenis_kontrak,
                    "pejabat_procurement_nama": t_proc_nama,
                    "pejabat_procurement_jabatan": t_proc_jabatan,
                    "pejabat_berwenang": t_pejabat_wenang,
                    "pengawas_pekerjaan": t_pengawas,
                    "prebid_tanggal": t_pb_tgl,
                    "prebid_waktu": t_pb_waktu,
                    "prebid_tempat": t_pb_tempat,
                    "pemasukan_mulai": t_pm_mulai,
                    "pemasukan_selesai": t_pm_selesai
                }

                files_payload = {}
                if t_file:
                    files_payload["file"] = (t_file.name, t_file.getvalue(), "application/pdf")

                try:
                    res = requests.post(
                        API_TENDER_URL,
                        data=form_payload,
                        files=files_payload if files_payload else None,
                        timeout=600
                    )

                    if res.status_code == 200:
                        st.success("✅ Paket Dokumen Tender berhasil dibuat lengkap!")

                        safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in t_nama)[:40].strip()
                        tender_filename = f"Dokumen_Tender_{safe_title}.docx"
                        cd = res.headers.get("content-disposition")
                        if cd and "filename=" in cd:
                            tender_filename = cd.split("filename=")[1].strip('"\'')

                        st.download_button(
                            label="📥 Unduh Dokumen Tender Lengkap (.docx)",
                            data=res.content,
                            file_name=tender_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Terjadi kesalahan pada server (Status: {res.status_code})")
                        try:
                            st.json(res.json())
                        except Exception:
                            st.text(res.text)
                except requests.exceptions.RequestException as e:
                    st.error("❌ Gagal terhubung ke API backend.")
                    st.info("Pastikan server FastAPI sudah berjalan: `uv run uvicorn api:app --reload`")
                    st.caption(f"Error detail: {e}")
