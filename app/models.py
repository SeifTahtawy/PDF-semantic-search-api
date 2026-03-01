from pydantic import BaseModel
from typing import List


class SearchRequest(BaseModel):
    query: str 


class SearchResult(BaseModel):
    score: float
    page_number: int
    chunk_index: int
    source_file: str
    text: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class ErrorResponse(BaseModel):
    detail: str 


class IngestResponse(BaseModel):
    filename: str 
    pages_processed: int
    vectors_inserted: int 