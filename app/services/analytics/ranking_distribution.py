# placeholder
import json


def load_students():
    with open("data/mock/sample_students.json", "r") as file:
        return json.load(file)


def calculate_percentile(student_cgpa):

    students = load_students()

    cgpas = sorted([s["cgpa"] for s in students])

    below_count = sum(1 for cgpa in cgpas if cgpa < student_cgpa)

    percentile = (below_count / len(cgpas)) * 100

    if percentile >= 90:
        tier = "Top 10%"

    elif percentile >= 75:
        tier = "Top 25%"

    elif percentile >= 50:
        tier = "Top 50%"

    else:
        tier = "Below Top 50%"

    return {
        "percentile": round(percentile, 2),
        "tier": tier
    }


if __name__ == "__main__":

    result = calculate_percentile(8.4)

    print(result)
