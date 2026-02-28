from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config import settings
from app.embedding import get_embedding_dimension
import logging

logger = logging.getLogger("app")

qdrant_client = None



def initialize_qdrant():
    global qdrant_client

    logger.info("Initializing Qdrant client...")

    qdrant_client = QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )

    collections = qdrant_client.get_collections()

    if not collections.collections:
        logger.info("No collections found. Creating collection...")

        EMBEDDING_DIMENSION = get_embedding_dimension()  # all-MiniLM-L6-v2

        qdrant_client.create_collection(
            collection_name="pdf_chunks",
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )

        logger.info("Collection created.")
    else:
        logger.info("Collection already exists.")

    logger.info("Qdrant initialization complete.")