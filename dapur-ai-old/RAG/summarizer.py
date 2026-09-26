import io
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import config

def get_summarizer_llm():
    return ChatOpenAI(
        base_url=config.REMOTE_LLM_URL,
        api_key="ollama",
        model=config.LLM_MODEL_NAME,
        temperature=0,
        timeout=600,
        streaming=False,
        default_headers={"ngrok-skip-browser-warning": "true"},
    )

def extract_text_from_pdfs(pdf_bytes_list: list[bytes]) -> str:
    """Extract text from a list of PDF byte arrays."""
    combined_text = []
    for pdf_bytes in pdf_bytes_list:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                combined_text.append(text)
    return "\n".join(combined_text)

def summarize_context(text: str) -> str:
    """Use the LLM to summarize BOQ and other project specific details from the raw text."""
    if not text.strip():
        return ""
    
    llm = get_summarizer_llm()
    system_prompt = (
        "Kamu adalah asisten AI ahli yang bertugas mengekstrak informasi penting dari dokumen proyek "
        "(seperti Bill of Quantities/BOQ, spesifikasi material, dan ruang lingkup pekerjaan).\n\n"
        "Tugasmu: Buatlah ringkasan terstruktur dari teks yang diberikan. Fokus pada:\n"
        "1. Material utama yang digunakan\n"
        "2. Kuantitas atau volume pekerjaan\n"
        "3. Ruang lingkup spesifik proyek\n"
        "4. Persyaratan teknis khusus jika ada\n\n"
        "Ringkasan ini akan digunakan sebagai konteks tambahan untuk membuat dokumen RKS (Rencana Kerja dan Syarat-Syarat). "
        "Gunakan bahasa Indonesia yang baku dan jelas."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Teks dokumen:\n{text[:15000]}") # Limiting text length just in case
    ]
    
    response = llm.invoke(messages)
    return response.content
