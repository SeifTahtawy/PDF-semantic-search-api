from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware

app = FastAPI(title="PDF Semantic Search API")
app.add_middleware(RequestLoggingMiddleware)
@app.get("/health")
def health():
    return{"status": "healthy"}