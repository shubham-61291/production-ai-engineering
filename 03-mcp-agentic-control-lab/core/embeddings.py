from typing import List
from sentence_transformers import SentenceTransformer
import config

class EmbeddingEngine:
    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME):
        print(f"[INFO] Loading Embedding Model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

_embedding_engine_instance = None

def get_embedding_engine() -> EmbeddingEngine:
    global _embedding_engine_instance
    if _embedding_engine_instance is None:
        _embedding_engine_instance = EmbeddingEngine()
    return _embedding_engine_instance
