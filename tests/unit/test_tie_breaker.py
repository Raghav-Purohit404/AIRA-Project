from app.services.aira.tie_breaker import (
    resolve_tie
)


def test_tie_breaker():

    student_a = {
        "cgpa": 8.9,
        "internships": 1
    }

    student_b = {
        "cgpa": 8.5,
        "internships": 2
    }

    winner = resolve_tie(
        student_a,
        student_b
    )

    print("\nWINNER:")
    print(winner)

    assert winner == student_a