def resolve_tie(student_a: dict, student_b: dict):

    # Higher CGPA wins

    if student_a["cgpa"] > student_b["cgpa"]:
        return student_a

    if student_b["cgpa"] > student_a["cgpa"]:
        return student_b

    # More internships wins

    if student_a["internships"] > student_b["internships"]:
        return student_a

    if student_b["internships"] > student_a["internships"]:
        return student_b

    return "Tie"
