import os
import json
import hashlib
from typing import List, Optional
from pathlib import Path

from backend.rag.models import KnowledgeDocument, SourceMetadata
from backend.utils.logger import logger


class DocumentLoader:
    """Document loader for loading Markdown (.md) and JSON (.json) reference documents."""

    @classmethod
    def load_directory(cls, dir_path: str) -> List[KnowledgeDocument]:
        """Recursively loads all .json and .md documents in dir_path."""
        base_path = Path(dir_path)
        if not base_path.exists():
            logger.warning(f"Knowledge directory '{dir_path}' does not exist.")
            return []

        documents: List[KnowledgeDocument] = []
        for file_path in base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [".json", ".md"]:
                doc = cls.load_file(str(file_path))
                if doc:
                    documents.append(doc)

        logger.info(f"Loaded {len(documents)} knowledge documents from '{dir_path}'")
        return documents

    @classmethod
    def load_file(cls, file_path: str) -> Optional[KnowledgeDocument]:
        """Loads a single document file and constructs KnowledgeDocument with metadata."""
        p = Path(file_path)
        try:
            rel_path = str(p)
            doc_id = hashlib.md5(rel_path.encode("utf-8")).hexdigest()[:12]

            if p.suffix.lower() == ".json":
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)

                meta_dict = data.get("metadata", {})
                content = data.get("content", "")
                if isinstance(content, dict) or isinstance(content, list):
                    content = json.dumps(content, indent=2)

                meta_dict["file_path"] = rel_path
                metadata = SourceMetadata(**meta_dict)
                return KnowledgeDocument(document_id=doc_id, metadata=metadata, content=str(content))

            elif p.suffix.lower() == ".md":
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()

                # Basic YAML frontmatter parser if present
                meta_dict = {
                    "source": "Reference Knowledge Base",
                    "title": p.stem.replace("_", " ").title(),
                    "file_path": rel_path,
                    "document_type": p.parent.name,
                }
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].strip().split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                meta_dict[k.strip()] = v.strip().strip('"').strip("'")
                        content = parts[2].strip()

                metadata = SourceMetadata(**meta_dict)
                return KnowledgeDocument(document_id=doc_id, metadata=metadata, content=content)

        except Exception as e:
            logger.error(f"Failed to load document '{file_path}': {e}")

        return None
