from app.models import SearchRequest
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.embedding import embed_chunks
from app.config import settings
from app.models import SearchRequest, SearchResponse, SearchResult
import app.vector_db as vector_db
import logging
from app.tracing import trace


logger = logging.getLogger("app")

router = APIRouter()


@router.post("/search/", response_model=SearchResponse)
@trace
async def search(request: SearchRequest):

    
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    query_vector = await run_in_threadpool(embed_chunks, [request.query])
    query_vector = query_vector[0]

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

    

    return SearchResponse(
        query=request.query,
        results=results,
    )
