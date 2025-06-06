
import logging
import random
from typing import Dict, List
from timing import timing
import numpy as np


@timing
def genetic_algorithm(population_size: int,generations: int,cluster: List[int], listings: List[Dict], weights: np.ndarray, context_features: Dict, favorite_ids: List[str] = None) -> List[List[int]]:
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
    #if run 
    if len(cluster) <= 1:
        logging.info("Cluster too small for GA, returning as-is")
        return [cluster]
    

    favorite_ids = set(favorite_ids or [])  # Convert to set for O(1) lookup
    FAVORITE_BONUS = 0.05

    # Precompute max values for normalization
    max_price = max(l.get("price", 1) for l in listings) or 1
    max_room = max(l.get("roomCount", 1) for l in listings) or 1
    max_bath = max(l.get("bathroomCount", 1) for l in listings) or 1
    max_guest = max(l.get("guestCount", 1) for l in listings) or 1
    max_rating = max(l.get("averageRating", 5) for l in listings) or 5

    # Get user's preferred location from context_features (derived from reservations/favorites)
    # main_location = context_features.get("main_location", None)
    main_location = 'VN'
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
                1 if listing["_id"] in favorite_ids else 0
            ])
            # Weighted sum of feature alignment
            #context_features["features"] = np.array(context_features["features"])
            #listing_score = np.sum(weights * (1 - np.abs(features - context_features["features"])))
            listing_score = np.sum(weights * (1 - np.abs(features - context_vec)))
            if listing["_id"] in favorite_ids:
                listing_score += FAVORITE_BONUS
            score += listing_score
        return score / len(pi) if pi else 0

    # Initialize population
    population = [random.sample(cluster, len(cluster)) for _ in range(population_size)]
    print("Cluster:", cluster)
    #check for valid parents
    def is_valid(individual: List[int], cluster: List[int]) -> bool:
        return sorted(individual) == sorted(cluster)
    
    for generation in range(generations):
        if len(population) == 0:
            logging.error("Population became empty. Reinitializing population.")
            population = [random.sample(cluster, len(cluster)) for _ in range(population_size)]
        #recalculate fitness
        fitness_scores = [compute_fitness(pi) for pi in population]
        total_fitness = sum(fitness_scores) or 1  # Avoid division by zero

        # Tournament selection
        new_population = []
        for _ in range(population_size):
            tournament_size = min(5, len(population))
            if tournament_size == 0:
                continue
            #choosing parent 1 and 2
            candidates = random.sample(list(zip(population, fitness_scores)), tournament_size)
            if not candidates:
                continue
            parent1 = max(candidates, key=lambda x: x[1])[0]
            candidates = random.sample(list(zip(population, fitness_scores)), tournament_size)
            if not candidates:
                continue
            parent2 = max(candidates, key=lambda x: x[1])[0]

            # Safety check before crossover
            assert is_valid(parent1, cluster), f"Invalid parent1: {parent1}"
            assert is_valid(parent2, cluster), f"Invalid parent2: {parent2}"

            child = pmx_crossover(parent1, parent2)

            # Mutation: swap two indices
            if random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]
                    # Final check before adding child to next generation

            if not is_valid(child, cluster):
                # logging.warning(f"Invalid child: {child}, parent1: {parent1}, parent2: {parent2}")
                # Option 1: fallback to one of the parents
                child = parent1.copy()
                
            new_population.append(child)
            
        population = new_population
        
        if generation % 10 == 0:
            best_fitness = max(fitness_scores) if fitness_scores else 0
            # 

    # Select top 5 solutions
    fitness_scores = [compute_fitness(pi) for pi in population]
    top_indices = np.argsort(fitness_scores)[-5:]
    top_solutions = [population[i] for i in top_indices]

    logging.info(f"GA completed, returning top solutions")

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
