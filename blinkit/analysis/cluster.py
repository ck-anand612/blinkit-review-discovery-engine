import logging
import numpy as np
import hdbscan
from typing import List, Tuple

from blinkit.models import Review, Cluster

logger = logging.getLogger(__name__)


def run_clustering(
    reduced_embeddings: np.ndarray,
    min_cluster_size: int = 15,
    min_samples: int = 10
) -> np.ndarray:
    """Run HDBSCAN clustering on reduced embeddings."""
    if len(reduced_embeddings) == 0:
        return np.array([])

    logger.info(
        f"Running HDBSCAN (min_cluster_size={min_cluster_size}, min_samples={min_samples})...")

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method="leaf"
    )

    labels = clusterer.fit_predict(reduced_embeddings)
    unique, counts = np.unique(labels, return_counts=True)
    n_clusters = len([label for label in unique if label != -1])
    n_noise = counts[unique == -1][0] if -1 in unique else 0

    logger.info(
        f"HDBSCAN complete: found {n_clusters} clusters, {n_noise} noise points.")
    return labels


def build_clusters(
    reviews: List[Review],
    labels: np.ndarray,
    top_k: int = 6
) -> Tuple[List[Cluster], int]:
    """
    Build structured Cluster objects from HDBSCAN labels, ranked by a composite score.
    Returns (List of top K clusters, number of noise reviews).
    """
    unique_labels = np.unique(labels)
    clusters = []
    noise_count = 0

    for label in unique_labels:
        # Get indices for this cluster
        indices = np.where(labels == label)[0]

        if label == -1:
            noise_count = len(indices)
            continue

        cluster_reviews = [reviews[i] for i in indices]

        # Calculate cluster metrics
        size = len(cluster_reviews)

        # Only Play Store has ratings, so we filter out Nones just in case
        ratings = [r.rating for r in cluster_reviews if r.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        dates = [r.date for r in cluster_reviews]
        earliest_date = min(dates)
        latest_date = max(dates)

        review_ids = [r.id for r in cluster_reviews]

        # Dummy rank for now, we will sort and reassign
        c = Cluster(
            rank=0,
            size=size,
            average_rating=avg_rating,
            earliest_date=earliest_date,
            latest_date=latest_date,
            review_ids=review_ids
        )
        clusters.append((c, cluster_reviews))

    # Sort clusters: prioritizing large size and low average rating (severity)
    def composite_score(cluster_tuple):
        c, _ = cluster_tuple
        # Inverse rating (lower rating = higher severity score),
        # assume 3.0 if no rating available
        rating_score = 6.0 - (c.average_rating if c.average_rating else 3.0)
        # Score = size * rating severity
        return c.size * rating_score

    clusters.sort(key=composite_score, reverse=True)

    # Assign final ranks and slice top-K
    final_clusters = []
    for i, (c, _) in enumerate(clusters[:top_k]):
        c.rank = i + 1
        final_clusters.append(c)

    return final_clusters, noise_count
