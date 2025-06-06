#fix compute fitness in both GA and SA
from multiprocessing import Pool
from timing import timing
from collections import Counter, defaultdict
import os
from typing import Dict, List, Set
from bson import ObjectId
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans

from utils.data_extract import calculate_average_ratings, enrich_listings_with_ratings, fetch_user_data
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging (optional, as no TensorFlow is used)

import json
import numpy as np
from sklearn.cluster import KMeans
import random
from copy import deepcopy
import logging
from utils.simulated_annealing import simulated_annealing
from utils.genetic_algorithm import genetic_algorithm
from utils.kmean_clustering import kmeans_clustering

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Get context features
@timing
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

    return context_features


# Modified Hybrid Metaheuristic Recommendation
@timing
def hybrid_metaheuristic_recommendation(listings, user_id=None, reservations=None, favorite_ids=None):
    logging.info("Starting hybrid metaheuristic recommendation")
    
    # Align weights with context features (7 features)
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.15, 0.05])  # Example weights, sum to 1
    
    context_features = get_context_features(user_id, listings, reservations, favorite_ids)
    population_size = 50
    generations = 50
    alpha = 0.95
    iterations_per_temp = 30

    # Use clustering for larger datasets
    if len(listings) <= 5:
        logging.info("Small dataset, treating as single cluster")
        clusters = [list(range(len(listings)))]
        population_size = 20
        generations =20
        alpha = 0.9
        iterations_per_temp = 10

    else:
        clusters = kmeans_clustering(listings, K=5)
    
    ranked_indices = []
    
    for cluster in clusters:
        if not cluster:
            continue
        top_solutions = genetic_algorithm(population_size,generations,cluster, listings, weights, context_features,favorite_ids)  # Pass context_features
        best_solution = simulated_annealing(alpha,iterations_per_temp,top_solutions, listings, weights, context_features)  # Pass context_features
        ranked_indices.extend(best_solution)
    
    result = {
        "ranked_listings": [
            {
                "index": idx,
                "listing_id": listings[idx]["_id"],
                # "price": listings[idx]["price"],
                # "roomCount": listings[idx]["roomCount"],
                # "bathroomCount": listings[idx]["bathroomCount"],
                # "guestCount": listings[idx]["guestCount"],
                # "locationValue": listings[idx]["locationValue"],
                # "averageRating": listings[idx]["averageRating"]
            } for idx in ranked_indices
        ]
    }
    
    logging.info("Recommendation completed, returning JSON")
    
    return json.dumps(result)


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


# # Example usage
# if __name__ == "__main__":
#     main("6774cf4f51e027387aff78f7")




