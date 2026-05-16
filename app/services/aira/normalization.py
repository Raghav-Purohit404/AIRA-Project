def normalize_cgpa(cgpa: float):

    if cgpa < 0:
        return 0

    if cgpa > 10:
        return 10

    return round(cgpa, 2)


def normalize_hackathons(count: int):

    if count < 0:
        return 0

    if count > 10:
        return 10

    return count


def normalize_internships(count: int):

    if count < 0:
        return 0

    if count > 5:
        return 5

    return count
