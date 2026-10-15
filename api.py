import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
import uvicorn

from RAG.summarizer import extract_text_from_pdfs, summarize_context, extract_tender_metadata_from_docs
from RAG.tools import generate_rks_document, export_rks_to_docx
from RAG.vector_store import Vector_Store
from tender.generator import generate_tender_document, export_tender_to_docx
from contract.generator import generate_kontrak_document, export_kontrak_to_docx
from contract.amendment_generator import generate_amendemen_document, export_amendemen_to_docx
from config import COLLECTION_RKS, COLLECTION_CONTRACT, COLLECTION_AMENDMENT

app = FastAPI(
    title="Pertamina Procurement AI System - API",
    description="RKS, Tender, Rancangan Kontrak & Amendemen Generator + Knowledge Base Management",
    version="2.1.0",
)

VALID_COLLECTIONS = {
    "rks_kb": COLLECTION_RKS,
    "contract_kb": COLLECTION_CONTRACT,
    "amendment_kb": COLLECTION_AMENDMENT,
}


# ──────────────────────────────────────────────────────────────
# Knowledge Base Management Endpoints
# ──────────────────────────────────────────────────────────────

@app.post("/api/kb/ingest", summary="Ingest PDF into Knowledge Base")
async def kb_ingest(
    collection: str = Form(..., description="Target collection: rks_kb | contract_kb | amendment_kb"),
    files: List[UploadFile] = File(default=[], description="One or more PDF files to ingest"),
):
    """
    Upload one or more PDF files and ingest them into the specified Qdrant collection.
    Re-uploading the same filename replaces its chunks (idempotent).
    """
    if collection not in VALID_COLLECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid collection '{collection}'. Must be one of: {list(VALID_COLLECTIONS.keys())}"
        )

    if not files:
        return {"collection": collection, "results": [], "message": "Tidak ada file yang diunggah"}

    results = []
    vs = Vector_Store(collection_name=collection)

    for file in files:
        fname = file.filename or "unknown.pdf"
        if not fname.lower().endswith(".pdf"):
            results.append({"filename": fname, "status": "skipped", "reason": "Bukan file PDF (.pdf)"})
            continue
        try:
            content = await file.read()
            if not content or len(content) == 0:
                results.append({"filename": fname, "status": "error", "reason": "File kosong (0 bytes)"})
                continue
            n_chunks = await run_in_threadpool(vs.ingest_bytes, content, fname)
            results.append({"filename": fname, "status": "success", "chunks": n_chunks})
        except ValueError as e:
            results.append({"filename": fname, "status": "error", "reason": str(e)})
        except Exception as e:
            results.append({"filename": fname, "status": "error", "reason": f"Unexpected error: {e}"})

    return {"collection": collection, "results": results}


@app.get("/api/kb/list", summary="List documents in a Knowledge Base collection")
async def kb_list(
    collection: str,
):
    """
    Return all ingested documents and their chunk counts for the given collection.
    """
    if collection not in VALID_COLLECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid collection '{collection}'. Must be one of: {list(VALID_COLLECTIONS.keys())}"
        )
    try:
        vs = Vector_Store(collection_name=collection)
        sources = await run_in_threadpool(vs.list_sources)
        return {"collection": collection, "documents": sources, "total": len(sources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/kb/delete", summary="Delete a document from a Knowledge Base collection")
async def kb_delete(
    collection: str = Form(...),
    filename: str = Form(..., description="Filename to remove from the collection"),
):
    """
    Remove all vector chunks belonging to the specified document.
    """
    if collection not in VALID_COLLECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid collection '{collection}'. Must be one of: {list(VALID_COLLECTIONS.keys())}"
        )
    try:
        vs = Vector_Store(collection_name=collection)
        await run_in_threadpool(vs.delete_source, filename)
        return {"status": "success", "deleted": filename, "collection": collection}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-tender-metadata")
async def extract_tender_metadata(
    tanggal: str = Form(""),
    resiko_csms: str = Form("Tinggi"),
    file_rks: Optional[UploadFile] = File(None, description="Dokumen RKS (PDF)"),
    file_boq: Optional[UploadFile] = File(None, description="Dokumen BOQ (PDF or Excel)"),
):
    """Scan and extract procurement metadata from RKS & BOQ files using LLM."""
    try:
        rks_bytes = None
        rks_filename = None
        if file_rks and file_rks.filename:
            rks_bytes = await file_rks.read()
            rks_filename = file_rks.filename

        boq_bytes = None
        boq_filename = None
        if file_boq and file_boq.filename:
            boq_bytes = await file_boq.read()
            boq_filename = file_boq.filename

        extracted_data = await run_in_threadpool(
            extract_tender_metadata_from_docs,
            rks_bytes=rks_bytes,
            rks_filename=rks_filename,
            boq_bytes=boq_bytes,
            boq_filename=boq_filename,
            tanggal_str=tanggal,
            resiko_csms=resiko_csms
        )

        return {"status": "success", "data": extracted_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-tender")
async def generate_tender(
    nama_pengadaan: str = Form(...),
    nomor_tender: str = Form("No.Project/DT/PND970000/2026-S7"),
    tanggal: str = Form("04 Desember 2025"),
    prime_cost: float = Form(13283434534.0),
    total_dengan_kr: float = Form(14346100000.0),
    resiko_csms: str = Form("Tinggi"),
    tkdn_minimal: float = Form(20.12),
    metode_pemenuhan: str = Form("Tender Terbatas"),
    jenis_kontrak: str = Form("Gabungan Harga Satuan & Lumpsum"),
    pejabat_procurement_nama: str = Form("Rigga Widar Atmagi"),
    pejabat_procurement_jabatan: str = Form("Area Manager Procurement Kalimantan"),
    pejabat_berwenang: str = Form("Sr. Manager Opt. & Maint. Regional Kalimantan"),
    pengawas_pekerjaan: str = Form("Region Manager RPD Regional Kalimantan"),
    prebid_tanggal: str = Form("Senin, 08 Desember 2025"),
    prebid_waktu: str = Form("10.00 WITA"),
    prebid_tempat: str = Form("Microsoft Teams Meeting dengan link yang disampaikan melalui email Undangan Prebid Meeting"),
    pemasukan_mulai: str = Form("Senin, 08 Desember 2025"),
    pemasukan_selesai: str = Form("Senin, 15 Desember 2025"),
    context_summary: str = Form(""),
    file: Optional[UploadFile] = File(None, description="Upload RKS or BOQ PDF file for context")
):
    try:
        if not context_summary and file and file.filename and file.filename.lower().endswith(".pdf"):
            print(f"Receiving context file: {file.filename}...")
            content = await file.read()
            raw_text = await run_in_threadpool(extract_text_from_pdfs, [content])
            context_summary = await run_in_threadpool(summarize_context, raw_text)

        print(f"Generating Dokumen Tender for: {nama_pengadaan}...")
        gen_result = await run_in_threadpool(
            generate_tender_document.invoke,
            {
                "nama_pengadaan": nama_pengadaan,
                "nomor_tender": nomor_tender,
                "tanggal": tanggal,
                "prime_cost": prime_cost,
                "total_dengan_kr": total_dengan_kr,
                "resiko_csms": resiko_csms,
                "tkdn_minimal": tkdn_minimal,
                "metode_pemenuhan": metode_pemenuhan,
                "jenis_kontrak": jenis_kontrak,
                "pejabat_procurement_nama": pejabat_procurement_nama,
                "pejabat_procurement_jabatan": pejabat_procurement_jabatan,
                "pejabat_berwenang": pejabat_berwenang,
                "pengawas_pekerjaan": pengawas_pekerjaan,
                "prebid_tanggal": prebid_tanggal,
                "prebid_waktu": prebid_waktu,
                "prebid_tempat": prebid_tempat,
                "pemasukan_mulai": pemasukan_mulai,
                "pemasukan_selesai": pemasukan_selesai,
                "context_summary": context_summary
            }
        )

        if "Error" in gen_result:
            raise HTTPException(status_code=400, detail=gen_result)

        print("Exporting Dokumen Tender to DOCX...")
        safe_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in nama_pengadaan)[:40].strip()
        export_result = await run_in_threadpool(
            export_tender_to_docx.invoke,
            {"output_filename": f"Dokumen_Tender_{safe_name}.docx"}
        )

        if "Error" in export_result:
            raise HTTPException(status_code=400, detail=export_result)

        file_path = ""
        for line in export_result.split("\n"):
            if "📄 File:" in line:
                file_path = line.split("📄 File:")[1].strip()
                break

        if not file_path or not os.path.exists(file_path):
            return {
                "status": "success",
                "message": "Generated draft but file path not found",
                "detail": export_result
            }

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-rks")
async def generate_rks(
    jenis_pekerjaan: str = Form(...),
    detail_pekerjaan: str = Form(...),
    lokasi: str = Form(""),
    resiko_csms: str = Form("MEDIUM"),
    nomor_dokumen: str = Form("RKS-[KODE]-[TAHUN]"),
    nama_perusahaan: str = Form("PT PERTAMINA"),
    file: UploadFile = File(..., description="Upload BOQ/Context PDF file here")
):
    try:
        context_summary = ""
        
        # 1. Process files and summarize context
        pdf_bytes_list = []
        if file and file.filename and file.filename.lower().endswith('.pdf'):
            print(f"Receiving file {file.filename} for context...")
            content = await file.read()
            pdf_bytes_list.append(content)
            
        if pdf_bytes_list:
                print("Extracting text from PDFs...")
                raw_text = await run_in_threadpool(extract_text_from_pdfs, pdf_bytes_list)
                print("Summarizing context using LLM...")
                context_summary = await run_in_threadpool(summarize_context, raw_text)
                print(f"Context Summary:\n{context_summary}\n")

        # 2. Generate RKS Draft
        print("Generating RKS document...")
        gen_result = await run_in_threadpool(
            generate_rks_document.invoke,
            {
                "jenis_pekerjaan": jenis_pekerjaan,
                "detail_pekerjaan": detail_pekerjaan,
                "lokasi": lokasi,
                "context_summary": context_summary,
                "resiko_csms": resiko_csms,
                "nomor_dokumen": nomor_dokumen,
                "nama_perusahaan": nama_perusahaan
            }
        )

        if "Error" in gen_result or "Tidak ditemukan" in gen_result:
            raise HTTPException(status_code=400, detail=gen_result)

        # 3. Export to Docx
        print("Exporting to DOCX...")
        export_result = await run_in_threadpool(
            export_rks_to_docx.invoke,
            {"output_filename": f"RKS_{jenis_pekerjaan.replace(' ', '_')}.docx"}
        )
        
        if "Error" in export_result or "Tidak ada draft" in export_result:
            raise HTTPException(status_code=400, detail=export_result)
            
        # Parse the output path from export_result
        lines = export_result.split('\n')
        file_path = ""
        for line in lines:
            if "📄 File:" in line:
                file_path = line.split("📄 File:")[1].strip()
                break

        if not file_path or not os.path.exists(file_path):
             return {
                 "status": "success", 
                 "message": "Generated but could not find docx path", 
                 "raw_generation_result": gen_result,
                 "raw_export_result": export_result
             }

        # Return FileResponse to download the docx immediately
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path), 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-kontrak")
async def generate_kontrak(
    nama_pekerjaan: str = Form(""),
    nomor_kontrak: str = Form(""),
    tanggal_kontrak: str = Form(""),
    lokasi_pekerjaan: str = Form(""),
    jenis_kontrak: str = Form(""),
    nama_vendor: str = Form(""),
    npwp_vendor: str = Form(""),
    nilai_kontrak: str = Form("0"),
    sistem_pembayaran: str = Form(""),
    durasi_hari: str = Form("180"),
    masa_pemeliharaan: str = Form("90"),
    resiko_csms: str = Form(""),
    pejabat_ttd_pertamina: str = Form(""),
    file: Optional[UploadFile] = File(None, description="PDF RKS/BOQ untuk context opsional")
):
    try:
        context_summary = ""
        if file and file.filename and file.filename.lower().endswith('.pdf'):
            content = await file.read()
            raw_text = await run_in_threadpool(extract_text_from_pdfs, [content])
            context_summary = await run_in_threadpool(summarize_context, raw_text)
            
        gen_result = await run_in_threadpool(
            generate_kontrak_document.invoke,
            {
                "nama_pekerjaan": nama_pekerjaan,
                "nomor_kontrak": nomor_kontrak,
                "tanggal_kontrak": tanggal_kontrak,
                "lokasi_pekerjaan": lokasi_pekerjaan,
                "jenis_kontrak": jenis_kontrak,
                "nama_vendor": nama_vendor,
                "npwp_vendor": npwp_vendor,
                "nilai_kontrak": float(nilai_kontrak) if nilai_kontrak else 0.0,
                "sistem_pembayaran": sistem_pembayaran,
                "durasi_hari": durasi_hari,
                "masa_pemeliharaan": masa_pemeliharaan,
                "resiko_csms": resiko_csms,
                "pejabat_ttd_pertamina": pejabat_ttd_pertamina,
                "context_summary": context_summary
            }
        )
        if "Error" in gen_result:
            raise HTTPException(status_code=400, detail=gen_result)
            
        safe_name = "".join(c if c.isalnum() else "_" for c in nama_pekerjaan)[:30]
        export_result = await run_in_threadpool(
            export_kontrak_to_docx.invoke,
            {"output_filename": f"Rancangan_Kontrak_{safe_name}.docx"}
        )
        
        file_path = ""
        for line in export_result.split("\n"):
            if "📄 File:" in line:
                file_path = line.split("📄 File:")[1].strip()
                break
                
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Generated but docx not found")
            
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path), 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-amendemen")
async def generate_amendemen(
    nomor_addendum: str = Form(""),
    tanggal_amendemen: str = Form(""),
    tanggal_berlaku_efektif: str = Form(""),
    nomor_kontrak_asal: str = Form(""),
    judul_pekerjaan: str = Form(""),
    tanggal_kontrak_asal: str = Form(""),
    nama_vendor: str = Form(""),
    nilai_kontrak_asal_str: str = Form(""),
    ttd_pertamina_nama: str = Form(""),
    ttd_pertamina_jabatan: str = Form(""),
    ttd_vendor_nama: str = Form(""),
    ttd_vendor_jabatan: str = Form(""),
    detail_perubahan_json: str = Form("[]"),
    file: Optional[UploadFile] = File(None, description="PDF Kontrak asal untuk context opsional")
):
    try:
        import json
        detail_perubahan_list = json.loads(detail_perubahan_json)
        
        context_summary = ""
        if file and file.filename and file.filename.lower().endswith('.pdf'):
            content = await file.read()
            raw_text = await run_in_threadpool(extract_text_from_pdfs, [content])
            context_summary = await run_in_threadpool(summarize_context, raw_text)
            
        gen_result = await run_in_threadpool(
            generate_amendemen_document.invoke,
            {
                "nomor_addendum": nomor_addendum,
                "tanggal_amendemen": tanggal_amendemen,
                "tanggal_berlaku_efektif": tanggal_berlaku_efektif,
                "nomor_kontrak_asal": nomor_kontrak_asal,
                "judul_pekerjaan": judul_pekerjaan,
                "tanggal_kontrak_asal": tanggal_kontrak_asal,
                "nama_vendor": nama_vendor,
                "nilai_kontrak_asal_str": nilai_kontrak_asal_str,
                "ttd_pertamina_nama": ttd_pertamina_nama,
                "ttd_pertamina_jabatan": ttd_pertamina_jabatan,
                "ttd_vendor_nama": ttd_vendor_nama,
                "ttd_vendor_jabatan": ttd_vendor_jabatan,
                "detail_perubahan_list": detail_perubahan_list,
                "context_summary": context_summary
            }
        )
        if "Error" in gen_result:
            raise HTTPException(status_code=400, detail=gen_result)
            
        safe_name = "".join(c if c.isalnum() else "_" for c in judul_pekerjaan)[:30]
        export_result = await run_in_threadpool(
            export_amendemen_to_docx.invoke,
            {"output_filename": f"Draft_Amendemen_{safe_name}.docx"}
        )
        
        file_path = ""
        for line in export_result.split("\n"):
            if "📄 File:" in line:
                file_path = line.split("📄 File:")[1].strip()
                break
                
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Generated but docx not found")
            
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path), 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

