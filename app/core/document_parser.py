import re
from typing import List
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(file_path: str, ext: str) -> str:
    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(text: str, size_words: int = 350, overlap_words: int = 60, max_chunks: int = 120) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    words = text.split()
    step = max(1, size_words - overlap_words)
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+size_words])
        if chunk:
            chunks.append(chunk)
        if len(chunks) >= max_chunks:
            break
    return chunks
