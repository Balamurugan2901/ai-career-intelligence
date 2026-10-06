from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceMetadata(BaseModel):
    """Metadata for source knowledge documents and chunks."""
    source: str = Field(default="Reference Knowledge Base", description="Source provider or dataset name")
    title: str = Field(default="Career Knowledge Document", description="Document title")
    role: Optional[str] = Field(default=None, description="Associated role name if applicable")
    document_type: str = Field(default="general", description="Category e.g. job_description, skill_dependency, career_guide")
    version: str = Field(default="1.0", description="Document schema version")
    file_path: Optional[str] = Field(default=None, description="Relative file path")
    chunk_id: Optional[str] = Field(default=None, description="Unique chunk identifier")


class KnowledgeDocument(BaseModel):
    """Raw knowledge document loaded from file."""
    document_id: str
    metadata: SourceMetadata
    content: str


class DocumentChunk(BaseModel):
    """Segmented chunk of a knowledge document for vector embedding."""
    chunk_id: str
    document_id: str
    text: str
    metadata: SourceMetadata


class RAGSearchResult(BaseModel):
    """Similarity search result item with score and preserved metadata."""
    chunk: DocumentChunk
    score: float = Field(description="Cosine similarity score (0.0 to 1.0)")
    source_metadata: SourceMetadata
