import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    def embed(self, text, quantize=True):
        embedding = self.model.encode(text)
        if quantize:
            embedding = self.quantize(embedding)
        return embedding

    def embed_batch(self, batch, quantize=True):
        embeddings = self.model.encode(batch)
        if quantize:
            embeddings = self.quantize(embeddings)
        return embeddings

    def quantize(self, emb):
        normalized_embedding = (emb - np.mean(emb)) / np.std(emb)
        clipped_embedding = np.clip(normalized_embedding, -3, 3)
        scaled_embedding = 255 * (clipped_embedding) / 6
        quantized_embedding = np.round(scaled_embedding).astype(np.int8)
        return quantized_embedding
