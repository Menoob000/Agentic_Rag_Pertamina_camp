import streamlit as st
import requests
import os
from datetime import datetime, date, timedelta

# FastAPI Backend URLs
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_KB_INGEST_URL = f"{BASE_URL}/api/kb/ingest"
API_KB_LIST_URL = f"{BASE_URL}/api/kb/list"
API_KB_DELETE_URL = f"{BASE_URL}/api/kb/delete"
API_KONTRAK_URL = f"{BASE_URL}/api/generate-kontrak"
API_AMENDEMEN_URL = f"{BASE_URL}/api/generate-amendemen"
API_EXTRACT_TENDER_URL= f"{BASE_URL}/api/extract-tender-metadata"
API_TENDER_URL = f"{BASE_URL}/api/generate-tender"
API_RKS_URL = f"{BASE_URL}/api/generate-rks"

INDONESIAN_MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
INDONESIAN_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

def format_id_date(d: date, with_day: bool = True) -> str:
    day_name = INDONESIAN_DAYS[d.weekday()]
    month_name = INDONESIAN_MONTHS[d.month - 1]
    if with_day:
        return f"{day_name}, {d.day:02d} {month_name} {d.year}"
    return f"{d.day:02d} {month_name} {d.year}"

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
            "📄 Dokumen Tender (IKPP & Kontrak)",
            "📝 Rancangan Kontrak Definitif",
            "📎 Draft Amendemen / Addendum",
            "🗄️ Knowledge Base",
        ],
        index=1,
        help="Pilih modul yang ingin digunakan."
    )

    st.divider()
    st.info(
        "💡 **Panduan Cepat:**\n\n"
        "• **RKS:** Menyusun Rencana Kerja & Syarat teknis.\n"
        "• **Dokumen Tender:** Menyusun paket tender resmi (IKPP Bab I-II, Lampiran 1A-8, dan Bagian B Rancangan Kontrak).\n"
        "• **Rancangan Kontrak:** Menyusun Kontrak mandiri yang komprehensif.\n"
        "• **Amendemen:** Menyusun Draft Addendum Kontrak yang sudah berjalan.\n"
        "• **Knowledge Base:** Upload & kelola dokumen referensi untuk RAG."
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
elif doc_type == "📄 Dokumen Tender (IKPP & Kontrak)":
    st.title("📄 Pertamina Dokumen Tender Generator")
    st.write(
        "Menghasilkan paket resmi **Dokumen Tender Pertamina Patra Niaga** (Versi 2.0) lengkap: "
        "**Bagian A** (IKPP Ketentuan Khusus 40 Poin, Bab II Ketentuan Umum, Lampiran 1 s.d. 8) "
        "dan **Bagian B** (Rancangan Kontrak Definitif, Pakta Integritas PI-07, Template SP3MK)."
    )
    st.markdown("---")

    # TAHAP 1: INPUT RINGKAS PENGGUNA
    st.subheader("🎯 Parameter Awal & Dokumen Pendukung")
    st.caption("Cukup tentukan tanggal dokumen, tingkat risiko CSMS, dan unggah dokumen pendukung (RKS & BOQ). AI akan memindai seluruh parameter pengadaan secara otomatis.")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        t_tgl_input = st.date_input(
            "📅 Tanggal Dokumen Tender",
            value=date.today(),
            help="Sistem otomatis memformat tanggal ke format resmi Bahasa Indonesia dan mengkalkulasi jadwal Pre-bid serta Pemasukan Penawaran."
        )
        t_tanggal_formatted = format_id_date(t_tgl_input, with_day=False)
        st.caption(f"Format Resmi: **{t_tanggal_formatted}**")

    with col_in2:
        t_csms = st.selectbox(
            "🛡️ Tingkat Risiko CSMS (HSSE)",
            options=["Tinggi", "Sedang", "Rendah"],
            index=0,
            help="Menentukan ambang batas passing grade CSMS pada Lampiran 3A Dokumen Tender."
        )

    st.markdown("##### 📎 Unggah Dokumen Pendukung (RKS & BOQ)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        t_rks_file = st.file_uploader(
            "📘 Dokumen RKS (PDF)",
            type=["pdf"],
            key="tender_rks_uploader",
            help="Dokumen RKS untuk ekstraksi nama pengadaan, lingkup pekerjaan, dan kriteria evaluasi teknis."
        )
    with col_f2:
        t_boq_file = st.file_uploader(
            "📊 Dokumen BOQ (PDF / Excel .xlsx)",
            type=["pdf", "xlsx", "xls"],
            key="tender_boq_uploader",
            help="Dokumen BOQ untuk ekstraksi HPS Prime Cost, Total HPS (+K&R), dan target TKDN."
        )

    col_btn_scan, col_btn_reset = st.columns([3, 1])
    with col_btn_scan:
        scan_clicked = st.button("🔍 Pindai & Ekstrak Data Dokumen Pendukung", type="primary", use_container_width=True)
    with col_btn_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.pop("tender_metadata", None)
            st.session_state.pop("tender_extracted", None)
            st.rerun()

    if scan_clicked:
        with st.spinner("⏳ Sedang memindai dokumen RKS & BOQ menggunakan LLM... (Mohon tunggu)"):
            files_payload = {}
            if t_rks_file:
                files_payload["file_rks"] = (t_rks_file.name, t_rks_file.getvalue(), "application/pdf")
            if t_boq_file:
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if t_boq_file.name.endswith(".xlsx") else "application/pdf"
                files_payload["file_boq"] = (t_boq_file.name, t_boq_file.getvalue(), mime_type)

            data_payload = {
                "tanggal": t_tanggal_formatted,
                "resiko_csms": t_csms
            }

            try:
                res = requests.post(API_EXTRACT_TENDER_URL, data=data_payload, files=files_payload if files_payload else None, timeout=300)
                if res.status_code == 200:
                    resp_json = res.json()
                    st.session_state["tender_metadata"] = resp_json.get("data", {})
                    st.session_state["tender_extracted"] = True
                    st.success("✅ Dokumen berhasil dipindai! Silakan periksa ringkasan di bawah.")
                else:
                    st.error(f"❌ Gagal memindai dokumen (Status: {res.status_code})")
                    try:
                        st.json(res.json())
                    except Exception:
                        st.text(res.text)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal terhubung ke API backend ({API_EXTRACT_TENDER_URL}).")
                st.info("Pastikan server FastAPI sudah berjalan: `uv run uvicorn api:app --reload`")
                st.caption(f"Error detail: {e}")

    # TAHAP 2: REVIEW RINGKASAN & GENERATE
    if st.session_state.get("tender_extracted") and st.session_state.get("tender_metadata"):
        st.markdown("---")
        meta = st.session_state["tender_metadata"]

        st.subheader("📋 Ringkasan Hasil Ekstraksi AI")
        st.info(f"📌 **Nama Pengadaan:** {meta.get('nama_pengadaan', '-')}")

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        prime_val = float(meta.get("prime_cost", 0))
        total_kr_val = float(meta.get("total_dengan_kr", 0))
        tkdn_val = float(meta.get("tkdn_minimal", 0))

        with c_m1:
            st.metric("Prime Cost (HPS Riil)", f"Rp {int(prime_val):,}".replace(",", "."))
        with c_m2:
            st.metric("Total HPS (+K&R)", f"Rp {int(total_kr_val):,}".replace(",", "."))
        with c_m3:
            st.metric("Target Min. TKDN", f"{tkdn_val:.2f}%")
        with c_m4:
            st.metric("Nomor Tender", meta.get("nomor_tender", "-"))

        # Expander untuk penyesuaian detail jika dibutuhkan
        with st.expander("✏️ Ubah / Sesuaikan Detail Tambahan (Pejabat, Jadwal, HPS, dll.)", expanded=False):
            st.caption("Semua field di bawah sudah terisi secara otomatis oleh AI dan default pintar. Ubah hanya jika diperlukan.")

            t_nama_val = st.text_area("Nama Pengadaan (Judul Lengkap)", value=meta.get("nama_pengadaan", ""), height=80)

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                t_nomor_val = st.text_input("Nomor Dokumen Tender", value=meta.get("nomor_tender", "No.Project/DT/PND970000/2026-S7"))
                t_metode_options = ["Tender Terbatas", "Tender Terbuka", "Pemilihan Langsung", "Penunjukan Langsung"]
                cur_metode = meta.get("metode_pemenuhan", "Tender Terbatas")
                idx_metode = t_metode_options.index(cur_metode) if cur_metode in t_metode_options else 0
                t_metode_val = st.selectbox("Metode Pemenuhan Kebutuhan", options=t_metode_options, index=idx_metode)
            with col_e2:
                t_tanggal_val = st.text_input("Tanggal Dokumen Tender", value=meta.get("tanggal", t_tanggal_formatted))
                t_kontrak_options = ["Gabungan Harga Satuan & Lumpsum", "Harga Satuan", "Harga Lumpsum"]
                cur_kontrak = meta.get("jenis_kontrak", "Gabungan Harga Satuan & Lumpsum")
                idx_kontrak = t_kontrak_options.index(cur_kontrak) if cur_kontrak in t_kontrak_options else 0
                t_kontrak_val = st.selectbox("Jenis Kontrak", options=t_kontrak_options, index=idx_kontrak)

            st.markdown("##### 🏢 Pejabat & Pengawas")
            col_ep1, col_ep2 = st.columns(2)
            with col_ep1:
                t_proc_nama_val = st.text_input("Nama Pejabat Procurement", value=meta.get("pejabat_procurement_nama", "Rigga Widar Atmagi"))
                t_proc_jabatan_val = st.text_input("Jabatan Pejabat Procurement", value=meta.get("pejabat_procurement_jabatan", "Area Manager Procurement Kalimantan"))
            with col_ep2:
                t_pejabat_wenang_val = st.text_input("Pejabat Berwenang", value=meta.get("pejabat_berwenang", "Sr. Manager Opt. & Maint. Regional Kalimantan"))
                t_pengawas_val = st.text_input("Pengawas Pekerjaan / Direksi", value=meta.get("pengawas_pekerjaan", "Region Manager RPD Regional Kalimantan"))

            st.markdown("##### 💰 Finansial & TKDN")
            col_eh1, col_eh2, col_eh3 = st.columns(3)
            with col_eh1:
                t_prime_cost_val = st.number_input("Total Prime Cost (Rp)", min_value=0.0, value=prime_val, step=1000000.0, format="%.2f")
            with col_eh2:
                t_total_kr_val = st.number_input("Total HPS (+K&R) (Rp)", min_value=0.0, value=total_kr_val, step=1000000.0, format="%.2f")
            with col_eh3:
                t_tkdn_val = st.number_input("Target TKDN Minimal (%)", min_value=0.0, max_value=100.0, value=tkdn_val, step=0.1)

            st.markdown("##### 📅 Jadwal Pelaksanaan")
            col_ej1, col_ej2 = st.columns(2)
            with col_ej1:
                t_pb_tgl_val = st.text_input("Hari & Tanggal Pre-Bid", value=meta.get("prebid_tanggal", ""))
                t_pb_waktu_val = st.text_input("Waktu Pre-Bid", value=meta.get("prebid_waktu", "10.00 WITA"))
                t_pb_tempat_val = st.text_input("Tempat / Platform Pre-Bid", value=meta.get("prebid_tempat", ""))
            with col_ej2:
                t_pm_mulai_val = st.text_input("Mulai Pemasukan Penawaran", value=meta.get("pemasukan_mulai", ""))
                t_pm_selesai_val = st.text_input("Batas Akhir Pemasukan Penawaran", value=meta.get("pemasukan_selesai", ""))

            st.markdown("##### 📝 Konteks Dokumen RKS / BOQ (Lingkup & Spesifikasi)")
            t_context_val = st.text_area("Ringkasan Konteks Ekstraksi AI", value=meta.get("context_summary", ""), height=100)

        st.markdown("")
        if st.button("🚀 Generate Paket Dokumen Tender Lengkap (.docx)", type="primary", use_container_width=True):
            if not t_nama_val:
                st.warning("⚠️ Mohon lengkapi Nama Pengadaan.")
            else:
                with st.spinner("⏳ AI sedang menyusun Dokumen Tender (IKPP 40 Poin, Lampiran 1-8 & Kontrak Bagian B)... Ini memerlukan waktu 1-2 menit."):
                    generate_payload = {
                        "nama_pengadaan": t_nama_val,
                        "nomor_tender": t_nomor_val,
                        "tanggal": t_tanggal_val,
                        "prime_cost": t_prime_cost_val,
                        "total_dengan_kr": t_total_kr_val,
                        "resiko_csms": meta.get("resiko_csms", t_csms),
                        "tkdn_minimal": t_tkdn_val,
                        "metode_pemenuhan": t_metode_val,
                        "jenis_kontrak": t_kontrak_val,
                        "pejabat_procurement_nama": t_proc_nama_val,
                        "pejabat_procurement_jabatan": t_proc_jabatan_val,
                        "pejabat_berwenang": t_pejabat_wenang_val,
                        "pengawas_pekerjaan": t_pengawas_val,
                        "prebid_tanggal": t_pb_tgl_val,
                        "prebid_waktu": t_pb_waktu_val,
                        "prebid_tempat": t_pb_tempat_val,
                        "pemasukan_mulai": t_pm_mulai_val,
                        "pemasukan_selesai": t_pm_selesai_val,
                        "context_summary": t_context_val
                    }

                    try:
                        res = requests.post(
                            API_TENDER_URL,
                            data=generate_payload,
                            timeout=600
                        )

                        if res.status_code == 200:
                            st.success("✅ Paket Dokumen Tender berhasil dibuat lengkap!")
                            safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in t_nama_val)[:40].strip()
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
                        st.error(f"❌ Gagal terhubung ke API backend ({API_TENDER_URL}).")
                        st.info("Pastikan server FastAPI sudah berjalan: `uv run uvicorn api:app --reload`")
                        st.caption(f"Error detail: {e}")


# ──────────────────────────────────────────────────────────────
# MODE 3: RANCANGAN KONTRAK DEFINITIF
# ──────────────────────────────────────────────────────────────
elif doc_type == "📝 Rancangan Kontrak Definitif":
    st.title("📝 Generator Rancangan Kontrak")
    st.write("Isi formulir di bawah untuk men-generate Rancangan Kontrak (20 Pasal) secara otomatis.")
    
    with st.form("form_kontrak"):
        col1, col2 = st.columns(2)
        with col1:
            nama_pekerjaan = st.text_input("Judul Pekerjaan*", placeholder="Contoh: Pengadaan Material X")
            nomor_kontrak = st.text_input("Nomor Kontrak*", value="KTR-001/PND/2026")
            tanggal_kontrak = st.text_input("Tanggal Kontrak*", value="01 Januari 2026")
            lokasi_pekerjaan = st.text_input("Lokasi Pekerjaan*", placeholder="Contoh: Balikpapan")
            jenis_kontrak = st.selectbox("Jenis Kontrak*", ["Gabungan Harga Satuan & Lumpsum", "Lumpsum", "Harga Satuan", "Terima Jadi (Turnkey)"])
            
        with col2:
            nama_vendor = st.text_input("Nama Penyedia (Vendor)*", placeholder="PT Nama Vendor")
            npwp_vendor = st.text_input("NPWP Vendor*", placeholder="00.000.000.0-000.000")
            nilai_kontrak = st.text_input("Nilai Kontrak (Rp)*", value="1000000000", help="Hanya angka")
            sistem_pembayaran = st.selectbox("Sistem Pembayaran*", ["Monthly Progress", "Milestone", "Termin", "Sekaligus (Lumpsum)"])
            
        col3, col4 = st.columns(2)
        with col3:
            durasi_hari = st.number_input("Durasi Pekerjaan (Hari)*", min_value=1, value=180)
            masa_pemeliharaan = st.number_input("Masa Pemeliharaan (Hari)*", min_value=0, value=90)
            resiko_csms = st.selectbox("Risiko CSMS*", ["Tinggi", "Sedang", "Rendah"])
        
        with col4:
            pejabat_ttd = st.text_input("Jabatan Penandatangan Pertamina*", value="Executive General Manager")
            file_upload = st.file_uploader("Upload PDF (RKS/BOQ) untuk Konteks Lingkup (Opsional)", type=["pdf"])

        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate Rancangan Kontrak (.docx)", use_container_width=True)

    if submitted:
        if not nama_pekerjaan or not nomor_kontrak or not nama_vendor or not nilai_kontrak:
            st.warning("⚠️ Mohon lengkapi field yang bertanda bintang (*).")
        else:
            with st.spinner("⏳ Men-generate Rancangan Kontrak (Estimasi 1-2 Menit)..."):
                try:
                    payload_data = {
                        "nama_pekerjaan": nama_pekerjaan,
                        "nomor_kontrak": nomor_kontrak,
                        "tanggal_kontrak": tanggal_kontrak,
                        "lokasi_pekerjaan": lokasi_pekerjaan,
                        "jenis_kontrak": jenis_kontrak,
                        "nama_vendor": nama_vendor,
                        "npwp_vendor": npwp_vendor,
                        "nilai_kontrak": nilai_kontrak,
                        "sistem_pembayaran": sistem_pembayaran,
                        "durasi_hari": str(durasi_hari),
                        "masa_pemeliharaan": str(masa_pemeliharaan),
                        "resiko_csms": resiko_csms,
                        "pejabat_ttd_pertamina": pejabat_ttd
                    }
                    
                    files_payload = None
                    if file_upload:
                        files_payload = {"file": (file_upload.name, file_upload.getvalue(), "application/pdf")}
                        
                    res = requests.post(API_KONTRAK_URL, data=payload_data, files=files_payload, timeout=600)
                    if res.status_code == 200:
                        st.success("✅ Rancangan Kontrak berhasil dibuat!")
                        st.download_button(
                            label="⬇️ Download Rancangan Kontrak (.docx)",
                            data=res.content,
                            file_name=f"Rancangan_Kontrak_{nama_pekerjaan.replace(' ', '_')[:30]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Server error (Status: {res.status_code})")
                        try:
                            st.json(res.json())
                        except:
                            st.text(res.text)
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan koneksi: {e}")


# ──────────────────────────────────────────────────────────────
# MODE 4: DRAFT AMENDEMEN / ADDENDUM
# ──────────────────────────────────────────────────────────────
elif doc_type == "📎 Draft Amendemen / Addendum":
    st.title("📎 Generator Draft Amendemen (Addendum)")
    st.write("Buat draft addendum untuk kontrak yang sudah berjalan. Masukkan informasi kontrak asal dan rincian perubahan.")
    
    with st.form("form_amendemen"):
        st.subheader("1. Informasi Addendum & Kontrak Asal")
        col1, col2 = st.columns(2)
        with col1:
            nomor_addendum = st.text_input("Nomor Addendum*", value="Addendum Ke-1")
            tanggal_amendemen = st.text_input("Tanggal Addendum*", value="01 Februari 2026")
            tanggal_efektif = st.text_input("Tanggal Berlaku Efektif*", value="01 Februari 2026")
        with col2:
            nomor_kontrak_asal = st.text_input("Nomor Kontrak Asal*", placeholder="KTR-XXX")
            judul_pekerjaan = st.text_input("Judul Pekerjaan*", placeholder="Pengadaan Material X")
            tanggal_kontrak_asal = st.text_input("Tanggal Kontrak Asal*", value="01 Januari 2026")
            
        col3, col4 = st.columns(2)
        with col3:
            nama_vendor = st.text_input("Nama Penyedia (Vendor)*", placeholder="PT Nama Vendor")
            nilai_asal = st.text_input("Nilai Kontrak Asal*", placeholder="Rp1.000.000.000,00")
            ttd_pertamina = st.text_input("Pejabat TTD Pertamina*", value="Executive General Manager")
        with col4:
            ttd_vendor = st.text_input("Jabatan Penandatangan Vendor*", value="Direktur Utama")
            file_upload = st.file_uploader("Upload PDF Kontrak Asal (Opsional)", type=["pdf"])

        st.markdown("---")
        st.subheader("2. Detail Perubahan")
        import json
        st.info("💡 Karena limitasi form UI standar, isi satu poin perubahan utama. LLM akan merumuskannya dalam Legal Drafting.")
        
        jenis_perubahan = st.selectbox("Kategori Utama Perubahan*", ["Nilai Kontrak", "Waktu Pelaksanaan", "Lingkup Pekerjaan", "Personel Inti", "Harga Satuan / BOQ", "Sistem Pembayaran", "Lainnya"])
        pasal_referensi = st.text_input("Referensi Pasal yang Diubah*", placeholder="Contoh: Pasal 3 - Jangka Waktu Pelaksanaan")
        isi_lama = st.text_area("Kondisi / Klausul Lama*", placeholder="Tuliskan aturan atau bunyi pasal sebelumnya...")
        isi_baru = st.text_area("Kondisi / Klausul Baru*", placeholder="Tuliskan aturan atau nilai yang baru disepakati...")
        alasan = st.text_input("Alasan / Dasar Perubahan*", placeholder="Contoh: Berita Acara Kesepakatan tanggal X")
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate Draft Amendemen (.docx)", use_container_width=True)

    if submitted:
        if not nomor_addendum or not nomor_kontrak_asal or not isi_baru:
            st.warning("⚠️ Mohon lengkapi field yang bertanda bintang (*).")
        else:
            with st.spinner("⏳ Men-generate Draft Amendemen (Estimasi 1-2 Menit)..."):
                try:
                    perubahan_detail = [{
                        "jenis_perubahan": jenis_perubahan,
                        "pasal_referensi": pasal_referensi,
                        "isi_lama": isi_lama,
                        "isi_baru": isi_baru,
                        "alasan": alasan
                    }]
                    
                    payload_data = {
                        "nomor_addendum": nomor_addendum,
                        "tanggal_amendemen": tanggal_amendemen,
                        "tanggal_berlaku_efektif": tanggal_efektif,
                        "nomor_kontrak_asal": nomor_kontrak_asal,
                        "judul_pekerjaan": judul_pekerjaan,
                        "tanggal_kontrak_asal": tanggal_kontrak_asal,
                        "nama_vendor": nama_vendor,
                        "nilai_kontrak_asal_str": nilai_asal,
                        "ttd_pertamina_nama": "",
                        "ttd_pertamina_jabatan": ttd_pertamina,
                        "ttd_vendor_nama": "",
                        "ttd_vendor_jabatan": ttd_vendor,
                        "detail_perubahan_json": json.dumps(perubahan_detail)
                    }
                    
                    files_payload = None
                    if file_upload:
                        files_payload = {"file": (file_upload.name, file_upload.getvalue(), "application/pdf")}
                        
                    res = requests.post(API_AMENDEMEN_URL, data=payload_data, files=files_payload, timeout=600)
                    if res.status_code == 200:
                        st.success("✅ Draft Amendemen berhasil dibuat!")
                        st.download_button(
                            label="⬇️ Download Draft Amendemen (.docx)",
                            data=res.content,
                            file_name=f"Draft_Amendemen_{judul_pekerjaan.replace(' ', '_')[:30]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Server error (Status: {res.status_code})")
                        try:
                            st.json(res.json())
                        except:
                            st.text(res.text)
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan koneksi: {e}")

# ──────────────────────────────────────────────────────────────
# MODE 5: KNOWLEDGE BASE MANAGEMENT
# ──────────────────────────────────────────────────────────────
elif doc_type == "🗄️ Knowledge Base":
    st.title("🗄️ Knowledge Base Management")
    st.write(
        "Upload dan kelola dokumen referensi PDF yang digunakan AI sebagai konteks "
        "saat menyusun RKS, Rancangan Kontrak, dan Draft Amendemen. "
        "Dokumen akan diproses (**chunking + embedding**) dan disimpan ke **Qdrant Cloud**."
    )
    st.markdown("---")

    COLLECTION_LABELS = {
        "rks_kb": "📋 RKS Knowledge Base",
        "contract_kb": "📝 Contract Knowledge Base",
        "amendment_kb": "📎 Amendment Knowledge Base",
    }
    COLLECTION_DESCRIPTIONS = {
        "rks_kb": "Dokumen referensi RKS (template, contoh RKS serupa, spesifikasi teknis).",
        "contract_kb": "Template dan contoh Rancangan Kontrak Definitif Pertamina.",
        "amendment_kb": "Contoh Addendum / Amendemen kontrak yang pernah dibuat.",
    }

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        selected_collection = st.selectbox(
            "📂 Pilih Knowledge Base Collection",
            options=list(COLLECTION_LABELS.keys()),
            format_func=lambda k: COLLECTION_LABELS[k],
            key="kb_collection_selector",
        )
    with col_info:
        st.info(f"ℹ️ {COLLECTION_DESCRIPTIONS[selected_collection]}")

    st.markdown("---")

    # ── SECTION A: Upload & Ingest ──────────────────────────
    st.subheader("⬆️ Upload Dokumen Baru")
    st.caption(
        "Upload satu atau lebih file PDF. AI akan melakukan parsing, chunking semantik, "
        "dan embedding secara otomatis. Re-upload file dengan nama sama akan menggantikan versi lama."
    )

    uploaded_files = st.file_uploader(
        "Pilih file PDF (bisa multi-file)",
        type=["pdf"],
        accept_multiple_files=True,
        key="kb_file_uploader",
    )

    if st.button("🚀 Upload & Ingest ke Knowledge Base", type="primary", use_container_width=True, key="kb_ingest_btn"):
        if not uploaded_files:
            st.warning("⚠️ Pilih minimal satu file PDF terlebih dahulu.")
        else:
            with st.spinner(f"⏳ Sedang memproses {len(uploaded_files)} file... (chunking + embedding, mohon tunggu)"):
                files_payload = [
                    ("files", (f.name, f.getvalue(), "application/pdf"))
                    for f in uploaded_files
                ]
                data_payload = {"collection": selected_collection}
                try:
                    res = requests.post(
                        API_KB_INGEST_URL,
                        data=data_payload,
                        files=files_payload,
                        timeout=600,
                    )
                    if res.status_code == 200:
                        results = res.json().get("results", [])
                        success_count = sum(1 for r in results if r.get("status") == "success")
                        error_count = sum(1 for r in results if r.get("status") == "error")

                        if success_count > 0:
                            st.success(f"✅ {success_count} file berhasil diingestion!")
                        if error_count > 0:
                            st.warning(f"⚠️ {error_count} file gagal diproses.")

                        # Show per-file result
                        for r in results:
                            status_icon = "✅" if r["status"] == "success" else ("⚠️" if r["status"] == "skipped" else "❌")
                            detail = f"{r.get('chunks', '')} chunks" if r["status"] == "success" else r.get("reason", "")
                            st.caption(f"{status_icon} **{r['filename']}** — {detail}")

                        # Refresh document list
                        st.rerun()
                    else:
                        st.error(f"❌ Server error (Status: {res.status_code})")
                        try:
                            st.json(res.json())
                        except Exception:
                            st.text(res.text)
                except requests.exceptions.RequestException as e:
                    st.error("❌ Gagal terhubung ke API backend.")
                    st.info("Pastikan server FastAPI sudah berjalan: `uv run uvicorn api:app --reload`")
                    st.caption(f"Error detail: {e}")

    st.markdown("---")

    # ── SECTION B: List & Delete ────────────────────────────
    st.subheader(f"📋 Dokumen Terindex — {COLLECTION_LABELS[selected_collection]}")

    col_refresh, _ = st.columns([1, 4])
    with col_refresh:
        refresh_clicked = st.button("🔄 Refresh Daftar", key="kb_refresh_btn")

    try:
        res_list = requests.get(
            API_KB_LIST_URL,
            params={"collection": selected_collection},
            timeout=30,
        )
        if res_list.status_code == 200:
            list_data = res_list.json()
            documents: dict = list_data.get("documents", {})
            total = list_data.get("total", 0)

            if total == 0:
                st.info("📭 Belum ada dokumen yang terindex di collection ini. Upload PDF di atas untuk memulai.")
            else:
                st.caption(f"Total: **{total} dokumen** tersimpan di `{selected_collection}`")

                # Render table with per-row delete button
                for filename, chunk_count in documents.items():
                    col_name, col_chunks, col_del = st.columns([4, 1, 1])
                    with col_name:
                        st.write(f"📄 {filename}")
                    with col_chunks:
                        st.write(f"`{chunk_count}` chunks")
                    with col_del:
                        del_key = f"del_{selected_collection}_{filename}"
                        if st.button("🗑️ Hapus", key=del_key, type="secondary"):
                            try:
                                del_res = requests.delete(
                                    API_KB_DELETE_URL,
                                    data={"collection": selected_collection, "filename": filename},
                                    timeout=30,
                                )
                                if del_res.status_code == 200:
                                    st.success(f"✅ '{filename}' berhasil dihapus.")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Gagal menghapus: {del_res.text}")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
        else:
            st.error(f"❌ Gagal mengambil daftar dokumen (Status: {res_list.status_code})")
    except requests.exceptions.RequestException:
        st.warning("⚠️ Tidak dapat terhubung ke backend. Pastikan FastAPI sudah berjalan.")
        st.info("`uv run uvicorn api:app --reload --port 8000`")
