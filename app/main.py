from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware
from app.vector_db import initialize_qdrant

app = FastAPI(title="PDF Semantic Search API")

app.add_middleware(RequestLoggingMiddleware)

@app.on_event("startup")
def startup_event():
    initialize_qdrant()


@app.get("/health")
def health():
    return{"status": "healthy"}