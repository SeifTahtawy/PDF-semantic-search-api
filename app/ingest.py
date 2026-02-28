from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from qdrant_client.models import PointStruct
from app.pdf_parser import extract_text_from_pdf
from app.chunking import chunk_pages
from app.embedding import embed_chunks
from app.config import settings
import logging
import time
import uuid
import app.vector_db as vector_db


logger = logging.getLogger("app")

router = APIRouter()


@router.post("/ingest/", status_code=201)
async def ingest(input: UploadFile = File(...)):

    logger.info(f"Ingest request received | filename={input.filename}")

    if input.content_type != "application/pdf":
        logger.warning("Rejected file due to invalid content type.")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await input.read()

    if not file_bytes.startswith(b"%PDF"):
        logger.warning("Rejected file due to invalid PDF signature.")
        raise HTTPException(status_code=400, detail="Invalid PDF file.")

    filename = input.filename.replace(" ", "_")

    logger.info("Starting PDF Parsing...")
    pages = extract_text_from_pdf(file_bytes)
    logger.info(f"PDF parsing complete | Total pages = {len(pages)}")

    logger.info("Starting Text Chunking...")
    chunks = chunk_pages(pages)
    logger.info(f"Text chunking complete | Total chunks = {len(chunks)}")

    if not chunks:
        logger.warning("No chunks created from PDF")
        raise HTTPException(status_code=400, detail="No text extracted from PDF.")

    texts = [chunk["text"] for chunk in chunks]

    logger.info("Starting Embedding")
    embedding_start_time = time.perf_counter()

    embeddings = await run_in_threadpool(embed_chunks, texts)

    embedding_duration = 1000*(time.perf_counter() - embedding_start_time)
    logger.info(f"Embedding Complete | Total chunks = {len(chunks)} | Elapsed Time(ms) = {embedding_duration}")
    
    points = []

    for chunk, vector in zip(chunks, embeddings):
        raw_id = f"{filename}::{chunk['page_number']}::{chunk['chunk_index']}"
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))

        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "source_file": filename,
                    "text": chunk["text"],
                },
            )
        )

    logger.info("Upserting vector into Qdrant...")

    await vector_db.qdrant_client.upsert(
        collection_name="pdf_chunks",
        points=points,
    )
    

    logger.info(f"Upserting Complete | Total vectors = {len(points)}")
    logger.info(f"Ingest Complete | filename = {filename}")
    return {
        "filename": filename,
        "pages_processed": len(pages),
        "chunks_created": len(chunks),
        "vectors_inserted": len(points),
    }