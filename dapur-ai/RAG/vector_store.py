from qdrant_client import QdrantClient, models
import os 
os.environ["DOCLING_ALLOW_EXTERNAL_PLUGINS"] = "true"
from dotenv import load_dotenv
from config import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL
import logging
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import PyPDFLoader

embedding_model = EMBEDDING_MODEL # Default is qwen/qwen3-embedding-4b
load_dotenv()


_CLIENT = None
_EMBEDDINGS = None


def get_qdrant_client(collection_name='Documents'):
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = QdrantClient(
            url=os.getenv('QDRANT_CLUSTER_ENDPOINT'),
            api_key=os.getenv("QDRANT_API_KEY"),
            cloud_inference=True
        )
    if not _CLIENT.collection_exists(collection_name):
        _CLIENT.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
            ),
        )
    return _CLIENT


def get_embeddings(model_name=embedding_model):
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name=model_name)
    return _EMBEDDINGS


class Vector_Store():
    def __init__(self, collection_name='Documents', embed_model=embedding_model):
        self.collection_name = collection_name
        self.embed_model = embed_model
        self.client = get_qdrant_client(collection_name)

    @property
    def embeddings(self):
        return get_embeddings(self.embed_model)

    @property
    def doc_store(self):
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def ingest_file(self, file_path):
        """Ingest ONE pdf. Idempotent: chunk IDs are deterministic, so
        re-ingesting the same file replaces its chunks (no duplicates)."""
        fp = Path(file_path)
        source = fp.name
        loaded = PyPDFLoader(str(fp)).load()
        for d in loaded:
            d.metadata["source"] = source  # store filename only, not container path

        text_splitter = SemanticChunker(self.embeddings)
        docs = text_splitter.split_documents(loaded)
        docs = [d for d in docs if d.page_content and isinstance(d.page_content, str) and d.page_content.strip()]
        if not docs:
            raise ValueError(f"Tidak ada teks yang bisa diekstrak dari {source} (mungkin PDF hasil scan).")

        ids = [str(uuid5(NAMESPACE_URL, f"{source}::{i}")) for i in range(len(docs))]
        # Remove stale chunks of an older version of this file (may have had more chunks)
        self.delete_source(source)
        self.doc_store.add_documents(documents=docs, ids=ids)
        return len(docs)

    def load_documents(self, file_path):
        data_path = Path(file_path)
        if not data_path.exists(): 
            data_path.mkdir(parents=True, exist_ok=True)
            print(f"[RAG] Created directory: {data_path}. Place your PDF files here.")
            return 
        file_paths = [str(file) for file in data_path.glob('*.pdf')]
        print(f"Files found : {file_paths} ")
        print(f'loading documents of length {len(file_paths)}')
        for fp in file_paths:
            n = self.ingest_file(fp)
            print(f"[RAG] {Path(fp).name}: {n} chunks")

    def list_sources(self, collection_name='Documents'):
        """Return {source_filename: chunk_count} for everything in Qdrant."""
        counts = {}
        offset = None
        while True:
            points, offset = self.client.scroll(
                collection_name=collection_name,
                limit=256,
                offset=offset,
                with_payload=["metadata"],
                with_vectors=False,
            )
            for p in points:
                src = ((p.payload or {}).get("metadata") or {}).get("source", "unknown")
                src = os.path.basename(str(src))
                counts[src] = counts.get(src, 0) + 1
            if offset is None:
                break
        return counts

    def delete_source(self, source, collection_name='Documents'):
        self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[
                    models.FieldCondition(key="metadata.source", match=models.MatchValue(value=source))
                ])
            ),
        )

    def retrieve_documents(self, query): 
        results = self.doc_store.similarity_search(query, k=3)
        return [doc.page_content for doc in results]

    def _retriever_(self): 
        retriever = self.doc_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 1, "fetch_k": 2, "lambda_mult": 0.5},
        )
        return retriever
    
def main():
    logging.info('v5')
    vector_store = Vector_Store()
    # vector_store.load_documents(r'D:\Coding practice\Pertamina\AI_System_V2\RAG\Data')
    response = vector_store.retrieve_documents('Apa isi dari Daftar Isi RKS')
    print(response)

if __name__ == "__main__":
    main()



