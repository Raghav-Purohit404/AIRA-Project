def validate_cgpa(cgpa: float):

    if not (0 <= cgpa <= 10):
        raise ValueError(
            "CGPA must be between 0 and 10"
        )

    return True


def validate_internships(count: int):

    if count < 0:
        raise ValueError(
            "Internship count cannot be negative"
        )

    return True


def validate_hackathons(count: int):

    if count < 0:
        raise ValueError(
            "Hackathon count cannot be negative"
        )

    return True
