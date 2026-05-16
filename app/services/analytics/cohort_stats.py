
import json


def load_students():
    with open("data/mock/sample_students.json", "r") as file:
        return json.load(file)


def generate_cohort_stats():
    students = load_students()

    total_students = len(students)

    avg_cgpa = sum(s["cgpa"] for s in students) / total_students
    avg_projects = sum(s["projects"] for s in students) / total_students
    avg_internships = sum(s["internships"] for s in students) / total_students

    return {
        "total_students": total_students,
        "average_cgpa": round(avg_cgpa, 2),
        "average_projects": round(avg_projects, 2),
        "average_internships": round(avg_internships, 2)
    }


if __name__ == "__main__":
    stats = generate_cohort_stats()
    print(stats)