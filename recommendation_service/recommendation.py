import os
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
def get_context_features(user_id, listings):
    logging.info("Getting context features")
    if user_id and 'history' in user_id:
        history = user_id['history']
        avg_price = np.mean([listing['price'] for listing in history])
        avg_distance = np.mean([listing['distance'] for listing in history])
        avg_amenities = np.mean([len(listing['amenities']) for listing in history])
        context_features = [avg_price / max([l['price'] for l in listings]), 
                           avg_distance / max([l['distance'] for l in listings]), 
                           avg_amenities / max([len(l['amenities']) for l in listings]), 
                           1.0]
    else:
        context_features = [0.25, 0.25, 0.25, 0.25]
    return np.array(context_features)

# Step 1: K-Means Clustering
def kmeans_clustering(listings, K=5):
    logging.info("Running K-Means clustering")
    X = np.array([[l['price'], l['distance'], len(l['amenities'])] for l in listings])
    n_samples = len(X)
    K = min(K, n_samples)
    if n_samples == 0:
        logging.warning("No listings provided, returning empty clusters")
        return [[]]
    
    kmeans = KMeans(n_clusters=K, random_state=42)
    kmeans.fit(X)
    labels = kmeans.labels_
    clusters = [[] for _ in range(K)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)
    logging.info(f"Created {K} clusters")
    return clusters

# Step 2: Genetic Algorithm
def genetic_algorithm(cluster, listings, weights):
    logging.info(f"Running Genetic Algorithm for cluster with {len(cluster)} listings")
    
    # If cluster has 1 or fewer listings, return it as-is
    if len(cluster) <= 1:
        logging.info("Cluster too small for GA, returning as-is")
        return [cluster]  # Return single solution
    
    population_size = 50
    population = [random.sample(cluster, len(cluster)) for _ in range(population_size)]
    
    def compute_fitness(pi):
        score = 0
        for idx in pi:
            listing = listings[idx]
            price_match = 1 - abs(listing['price'] - np.mean([l['price'] for l in listings])) / max([l['price'] for l in listings])
            distance_match = 1 - listing['distance'] / max([l['distance'] for l in listings])
            amenities_match = len(set(listing['amenities']) & set(['wifi', 'kitchen'])) / 2
            rating = listing['rating'] / 5.0
            score += weights[0] * price_match + weights[1] * distance_match + weights[2] * amenities_match + weights[3] * rating
        return score / len(pi) if pi else 0
    
    for generation in range(50):
        fitness_scores = [compute_fitness(pi) for pi in population]
        new_population = []
        for _ in range(population_size):
            total_fitness = sum(fitness_scores)
            pick = random.uniform(0, total_fitness)
            current = 0
            for i, fitness in enumerate(fitness_scores):
                current += fitness
                if current > pick:
                    parent1 = population[i]
                    break
            pick = random.uniform(0, total_fitness)
            current = 0
            for i, fitness in enumerate(fitness_scores):
                current += fitness
                if current > pick:
                    parent2 = population[i]
                    break
            child = pmx_crossover(parent1, parent2)
            if random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]
            new_population.append(child)
        population = new_population
        if generation % 10 == 0:
            logging.info(f"GA Generation {generation}/50")
    
    fitness_scores = [compute_fitness(pi) for pi in population]
    top_indices = np.argsort(fitness_scores)[-5:]
    top_solutions = [population[i] for i in top_indices]
    logging.info("GA completed, returning top solutions")
    return top_solutions

def pmx_crossover(parent1, parent2):
    size = len(parent1)
    child = [None] * size
    start, end = sorted(random.sample(range(size), 2))
    child[start:end] = parent1[start:end]
    for i in range(start, end):
        if parent2[i] not in child:
            pos = i
            while child[pos] is not None:
                pos = parent2.index(parent1[pos])
            child[pos] = parent2[i]
    for i in range(size):
        if child[i] is None:
            child[i] = parent2[i]
    return child

# Step 3: Simulated Annealing
def simulated_annealing(top_solutions, listings, weights):
    logging.info("Running Simulated Annealing")
    T = 1000
    T_min = 0.1
    alpha = 0.95
    iterations_per_temp = 10
    
    def compute_fitness(pi):
        score = 0
        for idx in pi:
            listing = listings[idx]
            price_match = 1 - abs(listing['price'] - np.mean([l['price'] for l in listings])) / max([l['price'] for l in listings])
            distance_match = 1 - listing['distance'] / max([l['distance'] for l in listings])
            amenities_match = len(set(listing['amenities']) & set(['wifi', 'kitchen'])) / 2
            rating = listing['rating'] / 5.0
            score += weights[0] * price_match + weights[1] * distance_match + weights[2] * amenities_match + weights[3] * rating
        return score / len(pi) if pi else 0
    
    best_solution = top_solutions[0]
    best_fitness = compute_fitness(best_solution)
    
    for solution in top_solutions:
        current_solution = solution
        current_fitness = compute_fitness(current_solution)
        iteration = 0
        while T > T_min:
            for _ in range(iterations_per_temp):
                neighbor = deepcopy(current_solution)
                i, j = random.sample(range(len(neighbor)), 2)
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbor_fitness = compute_fitness(neighbor)
                delta_f = neighbor_fitness - current_fitness
                if delta_f >= 0 or random.random() < np.exp(delta_f / T):
                    current_solution = neighbor
                    current_fitness = neighbor_fitness
                if current_fitness > best_fitness:
                    best_solution = current_solution
                    best_fitness = current_fitness
            T *= alpha
            iteration += 1
            if iteration % 10 == 0:
                logging.info(f"SA Temperature {T:.2f}")
    logging.info("SA completed")
    return best_solution

# Modified Hybrid Metaheuristic Recommendation
def hybrid_metaheuristic_recommendation(listings, user_id=None):
    logging.info("Starting hybrid metaheuristic recommendation")
    
    # Fixed weights (equal importance)
    weights = np.array([0.25, 0.25, 0.25, 0.8])
    logging.info(f"Using fixed weights: {weights}")
    
    context_features = get_context_features(user_id, listings)
    
    # Use clustering for larger datasets, single cluster for small ones
    if len(listings) <= 5:
        logging.info("Small dataset, treating as single cluster")
        clusters = [list(range(len(listings)))]
    else:
        clusters = kmeans_clustering(listings, K=5)
    
    ranked_indices = []
    for cluster in clusters:
        if not cluster:
            continue
        top_solutions = genetic_algorithm(cluster, listings, weights)
        best_solution = simulated_annealing(top_solutions, listings, weights)
        ranked_indices.extend(best_solution)
    
    result = {
        "ranked_listings": [
            {
                "index": idx,
                "price": listings[idx]["price"],
                "distance": listings[idx]["distance"],
                "amenities": listings[idx]["amenities"],
                "rating": listings[idx]["rating"]
            } for idx in ranked_indices
        ]
    }
    
    logging.info("Recommendation completed, returning JSON")
    return json.dumps(result, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    # listings = [
    #     {'price': 100, 'distance': 2.0, 'amenities': ['wifi', 'kitchen'], 'rating': 4.5},
    #     {'price': 150, 'distance': 1.5, 'amenities': ['wifi'], 'rating': 4.0},
    #     {'price': 80, 'distance': 3.0, 'amenities': ['kitchen'], 'rating': 3.5},
    #     {'price': 200, 'distance': 0.5, 'amenities': ['wifi', 'kitchen', 'pool'], 'rating': 4.8}
    # ]
    listings = [
        {'price': 100, 'distance': 2.0, 'amenities': ['wifi', 'kitchen'], 'rating': 4.5},
        {'price': 150, 'distance': 1.5, 'amenities': ['wifi'], 'rating': 4.0},
        {'price': 80, 'distance': 3.0, 'amenities': ['kitchen'], 'rating': 3.5},
        {'price': 120, 'distance': 1.2, 'amenities': ['wifi', 'tv', 'air conditioning'], 'rating': 4.6},
        {'price': 95, 'distance': 2.5, 'amenities': ['wifi', 'kitchen', 'hair dryer'], 'rating': 4.2},
        {'price': 150, 'distance': 0.8, 'amenities': ['wifi', 'tv', 'mini fridge'], 'rating': 4.9},
        {'price': 75, 'distance': 3.6, 'amenities': ['wifi', 'fan'], 'rating': 3.8},
        {'price': 200, 'distance': 0.3, 'amenities': ['wifi', 'tv', 'jacuzzi', 'mini bar'], 'rating': 5.0},
        {'price': 65, 'distance': 4.2, 'amenities': ['wifi', 'desk'], 'rating': 3.1},
        {'price': 110, 'distance': 2.0, 'amenities': ['wifi', 'tv', 'iron', 'safe'], 'rating': 4.4},
        {'price': 85, 'distance': 3.1, 'amenities': ['wifi', 'tv', 'kitchen'], 'rating': 3.9},
        {'price': 140, 'distance': 1.5, 'amenities': ['wifi', 'tv', 'balcony'], 'rating': 4.7},
        {'price': 90, 'distance': 3.3, 'amenities': ['wifi', 'tv', 'hair dryer'], 'rating': 3.6},
        {'price': 180, 'distance': 0.9, 'amenities': ['wifi', 'jacuzzi', 'air conditioning'], 'rating': 4.8},
        {'price': 70, 'distance': 4.0, 'amenities': ['wifi', 'fan', 'desk'], 'rating': 3.4},
        {'price': 130, 'distance': 1.1, 'amenities': ['wifi', 'tv', 'safe'], 'rating': 4.5},
        {'price': 100, 'distance': 2.8, 'amenities': ['wifi', 'mini fridge', 'tv'], 'rating': 4.0},
        {'price': 160, 'distance': 0.7, 'amenities': ['wifi', 'tv', 'mini bar', 'balcony'], 'rating': 4.9},
        {'price': 85, 'distance': 3.9, 'amenities': ['wifi', 'tv'], 'rating': 3.5},
        {'price': 115, 'distance': 2.1, 'amenities': ['wifi', 'air conditioning', 'iron'], 'rating': 4.3},
        {'price': 105, 'distance': 2.6, 'amenities': ['wifi', 'tv', 'hair dryer'], 'rating': 4.1},
        {'price': 55, 'distance': 5.0, 'amenities': ['wifi'], 'rating': 2.9},
        {'price': 125, 'distance': 1.0, 'amenities': ['wifi', 'tv', 'kitchen', 'safe'], 'rating': 4.6},
        {'price': 200, 'distance': 0.5, 'amenities': ['wifi', 'kitchen', 'pool'], 'rating': 4.8}
    ]
    user_id = {'history': [{'price': 120, 'distance': 2.5, 'amenities': ['wifi', 'kitchen']}]}
    
    json_output = hybrid_metaheuristic_recommendation(listings, user_id)
    print("JSON Output:")
    print(json_output)



