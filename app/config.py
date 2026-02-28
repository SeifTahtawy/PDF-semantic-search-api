from pydantic import BaseModel
import os


class Settings(BaseModel):
    qdrant_host: str
    qdrant_port: int
    embedding_model_name: str
    log_file_path: str


settings = Settings(
    qdrant_host=os.getenv("QDRANT_HOST"),
    qdrant_port=int(os.getenv("QDRANT_PORT")),
    embedding_model_name=os.getenv("EMBEDDING_MODEL_NAME"),
    log_file_path=os.getenv("LOG_FILE_PATH"),
)