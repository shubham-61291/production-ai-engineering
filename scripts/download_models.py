#!/usr/bin/env python3

import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import spacy

def main():
    print("Downloading DeBERTa-v3-base-prompt-injection...")
    tokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
    model = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection")
    os.makedirs("./models/deberta-v3-base-prompt-injection", exist_ok=True)
    tokenizer.save_pretrained("./models/deberta-v3-base-prompt-injection")
    model.save_pretrained("./models/deberta-v3-base-prompt-injection")

    print("Downloading all-MiniLM-L6-v2...")
    SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("Downloading spaCy en_core_web_sm...")
    spacy.cli.download("en_core_web_sm")

    print("All models downloaded successfully.")

if __name__ == "__main__":
    main()
