from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware
from app.vector_db import initialize_qdrant
from app.logging_config import configure_logging
from app.embedding import initialize_embedding_model
from app.ingest import router as ingest_router
from app.search import router as search_router
import torch


app = FastAPI(title="PDF Semantic Search API")

app.add_middleware(RequestLoggingMiddleware)

app.include_router(ingest_router)
app.include_router(search_router)

@app.on_event("startup")
async def startup_event():
    configure_logging()
    torch.set_num_threads(1)
    initialize_embedding_model()
    await initialize_qdrant()


@app.get("/health")
def health():
    return{"status": "healthy"}