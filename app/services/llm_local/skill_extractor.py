from app.services.llm_local.llm_service import generate


def extract_skills(text: str):

    prompt = f"""
    Extract all technical skills from the following text.

    Return ONLY comma-separated skills.

    Text:
    {text}
    """

    result = generate(prompt)

    skills = [
        skill.strip()
        for skill in result.split(",")
        if skill.strip()
    ]

    return skills