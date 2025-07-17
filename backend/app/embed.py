from sentence_transformers import SentenceTransformer
from typing import List

# Khởi tạo model 1 lần, cache toàn bộ
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed_text(text: str) -> List[float]:
    if not text.strip():
        raise ValueError("Empty input text for embedding.")
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()
