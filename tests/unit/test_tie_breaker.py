"""Tests for AIRA tie-breaking."""

from app.services.aira.tie_breaker import TieBreakCandidate, break_ties, rank_candidate_dicts


def test_break_ties_uses_configured_priority() -> None:
    """CGPA should break equal-score ties before activity counts."""
    candidates = [
        TieBreakCandidate(candidate_id="a", score=80, cgpa=8.0, internships=2, projects=3, hackathons=1),
        TieBreakCandidate(candidate_id="b", score=80, cgpa=8.5, internships=0, projects=1, hackathons=0),
    ]

    assert break_ties(candidates)[0].candidate_id == "b"


def test_rank_candidate_dicts_adds_rank() -> None:
    """Dictionary ranking should preserve data and add one-based ranks."""
    ranked = rank_candidate_dicts(
        [
            {"candidate_id": "a", "score": 90, "cgpa": 8},
            {"candidate_id": "b", "score": 91, "cgpa": 7},
        ]
    )

    assert ranked[0]["candidate_id"] == "b"
    assert ranked[0]["rank"] == 1


def test_tie_breaker_uses_internships_after_cgpa() -> None:
    """Internships should break ties when score and CGPA are equal."""
    candidates = [
        TieBreakCandidate(candidate_id="a", score=80, cgpa=8.0, internships=1, projects=4, hackathons=3),
        TieBreakCandidate(candidate_id="b", score=80, cgpa=8.0, internships=2, projects=1, hackathons=0),
    ]

    assert break_ties(candidates)[0].candidate_id == "b"
