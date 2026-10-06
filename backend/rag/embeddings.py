import os
import joblib
import numpy as np
from typing import List, Union
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from backend.utils.logger import logger


class LightweightEmbeddingEngine:
    """
    Ultra-lightweight CPU-friendly Embedding Engine (< 50 MB RAM, 0 GPU).
    Uses L2-normalized dense TF-IDF LSA (Latent Semantic Analysis) projection.
    Caches model and vector artifacts to disk in data/vector_store/.
    """

    def __init__(self, vector_dir: str = "data/vector_store", vector_dim: int = 64):
        self.vector_dir = Path(vector_dir)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dim = vector_dim

        self.model_path = self.vector_dir / "embedding_model.joblib"
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd: Optional[TruncatedSVD] = None
        self.is_fitted = False

        self._load_or_init()

    def _load_or_init(self):
        """Loads fitted embedding model from disk cache if present."""
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.vectorizer = data.get("vectorizer")
                self.svd = data.get("svd")
                self.is_fitted = True
                logger.info("Loaded cached embedding model from disk.")
            except Exception as e:
                logger.warning(f"Failed to load cached embedding model: {e}. Will fit new model.")
                self.is_fitted = False

    def fit(self, texts: List[str]):
        """Fits TF-IDF and SVD dense vectorizer on text corpus."""
        if not texts:
            return

        min_df = 1
        n_components = min(self.vector_dim, len(texts))
        if n_components < 2:
            n_components = min(2, len(texts))

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=min_df,
        )
        tfidf = self.vectorizer.fit_transform(texts)

        if tfidf.shape[1] >= n_components:
            self.svd = TruncatedSVD(n_components=n_components, random_state=42)
            self.svd.fit(tfidf)

        self.is_fitted = True
        joblib.dump({"vectorizer": self.vectorizer, "svd": self.svd}, self.model_path)
        logger.info(f"Fitted & saved lightweight CPU embedding model to {self.model_path}")

    def embed_text(self, text: str) -> np.ndarray:
        """Generates L2-normalized dense embedding vector for a single query text."""
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Generates matrix of L2-normalized dense embedding vectors for batch texts."""
        if not texts:
            return np.zeros((0, self.vector_dim), dtype=np.float32)

        if not self.is_fitted:
            self.fit(texts)

        try:
            tfidf = self.vectorizer.transform(texts)
            if self.svd is not None and tfidf.shape[1] >= self.svd.n_components:
                dense = self.svd.transform(tfidf)
            else:
                dense = tfidf.toarray()
        except Exception:
            # Fallback if un-fitted vocabulary terms
            self.fit(texts)
            tfidf = self.vectorizer.transform(texts)
            dense = tfidf.toarray() if self.svd is None else self.svd.transform(tfidf)

        # L2 Normalization for Cosine Distance
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (dense / norms).astype(np.float32)
        return normalized
