from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)


def test_normalization():

    print("\n========== CGPA NORMALIZATION ==========")

    print("8.756  ->", normalize_cgpa(8.756))
    print("15     ->", normalize_cgpa(15))
    print("-2     ->", normalize_cgpa(-2))

    print("\n========== HACKATHON NORMALIZATION ==========")

    print("5      ->", normalize_hackathons(5))
    print("20     ->", normalize_hackathons(20))

    print("\n========== INTERNSHIP NORMALIZATION ==========")

    print("2      ->", normalize_internships(2))
    print("10     ->", normalize_internships(10))

    assert normalize_cgpa(15) == 10
    assert normalize_hackathons(20) == 10
    assert normalize_internships(10) == 5