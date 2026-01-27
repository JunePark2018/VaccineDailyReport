import os
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# Singleton instances
_chroma_client = None
_embed_model = None
_collection = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        CHROMA_PATH = "./chroma_db"
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("--- [VectorStore] Loading SentenceTransformer Model... ---")
        _embed_model = SentenceTransformer("jhgan/ko-sroberta-multitask")
    return _embed_model

def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(name="news_articles_ko", metadata={"hnsw:space": "cosine"})
    return _collection

def encode_texts(texts: list[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts using the shared model.
    """
    model = get_embed_model()
    # normalize_embeddings=True is important for cosine similarity
    return model.encode(texts, normalize_embeddings=True)
