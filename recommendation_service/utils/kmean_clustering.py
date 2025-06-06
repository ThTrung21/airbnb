import logging
from typing import Dict, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import OneHotEncoder

from timing import timing


@timing
def kmeans_clustering(listings: List[Dict], favorite_ids: List[str] = None, K: int = 5) -> List[List[int]]:
    """
    Cluster listings using K-Means based on their features.

    Args:
        listings: List of listing dictionaries with price, roomCount, etc.
        favorite_ids: List of listing IDs favorited by the user (optional).
        K: Number of clusters (default 5).

    Returns:
        List of clusters, each containing indices of listings.
    """
    logging.info("Running K-Means clustering")

    if not listings:
        logging.warning("No listings provided, returning empty clusters")
        return [[]]

    # Extract feature vectors
    X_numeric = []
    locations = []
    favorite_feature = []
    favorite_ids = favorite_ids or []

    for l in listings:
        X_numeric.append([
            l.get("price", 0),
            l.get("roomCount", 0),
            l.get("bathroomCount", 0),
            l.get("guestCount", 0),
            l.get("averageRating", 0)
        ])
        locations.append(l.get("locationValue", "unknown"))
        favorite_feature.append(1 if str(l["_id"]) in favorite_ids else 0)

    X_numeric = np.array(X_numeric)
    favorite_feature = np.array(favorite_feature).reshape(-1, 1)

    # Encode categorical locationValue
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    location_encoded = encoder.fit_transform(np.array(locations).reshape(-1, 1))

    # Combine features
    X = np.hstack([X_numeric, location_encoded, favorite_feature])

    # Normalize numeric features (min-max normalization)
    X_min = X[:, :5].min(axis=0)  # Only normalize numeric features
    X_max = X[:, :5].max(axis=0)
    X_range = np.where(X_max - X_min == 0, 1, X_max - X_min)
    X_normalized = X.copy()
    X_normalized[:, :5] = (X[:, :5] - X_min) / X_range  # Normalize only numeric features

    n_samples = len(X)
    if n_samples <= 1:
        logging.warning("Too few samples for clustering, returning single cluster")
        return [list(range(n_samples))]

    # Dynamic K selection using silhouette score (optional)
    if n_samples > 5:  # Only try dynamic K for sufficient samples
        silhouette_scores = []
        k_range = range(2, min(10, n_samples))
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X_normalized)
            silhouette_scores.append(silhouette_score(X_normalized, kmeans.labels_))
        optimal_k = k_range[np.argmax(silhouette_scores)]
        K = min(K, optimal_k) if silhouette_scores else K
        logging.info(f"Selected K={K} based on silhouette score")

    K = min(K, n_samples)  # Ensure K <= n_samples

    # Run K-Means
    kmeans = KMeans(n_clusters=K, random_state=42)
    kmeans.fit(X_normalized)
    labels = kmeans.labels_

    # Organize indices into clusters
    clusters = [[] for _ in range(K)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)

    logging.info(f"Created {K} clusters with sizes: {[len(c) for c in clusters]}")
    return clusters

