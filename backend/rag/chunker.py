import hashlib
from typing import List

from backend.config import settings
from backend.rag.models import KnowledgeDocument, DocumentChunk, SourceMetadata


class DocumentChunker:
    """Splits knowledge documents into overlapping text chunks for vector indexing."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP

    def chunk_document(self, doc: KnowledgeDocument) -> List[DocumentChunk]:
        """Splits a single KnowledgeDocument into DocumentChunk list."""
        text = doc.content.strip()
        if not text:
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        text_length = len(text)
        index = 0

        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_hash = hashlib.md5(f"{doc.document_id}_{index}_{chunk_text[:30]}".encode("utf-8")).hexdigest()[:12]
                chunk_id = f"{doc.document_id}_c{index}_{chunk_hash}"

                meta = doc.metadata.model_copy()
                meta.chunk_id = chunk_id

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc.document_id,
                        text=chunk_text,
                        metadata=meta,
                    )
                )

            start += self.chunk_size - self.chunk_overlap
            index += 1

            # Prevent infinite loop if overlap >= size
            if self.chunk_size <= self.chunk_overlap:
                break

        return chunks

    def chunk_documents(self, docs: List[KnowledgeDocument]) -> List[DocumentChunk]:
        """Chunks a batch list of KnowledgeDocument objects."""
        all_chunks: List[DocumentChunk] = []
        for d in docs:
            all_chunks.extend(self.chunk_document(d))
        return all_chunks
