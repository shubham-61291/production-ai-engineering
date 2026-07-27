import os
import re
from typing import List, Optional
from pypdf import PdfReader
from docx import Document

def normalize_whitespace(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def chunk_text(text: str, size_words: int = 350, overlap_words: int = 60, max_chunks: int = 120) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []

    words = text.split()
    step = max(1, size_words - overlap_words)

    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + size_words]).strip()
        if chunk:
            chunks.append(chunk)
        if len(chunks) >= max_chunks:
            break

    return chunks

def read_txt_like(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)

def read_docx(path: str) -> str:
    doc = Document(path)
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    return "\n".join(parts)

def extract_documents_text(files: Optional[List[object]]) -> str:
    if not files:
        return ""

    texts = []
    for f in files:
        if f is None:
            continue

        path = f.name if hasattr(f, "name") else str(f)
        ext = os.path.splitext(path.lower())[1]

        try:
            if ext == ".pdf":
                texts.append(read_pdf(path))
            elif ext == ".docx":
                texts.append(read_docx(path))
            elif ext in [".txt", ".md", ".html", ".htm"]:
                texts.append(read_txt_like(path))
            else:
                texts.append(read_txt_like(path))
        except Exception as e:
            texts.append(f"[ERROR READING FILE {os.path.basename(path)}: {e}]")

    return "\n\n".join(texts)
