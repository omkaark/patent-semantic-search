from semantic.embed import Embedder
from semantic.db import VectorDB
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    embedder = Embedder()
    vector_db = VectorDB()
    vector_db.load('vector-db-save')
    while True:
        user_input = input("Enter your search query (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        query_embedding = embedder.embed(user_input)
        similar_patents = vector_db.find_similar(query_embedding, top_n=3)
        if similar_patents:
            print("Top similar patents:")
            for patent_id, title, similarity in similar_patents:
                print(f"ID: {patent_id}, Title: {title}, Similarity: {similarity}")
        else:
            print("No similar patents found.")

if __name__ == "__main__":
    main()

# Wind Turbine
# Automobile brake
# trust in blockchain