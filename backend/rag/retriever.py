from typing import List, Optional

from backend.config import settings
from backend.rag.models import RAGSearchResult, SourceMetadata
from backend.rag.embeddings import LightweightEmbeddingEngine
from backend.rag.vector_store import LocalVectorStore
from backend.rag.indexer import KnowledgeIndexer
from backend.utils.logger import logger


class RAGRetriever:
    """
    High-level RAG Retrieval Engine.
    Queries the persistent vector store using lightweight CPU embedding similarities
    and returns top matching context chunks with strictly preserved source metadata.
    """

    def __init__(
        self,
        knowledge_dir: str = "data/knowledge",
        vector_dir: str = "data/vector_store",
    ):
        self.vector_dir = vector_dir
        self.indexer = KnowledgeIndexer(knowledge_dir=knowledge_dir, vector_dir=vector_dir)
        self.embedding_engine = self.indexer.embedding_engine
        self.vector_store = self.indexer.vector_store

        # Ensure index is built on initialization
        self._ensure_index()

    def _ensure_index(self):
        """Ensures knowledge vector index exists."""
        if len(self.vector_store.chunks) == 0:
            self.indexer.build_index()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        role: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[RAGSearchResult]:
        """
        Retrieves top-k relevant knowledge chunks for a search query.
        Preserves source metadata (source, title, role, document_type, file_path).
        """
        if not settings.RAG_ENABLED:
            logger.info("RAG is disabled in configuration settings.")
            return []

        if not query or not query.strip():
            logger.warning("Empty query passed to RAGRetriever. Returning empty results.")
            return []

        top_k = top_k or settings.RAG_TOP_K
        self._ensure_index()

        try:
            # Embed query text
            query_vector = self.embedding_engine.embed_text(query.strip())
            results = self.vector_store.search(
                query_vector=query_vector,
                top_k=top_k,
                role=role,
                document_type=document_type,
            )
            logger.info(f"RAGRetriever retrieved {len(results)} relevant chunks for query: '{query[:40]}...'")
            return results
        except Exception as e:
            logger.error(f"Error during RAG retrieval: {e}")
            return []

    def format_context_and_sources(self, results: List[RAGSearchResult]):
        """Formats RAGSearchResult list into prompt context text string and source metadata dict list."""
        if not results:
            return "", []

        context_lines = []
        sources = []
        seen_titles = set()

        for idx, res in enumerate(results, 1):
            meta = res.source_metadata
            title = meta.title or f"Source {idx}"
            chunk_text = res.chunk.text.strip()
            context_lines.append(f"[{idx}] {title} (Type: {meta.document_type}):\n{chunk_text}")

            if title not in seen_titles:
                seen_titles.add(title)
                sources.append(meta.model_dump())

        context_text = "\n\n".join(context_lines)
        return context_text, sources


# Singleton instance for platform-wide access
rag_retriever = RAGRetriever()

