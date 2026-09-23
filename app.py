import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://localhost:8000/api/generate-rks"

st.set_page_config(page_title="RKS Generator", page_icon="📄", layout="wide")

st.title("📄 Pertamina RKS Generator")
st.write("Isi formulir di sidebar dan unggah dokumen referensi (seperti BoQ) untuk menyusun draft RKS secara otomatis.")

# Sidebar for Inputs
with st.sidebar:
    st.header("📝 Informasi Pekerjaan")
    jenis_pekerjaan = st.text_input("Judul Pekerjaan", placeholder="Contoh: Pembangunan Fasilitas...")
    detail_pekerjaan = st.text_area("Detail Pekerjaan", placeholder="Penjelasan singkat ruang lingkup...")
    lokasi = st.text_input("Lokasi", placeholder="Contoh: Kilang Balikpapan")
    
    st.divider()
    st.header("🏢 Metadata Dokumen")
    resiko_csms = st.selectbox("Risiko CSMS", options=["HIGH", "MIDDLE", "LOW"], index=0)
    nomor_dokumen = st.text_input("Nomor Dokumen", value="RKS-[KODE]-[TAHUN]")
    nama_perusahaan = st.text_input("Nama Perusahaan", value="PT PERTAMINA (PERSERO)")
    
    st.divider()
    st.header("📎 Referensi Dokumen")
    uploaded_file = st.file_uploader("Unggah BoQ / Spesifikasi (PDF)", type=["pdf"])
    st.caption("File PDF ini akan diekstrak menggunakan Docling dan diringkas oleh AI.")

# Main Action
if st.button("🚀 Generate Dokumen RKS", type="primary", use_container_width=True):
    # Validasi input
    if not jenis_pekerjaan or not detail_pekerjaan or not uploaded_file:
        st.warning("⚠️ Mohon lengkapi Judul Pekerjaan, Detail Pekerjaan, dan unggah file PDF.")
    else:
        # Tampilkan status loading
        with st.spinner("⏳ Sedang memproses dokumen dan menyusun RKS dengan AI... (Ini mungkin memakan waktu beberapa menit)"):
            
            # Siapkan form-data untuk API
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
            }
            data = {
                "jenis_pekerjaan": jenis_pekerjaan,
                "detail_pekerjaan": detail_pekerjaan,
                "lokasi": lokasi,
                "resiko_csms": resiko_csms,
                "nomor_dokumen": nomor_dokumen,
                "nama_perusahaan": nama_perusahaan
            }
            
            try:
                # Call FastAPI backend (timeout diset lama karena proses LLM & docling berat)
                response = requests.post(API_URL, data=data, files=files, timeout=600)
                
                if response.status_code == 200:
                    st.success("✅ Dokumen RKS berhasil dibuat!")
                    
                    # Ambil nama file dari header Content-Disposition jika ada
                    filename = f"RKS_{jenis_pekerjaan.replace(' ', '_')}.docx"
                    cd = response.headers.get('content-disposition')
                    if cd and 'filename=' in cd:
                        filename = cd.split('filename=')[1].strip('"\'')
                    
                    # Tampilkan tombol unduh
                    st.download_button(
                        label="📥 Unduh Dokumen RKS (.docx)",
                        data=response.content,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                else:
                    st.error(f"❌ Terjadi kesalahan pada server (Status Code: {response.status_code})")
                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)
                        
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal terhubung ke API backend.")
                st.info("💡 Pastikan server FastAPI sudah berjalan (jalankan `uvicorn api:app --reload` di terminal lain).")
                st.caption(f"Error detail: {e}")

