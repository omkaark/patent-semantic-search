import requests
from bs4 import BeautifulSoup
from semantic.embed import Embedder
from semantic.db import VectorDB
import logging
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_patent(session, patent_id):
    try:
        url = f"https://patents.google.com/patent/{patent_id}/en"
        r = session.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        title = soup.find('span', {'itemprop': 'title'}).get_text(strip=True)
        description = soup.find('meta', {'name':'description'}).get('content').strip()

        return patent_id, title, description
    except Exception as e:
        logging.error(f"Error scraping patent {patent_id}: {e}")
        return patent_id, None, None

def process_batch(batch_ids, session, embedder, vector_db):
    batch_data = [scrape_patent(session, patent_id) for patent_id in batch_ids]

    # Filter out None results
    valid_data = [(pid, title, desc) for pid, title, desc in batch_data if title and desc]

    # Process valid results
    if valid_data:
        descriptions = [desc for _, _, desc in valid_data]
        embeddings = embedder.embed_batch(descriptions)
        
        for (patent_id, title, _), embedding in zip(valid_data, embeddings):
            vector_db.add_vector(embedding, patent_id, title)
            logging.info(f"Processed and added patent {patent_id} to VectorDB")

    vector_db.create_save()

def main():
    embedder = Embedder()
    vector_db = VectorDB()

    batch_size = 100

    # Using a session for efficient network requests
    with requests.Session() as session, open('run_artifacts/crawler-2020-2021.txt', 'r') as file:
        patent_ids = [line.strip() for line in file]

        # Divide patent IDs into batches
        batches = [patent_ids[i:i + batch_size] for i in range(0, len(patent_ids), batch_size)]

        # Using ThreadPoolExecutor for parallel processing of batches
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda batch: process_batch(batch, session, embedder, vector_db), batches)

    logging.info("Completed processing all patents and saved VectorDB")

if __name__ == "__main__":
    main()
