import logging
import random
from typing import Dict, List

import numpy as np
from timing import timing

@timing
def simulated_annealing(alpha: int,iterations_per_temp: int,top_solutions: List[List[int]], listings: List[Dict], weights: np.ndarray, context_features: Dict, favorite_ids: List[str] = None) -> List[int]:
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


    favorite_ids = set(str(fid) for fid in (favorite_ids or []))  # Convert ObjectId to strings for comparison
    FAVORITE_BONUS = 0.05  # Consistent with GA

    # Precompute max values for normalization
    max_price = max(l.get("price", 1) for l in listings) or 1
    max_room = max(l.get("roomCount", 1) for l in listings) or 1
    max_bath = max(l.get("bathroomCount", 1) for l in listings) or 1
    max_guest = max(l.get("guestCount", 1) for l in listings) or 1
    max_rating = max(l.get("averageRating", 5) for l in listings) or 5

    # Get user's preferred location from context_features (from reservations/favorites)
    # main_location = context_features.get("main_location", None)
    main_location="VN"
    context_vec = np.array(context_features)  # rename for clarity


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
            #context_features["features"] = np.array(context_features["features"])

            listing_score = np.sum(weights * (1 - np.abs(features - context_vec)))
            if str(listing["_id"]) in favorite_ids:
                listing_score += FAVORITE_BONUS
            score += listing_score
        return score / len(pi) if pi else 0

    best_solution = top_solutions[0][:]
    best_fitness = compute_fitness(best_solution)
    #skipping too short solutions
    
    for solution in top_solutions:
        if len(solution) < 2:
            logging.warning(f"Skipping solution (too short for SA): {solution}")
            continue
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
            # if iteration % 10 == 0:
            #     logging.info(f"SA Temperature {T_current:.2f}, Best Fitness: {best_fitness:.4f}")

    logging.info("SA completed")
    return best_solution

