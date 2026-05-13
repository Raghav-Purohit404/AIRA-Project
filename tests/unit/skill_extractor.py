from app.services.llm_local.skill_extractor import extract_skills


def test_extract_skills():

    text = """
    Developed a machine learning dashboard using
    Python, FastAPI, React, Docker and PostgreSQL.
    """

    skills = extract_skills(text)

    print("\nExtracted Skills:")
    print(skills)

    assert isinstance(skills, list)