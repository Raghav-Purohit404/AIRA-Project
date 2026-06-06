from app.utils.validators import Validator


def test_validator():

    result = Validator.validate_cgpa(8.5)

    print("\n========== VALIDATOR OUTPUT ==========")
    print("CGPA Validation Result:", result)

    assert result == True