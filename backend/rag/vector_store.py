import os
import joblib
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.config import settings
from backend.rag.models import DocumentChunk, RAGSearchResult, SourceMetadata
from backend.utils.logger import logger


class LocalVectorStore:
    """
    Lightweight, persistent local vector store using NumPy dot-product cosine similarity.
    Persists vectors, chunk metadata, and document text to disk in data/vector_store/index.joblib.
    """

    def __init__(self, store_dir: str = "data/vector_store"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.store_dir / "vector_index.joblib"

        self.chunks: List[DocumentChunk] = []
        self.vectors: Optional[np.ndarray] = None  # Matrix of shape (N, Dim)

        self.load()

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        """Adds document chunks and corresponding dense vectors to store."""
        if not chunks or embeddings.size == 0:
            return

        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Chunks length and embeddings rows must match.")

        self.chunks.extend(chunks)
        if self.vectors is None or self.vectors.size == 0:
            self.vectors = embeddings.astype(np.float32)
        else:
            # Handle potential dimension mismatch by padding if necessary
            if self.vectors.shape[1] != embeddings.shape[1]:
                target_dim = max(self.vectors.shape[1], embeddings.shape[1])
                self.vectors = self._pad_matrix(self.vectors, target_dim)
                embeddings = self._pad_matrix(embeddings, target_dim)
            self.vectors = np.vstack([self.vectors, embeddings.astype(np.float32)])

        self.save()

    def _pad_matrix(self, mat: np.ndarray, target_dim: int) -> np.ndarray:
        """Pads matrix columns with zeros to match target dimension."""
        if mat.shape[1] >= target_dim:
            return mat
        pad_width = target_dim - mat.shape[1]
        return np.pad(mat, ((0, 0), (0, pad_width)), mode="constant")

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = None,
        role: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[RAGSearchResult]:
        """
        Executes Cosine Similarity search over local vector matrix.
        Returns top_k matching RAGSearchResult items with preserved SourceMetadata.
        """
        top_k = top_k or settings.RAG_TOP_K
        if self.vectors is None or len(self.chunks) == 0:
            return []

        query_vec = query_vector.flatten()
        target_dim = self.vectors.shape[1]
        if len(query_vec) < target_dim:
            query_vec = np.pad(query_vec, (0, target_dim - len(query_vec)))
        elif len(query_vec) > target_dim:
            query_vec = query_vec[:target_dim]

        # L2 norm query
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        # Cosine similarity dot product
        similarities = np.dot(self.vectors, query_vec)

        # Filter indices based on role or document_type
        filtered_indices = []
        for idx, chunk in enumerate(self.chunks):
            if role and chunk.metadata.role:
                if role.lower() not in chunk.metadata.role.lower() and chunk.metadata.role.lower() not in role.lower():
                    continue
            if document_type and chunk.metadata.document_type:
                if document_type.lower() != chunk.metadata.document_type.lower():
                    continue
            filtered_indices.append(idx)

        if not filtered_indices:
            # Fallback to unfiltered search if filtered search returned no matches
            filtered_indices = list(range(len(self.chunks)))

        # Sort filtered by similarity score descending
        sorted_indices = sorted(filtered_indices, key=lambda i: similarities[i], reverse=True)
        top_indices = sorted_indices[:top_k]

        results: List[RAGSearchResult] = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk = self.chunks[idx]
            results.append(
                RAGSearchResult(
                    chunk=chunk,
                    score=max(0.0, min(1.0, (score + 1.0) / 2.0 if score < 0 else score)),
                    source_metadata=chunk.metadata,
                )
            )

        return results

    def save(self):
        """Persists vector matrix and chunk metadata to disk."""
        data = {
            "chunks": [c.model_dump() for c in self.chunks],
            "vectors": self.vectors,
        }
        joblib.dump(data, self.index_path)
        logger.info(f"Persisted LocalVectorStore ({len(self.chunks)} chunks) to {self.index_path}")

    def load(self):
        """Loads persistent vector matrix and chunk metadata from disk."""
        if self.index_path.exists():
            try:
                data = joblib.load(self.index_path)
                chunk_dicts = data.get("chunks", [])
                self.chunks = [DocumentChunk(**cd) for cd in chunk_dicts]
                self.vectors = data.get("vectors")
                logger.info(f"Loaded LocalVectorStore with {len(self.chunks)} chunks from disk.")
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")
                self.chunks = []
                self.vectors = None

    def clear(self):
        """Clears in-memory and on-disk index."""
        self.chunks = []
        self.vectors = None
        if self.index_path.exists():
            try:
                os.remove(self.index_path)
            except Exception:
                pass
