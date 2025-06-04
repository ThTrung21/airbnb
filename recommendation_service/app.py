# app.py
from flask import Flask, jsonify,request
from waitress import serve
from search import  search_posts
import logging
from flask_cors import CORS
from recommendation import main as recommend_function
# Initialize the Flask app
app = Flask(__name__)


# CORS(app, resources={r"/search": {"origins": "*"}})
CORS(app, origins=["http://localhost:3000"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Define a GET endpoint to retrieve the posts with embeddings
@app.route("/search", methods=["GET"])
def get_posts():
    try:
        # Get embedded posts from the search module
        searchquery = request.args.get("query", "")
       
        results= search_posts(searchquery)
        # Return the posts as JSON
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommendation", methods = ["GET"])
def get_recommendations():
    try:
        userid = request.args.get("userId","")
        listings = recommend_function(userid)
        return jsonify(listings),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#===========================================================================
#running the server
# run app.py
if __name__ == "__main__":
    # Start the Flask app using Waitress
    logger.info("Starting the Flask API server...")
    serve(app, host="127.0.0.1", port=5000)
    logger.info("Server is running on http://127.0.0.1:5000")
