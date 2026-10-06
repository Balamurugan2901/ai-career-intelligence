# RAG Subsystem Documentation

## 1. Overview

The **Retrieval-Augmented Generation (RAG)** subsystem provides lightweight, local, CPU-based vector search across domain knowledge documents stored under `data/knowledge/`. It enriches multi-agent prompts with relevant reference context while strictly preserving source metadata for UI provenance display.

---

## 2. Knowledge Base Directory Structure

Reference files are structured in JSON/Markdown format across 6 domain subdirectories:

```
data/knowledge/
├── job_descriptions/       # Role requirements for 9 core tech roles
├── skills/                 # Prerequisite trees & skill descriptions
├── career_guides/          # Career pathway guides
├── learning_resources/     # Curated learning course & book catalogs
├── interview_questions/    # Technical question banks & rubrics
└── projects/               # Portfolio project blueprints
```

Every document adheres to the standard `KnowledgeDocument` schema:

```json
{
  "metadata": {
    "source": "Reference Knowledge Base",
    "title": "Generative AI Engineer Role Requirements",
    "role": "GenAI Engineer",
    "document_type": "job_description",
    "version": "1.0"
  },
  "content": "Role Overview: Architect RAG systems..."
}
```

---

## 3. CPU Dense Embedding Engine (TF-IDF + LSA TruncatedSVD)

To operate within **8 GB RAM / CPU-only machine boundaries**, the RAG subsystem avoids heavy local PyTorch/Transformer embedding models:

- **Vectorizer**: `TfidfVectorizer` (sublinear TF scaling, n-gram range (1, 2)).
- **Dimensionality Reduction**: `TruncatedSVD` (LSA - Latent Semantic Analysis) projecting sparse TF-IDF vectors into a **64-dimensional dense vector space**.
- **Similarity Metric**: Cosine similarity (`numpy.dot` over L2-normalized vectors).
- **Index Storage**: Saved locally as joblib artifacts in `data/vector_store/` (`vector_store.joblib`, `indexer_meta.json`).
- **Memory Footprint**: Peak memory usage is **<50 MB RAM** with index load time **<5 ms**.

---

## 4. Chunking Strategy

- **Module**: `backend.rag.chunker.DocumentChunker`
- **Method**: Character sliding window with configurable overlap (`RAG_CHUNK_SIZE=500`, `RAG_CHUNK_OVERLAP=50`).
- **Chunk Metadata Preservation**: Every chunk retains full `SourceMetadata` (source, title, role, document_type, file_path, chunk_id).

---

## 5. Retrieval & Source Traceability Mechanics

1. **Retrieval**: `RAGRetriever.retrieve(query, top_k=5, role=..., document_type=...)` queries the dense vector index and returns top matching `RAGSearchResult` items sorted by cosine similarity.
2. **Context Formatting**: `RAGRetriever.format_context_and_sources(results)` formats context text for agent prompt templates and extracts unique source provenance records.
3. **Graceful Degradation**: If `RAG_ENABLED=False` or no documents match, the retriever safely returns `""` context and `[]` sources without breaking downstream agent execution.
