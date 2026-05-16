# placeholder
import json


MEMORY_FILE = "data/mock/feedback_memory.json"


def load_memory():

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def update_feedback_memory(student_name, suggestions):

    memory = load_memory()

    if student_name not in memory:
        memory[student_name] = []

    for suggestion in suggestions:

        if suggestion not in memory[student_name]:
            memory[student_name].append(suggestion)

    save_memory(memory)

    return {
        "message": "Feedback memory updated",
        "stored_feedback": memory[student_name]
    }


if __name__ == "__main__":

    sample_suggestions = [
        "Improve project quality",
        "Participate in hackathons"
    ]

    result = update_feedback_memory(
        "BinLad",
        sample_suggestions
    )

    print(result)
