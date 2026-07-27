import os
import json
import threading
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from rank_bm25 import BM25Okapi
from app.core.config import settings

rag_lock = threading.Lock()

class RAGStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        os.makedirs(settings.BM25_DATA_DIR, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name="magnetar_documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.bm25_file = os.path.join(settings.BM25_DATA_DIR, "bm25_store.json")
        self.documents: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        self._load_bm25()

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def _load_bm25(self):
        with rag_lock:
            if os.path.exists(self.bm25_file):
                try:
                    with open(self.bm25_file, "r", encoding="utf-8") as f:
                        self.documents = json.load(f)
                    if self.documents:
                        corpus = [self._tokenize(doc["text"]) for doc in self.documents]
                        self.bm25 = BM25Okapi(corpus)
                except Exception:
                    self.documents = []
                    self.bm25 = None

    def _save_bm25(self):
        with open(self.bm25_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def add_chunks(self, doc_id: str, chunks: List[str], metadata: Dict[str, Any]):
        with rag_lock:
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{**metadata, "chunk_index": i, "doc_id": doc_id} for i in range(len(chunks))]
            
            self.collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )

            for i, chunk in enumerate(chunks):
                self.documents.append({
                    "id": ids[i],
                    "doc_id": doc_id,
                    "text": chunk,
                    "metadata": metadatas[i]
                })

            corpus = [self._tokenize(doc["text"]) for doc in self.documents]
            if corpus:
                self.bm25 = BM25Okapi(corpus)
            self._save_bm25()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        with rag_lock:
            results_dict = {}

            # Vector Search via Chroma
            try:
                chroma_res = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
                if chroma_res and chroma_res["documents"] and chroma_res["documents"][0]:
                    docs = chroma_res["documents"][0]
                    metas = chroma_res["metadatas"][0] if chroma_res["metadatas"] else [{}] * len(docs)
                    dists = chroma_res["distances"][0] if chroma_res["distances"] else [0.0] * len(docs)
                    
                    for doc, meta, dist in zip(docs, metas, dists):
                        text_key = doc
                        score = max(0.0, 1.0 - dist)
                        results_dict[text_key] = {
                            "text": doc,
                            "metadata": meta,
                            "score": score,
                            "source": "vector"
                        }
            except Exception:
                pass

            # BM25 Search
            if self.bm25 and self.documents:
                tokens = self._tokenize(query)
                bm25_scores = self.bm25.get_scores(tokens)
                top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
                
                for idx in top_indices:
                    if bm25_scores[idx] > 0:
                        doc_item = self.documents[idx]
                        text_key = doc_item["text"]
                        score = float(bm25_scores[idx])
                        if text_key in results_dict:
                            results_dict[text_key]["score"] += score
                            results_dict[text_key]["source"] = "hybrid"
                        else:
                            results_dict[text_key] = {
                                "text": doc_item["text"],
                                "metadata": doc_item["metadata"],
                                "score": score,
                                "source": "bm25"
                            }

            ranked = sorted(results_dict.values(), key=lambda x: x["score"], reverse=True)
            return ranked[:top_k]

    def delete_document(self, doc_id: str):
        with rag_lock:
            # Delete from ChromaDB
            try:
                self.collection.delete(where={"doc_id": doc_id})
            except Exception:
                pass

            # Delete from BM25 storage
            self.documents = [d for d in self.documents if d.get("doc_id") != doc_id]
            if self.documents:
                corpus = [self._tokenize(doc["text"]) for doc in self.documents]
                self.bm25 = BM25Okapi(corpus)
            else:
                self.bm25 = None
            self._save_bm25()

rag_store = RAGStore()
collection = rag_store.collection
