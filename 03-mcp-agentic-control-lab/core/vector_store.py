import time
import numpy as np
from typing import List, Dict, Any, Optional
import config
from core.embeddings import get_embedding_engine

class VectorStoreBase:
    def upsert(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> int:
        raise NotImplementedError

    def query(self, query_text: str, top_k: int = 3, min_score: float = 0.50) -> List[Dict[str, Any]]:
        raise NotImplementedError

class InMemoryVectorStore(VectorStoreBase):
    """Zero-dependency In-Memory Vector Store fallback."""
    def __init__(self):
        print("[INFO] Using In-Memory Vector Store Engine (Cosine Similarity)...")
        self.embedder = get_embedding_engine()
        self.documents: List[Dict[str, Any]] = []

    def upsert(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> int:
        if not texts:
            return 0
        embeddings = self.embedder.encode_batch(texts)
        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            meta = metadata[i] if metadata and i < len(metadata) else {"text": text}
            meta["text"] = text
            self.documents.append({
                "id": f"doc_{int(time.time()*1000)}_{i}",
                "text": text,
                "vector": np.array(emb, dtype=np.float32),
                "metadata": meta
            })
        return len(texts)

    def query(self, query_text: str, top_k: int = 3, min_score: float = 0.50) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        
        qv = np.array(self.embedder.encode(query_text), dtype=np.float32)
        qv_norm = np.linalg.norm(qv)
        if qv_norm == 0:
            return []

        results = []
        for doc in self.documents:
            vec = doc["vector"]
            v_norm = np.linalg.norm(vec)
            if v_norm == 0:
                continue
            sim = float(np.dot(qv, vec) / (qv_norm * v_norm))
            sim = round(sim, 3)
            if sim >= min_score:
                results.append({"text": doc["text"], "score": sim})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

class ChromaVectorStore(VectorStoreBase):
    def __init__(self, persist_dir: str = config.CHROMA_PERSIST_DIR):
        import chromadb
        print(f"[INFO] Initializing Persistent ChromaDB at: {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="mcp_policy_index",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = get_embedding_engine()

    def upsert(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> int:
        if not texts:
            return 0
        
        embeddings = self.embedder.encode_batch(texts)
        ids = [f"doc_{int(time.time()*1000)}_{i}" for i in range(len(texts))]
        metas = metadata if metadata is not None else [{"text": t} for t in texts]
        
        for m, t in zip(metas, texts):
            m["text"] = t

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metas
        )
        return len(texts)

    def query(self, query_text: str, top_k: int = 3, min_score: float = 0.50) -> List[Dict[str, Any]]:
        qv = self.embedder.encode(query_text)
        results = self.collection.query(
            query_embeddings=[qv],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        matches = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, distances):
                similarity = round(1.0 - float(dist), 3)
                if similarity >= min_score:
                    text_content = meta.get("text", doc)
                    matches.append({"text": text_content, "score": similarity})

        return sorted(matches, key=lambda x: x["score"], reverse=True)

class PineconeVectorStore(VectorStoreBase):
    def __init__(self):
        from pinecone import Pinecone, ServerlessSpec
        print("[INFO] Connecting to Pinecone Cloud Vector Store...")
        self.embedder = get_embedding_engine()
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)

        existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
        if config.PINECONE_INDEX_NAME not in existing_indexes:
            self.pc.create_index(
                name=config.PINECONE_INDEX_NAME,
                dimension=self.embedder.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=config.PINECONE_REGION)
            )

        index_desc = self.pc.describe_index(config.PINECONE_INDEX_NAME)
        self.pinecone_index = self.pc.Index(host=index_desc["host"])

    def upsert(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> int:
        if not texts:
            return 0
        
        vectors = []
        for i, text in enumerate(texts):
            emb = self.embedder.encode(text)
            meta = metadata[i] if metadata and i < len(metadata) else {"text": text}
            meta["text"] = text
            vectors.append((f"doc_{int(time.time()*1000)}_{i}", emb, meta))

        self.pinecone_index.upsert(vectors)
        return len(texts)

    def query(self, query_text: str, top_k: int = 3, min_score: float = 0.50) -> List[Dict[str, Any]]:
        qv = self.embedder.encode(query_text)
        res = self.pinecone_index.query(vector=qv, top_k=top_k, include_metadata=True)

        matches = []
        for m in res.matches:
            score = round(float(m.score), 3)
            if score >= min_score:
                matches.append({"text": m.metadata.get("text", ""), "score": score})
        return matches

_vector_store_instance = None

def get_vector_store() -> VectorStoreBase:
    global _vector_store_instance
    if _vector_store_instance is None:
        if config.VECTOR_STORE_PROVIDER == "pinecone":
            try:
                _vector_store_instance = PineconeVectorStore()
            except Exception as e:
                print(f"[WARNING] Pinecone vector store initialization failed ({e}). Falling back to In-Memory store.")
                _vector_store_instance = InMemoryVectorStore()
        elif config.VECTOR_STORE_PROVIDER == "chroma":
            try:
                _vector_store_instance = ChromaVectorStore()
            except ImportError:
                print("[WARNING] ChromaDB package not found. Falling back to zero-dependency In-Memory store.")
                _vector_store_instance = InMemoryVectorStore()
            except Exception as e:
                print(f"[WARNING] ChromaDB initialization error ({e}). Falling back to In-Memory store.")
                _vector_store_instance = InMemoryVectorStore()
        else:
            _vector_store_instance = InMemoryVectorStore()
    return _vector_store_instance
