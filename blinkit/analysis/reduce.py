import logging
import numpy as np
import umap

logger = logging.getLogger(__name__)


def reduce_dimensions(
    embeddings: np.ndarray,
    n_neighbors: int = 10,
    min_dist: float = 0.05,
    n_components: int = 5,
    random_state: int = 42,
    metric: str = "cosine"
) -> np.ndarray:
    """Reduce high-dimensional embeddings to lower-dimensional space using UMAP."""
    if len(embeddings) == 0:
        return np.array([])

    logger.info(
        f"Reducing dimensions via UMAP (n_components={n_components})...")

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        random_state=random_state,
        metric=metric
    )

    reduced_embeddings = reducer.fit_transform(embeddings)
    logger.info(f"Reduced embeddings shape: {reduced_embeddings.shape}")
    return reduced_embeddings
