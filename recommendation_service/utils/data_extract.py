import json
import logging
from pymongo import MongoClient
from typing import Dict, List
from dotenv import load_dotenv
import os
from collections import defaultdict
from bson import ObjectId
load_dotenv()
MONGO_URI = os.getenv("DATABASE_URL")

DATABASE_NAME = "test"



# # Collections and desired fields
# FIELDS = {
#     "User": {"_id": 1, "favoriteListingIds": 1},
#     "Listing": {
#         "_id": 1, "category": 1, "roomCount": 1, "bathroomCount": 1,
#         "guestCount": 1, "locationValue": 1, "price": 1
#     },
#     "Rating": {"_id": 1, "userId": 1, "listingId": 1, "stars": 1},
#     "Reservation": {"_id": 1, "userId": 1, "listingId": 1}
# }


def fetch_user_data(user_id: str) -> Dict:
    """
    Fetch user-specific data from MongoDB, converting ObjectId to strings.

    Args:
        user_id: User ID (string, converted to ObjectId for queries).

    Returns:
        Dictionary containing listings, ratings, reservations, and favorite IDs (strings).
    """
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DATABASE_NAME]

            listings = list(db["Listing"].find({}, {
                "_id": 1, "category": 1, "roomCount": 1, "bathroomCount": 1,
                "guestCount": 1, "locationValue": 1, "price": 1
            }))

            ratings = list(db["Rating"].find({}, {
                "_id": 1, "userId": 1, "listingId": 1, "stars": 1
            }))

            reservations = list(db["Reservation"].find({"userId": ObjectId(user_id)}, {
                "_id": 1, "userId": 1, "listingId": 1
            }))

            user = db["User"].find_one({"_id": ObjectId(user_id)}, {"favoriteIds": 1})
            favorite_ids = user.get("favoriteIds", []) if user else []

            def convert_object_ids(doc):
                return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}

            listings = [convert_object_ids(doc) for doc in listings]
            ratings = [convert_object_ids(doc) for doc in ratings]
            reservations = [convert_object_ids(doc) for doc in reservations]
            favorite_ids = [str(fid) for fid in favorite_ids]
            #print(json.dumps(listings, indent=4))
            logging.debug(f"Fetched {len(listings)} listings: {json.dumps(listings, ensure_ascii=False, indent=4)}")
            return {
                "Listing": listings,
                "Rating": ratings,
                "Reservation": reservations,
                "FavoriteIds": favorite_ids  # List[str]
            }
    except Exception as e:
        logging.error(f"Error fetching user data for user_id {user_id}: {e}")
        raise

def calculate_average_ratings(ratings):
    """
    Calculate the average rating for each listing.

    Args:
        ratings (list[dict]): List of rating objects, each with:
            - listingId (objectid)
            - stars (int)

    Returns:
        dict[str, float]: Dictionary of listingId to average star rating.
    """
    if not ratings:
        return {}
    rating_totals = defaultdict(int)
    rating_counts = defaultdict(int)

    for rating in ratings:
        listing_id = rating["listingId"]
        stars = rating["stars"]
        if not isinstance(stars, (int, float)) or stars < 1 or stars > 5:
            continue  # Skip invalid ratings
        rating_totals[listing_id] += stars
        rating_counts[listing_id] += 1

    # Compute averages
    average_ratings = {
        listing_id: round(rating_totals[listing_id] / rating_counts[listing_id], 2)
        for listing_id in rating_totals
    }

    return average_ratings

def enrich_listings_with_ratings(listings: List[Dict], avg_ratings: Dict[str, float]) -> List[Dict]:
    """
    Enrich listings with their average ratings.

    Args:
        listings: List of listing objects, each with _id.
        avg_ratings: Dictionary of listingId to average rating.

    Returns:
        New list of listings with averageRating field added.
    """
    enriched_listings = [
        {**listing, "averageRating": avg_ratings.get(listing["_id"], 0.0)}
        for listing in listings
    ]
    return enriched_listings

def main():
    data = fetch_user_data("66b0e2db49a8913674a6b869")

    # Calculate average ratings
    average_ratings = calculate_average_ratings(data["Rating"])

    # Attach average rating to each listing
    for listing in data["Listing"]:
        listing_id = str(listing["_id"])
        listing["averageRating"] = average_ratings.get(listing_id, None)
    print(json.dumps(data,indent=4))
    return data



if __name__ == "__main__":
    full_data = main()
    # # You can now use or save `full_data`
    # print(full_data["Listing"][:3])  # Example: print first 3 listings with ratings
    # fetch_user_data("66ab891c93d8ddbc50eec701")