import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class VectorDB:
    def __init__(self):
        self.vectors = np.array([])
        self.ids = []
        self.titles = []

    def add_vector(self, vector, vector_id, title):
        if self.vectors.size == 0:
            self.vectors = np.array([vector])
        else:
            self.vectors = np.vstack([self.vectors, vector])
        self.ids.append(vector_id)
        self.titles.append(title)

    def find_similar(self, query_vector, top_n=5):
        similarities = cosine_similarity([query_vector], self.vectors)
        indices = np.argsort(-similarities[0])[:top_n]
        return [(self.ids[i], self.titles[i], similarities[0][i]) for i in indices]
    
    def create_save(self, filename='vector-db-save'):
        with open(f'run_artifacts/{filename}', 'wb') as file:
            pickle.dump((self.vectors, self.ids, self.titles), file)

    def load(self, filename='vector-db-save'):
        with open(f'run_artifacts/{filename}', 'rb') as file:
            self.vectors, self.ids, self.titles = pickle.load(file)
