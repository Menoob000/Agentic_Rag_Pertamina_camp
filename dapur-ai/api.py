import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
import uvicorn

app = FastAPI(title="Pertamina RKS & Tender AI System - API")


@app.get("/")
async def root():
    return {"status": "success", "message": "API is running. Welcome to Pertamina RKS & Tender AI System - Dapur AI."}


def _run_ingest(file_path: str):
    """Background task: ingest a single PDF into Qdrant vector store."""
    try:
        from RAG.vector_store import Vector_Store
        vs = Vector_Store()
        data_dir = os.path.dirname(file_path)
        vs.load_documents(data_dir)
        print(f"[Ingest] Successfully ingested documents from {data_dir}")
    except Exception as e:
        print(f"[Ingest] Error: {e}")


@app.post("/api/ingest-pdf")
async def ingest_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save the file to RAG/Data
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAG", "Data")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Start ingestion in the background to prevent timeout
    background_tasks.add_task(_run_ingest, file_path)

    return {"status": "success", "message": f"File {file.filename} uploaded and ingestion started in the background."}

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
    file: Optional[UploadFile] = File(None, description="Upload RKS or BOQ PDF file for context")
):
    try:
        from RAG.summarizer import extract_text_from_pdfs, summarize_context
        from tender.generator import generate_tender_document, export_tender_to_docx

        context_summary = ""
        if file and file.filename and file.filename.lower().endswith(".pdf"):
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
        from RAG.summarizer import extract_text_from_pdfs, summarize_context
        from RAG.tools import generate_rks_document, export_rks_to_docx

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
