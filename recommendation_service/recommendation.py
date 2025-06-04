from collections import Counter, defaultdict
import os
from typing import Dict, List, Set
from bson import ObjectId
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans

from data_extract import calculate_average_ratings, enrich_listings_with_ratings, fetch_user_data
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging (optional, as no TensorFlow is used)

import json
import numpy as np
from sklearn.cluster import KMeans
import random
from copy import deepcopy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 0: Get context features
def get_context_features(user_id: str, listings: List[Dict], reservations: List[Dict], favorite_ids: List[str]) -> np.ndarray:
    """
    Extract context features based on user reservations and favorites.

    Args:
        user_id: User ID.
        listings: List of listing dictionaries with _id, price, roomCount, etc.
        reservations: List of user's reservation dictionaries.
        favorite_ids: List of listing IDs favorited by the user.

    Returns:
        Numpy array of normalized context features.
    """
    logging.info("Getting context features based on user data")

    if not user_id or not listings:
        return np.array([0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25])

    # Map listings by ID for quick lookup
    listing_map = {str(l["_id"]): l for l in listings}

    # Extract user past reserved listings
    reserved_listings = [listing_map[str(r["listingId"])] for r in reservations if str(r["listingId"]) in listing_map]

    if not reserved_listings:
        return np.array([0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25])

    # Numeric features to average
    prices = [l.get("price", 0) for l in reserved_listings]
    rooms = [l.get("roomCount", 0) for l in reserved_listings]
    baths = [l.get("bathroomCount", 0) for l in reserved_listings]
    guests = [l.get("guestCount", 0) for l in reserved_listings]
    ratings = [l.get("averageRating", 0) for l in reserved_listings]

    # LocationValue frequency in reserved listings
    reserved_locations = [l.get("locationValue") for l in reserved_listings if l.get("locationValue") is not None]
    location_counter = Counter(reserved_locations)
    main_location = location_counter.most_common(1)[0][0] if location_counter else None

    # Approximate distance feature
    distances = [0 if loc == main_location else 1 for loc in reserved_locations]
    avg_distance = np.mean(distances) if distances else 1.0

    # Favorite ratio in current listings
    favorite_in_listings = [1 if str(l["_id"]) in favorite_ids else 0 for l in listings]
    favorite_ratio = np.mean(favorite_in_listings) if favorite_in_listings else 0.0

    # Normalize numeric features
    max_price = max([l.get("price", 1) for l in listings]) or 1
    max_rooms = max([l.get("roomCount", 1) for l in listings]) or 1
    max_baths = max([l.get("bathroomCount", 1) for l in listings]) or 1
    max_guests = max([l.get("guestCount", 1) for l in listings]) or 1
    max_rating = max([l.get("averageRating", 5) for l in listings]) or 5

    context_features = np.array([
        np.mean(prices) / max_price if prices else 0.25,
        np.mean(rooms) / max_rooms if rooms else 0.25,
        np.mean(baths) / max_baths if baths else 0.25,
        np.mean(guests) / max_guests if guests else 0.25,
        np.mean(ratings) / max_rating if ratings else 0.25,
        1 - avg_distance,
        favorite_ratio
    ])

    logging.info(f"Context features: {context_features}")
    return context_features
# Step 1: K-Means Clustering

# def kmeans_clustering(listings: List[Dict], K: int = 5) -> List[List[int]]:
#     """
#     Cluster listings using K-Means based on their features.

#     Args:
#         listings: List of listing dictionaries with price, roomCount, etc.
#         K: Number of clusters (default 5).

#     Returns:
#         List of clusters, each containing indices of listings.
#     """
#     logging.info("Running K-Means clustering")

#     if not listings:
#         logging.warning("No listings provided, returning empty clusters")
#         return [[]]

#     # Extract feature vectors
#     X = []
#     for l in listings:
#         X.append([
#             l.get("price", 0),
#             l.get("roomCount", 0),
#             l.get("bathroomCount", 0),
#             l.get("guestCount", 0),
#             l.get("averageRating", 0)
#         ])
#     X = np.array(X)

#     # Normalize features (min-max normalization)
#     X_min = X.min(axis=0)
#     X_max = X.max(axis=0)
#     X_range = np.where(X_max - X_min == 0, 1, X_max - X_min)
#     X_normalized = (X - X_min) / X_range

#     n_samples = len(X)
#     K = min(K, n_samples)  # Avoid K > n_samples

#     kmeans = KMeans(n_clusters=K, random_state=42)
#     kmeans.fit(X_normalized)
#     labels = kmeans.labels_

#     # Organize indices into clusters
#     clusters = [[] for _ in range(K)]
#     for idx, label in enumerate(labels):
#         clusters[label].append(idx)

#     logging.info(f"Created {K} clusters with sizes: {[len(c) for c in clusters]}")
#     return clusters
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



#====================================================================================================================#
# Step 2: Genetic Algorithm
# def genetic_algorithm(cluster, listings, weights, favorite_ids=None):
#     logging.info(f"Running Genetic Algorithm for cluster with {len(cluster)} listings")
    
#     if len(cluster) <= 1:
#         logging.info("Cluster too small for GA, returning as-is")
#         return [cluster]

#     population_size = 50
#     generations = 50
#     favorite_ids = set(favorite_ids or [])
#     FAVORITE_BONUS = 0.05  # Bonus score for favorited listings

#     population = [random.sample(cluster, len(cluster)) for _ in range(population_size)]

#     def compute_fitness(pi):
#         score = 0
#         max_price = max(l['price'] for l in listings)
#         max_distance = max(l['distance'] for l in listings)
#         max_amenities = max(len(l['amenities']) for l in listings)

#         avg_price = np.mean([l['price'] for l in listings])

#         for idx in pi:
#             listing = listings[idx]
#             price_match = 1 - abs(listing['price'] - avg_price) / max_price
#             distance_match = 1 - listing['distance'] / max_distance if max_distance else 0
#             amenities_match = len(set(listing['amenities']) & {'wifi', 'kitchen'}) / 2
#             rating_score = listing.get('rating', 0) / 5.0

#             listing_score = (
#                 weights[0] * price_match +
#                 weights[1] * distance_match +
#                 weights[2] * amenities_match +
#                 weights[3] * rating_score
#             )

#             # Add bonus if the listing is a favorite
#             if listing["_id"] in favorite_ids:
#                 listing_score += FAVORITE_BONUS

#             score += listing_score

#         return score / len(pi) if pi else 0

#     for generation in range(generations):
#         fitness_scores = [compute_fitness(pi) for pi in population]
#         total_fitness = sum(fitness_scores)

#         new_population = []
#         for _ in range(population_size):
#             # Tournament-style selection using weighted fitness
#             def select_parent():
#                 pick = random.uniform(0, total_fitness)
#                 current = 0
#                 for i, fitness in enumerate(fitness_scores):
#                     current += fitness
#                     if current > pick:
#                         return population[i]
#                 return population[-1]

#             parent1 = select_parent()
#             parent2 = select_parent()

#             child = pmx_crossover(parent1, parent2)

#             # Mutation
#             if random.random() < 0.1:
#                 i, j = random.sample(range(len(child)), 2)
#                 child[i], child[j] = child[j], child[i]

#             new_population.append(child)

#         population = new_population

#         if generation % 10 == 0:
#             logging.info(f"GA Generation {generation}/{generations}")

#     fitness_scores = [compute_fitness(pi) for pi in population]
#     top_indices = np.argsort(fitness_scores)[-5:]
#     top_solutions = [population[i] for i in top_indices]
    
#     logging.info("GA completed, returning top solutions")
#     return top_solutions


def genetic_algorithm(cluster: List[int], listings: List[Dict], weights: np.ndarray, context_features: Dict, favorite_ids: List[str] = None) -> List[List[int]]:
    """
    Run Genetic Algorithm to rank listings in a cluster.

    Args:
        cluster: List of listing indices in the cluster.
        listings: List of listing dictionaries with price, roomCount, etc.
        weights: Array of weights for features (price, roomCount, bathroomCount, guestCount, averageRating, location, favorite).
        context_features: Dictionary with 'features' (7-element array) and 'main_location' from get_context_features.
        favorite_ids: List of listing IDs (numbers) favorited by the user (optional).

    Returns:
        List of top solutions (permutations of cluster indices).
    """
    logging.info(f"Running Genetic Algorithm for cluster with {len(cluster)} listings")

    if len(cluster) <= 1:
        logging.info("Cluster too small for GA, returning as-is")
        return [cluster]

    population_size = 50
    generations = 50
    favorite_ids = set(favorite_ids or [])  # Convert to set for O(1) lookup
    FAVORITE_BONUS = 0.05

    # Precompute max values for normalization
    max_price = max(l.get("price", 1) for l in listings) or 1
    max_room = max(l.get("roomCount", 1) for l in listings) or 1
    max_bath = max(l.get("bathroomCount", 1) for l in listings) or 1
    max_guest = max(l.get("guestCount", 1) for l in listings) or 1
    max_rating = max(l.get("averageRating", 5) for l in listings) or 5

    # Get user's preferred location from context_features (derived from reservations/favorites)
    main_location = context_features.get("main_location", None)

    def compute_fitness(pi: List[int]) -> float:
        score = 0
        for idx in pi:
            listing = listings[idx]
            # Normalize features to match context_features
            features = np.array([
                listing.get("price", 0) / max_price,
                listing.get("roomCount", 0) / max_room,
                listing.get("bathroomCount", 0) / max_bath,
                listing.get("guestCount", 0) / max_guest,
                listing.get("averageRating", 0) / 5.0,
                1 if listing.get("locationValue") == main_location else 0,
                1 if listing["_id"] in favorite_ids else 0
            ])
            # Weighted sum of feature alignment
            listing_score = np.sum(weights * (1 - np.abs(features - context_features["features"])))
            if listing["_id"] in favorite_ids:
                listing_score += FAVORITE_BONUS
            score += listing_score
        return score / len(pi) if pi else 0

    # Initialize population
    population = [random.sample(cluster, len(cluster)) for _ in range(population_size)]

    for generation in range(generations):
        fitness_scores = [compute_fitness(pi) for pi in population]
        total_fitness = sum(fitness_scores) or 1  # Avoid division by zero

        # Tournament selection
        new_population = []
        for _ in range(population_size):
            tournament_size = 5
            candidates = random.sample(list(zip(population, fitness_scores)), tournament_size)
            parent1 = max(candidates, key=lambda x: x[1])[0]
            candidates = random.sample(list(zip(population, fitness_scores)), tournament_size)
            parent2 = max(candidates, key=lambda x: x[1])[0]

            child = pmx_crossover(parent1, parent2)

            # Mutation: swap two indices
            if random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]

            new_population.append(child)

        population = new_population

        if generation % 10 == 0:
            best_fitness = max(fitness_scores) if fitness_scores else 0
            logging.info(f"GA Generation {generation}/{generations}, Best Fitness: {best_fitness:.4f}")

    # Select top 5 solutions
    fitness_scores = [compute_fitness(pi) for pi in population]
    top_indices = np.argsort(fitness_scores)[-5:]
    top_solutions = [population[i] for i in top_indices]

    logging.info("GA completed, returning top solutions")
    return top_solutions
def pmx_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    """
    Perform Partially Matched Crossover (PMX) for two parent permutations.
    """
    size = len(parent1)
    child = [-1] * size
    start, end = sorted(random.sample(range(size), 2))
    
    # Copy segment from parent1
    child[start:end] = parent1[start:end]
    
    # Map values from parent2
    for i in range(start, end):
        value = parent2[i]
        if value not in child:
            curr = value
            while True:
                idx = parent1.index(curr)
                if child[idx] == -1:
                    child[idx] = value
                    break
                curr = parent2[idx]
    
    # Fill remaining from parent2
    for i in range(size):
        if child[i] == -1:
            child[i] = parent2[i]
    
    return child


#============================================================================================#
# Step 3: Simulated Annealing
def simulated_annealing(top_solutions: List[List[int]], listings: List[Dict], weights: np.ndarray, context_features: Dict, favorite_ids: List[str] = None) -> List[int]:
    """
    Run Simulated Annealing to refine top GA solutions into a single best ranking.

    Args:
        top_solutions: List of solutions (permutations of listing indices) from GA.
        listings: List of listing dictionaries with price, roomCount, etc.
        weights: Array of weights for features (price, roomCount, bathroomCount, guestCount, averageRating, location, favorite).
        context_features: Dictionary with 'features' (7-element array) and 'main_location' from get_context_features.
        favorite_ids: List of listing IDs (ObjectId) favorited by the user (optional).

    Returns:
        Best solution (list of listing indices).
    """
    logging.info("Running Simulated Annealing")

    if not top_solutions:
        logging.warning("No solutions provided, returning empty list")
        return []

    # SA parameters
    T = 1000
    T_min = 0.1
    alpha = 0.95
    iterations_per_temp = 10

    favorite_ids = set(str(fid) for fid in (favorite_ids or []))  # Convert ObjectId to strings for comparison
    FAVORITE_BONUS = 0.05  # Consistent with GA

    # Precompute max values for normalization
    max_price = max(l.get("price", 1) for l in listings) or 1
    max_room = max(l.get("roomCount", 1) for l in listings) or 1
    max_bath = max(l.get("bathroomCount", 1) for l in listings) or 1
    max_guest = max(l.get("guestCount", 1) for l in listings) or 1
    max_rating = max(l.get("averageRating", 5) for l in listings) or 5

    # Get user's preferred location from context_features (from reservations/favorites)
    main_location = context_features.get("main_location", None)

    def compute_fitness(pi: List[int]) -> float:
        score = 0
        for idx in pi:
            listing = listings[idx]
            # Normalize features to match context_features
            features = np.array([
                listing.get("price", 0) / max_price,
                listing.get("roomCount", 0) / max_room,
                listing.get("bathroomCount", 0) / max_bath,
                listing.get("guestCount", 0) / max_guest,
                listing.get("averageRating", 0) / 5.0,
                1 if listing.get("locationValue") == main_location else 0,
                1 if str(listing["_id"]) in favorite_ids else 0
            ])
            # Weighted sum of feature alignment
            listing_score = np.sum(weights * (1 - np.abs(features - context_features["features"])))
            if str(listing["_id"]) in favorite_ids:
                listing_score += FAVORITE_BONUS
            score += listing_score
        return score / len(pi) if pi else 0

    best_solution = top_solutions[0][:]
    best_fitness = compute_fitness(best_solution)

    for solution in top_solutions:
        current_solution = solution[:]
        current_fitness = compute_fitness(current_solution)
        T_current = T
        iteration = 0

        while T_current > T_min:
            for _ in range(iterations_per_temp):
                # Generate neighbor by swapping two indices
                neighbor = current_solution[:]
                i, j = random.sample(range(len(neighbor)), 2)
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbor_fitness = compute_fitness(neighbor)
                delta_f = neighbor_fitness - current_fitness

                if delta_f >= 0 or random.random() < np.exp(delta_f / T_current):
                    current_solution = neighbor
                    current_fitness = neighbor_fitness

                if current_fitness > best_fitness:
                    best_solution = current_solution[:]
                    best_fitness = current_fitness

            T_current *= alpha
            iteration += 1
            if iteration % 10 == 0:
                logging.info(f"SA Temperature {T_current:.2f}, Best Fitness: {best_fitness:.4f}")

    logging.info("SA completed")
    return best_solution


# Modified Hybrid Metaheuristic Recommendation
def hybrid_metaheuristic_recommendation(listings, user_id=None, reservations=None, favorite_ids=None):
    logging.info("Starting hybrid metaheuristic recommendation")
    
    # Align weights with context features (7 features)
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.15, 0.05])  # Example weights, sum to 1
    
    context_features = get_context_features(user_id, listings, reservations, favorite_ids)
    
    # Use clustering for larger datasets
    if len(listings) <= 5:
        logging.info("Small dataset, treating as single cluster")
        clusters = [list(range(len(listings)))]
    else:
        clusters = kmeans_clustering(listings, K=5)
    
    ranked_indices = []
    for cluster in clusters:
        if not cluster:
            continue
        top_solutions = genetic_algorithm(cluster, listings, weights, context_features,favorite_ids)  # Pass context_features
        best_solution = simulated_annealing(top_solutions, listings, weights, context_features)  # Pass context_features
        ranked_indices.extend(best_solution)
    
    result = {
        "ranked_listings": [
            {
                "index": idx,
                "listing_id": listings[idx]["_id"],
                "price": listings[idx]["price"],
                "roomCount": listings[idx]["roomCount"],
                "bathroomCount": listings[idx]["bathroomCount"],
                "guestCount": listings[idx]["guestCount"],
                "locationValue": listings[idx]["locationValue"],
                "averageRating": listings[idx]["averageRating"]
            } for idx in ranked_indices
        ]
    }
    
    logging.info("Recommendation completed, returning JSON")
    return json.dumps(result, indent=2, ensure_ascii=False)
# Example usage
# if __name__ == "__main__":

#     listings = [
#         {'price': 100, 'distance': 2.0, 'amenities': ['wifi', 'kitchen'], 'rating': 4.5},
#         {'price': 150, 'distance': 1.5, 'amenities': ['wifi'], 'rating': 4.0},
#         {'price': 80, 'distance': 3.0, 'amenities': ['kitchen'], 'rating': 3.5},
#         {'price': 120, 'distance': 1.2, 'amenities': ['wifi', 'tv', 'air conditioning'], 'rating': 4.6},
#         {'price': 95, 'distance': 2.5, 'amenities': ['wifi', 'kitchen', 'hair dryer'], 'rating': 4.2},
#         {'price': 150, 'distance': 0.8, 'amenities': ['wifi', 'tv', 'mini fridge'], 'rating': 4.9},
#         {'price': 75, 'distance': 3.6, 'amenities': ['wifi', 'fan'], 'rating': 3.8},
#         {'price': 200, 'distance': 0.3, 'amenities': ['wifi', 'tv', 'jacuzzi', 'mini bar'], 'rating': 5.0},
#         {'price': 65, 'distance': 4.2, 'amenities': ['wifi', 'desk'], 'rating': 3.1},
#         {'price': 110, 'distance': 2.0, 'amenities': ['wifi', 'tv', 'iron', 'safe'], 'rating': 4.4},
#         {'price': 85, 'distance': 3.1, 'amenities': ['wifi', 'tv', 'kitchen'], 'rating': 3.9},
#         {'price': 140, 'distance': 1.5, 'amenities': ['wifi', 'tv', 'balcony'], 'rating': 4.7},
#         {'price': 90, 'distance': 3.3, 'amenities': ['wifi', 'tv', 'hair dryer'], 'rating': 3.6},
#         {'price': 180, 'distance': 0.9, 'amenities': ['wifi', 'jacuzzi', 'air conditioning'], 'rating': 4.8},
#         {'price': 70, 'distance': 4.0, 'amenities': ['wifi', 'fan', 'desk'], 'rating': 3.4},
#         {'price': 130, 'distance': 1.1, 'amenities': ['wifi', 'tv', 'safe'], 'rating': 4.5},
#         {'price': 100, 'distance': 2.8, 'amenities': ['wifi', 'mini fridge', 'tv'], 'rating': 4.0},
#         {'price': 160, 'distance': 0.7, 'amenities': ['wifi', 'tv', 'mini bar', 'balcony'], 'rating': 4.9},
#         {'price': 85, 'distance': 3.9, 'amenities': ['wifi', 'tv'], 'rating': 3.5},
#         {'price': 115, 'distance': 2.1, 'amenities': ['wifi', 'air conditioning', 'iron'], 'rating': 4.3},
#         {'price': 105, 'distance': 2.6, 'amenities': ['wifi', 'tv', 'hair dryer'], 'rating': 4.1},
#         {'price': 55, 'distance': 5.0, 'amenities': ['wifi'], 'rating': 2.9},
#         {'price': 125, 'distance': 1.0, 'amenities': ['wifi', 'tv', 'kitchen', 'safe'], 'rating': 4.6},
#         {'price': 200, 'distance': 0.5, 'amenities': ['wifi', 'kitchen', 'pool'], 'rating': 4.8}
#     ]
#     user_id = {'history': [{'price': 120, 'distance': 2.5, 'amenities': ['wifi', 'kitchen']}]}
    
#     json_output = hybrid_metaheuristic_recommendation(listings, user_id)
#     print("JSON Output:")
#     print(json_output)



def main(user_id):
    data = fetch_user_data(user_id)
    
    listings = data["Listing"]
    ratings = data["Rating"]
    reservations = data["Reservation"]
    favorite_ids = data["FavoriteIds"]
    avg_ratings = calculate_average_ratings(ratings)
    listings = enrich_listings_with_ratings(listings, avg_ratings)

    recommendations = hybrid_metaheuristic_recommendation(
        listings=listings,
        user_id=user_id,
        reservations=reservations,
        favorite_ids=favorite_ids
    )

    return recommendations


