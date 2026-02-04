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
        # 1. 도커 컨테이너 내부라면 /app/backend/chroma_db를 사용
        # 2. 로컬(윈도우 등)이라면 기존 로직대로 상대 경로 사용
        if os.path.exists("/app"):
            CHROMA_PATH = "/app/backend/chroma_db"
        else:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
            
        print(f"--- [DEBUG] ChromaDB Target Path: {CHROMA_PATH} ---")
        
        # 폴더 강제 생성 (권한 문제 방지)
        os.makedirs(CHROMA_PATH, exist_ok=True)
        
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
