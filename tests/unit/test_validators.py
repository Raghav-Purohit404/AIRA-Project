from app.utils.validators import (
    validate_cgpa
)


def test_validator():

    assert validate_cgpa(8.5) == True