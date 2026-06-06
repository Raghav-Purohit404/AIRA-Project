from app.services.similarity.profile_to_text import ProfileToTextConverter


def test_profile_conversion():
    profile = {
        "name": "Sam",
        "skills": ["Python", "FastAPI"],
        "cgpa": 9.1
    }

    text = ProfileToTextConverter.convert(profile)

    assert "Python" in text
    assert "FastAPI" in text