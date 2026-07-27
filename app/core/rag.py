import logging
import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = logging.getLogger(__name__)

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
    return _embedder

_qdrant_client = None

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=settings.QDRANT_URL)
    return _qdrant_client

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def init_qdrant_collection():
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info("Qdrant collection created")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")

def embed_texts(texts: List[str]) -> List[List[float]]:
    embedder = get_embedder()
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def store_chunks(chunks: List[Dict[str, Any]], session_id: str) -> int:
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    points = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        payload = {
            "text": chunk["text"],
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "session_id": session_id,
            "timestamp": chunk["timestamp"]
        }
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{session_id}_{chunk['filename']}_{i}"))
        point = qdrant_models.PointStruct(
            id=point_id,
            vector=vec,
            payload=payload
        )
        points.append(point)

    client = get_qdrant_client()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    return len(points)

def retrieve_chunks(query: str, session_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
    query_vec = embed_texts([query])[0]
    client = get_qdrant_client()
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k,
        query_filter=qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(
                key="session_id",
                match=qdrant_models.MatchValue(value=session_id)
            )]
        )
    )
    return [hit.payload for hit in search_result]
