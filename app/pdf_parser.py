import fitz
import re 
import logging
from typing import List, Dict
from app.tracing import trace


logger = logging.getLogger("app")

def normalize_text(text: str) -> str:
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'^[\-\*\•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+[\.\)]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[a-zA-Z][\.\)]\s+', '', text, flags=re.MULTILINE)


    return text.strip()



@trace
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
        
        text = normalize_text(text)

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