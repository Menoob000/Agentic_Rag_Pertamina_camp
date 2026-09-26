"""
RKS Template Extractor
Uses LLM to dynamically extract RKS structure from knowledge base chunks
and fill content for each section. No hardcoded template — structure is
inferred from the retrieved documents.
"""

import json
import re
from typing import Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage


# ──────────────────────────────────────────────────────────────
# Prompt Templates
# ──────────────────────────────────────────────────────────────

EXTRACT_STRUCTURE_PROMPT = """Kamu adalah ahli dalam membuat dokumen RKS (Rencana Kerja dan Syarat-Syarat) untuk Pertamina.

Berdasarkan potongan dokumen RKS referensi berikut, analisis dan ekstrak STRUKTUR TEMPLATE RKS yang sesuai untuk pekerjaan yang diminta.

**Jenis Pekerjaan:** {jenis_pekerjaan}
**Detail Pekerjaan:** {detail_pekerjaan}
**Lokasi:** {lokasi}

**Konteks Tambahan (Summary Dokumen Proyek / BOQ):**
{context_summary}

**Dokumen Referensi:**
{chunks}

**INSTRUKSI:**
1. Identifikasi pola struktur bab dan sub-bab dari dokumen referensi
2. Sesuaikan struktur dengan jenis pekerjaan yang diminta
3. Tentukan metadata cover page (judul pekerjaan, level risiko CSMS, nama unit perusahaan)

**OUTPUT FORMAT (JSON ONLY, tanpa markdown code block):**
{{
  "cover_page": {{
    "judul_pekerjaan": "DESKRIPSI PEKERJAAN LENGKAP DALAM HURUF KAPITAL",
    "bidder_list_no": "",
    "resiko_csms": "HIGH atau MIDDLE atau LOW",
    "nama_perusahaan": "PT ... (nama unit/anak perusahaan Pertamina yang sesuai)"
  }},
  "pengesahan": {{
    "disusun_oleh": {{"nama": "", "jabatan": ""}},
    "diperiksa_oleh": {{"nama": "", "jabatan": ""}},
    "disetujui_oleh": {{"nama": "", "jabatan": ""}}
  }},
  "metadata": {{
    "nomor_dokumen": "RKS-[KODE]-[TAHUN]",
    "jenis_pekerjaan": "...",
    "lokasi": "..."
  }},
  "bab": [
    {{
      "nomor": "I",
      "judul": "JUDUL BAB",
      "sub_bab": [
        {{
          "nomor": "1.1",
          "judul": "Judul Sub Bab",
          "tipe": "paragraf atau numbered_list atau bullet_list atau table atau heading_only",
          "konten_instruksi": "Instruksi singkat tentang apa yang harus diisi di sub-bab ini"
        }}
      ]
    }}
  ]
}}

PENTING:
- Jumlah bab, judul, dan sub-bab harus DINAMIS sesuai jenis pekerjaan
- Jangan gunakan struktur template tetap — pelajari dari dokumen referensi
- `konten_instruksi` berisi petunjuk untuk pengisian konten, bukan konten akhir
- Output HARUS valid JSON tanpa markdown code block
"""

FILL_CHAPTER_PROMPT = """Kamu adalah ahli dalam membuat dokumen RKS (Rencana Kerja dan Syarat-Syarat) untuk Pertamina.

Isi konten untuk SATU BAB berikut berdasarkan DOKUMEN REFERENSI.

**Bab yang harus diisi:**
{chapter_json}

**Dokumen Referensi:**
{chunks}

**Jenis Pekerjaan:** {jenis_pekerjaan}

**Konteks Tambahan (Summary Dokumen Proyek / BOQ):**
{context_summary}

**INSTRUKSI:**
1. Isi field "konten" di setiap sub_bab berdasarkan konteks dari dokumen referensi
2. Sesuaikan konten dengan jenis pekerjaan
3. Untuk tipe "paragraf": isi dengan teks deskriptif lengkap
4. Untuk tipe "numbered_list": isi dengan array of strings ["item 1", "item 2", ...]
5. Untuk tipe "bullet_list": isi dengan array of strings ["item 1", "item 2", ...]
6. Untuk tipe "table": isi dengan {{"headers": ["col1", "col2"], "rows": [["val1", "val2"]]}}
7. Untuk tipe "heading_only": biarkan konten kosong ("")
8. Hapus field "konten_instruksi" dan ganti dengan field "konten"

**OUTPUT FORMAT (JSON ONLY, tanpa markdown code block):**
Kembalikan JSON bab ini saja (bukan seluruh dokumen), dengan field "konten" terisi di setiap sub_bab.
"""

REVISE_SECTION_PROMPT = """Kamu adalah ahli dalam membuat dokumen RKS (Rencana Kerja dan Syarat-Syarat) untuk Pertamina.

Berikut adalah BAB yang perlu direvisi:

**Bab Saat Ini:**
{current_section_json}

**Instruksi Revisi dari User:**
{instruksi_revisi}

**Konteks Tambahan dari Knowledge Base (jika relevan):**
{chunks}

**INSTRUKSI:**
1. Revisi bab sesuai instruksi user
2. Pertahankan format dan struktur yang ada kecuali diminta untuk mengubahnya
3. Jika instruksi meminta menambah sub-bab, tambahkan dengan nomor yang sesuai
4. Jika instruksi meminta mengubah tipe konten (misal dari paragraf ke tabel), ubah sesuai

**OUTPUT FORMAT (JSON ONLY, tanpa markdown code block):**
Kembalikan JSON bab yang sudah direvisi dengan format yang sama.
"""


def _parse_json_response(response_text: str) -> dict:
    """Extract and parse JSON from LLM response, handling markdown code blocks."""
    text = response_text.strip()
    
    # Try to extract from markdown code block if present
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()
    
    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        brace_start = text.find('{')
        brace_end = text.rfind('}')
        if brace_start != -1 and brace_end != -1:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass
    
    raise ValueError(f"Failed to parse JSON from LLM response:\n{response_text[:500]}")


def extract_rks_structure(
    chunks: str,
    llm,
    jenis_pekerjaan: str,
    detail_pekerjaan: str,
    lokasi: str = "",
    context_summary: str = ""
) -> dict:
    """
    Use LLM to analyze knowledge base chunks and extract a dynamic RKS structure.
    Uses max_tokens=2000 to keep the structure skeleton fast (~15-20 seconds).
    
    Args:
        chunks: Retrieved document chunks from knowledge base
        llm: LangChain LLM instance
        jenis_pekerjaan: Type of work (e.g., "overhaul tangki")
        detail_pekerjaan: Detailed description of the work
        lokasi: Work location
    
    Returns:
        dict: RKS structure in intermediate format (without filled content)
    """
    prompt = EXTRACT_STRUCTURE_PROMPT.format(
        jenis_pekerjaan=jenis_pekerjaan,
        detail_pekerjaan=detail_pekerjaan,
        lokasi=lokasi,
        chunks=chunks,
        context_summary=context_summary if context_summary else "(Tidak ada konteks tambahan)"
    )
    
    # Use max_tokens to limit structure-only output (skeleton, not full content)
    response = llm.invoke(
        [HumanMessage(content=prompt)],
        max_tokens=2000,
    )
    structure = _parse_json_response(response.content)
    
    return structure


def fill_rks_content(
    structure: dict,
    chunks: str,
    llm,
    jenis_pekerjaan: str,
    on_chapter_progress: Optional[Callable[[int, int, str], None]] = None,
    context_summary: str = ""
) -> dict:
    """
    Use LLM to fill content for each chapter (bab) ONE AT A TIME.
    This avoids generating 6000+ tokens in a single call which causes
    ngrok gateway timeouts.
    
    Args:
        structure: RKS structure from extract_rks_structure()
        chunks: Retrieved document chunks for content reference
        llm: LangChain LLM instance
        jenis_pekerjaan: Type of work for context
        on_chapter_progress: Optional callback(current_index, total, chapter_title)
                             called after each chapter is filled
    
    Returns:
        dict: Complete RKS structure with content filled in
    """
    filled_structure = {
        "cover_page": structure.get("cover_page", {}),
        "pengesahan": structure.get("pengesahan", {}),
        "metadata": structure.get("metadata", {}),
        "bab": [],
    }
    
    chapters = structure.get("bab", [])
    total_chapters = len(chapters)
    
    for idx, chapter in enumerate(chapters):
        chapter_title = chapter.get("judul", f"Bab {chapter.get('nomor', '?')}")
        
        # Notify progress
        if on_chapter_progress:
            on_chapter_progress(idx + 1, total_chapters, chapter_title)
        
        prompt = FILL_CHAPTER_PROMPT.format(
            chapter_json=json.dumps(chapter, ensure_ascii=False, indent=2),
            chunks=chunks,
            jenis_pekerjaan=jenis_pekerjaan,
            context_summary=context_summary if context_summary else "(Tidak ada konteks tambahan)",
        )
        
        try:
            response = llm.invoke(
                [HumanMessage(content=prompt)],
                max_tokens=5000,
            )
            filled_chapter = _parse_json_response(response.content)
            filled_structure["bab"].append(filled_chapter)
        except Exception as e:
            # If one chapter fails, keep the original skeleton and continue
            print(f"  ⚠️ Gagal mengisi Bab {chapter.get('nomor', '?')} ({chapter_title}): {str(e)[:100]}")
            chapter_copy = dict(chapter)
            for sub in chapter_copy.get("sub_bab", []):
                if "konten_instruksi" in sub:
                    sub["konten"] = f"[GAGAL DIGENERATE: {str(e)[:80]}]"
                    del sub["konten_instruksi"]
            filled_structure["bab"].append(chapter_copy)
    
    return filled_structure


def revise_section(
    current_section: dict,
    instruksi_revisi: str,
    chunks: str,
    llm
) -> dict:
    """
    Use LLM to revise a single bab based on user instructions.
    
    Args:
        current_section: The current bab dict to revise
        instruksi_revisi: User's revision instructions
        chunks: Additional context from knowledge base (can be empty)
        llm: LangChain LLM instance
    
    Returns:
        dict: Revised bab dict
    """
    prompt = REVISE_SECTION_PROMPT.format(
        current_section_json=json.dumps(current_section, ensure_ascii=False, indent=2),
        instruksi_revisi=instruksi_revisi,
        chunks=chunks if chunks else "(Tidak ada konteks tambahan)"
    )
    
    response = llm.invoke(
        [HumanMessage(content=prompt)],
        max_tokens=5000,
    )
    revised = _parse_json_response(response.content)
    
    return revised

