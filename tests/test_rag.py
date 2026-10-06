import os
import shutil
import pytest
from pathlib import Path

from backend.config import settings
from backend.rag.models import KnowledgeDocument, DocumentChunk, SourceMetadata
from backend.rag.loader import DocumentLoader
from backend.rag.chunker import DocumentChunker
from backend.rag.embeddings import LightweightEmbeddingEngine
from backend.rag.vector_store import LocalVectorStore
from backend.rag.indexer import KnowledgeIndexer
from backend.rag.retriever import RAGRetriever


@pytest.fixture
def temp_knowledge_dir(tmp_path):
    """Fixture providing a temporary knowledge directory with test files."""
    k_dir = tmp_path / "knowledge"
    jd_dir = k_dir / "job_descriptions"
    jd_dir.mkdir(parents=True)

    # Add JSON doc
    doc1 = {
        "metadata": {
            "source": "Reference Knowledge Base",
            "title": "Machine Learning Engineer Role Requirements",
            "role": "Machine Learning Engineer",
            "document_type": "job_description",
            "version": "1.0"
        },
        "content": "Machine Learning Engineer responsibilities include designing PyTorch pipelines, feature stores, and model deployment."
    }
    import json
    with open(jd_dir / "ml_role.json", "w", encoding="utf-8") as f:
        json.dump(doc1, f)

    # Add Markdown doc
    doc2 = """---
source: "Reference Knowledge Base"
title: "Python Backend Skill Dependency Guide"
role: "Backend Developer"
document_type: "skill_dependency"
---
Python backend skills include FastAPI, Pydantic, SQLAlchemy ORM, and async RESTful API design.
"""
    with open(k_dir / "backend_skills.md", "w", encoding="utf-8") as f:
        f.write(doc2)

    return str(k_dir)


def test_document_loader(temp_knowledge_dir):
    """Verifies DocumentLoader recursively parses .json and .md files into KnowledgeDocument objects."""
    docs = DocumentLoader.load_directory(temp_knowledge_dir)
    assert len(docs) == 2

    titles = [d.metadata.title for d in docs]
    assert "Machine Learning Engineer Role Requirements" in titles
    assert "Python Backend Skill Dependency Guide" in titles


def test_document_chunker(temp_knowledge_dir):
    """Verifies DocumentChunker splits documents based on size and overlap constraints."""
    docs = DocumentLoader.load_directory(temp_knowledge_dir)
    chunker = DocumentChunker(chunk_size=60, chunk_overlap=10)

    chunks = chunker.chunk_documents(docs)
    assert len(chunks) > 0
    assert chunks[0].chunk_id is not None
    assert chunks[0].metadata.title is not None


def test_lightweight_embedding_engine(tmp_path):
    """Verifies LightweightEmbeddingEngine generates normalized dense CPU vectors and caches model."""
    vec_dir = str(tmp_path / "vector_store")
    engine = LightweightEmbeddingEngine(vector_dir=vec_dir, vector_dim=32)

    texts = [
        "Machine learning models using PyTorch and TensorFlow.",
        "SQL relational databases and PostgreSQL query optimization.",
        "FastAPI microservices and async Python REST APIs."
    ]

    embeddings = engine.embed_documents(texts)
    assert embeddings.shape[0] == 3
    assert embeddings.shape[1] > 0

    # Test cache reloading
    engine2 = LightweightEmbeddingEngine(vector_dir=vec_dir, vector_dim=32)
    assert engine2.is_fitted is True


def test_local_vector_store_search(tmp_path, temp_knowledge_dir):
    """Verifies LocalVectorStore cosine similarity retrieval and metadata preservation."""
    vec_dir = str(tmp_path / "vector_store")
    engine = LightweightEmbeddingEngine(vector_dir=vec_dir, vector_dim=32)
    store = LocalVectorStore(store_dir=vec_dir)

    docs = DocumentLoader.load_directory(temp_knowledge_dir)
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_documents(docs)

    texts = [c.text for c in chunks]
    embeddings = engine.embed_documents(texts)
    store.add_chunks(chunks, embeddings)

    assert len(store.chunks) == len(chunks)

    # Perform similarity search
    query_vec = engine.embed_text("PyTorch machine learning model deployment")
    results = store.search(query_vec, top_k=2)

    assert len(results) > 0
    top_result = results[0]
    assert top_result.score >= 0.0
    assert top_result.source_metadata.title is not None
    assert top_result.chunk.text is not None


def test_knowledge_indexer_hash_caching(tmp_path, temp_knowledge_dir):
    """Verifies KnowledgeIndexer builds index and skips re-indexing when content hash is unchanged."""
    vec_dir = str(tmp_path / "vector_store")
    indexer = KnowledgeIndexer(knowledge_dir=temp_knowledge_dir, vector_dir=vec_dir)

    # 1. Build index first time
    count1 = indexer.build_index(force_rebuild=True)
    assert count1 > 0

    # 2. Build index second time (should use cached hash)
    count2 = indexer.build_index(force_rebuild=False)
    assert count2 == count1


def test_rag_retriever_query_handling(tmp_path, temp_knowledge_dir):
    """Verifies RAGRetriever query processing, metadata traceability, and empty query edge cases."""
    vec_dir = str(tmp_path / "vector_store")
    retriever = RAGRetriever(knowledge_dir=temp_knowledge_dir, vector_dir=vec_dir)

    # Test empty query
    empty_res = retriever.retrieve("")
    assert len(empty_res) == 0

    # Test valid query
    results = retriever.retrieve("PyTorch features", top_k=2)
    assert len(results) > 0
    assert results[0].source_metadata.source == "Reference Knowledge Base"
    assert results[0].source_metadata.title is not None
