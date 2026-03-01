# PDF Semantic Search API

A containerized backend service for semantic search over PDF documents.

Built with **FastAPI**, **Qdrant**, and **Sentence Transformers**, this service enables ingestion of PDF files, transformation into vector embeddings, and similarity-based retrieval via a search endpoint.



## Architecture Overview

**Core components:**

* **Framework:** FastAPI (ASGI-based, async)
* **Vector Database:** Qdrant (async client)
* **Embedding Model:** `all-MiniLM-L6-v2` (Sentence Transformers)
* **PDF Parsing:** PyMuPDF
* **Containerization:** Docker + Docker Compose
* **Concurrency Model:** Multi-worker Uvicorn + async I/O


## System Design

### Ingestion Pipeline (`/ingest`)

The ingestion endpoint performs the following steps:

1. Accepts PDF files
2. Parses content using PyMuPDF
3. Splits text into semantic chunks
4. Generates embeddings using `all-MiniLM-L6-v2`
5. Upserts vectors into Qdrant

Example request:

```bash
curl -X POST "http://localhost:8000/ingest/" -F "input=@data/sample.pdf" 
``` 


### Batching Strategy

To prevent memory spikes during ingestion:

* Chunking and embedding are processed in batches
* Vector upserts to Qdrant are batched
* This ensures stable memory usage even with large PDFs


### Search Pipeline (`/search`)

The search endpoint:

1. Accepts a user query
2. Embeds the query using the same model
3. Performs similarity search in Qdrant
4. Returns the most relevant text chunks

Example request:

```bash
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does semantic search work?"}'
```


## Embedding Model

**Model:** `all-MiniLM-L6-v2`

* Lightweight transformer (384-dimensional embeddings)
* Optimized for semantic similarity tasks
* Good trade-off between speed and accuracy

The model loads at application startup.
Expect a short delay during first boot due to model initialization.


## Logging & Observability

Each request is assigned a **UUID** via middleware.

This request ID:

* Propagates through all internal function calls
* Is included in structured logs
* Logs execution duration per function

This allows:

* Per-request traceability
* Performance bottleneck detection
* High Observability

Example logged metadata:


## Concurrency Model

The application uses:

* **2 Uvicorn workers**
* FastAPI async event loop

### Why not 1 Worker?

Embedding generation is **CPU-bound**, while:

* Qdrant insertions
* Vector search operations

are **I/O-bound**.

Workers handle CPU-bound embedding tasks in parallel, while the async event loop efficiently handles I/O operations.

> You can increase worker count in `docker-compose.yml` depending on hardware capacity.


## Running the Application

### Start the system

```bash
./orchestrate.sh --action start
```

This will:

* Build containers
* Start Qdrant
* Start the FastAPI service

Model loading occurs during startup — allow time before sending requests.


### Terminate the system

```bash
./orchestrate.sh --action terminate
```


## API Endpoints

### `POST /ingest`

Uploads and processes PDF files.

**Process:**

* Parse → Chunk → Embed → Batch Upsert

---

### `POST /search`

Searches for semantically similar text.

**Request body:**

```json
{
  "query": "Your question here"
}
```

**Response:**
Returns top relevant text chunks from the vector database.

---

## Design Decisions

| Concern          | Decision                   |
| ---------------- | -------------------------- |
| Memory stability | Batched ingestion          |
| CPU-bound tasks  | Multi-worker Uvicorn       |
| I/O-bound tasks  | Async FastAPI              |
| Observability    | UUID-based request tracing |
| Deployment       | Dockerized environment     |
| Vector search    | Qdrant                     |




## Summary

This project implements a production-aware semantic search backend with:

* Efficient batching
* Clear concurrency separation (CPU vs I/O)
* Observability via request tracing
* Containerized reproducibility
* Clean separation of ingestion and retrieval pipelines
