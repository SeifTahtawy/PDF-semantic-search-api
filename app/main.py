from fastapi import FastAPI

app = FastAPI(title="PDF Semantic Search API")

@app.get("/health")
def health():
    return{"status": "healthy"}