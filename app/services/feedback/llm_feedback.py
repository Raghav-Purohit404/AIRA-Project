#placeholder
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "phi3:latest"


def generate_llm_feedback(student, suggestions):

    prompt = f"""
    You are an expert placement mentor.

    Student Profile:
    Name: {student['name']}
    CGPA: {student['cgpa']}
    Skills: {', '.join(student['skills'])}
    Projects: {student['projects']}
    Internships: {student['internships']}

    Suggestions:
    {', '.join(suggestions)}

    Generate professional placement guidance in 120 words.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload
    )

    result = response.json()

    print(result)

    if "response" not in result:

        return {
            "error": result
        }

    return {
        "llm_feedback": result["response"]
    }


if __name__ == "__main__":

    sample_student = {

        "name": "BinLad",

        "cgpa": 8.4,

        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ],

        "projects": 4,

        "internships": 1
    }

    suggestions = [
        "Participate in hackathons"
    ]

    result = generate_llm_feedback(
        sample_student,
        suggestions
    )

    print(result)