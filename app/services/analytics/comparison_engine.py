# placeholder
from app.services.analytics.cohort_stats import generate_cohort_stats


def compare_student(student):
    cohort = generate_cohort_stats()

    comparison = {}

    if student["cgpa"] >= cohort["average_cgpa"]:
        comparison["cgpa_status"] = "Above Average"
    else:
        comparison["cgpa_status"] = "Below Average"

    if student["projects"] >= cohort["average_projects"]:
        comparison["project_status"] = "Strong"

    else:
        comparison["project_status"] = "Needs Improvement"

    if student["internships"] >= cohort["average_internships"]:
        comparison["internship_status"] = "Good"

    else:
        comparison["internship_status"] = "Low"

    return comparison


if __name__ == "__main__":

    sample_student = {
        "name": "BinLad",
        "cgpa": 8.4,
        "projects": 4,
        "internships": 1
    }

    result = compare_student(sample_student)

    print(result)