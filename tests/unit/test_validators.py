import pytest

from app.utils.validators import validate_cgpa


def test_validate_cgpa_accepts_valid_value() -> None:
    assert validate_cgpa(8.5) == 8.5


def test_validate_cgpa_rejects_out_of_range_value() -> None:
    with pytest.raises(ValueError):
        validate_cgpa(10.5)
