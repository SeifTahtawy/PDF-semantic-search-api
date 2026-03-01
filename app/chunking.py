from typing import List, Dict
import logging
from app.tracing import trace
logger = logging.getLogger("app")

@trace
def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 600,
    overlap: int = 100,
) -> List[Dict]:

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk_size.")

    chunks = []

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        start = 0
        chunk_index = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                    }
                )
                chunk_index += 1

            start += chunk_size - overlap

    logger.info(f"Created {len(chunks)} total chunks.")

    return chunks