import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List

from backend.rag.loader import DocumentLoader
from backend.rag.chunker import DocumentChunker
from backend.rag.embeddings import LightweightEmbeddingEngine
from backend.rag.vector_store import LocalVectorStore
from backend.utils.logger import logger


class KnowledgeIndexer:
    """
    Builds and updates the local RAG knowledge index.
    Tracks document content hashes to prevent unnecessary re-embedding on startup.
    """

    def __init__(
        self,
        knowledge_dir: str = "data/knowledge",
        vector_dir: str = "data/vector_store",
    ):
        self.knowledge_dir = knowledge_dir
        self.vector_dir = Path(vector_dir)
        self.hash_path = self.vector_dir / "knowledge_hash.json"

        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embedding_engine = LightweightEmbeddingEngine(vector_dir=vector_dir)
        self.vector_store = LocalVectorStore(store_dir=vector_dir)

    def compute_knowledge_hash(self) -> str:
        """Computes aggregate MD5 hash of all documents in knowledge directory."""

        hasher = hashlib.md5()
        base_path = Path(self.knowledge_dir)
        if not base_path.exists():
            return ""

        for file_path in sorted(base_path.rglob("*")):
            if file_path.is_file() and file_path.suffix.lower() in [".json", ".md"]:
                hasher.update(file_path.name.encode("utf-8"))
                with open(file_path, "rb") as f:
                    hasher.update(f.read())
        return hasher.hexdigest()

    def build_index(self, force_rebuild: bool = False) -> int:
        """
        Builds or refreshes the local vector index.
        Skips indexing if document content hash has not changed unless force_rebuild is True.
        Returns total number of chunks indexed.
        """
        current_hash = self.compute_knowledge_hash()
        cached_hash = self._get_cached_hash()

        if not force_rebuild and current_hash and current_hash == cached_hash and len(self.vector_store.chunks) > 0:
            logger.info("Knowledge index is up-to-date. Skipping re-indexing.")
            return len(self.vector_store.chunks)

        logger.info("Building/updating local RAG knowledge vector index...")

        # 1. Load documents
        docs = self.loader.load_directory(self.knowledge_dir)
        if not docs:
            logger.warning("No knowledge documents found for indexing.")
            return 0

        # 2. Chunk documents
        chunks = self.chunker.chunk_documents(docs)
        if not chunks:
            logger.warning("No chunks created from loaded documents.")
            return 0

        # 3. Fit embedding engine & generate embeddings
        texts = [c.text for c in chunks]
        self.embedding_engine.fit(texts)
        embeddings = self.embedding_engine.embed_documents(texts)

        # 4. Save to vector store
        self.vector_store.clear()
        self.vector_store.add_chunks(chunks, embeddings)

        # 5. Save cached hash
        self._save_cached_hash(current_hash)

        logger.info(f"Successfully built local RAG knowledge index with {len(chunks)} chunks.")
        return len(chunks)

    def _get_cached_hash(self) -> Optional[str]:
        if self.hash_path.exists():
            try:
                with open(self.hash_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("hash")
            except Exception:
                pass
        return None

    def _save_cached_hash(self, hash_val: str):
        try:
            with open(self.hash_path, "w", encoding="utf-8") as f:
                json.dump({"hash": hash_val}, f)
        except Exception as e:
            logger.warning(f"Failed to save knowledge hash: {e}")
