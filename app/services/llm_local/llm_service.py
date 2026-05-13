import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "phi3:3.8b"


def generate(prompt: str):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]