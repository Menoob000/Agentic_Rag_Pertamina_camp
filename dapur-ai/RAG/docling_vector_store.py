from qdrant_client import QdrantClient, models
import os 
os.environ["DOCLING_ALLOW_EXTERNAL_PLUGINS"] = "true"
from dotenv import load_dotenv
from config import EMBEDDING_MODEL
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
# from langchain_docling.loader import DoclingLoader
from langchain_core.documents import Document
from pathlib import Path
from docling.chunking import HybridChunker
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from uuid import uuid4
import logging
from docling.document_converter import DocumentConverter

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
pipeline_options.allow_external_plugins = True
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

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
                    size=2560,  # Vector size is defined by used model Qwen3.8/embeddings
                    distance=models.Distance.COSINE,
                ),
            )

        embeddings = OpenAIEmbeddings(
            model=embed_model,
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base="https://openrouter.ai/api/v1",
            tiktoken_enabled=False,
            )

        self.doc_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=embeddings,
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

        # Old LangChain wrapper approach (commented out for reference):
        # self.loader = DoclingLoader(
        #     file_path=file_paths,
        #     chunker=HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2", max_tokens=510),
        #     converter=doc_converter
        # )
        # self.docs = self.loader.load()
        # self.docs = [doc for doc in self.docs if doc.page_content and isinstance(doc.page_content, str)]

        chunker = HybridChunker(
            tokenizer="sentence-transformers/all-MiniLM-L6-v2",
            max_tokens=510
        )

        all_docs = []
        for fp in file_paths:
            print(f"Processing: {fp}")
            conv_res = doc_converter.convert(fp)
            for chunk in chunker.chunk(conv_res.document):
                if chunk.text and isinstance(chunk.text, str):
                    all_docs.append(
                        Document(page_content=chunk.text, metadata={"source": fp})
                    )
                    
        self.docs = all_docs
        print(f"Successfully chunked into {len(self.docs)} chunks.")
        
        uuids = [str(uuid4()) for _ in range(len(self.docs))]
        self.doc_store.add_documents(
            documents=self.docs,
            ids=uuids
        )

    def retrieve_documents(self, query): 
        results = self.doc_store.similarity_search(query)
        return results
    
def main():
    logging.info('v5')
    vector_store = Vector_Store()
    vector_store.load_documents(r'D:\Coding practice\Pertamina\AI_System_V2\RAG\Data')
    response = vector_store.retrieve_documents('Apa isi dari Daftar Isi RKS')
    print(response)

if __name__ == "__main__":
    main()



