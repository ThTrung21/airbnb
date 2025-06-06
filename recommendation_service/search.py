# from pymongo import MongoClient
# from transformers import AutoModel, AutoTokenizer
# from sentence_transformers import SentenceTransformer
# import json
# import numpy as np

# model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# model = SentenceTransformer(model_name)

# # Replace this with your MongoDB URI
# MONGODB_URI = "mongodb+srv://trung:XAoFKu8ucSMULjCs@cluster0.mpt8ire.mongodb.net/test?retryWrites=true&w=majority"
# DB_NAME = "test"
# COLLECTION_NAME = "Post"

# # Connect to MongoDB
# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]
# posts_collection = db[COLLECTION_NAME]

# def get_embedded_posts():
#     # Fetch all posts from MongoDB
#     posts = list(posts_collection.find())

#     # Initialize an empty list to store the updated posts
#     embedded_posts = []

#     # Loop over each post
#     for post in posts:
#         title = post.get("title", "")
#         description = post.get("description", "")

#         # Create embeddings for title and description
#         title_embedding = model.encode(title)
#         description_embedding = model.encode(description)

#         post["_id"] = str(post["_id"])

#         # Add embeddings to the post
#         embedded_post = {}
        
#         embedded_post["str_id"]=str(post["_id"])
#         embedded_post["title_embedding"] = title_embedding.tolist()  # Convert numpy array to list for MongoDB
#         embedded_post["description_embedding"] = description_embedding.tolist()

#         # Append the updated post with embeddings to the list
#         embedded_posts.append(embedded_post)

#     return embedded_posts

# def cosine_similarity(vec1, vec2):
#     """Calculate cosine similarity between two vectors."""
#     dot_product = np.dot(vec1, vec2)
#     norm_vec1 = np.linalg.norm(vec1)
#     norm_vec2 = np.linalg.norm(vec2)
#     return dot_product / (norm_vec1 * norm_vec2)

# def search_posts(query):
#     embedded_posts= get_embedded_posts()
#     emb_query = model.encode(query)
    
#     scored_posts = []
#     for post in embedded_posts:
#         #get similarity score
#         title_similarity = cosine_similarity(emb_query, post["title_embedding"])
#         description_similarity = cosine_similarity(emb_query, post["description_embedding"])
        
#         #using whichever has higher score as that post similarity score
#         max_similarity = max(title_similarity, description_similarity)
#         scored_posts.append((post['str_id'], max_similarity))
#     scored_posts.sort(key=lambda x: x[1], reverse=True)
#     top_posts = [post for post, score in scored_posts[:15]]

#     return top_posts    

# def get_posts():
#     embedded_posts = get_embedded_posts()
#     print(embedded_posts[1])
#     # Print all posts
#     # for post in embedded_posts:
#     #     print(post)

# if __name__ == "__main__":
#     get_posts()
