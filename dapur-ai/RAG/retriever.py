from qdrant_client import QdrantClient, models
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
import os 
import config

embedding_model = config.EMBEDDING_MODEL

def retriever(text, collection_name='Documents', embed_model=embedding_model):
    QdrantClient(
            url=os.getenv('QDRANT_CLUSTER_ENDPOINT'),
            api_key=os.getenv("QDRANT_API_KEY"),
            cloud_inference=True
        )  
    QdrantVectorStore.from_existing_collection(
        collection_name=collection_name,
        embedding=embed_model
    )