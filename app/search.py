from app.models import SearchRequest
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.embedding import embed_chunks
from app.config import settings
from app.models import SearchRequest, SearchResponse, SearchResult
import app.vector_db as vector_db
import logging

logger = logging.getLogger("app")

router = APIRouter()


@router.post("/search/", response_model=SearchResponse)
async def search(request: SearchRequest):

    logger.info(f"Search request received | query='{request.query}'")
    if not request.query.strip():
        logger.info("Query is empty")
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    logger.info("Embedding Query...")
    query_vector = await run_in_threadpool(embed_chunks, [request.query])
    query_vector = query_vector[0]

    logger.info("Searching for results...")
    search_result = await vector_db.qdrant_client.search(
        collection_name="pdf_chunks",
        query_vector=query_vector,
        limit=5,
        with_payload=True,
    )

    results = []

    for point in search_result:
        payload = point.payload

        results.append(
            SearchResult(
                score=point.score,
                page_number=payload["page_number"],
                chunk_index=payload["chunk_index"],
                source_file=payload["source_file"],
                text=payload["text"],
            )
        )

    logger.info(f"Search complete | returned_results={len(results)}")

    return SearchResponse(
        query=request.query,
        results=results,
    )
