from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from app.config import settings
import logging

logger = logging.getLogger("app")

qdrant_client = None



async def initialize_qdrant():
    global qdrant_client

    logger.info("Initializing Qdrant client...")

    qdrant_client = AsyncQdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        timeout=60.0
    )

    # collections = await qdrant_client.get_collections()
    # existing_collections = [c.name for c in collections.collections]
    # if "pdf_chunks" not in existing_collections:
    #     logger.info("No collections found. Creating collection...")

    EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2


    try:
        await qdrant_client.create_collection(
            collection_name="pdf_chunks",
            vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE,
            ),
        )

        logger.info("Collection created.")
    except UnexpectedResponse as e:
        if e.status_code == 409:
            logger.info("Collection already exists.")
        else:
            raise

    logger.info("Qdrant initialization complete.")