import sys, torch
import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import config
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
load_dotenv()  # Load environment variables from .env file

def get_embedding_function() -> HuggingFaceEmbeddings:
    """Loads the Qwen3 embedding model on local CPU."""
    
    # return HuggingFaceEmbeddings(
    #     model_name=config.EMBEDDING_MODEL_NAME,
    #     model_kwargs={"device": "cpu"},
    #     encode_kwargs={"normalize_embeddings": True},
    # )

    native_ollama_url = config.REMOTE_LLM_URL.replace("/v1", "").rstrip("/")
    
    return OllamaEmbeddings(
        base_url=native_ollama_url,
        model=config.OLLAMA_EMBEDDING,
        client_kwargs={
            "headers": {"ngrok-skip-browser-warning": "true"}
        }
    )

def ingest_pdf_documents() -> None:
    """Scans rag/Data for PDFs, chunks their content, and persists vectors to ChromaDB."""
    data_path = Path("./RAG/sample_data")

    print(sys.executable)
    print(torch.__version__)
    print(torch.__file__)
    print(torch.version.cuda)
    print(torch.cuda.is_available())

    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"[RAG] Created directory: {data_path}. Place your PDF files here.")
        return

    pdf_files = list(data_path.glob("*.pdf"))
    if not pdf_files:
        print(f"[RAG] No PDF files found in {data_path}. Ingestion skipped.")
        return

    print(f"[RAG] Found {len(pdf_files)} PDF(s) in {data_path}. Loading pages...")
    loader = PyPDFDirectoryLoader(str(data_path))
    raw_pages = loader.load()
    print(f"[RAG] Loaded {len(raw_pages)} total page(s).")

    # Split pages into semantic chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", " ", ""]
    )
    chunked_docs = splitter.split_documents(raw_pages)
    print(f"[RAG] Generated {len(chunked_docs)} chunks. Generating embeddings...")

    # Embed and persist to disk
    embeddings = get_embedding_function()
    Chroma.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        collection_name=config.COLLECTION_NAME,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )
    print(f"[RAG] Ingestion complete. Stored in: {config.CHROMA_PERSIST_DIR}")

def get_vector_store() -> Chroma:
    """Returns the Chroma store. Automatically triggers ingestion if database is absent."""
    # Self-healing: if the persistent store doesn't exist yet, ingest automatically
    if not os.path.exists(config.CHROMA_PERSIST_DIR):
        print("[RAG] Vector store not detected. Triggering initial ingestion...")
        ingest_pdf_documents()

    embeddings = get_embedding_function()
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )

if __name__ == "__main__":
    # Allows running `python -m rag.store` independently to ingest or rebuild
    print("[RAG] Executing standalone PDF ingestion pipeline...")
    ingest_pdf_documents()