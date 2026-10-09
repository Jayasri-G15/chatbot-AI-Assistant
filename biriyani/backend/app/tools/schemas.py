from typing import Optional
from pydantic import BaseModel, Field


class RAGSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="The search query for document RAG retrieval.")
    top_k: int = Field(default=5, ge=1, le=10, description="Maximum number of document chunks to retrieve.")


class WebSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, description="The query string for web intelligence search.")
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum web search results to return.")


class DataAnalysisInput(BaseModel):
    data_or_text: str = Field(..., min_length=1, max_length=10000, description="CSV tabular text or numerical expressions to inspect.")


class SearchUsersInput(BaseModel):
    query: Optional[str] = Field(default=None, max_length=100, description="Name or email search query for users.")
    role: Optional[str] = Field(default=None, max_length=20, description="Filter by user role (USER, ADMIN).")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum user records to return.")


class EmptyInput(BaseModel):
    pass
