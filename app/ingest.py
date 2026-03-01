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
from app.tracing import trace



logger = logging.getLogger("app")

router = APIRouter()


@router.post("/ingest/", status_code=201)
@trace
async def ingest(input: UploadFile = File(...)):

    

    if input.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await input.read()

    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Invalid PDF file.")

    filename = input.filename.replace(" ", "_")
    pages = extract_text_from_pdf(file_bytes)
    

    chunk_batch = []
    BATCH_SIZE = 64
    total_vectors = 0
    logger.info("Starting streaming ingestion...")

    for page in pages:

        page_chunks = chunk_pages([page])

        for chunk in page_chunks:
            chunk_batch.append(chunk)

            if len(chunk_batch) >= BATCH_SIZE:
                texts = [c["text"] for c in chunk_batch]
                embeddings = embed_chunks(texts)

                points = []
                for c, vector in zip(chunk_batch, embeddings):
                    raw_id = f"{filename}::{c['page_number']}::{c['chunk_index']}"
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))

                    points.append(
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "page_number": c["page_number"],
                                "chunk_index": c["chunk_index"],
                                "source_file": filename,
                                "text": c["text"],
                            },
                        )
                    )

                
                await vector_db.qdrant_client.upsert(
                    collection_name="pdf_chunks",
                    points=points,
                )

                total_vectors += len(points)
                logger.info(f"Upserted batch | Size = {len(points)}")

                chunk_batch.clear()

    if chunk_batch:

        texts = [c["text"] for c in chunk_batch]
        embeddings = embed_chunks(texts)

        points = []
        for c, vector in zip(chunk_batch, embeddings):
            raw_id = f"{filename}::{c['page_number']}::{c['chunk_index']}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "page_number": c["page_number"],
                        "chunk_index": c["chunk_index"],
                        "source_file": filename,
                        "text": c["text"],
                    },
                )
            )

        await vector_db.qdrant_client.upsert(
            collection_name="pdf_chunks",
            points=points,
        )

        total_vectors += len(points)
        logger.info(f"Upserted final batch | Size = {len(points)}")

    # if not chunks:
    #     logger.warning("No chunks created from PDF")
    #     raise HTTPException(status_code=400, detail="No text extracted from PDF.")

    # texts = [chunk["text"] for chunk in chunks]

    
    # embedding_start_time = time.perf_counter()

    # embeddings = embed_chunks(texts)

    # embedding_duration = 1000*(time.perf_counter() - embedding_start_time)
    
    
    # logger.info("Upserting vectors into Qdrant (batched)...")


    # for i in range(0, len(chunks), BATCH_SIZE):
    #     batch_chunks = chunks[i:i + BATCH_SIZE]
    #     batch_embeddings = embeddings[i:i + BATCH_SIZE]

    #     batch_points = []

    #     for chunk, vector in zip(batch_chunks, batch_embeddings):
    #         raw_id = f"{filename}::{chunk['page_number']}::{chunk['chunk_index']}"
    #         point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))

    #         batch_points.append(
    #             PointStruct(
    #                 id=point_id,
    #                 vector=vector,
    #                 payload={
    #                     "page_number": chunk["page_number"],
    #                     "chunk_index": chunk["chunk_index"],
    #                     "source_file": filename,
    #                     "text": chunk["text"],
    #                 },
    #             )
    #         )

    #     await vector_db.qdrant_client.upsert(
    #         collection_name="pdf_chunks",
    #         points=batch_points,
    #     )

    #     total_vectors += len(batch_points)
    

    logger.info(f"Upserting Complete | Total vectors = {len(points)}")
    
    return {
        "filename": filename,
        "pages_processed": len(pages),
        "vectors_inserted": len(points),
    }