from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)


def test_normalization():

    print("\nCGPA TESTS:")
    print(normalize_cgpa(8.756))
    print(normalize_cgpa(15))
    print(normalize_cgpa(-2))

    print("\nHACKATHON TESTS:")
    print(normalize_hackathons(5))
    print(normalize_hackathons(20))

    print("\nINTERNSHIP TESTS:")
    print(normalize_internships(2))
    print(normalize_internships(10))

    assert normalize_cgpa(15) == 10
    assert normalize_hackathons(20) == 10
    assert normalize_internships(10) == 5