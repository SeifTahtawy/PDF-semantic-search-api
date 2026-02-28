from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logger = logging.getLogger("app")

_model = None


def initialize_embedding_model() -> None:
    global _model

    if _model is not None:
        return

    logger.info(f"Loading embedding model: {settings.embedding_model_name}")

    _model = SentenceTransformer(settings.embedding_model_name)

    logger.info("Embedding model loaded successfully.")


def get_embedding_dimension() -> int:
    if _model is None:
        raise RuntimeError("Embedding model is not initialized.")
    return _model.get_sentence_embedding_dimension()


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    if _model is None:
        raise RuntimeError("Embedding model is not initialized.")

    embeddings = _model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()