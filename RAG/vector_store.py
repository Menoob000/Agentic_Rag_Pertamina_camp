from qdrant_client import QdrantClient, models
import os 
os.environ["DOCLING_ALLOW_EXTERNAL_PLUGINS"] = "true"
from dotenv import load_dotenv
from config import EMBEDDING_MODEL
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from pathlib import Path
from uuid import uuid4
import logging
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import PyPDFLoader

embedding_model = EMBEDDING_MODEL # Default is qwen/qwen3-embedding-4b
load_dotenv()


class Vector_Store():
    def __init__(self, collection_name='Documents', embed_model=embedding_model):
      
        self.client = QdrantClient(
            url=os.getenv('QDRANT_CLUSTER_ENDPOINT'),
            api_key=os.getenv("QDRANT_API_KEY"),
            cloud_inference=True
        )

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384 ,  # Vector size is defined by used model Qwen3.8/embeddings
                    distance=models.Distance.COSINE,
                ),
            )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model
        )

        self.doc_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

    def load_documents(self, file_path):
        data_path = Path(file_path)
        if not data_path.exists(): 
            data_path.mkdir(parents=True, exist_ok=True)
            print(f"[RAG] Created directory: {data_path}. Place your PDF files here.")
            return 
        file_paths = [str(file) for file in data_path.glob('*.pdf')]
        print(f"Files found : {file_paths} ")
        print(f'loading documents of length {len(file_paths)}')

        all_loaded_docs = []
        for fp in file_paths:
            loader = PyPDFLoader(fp)
            all_loaded_docs.extend(loader.load())

        text_splitter = SemanticChunker(self.embeddings)
        self.docs = text_splitter.split_documents(all_loaded_docs)
        
        self.docs = [doc for doc in self.docs if doc.page_content and isinstance(doc.page_content, str)]
        
        uuids = [str(uuid4()) for _ in range(len(self.docs))]
        self.doc_store.add_documents(
            documents=self.docs,
            ids=uuids
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



