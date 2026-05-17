from app.services.similarity.similarity_service import SimilarityService


service = SimilarityService()


def test_similarity_score():
    text1 = "Python FastAPI developer"
    text2 = "Backend developer using Python"

    score = service.calculate_similarity(text1, text2)

    assert score > 0