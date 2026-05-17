
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityService:
    """Handles embedding generation and similarity scoring."""

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text: str):
        return self.model.encode(text)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        embedding1 = self.generate_embedding(text1)
        embedding2 = self.generate_embedding(text2)

        similarity = cosine_similarity(
            [embedding1],
            [embedding2]
        )[0][0]

        return round(float(similarity), 4)