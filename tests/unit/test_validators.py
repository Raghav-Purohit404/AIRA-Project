from app.utils.validators import (
    validate_cgpa
)


def test_validator():

    result = validate_cgpa(8.5)

    print("\n========== VALIDATOR OUTPUT ==========")
    print("CGPA Validation Result:", result)

    assert result == True