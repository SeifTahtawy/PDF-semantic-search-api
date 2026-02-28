import fitz  # PyMuPDF
import logging
from typing import List, Dict

logger = logging.getLogger("app")


def extract_text_from_pdf(file_bytes: bytes) -> List[Dict]:

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        logger.error(f"Failed to open PDF: {str(e)}")
        raise RuntimeError("Invalid or corrupted PDF file.")

    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text()

        
        text = text.strip()

        if not text:
            continue  

        pages.append(
            {
                "page_number": page_index + 1,
                "text": text,
            }
        )

    doc.close()

    logger.info(f"Extracted text from {len(pages)} non-empty pages.")

    return pages