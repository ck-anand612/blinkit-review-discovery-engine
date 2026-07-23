import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
from blinkit.models import Review

logger = logging.getLogger(__name__)

# Cache model in memory
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = "BAAI/bge-small-en-v1.5"
        logger.info(f"Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model


def generate_embeddings(reviews: List[Review]) -> np.ndarray:
    """Generate 384-dimensional embeddings for a list of reviews."""
    if not reviews:
        return np.array([])

    logger.info(f"Generating embeddings for {len(reviews)} reviews...")
    texts = [r.text for r in reviews]

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)

    logger.info(f"Embeddings generated with shape: {embeddings.shape}")
    return embeddings
