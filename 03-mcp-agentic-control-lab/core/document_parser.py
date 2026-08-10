import io
from typing import List, Dict, Any, Union
import PyPDF2
from docx import Document
import tiktoken
import config

tokenizer = tiktoken.get_encoding("cl100k_base")

def extract_text_from_file(file_input: Union[str, bytes], filename: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT file input."""
    if isinstance(file_input, str):
        with open(file_input, "rb") as f:
            file_bytes = f.read()
    else:
        file_bytes = file_input

    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    elif filename_lower.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs if p.text])
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    return text

def chunk_text(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """Token-aware chunking with overlap using tiktoken."""
    tokens = tokenizer.encode(text)
    if not tokens:
        return []

    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text_str = tokenizer.decode(chunk_tokens)
        if chunk_text_str.strip():
            chunks.append(chunk_text_str.strip())

    return chunks
